import re
from typing import Dict
from typing import Optional
from argparse import ArgumentParser
from subprocess import CalledProcessError
from rkd.contract import TaskInterface, ExecutionContext
from rkd.syntax import TaskDeclaration
from rkd.standardlib.docker import TagImageTask
from rkd.standardlib.docker import PushTask
from .github import ForEachGithubReleaseTask
from .github import FindClosestReleaseTask
from .docker import DockerTagExistsTask
from .tools import VersionTools, GitTools


class ProcessRequestTask(TaskInterface):
    """Takes incoming request from the CI

    Responsibility:
        - Decide about the destination version number and format
        - Decide if we REBUILD existing tags or not (release enforces this)
    """

    def get_name(self) -> str:
        return ':process'

    def get_group_name(self) -> str:
        return ':boat-ci'

    def execute(self, context: ExecutionContext) -> bool:
        self.io().h1('BOAT CI - Shifts everything into the Harbor')

        # input
        commit_message: str = context.args['commit_message']
        cmd_to_exec: str = context.args['exec']
        task_type: str = context.args['type']
        git_tag: str = GitTools.get_current_tag() if GitTools.is_currently_on_tag() else ''

        # logic
        rebuild = False
        tag_template = context.args['dev_version_template']

        if GitTools.is_currently_on_tag():
            self.io().h4('Rebuilding as currently on a tag')
            rebuild = True
            tag_template = context.args['release_version_template']

        if "@force-rebuild" in commit_message:
            self.io().h4('Rebuilding as @force-rebuild specified')
            rebuild = True

        if "@force-rebuild-last-tag" in commit_message:
            self.io().h4('Rebuilding last tag - @force-rebuild-last-tag specified')
            git_tag = GitTools.get_last_tag()
            tag_template = context.args['release_version_template']

        # Parsing
        tag_template = self._parse_template_str(
            tag_template,
            task_type=task_type,
            should_rebuild=rebuild,
            version='',
            git_tag=git_tag
        )

        self.io().h4('Boat-CI produced tag template: %s' % tag_template)

        cmd_to_exec = self._parse_template_str(
            cmd_to_exec,
            task_type=task_type,
            should_rebuild=rebuild,
            version=tag_template,
            git_tag=git_tag
        )

        try:
            self.sh('set -x; %s' % cmd_to_exec, verbose=True)
        except CalledProcessError as e:
            self.io().error_msg(str(e))
            return False

        return True

    def _parse_template_str(self, template: str, task_type: str, should_rebuild: bool, git_tag: str,
                            version: str = '') -> str:
        parsed = template

        if "%NEXT_VERSION%" in template:
            parsed = parsed.replace('%NEXT_VERSION%', VersionTools.get_next_version())

        parsed = parsed.replace('%REBUILD_FLAG%', '' if should_rebuild else ' --dont-rebuild-when-exists')

        if version:
            parsed = parsed.replace('%VERSION%', version)

        if task_type in ['each-release', 'specific-release']:
            task_type = self.get_group_name() + ':' + task_type

        parsed = parsed.replace('%RELEASE_TASK%', task_type)\
            .replace('%VERSION_TEMPLATE%', version)\
            .replace('%GIT_TAG%', git_tag)

        return parsed

    def configure_argparse(self, parser: ArgumentParser):
        # CI input
        parser.add_argument('--commit-message', required=True, help='Commit message')

        # Build mode
        parser.add_argument(
            '--type', '-t',
            default='each-release',
            help='Task type, or task name eg. each-release, specific-release. Pasted as %RELEASE_TASK% to the --exec'
        )
        parser.add_argument(
            '--exec', '-e',
            help='Build task name. Defaults to building all releases from github',
            default='rkd --no-ui %RELEASE_TASK% -rl info %REBUILD_FLAG% --version-template="%VERSION_TEMPLATE%"'
        )
        parser.add_argument('--dev-version-template', default='%MATCH_0%-SNAPSHOT',
                            help='Examples: %MATCH_0%-D%NEXT_VERSION%-SNAPSHOT')
        parser.add_argument('--release-version-template', default='%MATCH_0%-D%GIT_TAG%')


