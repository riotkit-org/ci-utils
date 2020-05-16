from abc import ABC
from typing import Union, Pattern, Match

import requests
import time
import re
import subprocess
from argparse import ArgumentParser
from rkd.contract import TaskInterface, ExecutionContext


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]

    return sorted(l, key=alphanum_key)


class BaseGithubTask(TaskInterface, ABC):
    def get_group_name(self) -> str:
        return ':github'

    def get_available_tags(self, url: str, sleep_time: int, retries: int = 5) -> list:
        """ Lists all tags from github project """

        tags_url = url + '/tags'
        self.io().h2('Getting latest github releases from %s' % tags_url)

        try:
            response = requests.get(tags_url).json()

            if "message" in response and response['message'] == 'Not Found':
                raise Exception('Repository on github not found')

            return list(map(
                lambda tag_object: str(tag_object['name']),
                response
            ))
        except TypeError:
            if retries <= 0:
                raise

            time.sleep(sleep_time)
            return self.get_available_tags(url, sleep_time, retries - 1)

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('--retries', '-r', default='5', help='Maximum number of retries in request to github')
        parser.add_argument('--retry-wait', '-w', default='5', help='Amount of seconds between retries')
        parser.add_argument('--repository', '-n', required=True, help='Repository name eg. riotkit-org/filerepository')


class FindClosestReleaseTask(BaseGithubTask):
    """ Find a github release that is closest to the selected number """

    def get_name(self) -> str:
        return ':find-closest-release'

    def execute(self, context: ExecutionContext) -> bool:
        url = 'https://api.github.com/repos/%s' % context.args['repository']

        self._io.out(self.find_closest_version(
            version=context.args['compare_with'],
            url=url,
            sleep_time=int(context.args['retry_wait']),
            retries=int(context.args['retries'])
        ))

        return True

    def configure_argparse(self, parser: ArgumentParser):
        super().configure_argparse(parser)
        parser.add_argument('--compare-with', '-c', required=True, help='Version to compare with')

    def find_closest_version(self, version: str, url: str, sleep_time: int, retries: int) -> str:
        all_versions = self.get_available_tags(url, sleep_time, retries)

        if version in all_versions:
            return version

        all_versions += [version]
        sorted_desc = list(reversed(natural_sort(all_versions)))
        current_version_position = sorted_desc.index(version)

        if len(sorted_desc) == 1:
            return version

        if current_version_position == len(sorted_desc) - 1:
            return sorted_desc[len(sorted_desc) - 2]

        return sorted_desc[current_version_position + 1]


