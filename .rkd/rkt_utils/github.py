from abc import ABC

import requests
import time
import re
from argparse import ArgumentParser
from rkd.contract import TaskInterface, ExecutionContext


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]

    return sorted(l, key=alphanum_key)


class BaseGithubTask(TaskInterface, ABC):
    def get_group_name(self) -> str:
        return ':github'


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
        parser.add_argument('--retries', '-r', default=5, help='Maximum number of retries in request to github')
        parser.add_argument('--retry-wait', '-w', default=5, help='Amount of seconds between retries')
        parser.add_argument('--repository', '-n', required=True, help='Repository name eg. riotkit-org/filerepository')
        parser.add_argument('--compare-with', '-c', required=True, help='Version to compare with')

    def get_available_tags(self, url: str, sleep_time: int, retries: int = 5) -> list:
        """ Lists all tags from github project """

        try:
            response = requests.get(url + '/tags').json()

            return list(map(
                lambda tag_object: str(tag_object['name']),
                response
            ))
        except TypeError:
            if retries <= 0:
                raise

            time.sleep(sleep_time)
            return self.get_available_tags(url, sleep_time, retries - 1)

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