class EachRelease(TaskInterface):
    def get_name(self) -> str:
        return ':each-release'

    def get_group_name(self) -> str:
        return ':boat-ci'

    def execute(self, context: ExecutionContext) -> bool:
        # input
        allowed_tags_regexp: str = context.get_env('ALLOWED_TAGS_REGEXP')
        dest_docker_repo: str = context.get_env('DEST_DOCKER_REPO')
        max_versions: int = int(context.get_env('MAX_VERSIONS'))
        github_repository: str = context.get_env('GITHUB_REPOSITORY')
        version_template: str = context.args['version_template']
        rebuild: bool = not context.args['dont_rebuild_when_exists']
        version_build_cmd: str = context.get_env('VERSION_BUILD_CMD')\
            .replace('%VERSION_TEMPLATE%', version_template)\
            .replace('%IMAGE%', dest_docker_repo)

        opts = ''

        if not rebuild:
            opts += ' --dont-rebuild '

        cmd = ('set -x; rkd :github:for-each-release --repository=%s --exec="%s" ' +
               ' --dest-docker-repo="%s" --allowed-tags-regexp="%s" ' +
               '--release-tag-template="%s" --max-versions=%i %s') % (
            github_repository,
            version_build_cmd,
            dest_docker_repo,
            allowed_tags_regexp,
            version_template,
            max_versions,
            opts
        )

        try:
            self.sh(cmd)
        except CalledProcessError as e:
            self.io().error_msg(str(e))
            return False

        return True

    def get_declared_envs(self) -> Dict[str, str]:
        return {
            'ALLOWED_TAGS_REGEXP': 'v([0-9.]+)',
            'DEST_DOCKER_REPO': '',
            'MAX_VERSIONS': '2',
            'GITHUB_REPOSITORY': '',
            'VERSION_BUILD_CMD': 'rkd :boat-ci:specific-release --dockerfile=./Dockerfile ' +
                                 ' --dir=. --docker-version="%VERSION_TEMPLATE%" --app-version="%MATCH_0%" ' +
                                 ' --dest-docker-repo=%IMAGE%'
        }

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument(
            '--dont-rebuild-when-exists',
            action='store_true'
        )
        parser.add_argument('--version-template', required=True)


class SpecificRelease(TaskInterface):
    """ Performs a docker build & tag & push """

    def get_name(self) -> str:
        return ':specific-release'

    def get_group_name(self) -> str:
        return ':boat-ci'

    def get_declared_envs(self) -> Dict[str, Optional[str]]:
        return {
            'DOCKER_BUILD_OPTS': None,
            'DEST_DOCKER_REPO': None,
            'DOCKERFILE': None,
            'DIR': None
        }

    def execute(self, context: ExecutionContext) -> bool:
        # facts
        work_dir = context.get_arg_or_env('--dir')
        dockerfile_path = context.get_arg_or_env('--dockerfile')
        image = context.get_arg_or_env('--dest-docker-repo')
        image_version = context.args['docker_version']
        app_version = context.args['app_version']
        opts = self._parse_opts(context.get_arg_or_env('--docker-build-opts'), app_version)
        push: bool = not bool(context.args['no_push'])

        # complete docker image address with version
        tag = image + ':' + image_version

        # build & tag & publish
        if not self.silent_sh(('docker build %s -f %s -t %s %s ' +
                               '--build-arg RKT_APP_VERSION="%s" --build-arg RKT_IMG_VERSION=%s') %
                              (work_dir, dockerfile_path, tag, opts, app_version, image_version),
                              verbose=True):
            self.io().error('Cannot build docker image')
            return False

        self.rkd([':docker:tag', '--image=%s' % tag, '--propagate', '-rl=debug'], verbose=True)

        if push:
            self.rkd([':docker:push', '--image=%s' % tag, '--propagate', '-rl=debug'], verbose=True)

        return True

    def _parse_opts(self, template: str, app_version: str) -> str:
        """Templating - allows to append additional information to build args of the Docker image

        Example case:
            --build-arg FRONTEND_VERSION=%FIND_CLOSEST_RELEASE(taigaio/taiga-front-dist)%
            To find and paste a closest matching release of Taiga frontend, when building the backend.
            The algorithm is in :github:find-closest-release task and is always reproducible.
        """

        if '%FIND_CLOSEST_RELEASE' in template:
            all_matches = re.findall('%FIND_CLOSEST_RELEASE\((.*)\)%', template)

            for match in all_matches:
                template = template.replace(
                    '%%FIND_CLOSEST_RELEASE(%s)%%' % match,
                    self.sh(' '.join([
                        'rkd', '--silent',
                        ':github:find-closest-release',
                        '--repository=%s' % match,
                        '--compare-with=%s' % app_version
                    ]), capture=True).strip()
                )

        return template

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('--dockerfile', '-f', help='Path to Dockerfile', default='./Dockerfile')
        parser.add_argument('--dir', '-d', help='Build directory / build root')
        parser.add_argument('--docker-version', '-v', required=True, help='Version of the docker image (image tag)')
        parser.add_argument('--dest-docker-repo', '-i', help='Image eg. quay.io/riotkit/tunman')
        parser.add_argument('--app-version', '-av', help='Application version')
        parser.add_argument('--docker-build-opts', '-o', default=None,
                            help='Docker build opts eg. --build-arg SOME=THING')
        parser.add_argument('--no-push', help='Don\'t push to docker registry', action='store_true')


def imports():
    return [
        TaskDeclaration(EachRelease()),
        TaskDeclaration(ProcessRequestTask()),
        TaskDeclaration(SpecificRelease()),

        # dependencies
        TaskDeclaration(ForEachGithubReleaseTask()),
        TaskDeclaration(FindClosestReleaseTask()),
        TaskDeclaration(TagImageTask()),
        TaskDeclaration(PushTask()),
        TaskDeclaration(DockerTagExistsTask())
    ]
