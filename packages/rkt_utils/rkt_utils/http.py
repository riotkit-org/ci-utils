import time

import requests
from argparse import ArgumentParser
from rkd.api.contract import TaskInterface, ExecutionContext
from rkd.api.syntax import TaskDeclaration


class WaitForHttpTask(TaskInterface):
    """
    Waits for HTTP endpoint
    """

    def get_name(self) -> str:
        return ':wait-for'

    def get_group_name(self) -> str:
        return ':http'

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('url', help='URL address')
        parser.add_argument('--timeout', help='Timeout in seconds', default=30)
        parser.add_argument('--expected-code', help='Expected HTTP response code', default=200)
        parser.add_argument('--expected-contains-msg', help='Expect that selected message will be present', default='')
        parser.add_argument('--method', help='HTTP method name', default='GET')

    def execute(self, context: ExecutionContext) -> bool:
        url = context.get_arg('url')
        timeout = int(context.get_arg('--timeout'))
        expected_code = int(context.get_arg('--expected-code'))
        expected_contains_msg = context.get_arg('--expected-contains-msg')
        method = context.get_arg('--method')

        remaining_time = timeout

        while remaining_time > 0:
            remaining_time -= 1

            try:
                response = requests.request(method, url, timeout=1)
            except Exception as e:
                self.io().info('Not ready yet: ' + str(e))
                time.sleep(1)
                continue

            if response.status_code == expected_code:
                if expected_contains_msg and expected_contains_msg not in response.content.decode('utf-8'):
                    time.sleep(1)
                    continue

                self.io().info('Service is ready after %i seconds' % (timeout - remaining_time))
                return True

        self.io().error('Service under specified URL address failed to respond in expected time of %i seconds' %
                        timeout)
        return False


def imports():
    return [
        TaskDeclaration(WaitForHttpTask())
    ]
