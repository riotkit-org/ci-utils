import re
from subprocess import check_output, CalledProcessError, STDOUT
from typing import Union


class GitTools:
    @classmethod
    def get_current_tag(cls) -> Union[str, None]:
        try:
            return check_output(
                'git describe --exact-match --tags $(git log -n1 --pretty=\'%h\')',
                shell=True,
                stderr=STDOUT
            )\
                .decode('utf-8').strip()
        except CalledProcessError:
            return None

    @classmethod
    def is_currently_on_tag(cls) -> bool:
        return cls.get_current_tag() is not None

    @classmethod
    def get_last_tag(cls) -> str:
        return check_output(
                'git for-each-ref refs/tags --sort=-taggerdate --format=\'%(refname)\' --count=1',
                shell=True,
                stderr=STDOUT
        )\
            .decode('utf-8').strip().replace('refs/tags/', '')


class VersionTools:
    @classmethod
    def get_next_version(cls) -> str:
        return cls.increment_version(GitTools.get_last_tag())

    @classmethod
    def increment_version(cls, version: str) -> str:
        if not version:
            return '0.0.1'

        matches = re.match('([0-9.]+)', version)
        parts = ['0', '0', '1']

        # find first numeric part that contains a dot (to exclude eg. RC-1 or dev8, dev.12)
        for match in reversed(matches.groups()):
            if "." in match:
                parts = match.split('.')
                break

        # increment 3rd part (patch)
        if len(parts) >= 3:
            parts[2] = str(int(parts[2]) + 1)
        else:
            parts.append('1')

        return '.'.join(parts)
