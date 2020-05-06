
import time
import subprocess
from argparse import ArgumentParser
from typing import Callable
from rkd.contract import TaskInterface, ExecutionContext


class WaitForDatabaseTask(TaskInterface):
    """ Waits for the database to be ready """

    def get_name(self) -> str:
        return ':wait-for'

    def get_group_name(self) -> str:
        return ':db'

    def execute(self, context: ExecutionContext) -> bool:
        return self.check_if_instance_is_alive(
            db_type=context.args['type'],
            db_name=context.args['db_name'],
            timeout=int(context.args['timeout']),
            user=context.args['username'],
            password=context.args['password'],
            port=int(context.args['port']),
            host=context.args['host']
        )

    def _get_checker_command(self, db_type: str, db_name: str, user: str,
                             password: str, host: str, port: int) -> Callable:
        """
        Detect which checking command fits best
        :return:
        """

        if db_type == 'mysql':
            if self.is_mysql_tool_available() and user:
                self._io.debug(' >> MySQL tool checker was selected')
                return self.get_wait_command_for_mysql(host=host, port=port, user=user, password=password)

            self._io.debug(' >> NC tool was selected')
            return self.get_wait_command_for_mysql_nc(host=host, port=port)

        if db_type == 'postgres':
            if self.is_postgres_toolkit_available():
                self._io.debug(' >> PostgreSQL toolkit is available and will be used')
                return self.get_wait_command_for_pg_is_ready(db_name=db_name, user=user, host=host, port=port)

            self._io.debug(' >> NC tool was selected for PostgreSQL')
            return self.get_wait_command_for_postgres_nc(host=host, port=port)

        raise Exception('Unsupported database type. Only mysql and postgres are supported.')

    def check_if_instance_is_alive(self, db_type: str, db_name: str, user: str,
                                   password: str, host: str, port: int, timeout: int) -> bool:

        checker = self._get_checker_command(db_type=db_type, db_name=db_name, user=user, password=password,
                                            host=host, port=port)
        time_left = timeout

        while time_left != 0:
            if checker():
                self._io.success_msg(' >> The DB seems to be online')
                return True

            time.sleep(1)
            time_left -= 1

        self._io.error_msg(' >> Error: The DB is still down')
        return False

    def get_wait_command_for_mysql(self, host: str, port: int, user: str, password: str) -> Callable:
        return lambda: self.is_command_of_success_code(
            'mysql ' +
            '-h "' + host + '" ' +
            '-P "' + str(port) + '" ' +
            '-u"' + user + '" ' +
            ('-p"' + password + '" ' if password else ' ') +
            '-e "SELECT 1;"'
        )

    def get_wait_command_for_mysql_nc(self, host: str, port: int) -> Callable:
        return lambda: self.is_command_of_success_code(
            'echo "ttttt\n\n" | nc -w 1 "%s" "%i" | grep "mysql_native"' % (
                host, port
            )
        )

    def get_wait_command_for_postgres_nc(self, host: str, port: int) -> Callable:
        return lambda: self.is_command_of_success_code(
            'nc -z %s %i' % (host, port)
        )

    def get_wait_command_for_pg_is_ready(self, db_name: str, user: str, host: str, port: int) -> Callable:
        opts = ''

        if db_name:
            opts += ' --dbname=%s ' % db_name

        if user:
            opts += ' --username=%s ' % user

        return lambda: self.is_command_of_success_code(
            'pg_isready %s --host=%s --port=%i --timeout=1' % (opts, host, port)
        )

    def is_mysql_tool_available(self) -> bool:
        return self.is_command_of_success_code('command -v mysql')

    def is_postgres_toolkit_available(self) -> bool:
        return self.is_command_of_success_code('command -v pg_isready')

    @staticmethod
    def is_command_of_success_code(cmd: str) -> bool:
        try:
            subprocess.check_output(cmd, shell=True)
            return True

        except subprocess.CalledProcessError as e:
            print(e.output.decode('utf-8'))
            return False

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('--host', '-a',
                            help='IP address or UNIX socket',
                            required=True)
        parser.add_argument('--port', '-p',
                            help='Port',
                            required=True)
        parser.add_argument('--type', '-t',
                            help='Database type. Possible values: postgres, mysql',
                            required=True)
        parser.add_argument('--username', '-u',
                            help='Username (optional, when not specified, then only port will be checked)',
                            required=False)
        parser.add_argument('--db-name', '-n',
                            help='Database name (optional)',
                            default='')
        parser.add_argument('--password', '-P',
                            help='Password (optional)',
                            default='')
        parser.add_argument('--timeout', '-T',
                            help='Timeout in seconds (optional, defaults to 15)',
                            default=15)
