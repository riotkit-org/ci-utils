
import json
from argparse import ArgumentParser
from rkd.contract import TaskInterface, ExecutionContext


class EnvToJsonTask(TaskInterface):
    """ Dump environment variables into JSON """

    def get_name(self) -> str:
        return ':env-to-json'

    def get_group_name(self) -> str:
        return ':utils'

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('--parse-json', '-p',
                            help='Parse JSON values of all variables which have JSON as value',
                            action='store_true')

    def execute(self, context: ExecutionContext) -> bool:
        env = dict(context.env)
        to_serialize = {}

        for name, value in env.items():
            if context.args['parse_json']:
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass

            to_serialize[name] = value

        self._io.out(json.dumps(to_serialize, indent=2, sort_keys=True))
        return True