class ForEachGithubReleaseTask(BaseGithubTask):
    """ Iterate over recent X github releases and execute a task """

    def get_name(self) -> str:
        return ':for-each-release'

    def execute(self, context: ExecutionContext) -> bool:
        self.io().h1('Iterating over each github release')

        url = 'https://api.github.com/repos/%s' % context.args['repository']
        force_rebuild = not context.args['dont_rebuild']
        tags = self.get_available_tags(
            url,
            int(context.args['retry_wait']),
            int(context.args['retries'])
        )
        self.io().h4('Release tag template is "%s"' % context.args['release_tag_template'])

        return self.print_last_versions(
            tags=tags,
            max_versions=int(context.args['max_versions']),
            allowed_tags_regexp=re.compile(context.args['allowed_tags_regexp']) \
            if context.args['allowed_tags_regexp'] else None,
            release_tag_template=context.args['release_tag_template'],
            force_rebuild=force_rebuild,
            build_command=context.args['exec'],
            dest_docker_repo=context.args['dest_docker_repo'],
            dry_run=bool(context.args['dry_run'])
        )

    def print_last_versions(self, tags: list, max_versions: int, allowed_tags_regexp: Union[Pattern, None],
                            release_tag_template: str, force_rebuild: bool, build_command: str,
                            dest_docker_repo: str, dry_run: bool):
        to_build = {}
        result = True

        self.io().print_opt_line()
        self.io().h1('Parsing GIT tags to find out those that are release tags')

        # collect items to build
        for tag in tags:
            properties = None

            if allowed_tags_regexp:
                matches = allowed_tags_regexp.match(tag)
                if not matches:
                    self.io().h2("Not matched tag \"%s\"" % tag)
                    continue

                self.io().h2('Matched %s' % tag)
                properties = matches

            to_build[tag] = properties

        processed = 0
        self.io().h1('Processing tags (max amount: %i)' % max_versions)

        for git_tag, matches in to_build.items():
            if 0 < max_versions <= processed:
                break

            release_tag = self.create_release_tag(git_tag, matches, release_tag_template)

            if not force_rebuild and self.was_already_built(dest_docker_repo, release_tag):
                self.io().h2('Skipping "%s" as the docker tag already exists' % release_tag)
                processed += 1
                continue

            command = self.render_template(build_command, git_tag, matches)

            self.io().h2('Calling generated command %s' % command)

            if not dry_run:
                try:
                    self.sh(command)
                except subprocess.CalledProcessError:
                    result = False

            processed += 1
            self.io().print_separator()
            self.io().print_opt_line()

        return result

    def create_release_tag(self, git_tag: str, matches: Union[Match, None], release_tag_template: str):
        return self.render_template(release_tag_template, git_tag, matches, False)

    def render_template(self, original_text: str, git_tag: str,
                        matches: [Union, Match, None], with_release_tag: bool = True):

        """ Inject variable values into the template ex. input: release-%GIT_TAG% output: release-1.0.5 """

        text = original_text \
            .replace('%GIT_TAG%', git_tag)

        groups = matches.groups() if matches else None

        if groups:
            for match_num in range(0, len(groups)):
                text = text.replace('%MATCH_' + str(match_num) + '%', groups[match_num])

        if with_release_tag:
            text = text.replace('%RELEASE_TAG%', self.create_release_tag(git_tag, matches, original_text))

        self.io().h3('render_template(): "%s" into "%s"' % (original_text, text))

        return text

    def was_already_built(self, image_name: str, docker_tag: str) -> bool:
        """ Checks if the docker tag was already pushed """

        self.io().h3('Checking if docker tag "%s" was already pushed' % docker_tag)

        try:
            self.rkd([':docker:tag-exists', '--image=%s:%s' % (image_name, docker_tag)], verbose=True)
            return True

        except subprocess.CalledProcessError as e:
            if e.returncode == 127:
                raise Exception(':docker-tag-exists command is not registered')

            return False

    def configure_argparse(self, parser: ArgumentParser):
        super().configure_argparse(parser)

        parser.description = "For each released version of application on github perform a command. " + \
                             "Example: rkd :github:for-each-release --repository=riotkit-org/file-repository " + \
                             "--exec 'echo \"[%MATCH_0%]\"' --dest-docker-repo quay.io/riotkit/file-repository " + \
                             "-tr 'v([0-9.]+)'"

        parser.add_argument('--dest-docker-repo',
                            help='Docker repository ex. quay.io/riotkit/phpbb',
                            required=True)
        parser.add_argument('--exec', '-e',
                            help='Command to execute. Variables: %%GIT_TAG%% (original git tag name), ' +
                                 '%%MATCH_0%% (regexp match-0), ' +
                                 '%%MATCH_N%% (regexp match-N), %%RELEASE_TAG%% ' +
                                 '(defined by --release-tag-template)',
                            default='echo "%%GIT_TAG%%"')
        parser.add_argument('--dont-rebuild', '-dr',
                            help='Do not build the same version twice ' +
                                 '(checks existence of a docker tag for --docker-repo)',
                            action='store_true')
        parser.add_argument('--allowed-tags-regexp', '-tr',
                            help='Optional regexp to filter tags (eg. release-([0-9.]+) or v([0-9.]+))')
        parser.add_argument('--release-tag-template', '-t',
                            help='Tag that will be pushed to docker registry. The same variables apply there as for ' +
                                 '--exec, except %%RELEASE_TAG%%',
                            default='%GIT_TAG%')
        parser.add_argument('--max-versions', '-mv',
                            help='Max versions to check/build',
                            default='5')
        parser.add_argument('--dry-run',
                            help='Print instead of performing',
                            action='store_true')
        parser.add_argument('--verbose',
                            help='Print all messages like --debug, but also perform',
                            action='store_true')
