
import os
import json
import shlex
from typing import List, Dict
from argparse import ArgumentParser
from rkd.contract import TaskInterface, ExecutionContext
from rkd.standardlib.shell import BaseShellCommandWithArgumentParsingTask
from collections import namedtuple


EnvironmentVariable = namedtuple('EnvironmentVariable', 'name value comment')


class DockerTagExistsTask(BaseShellCommandWithArgumentParsingTask):
    """ Check if a docker tag exists """

    def __init__(self):
        super().__init__(
            name=':tag-exists',
            group=':docker',
            description='',
            arguments_definition=None,
            command='''
                image_full_name="$ARG_IMAGE";
                wait_time="${ARG_WAIT_TIME:-10}"
                search_term='Pulling|is up to date|not found'
                
                result="$((timeout --preserve-status "$wait_time" docker 2>&1 pull "$image_full_name" &) | grep -v 'Pulling repository' | egrep -o "$search_term")"
                test "$result" || { echo "Timed out too soon. Try using a wait_time greater than $wait_time..."; return 1 ;}
                
                if echo $result | grep -vq 'not found'; then
                    echo "Image found."
                    exit 0
                else
                    echo "Image not found"
                    exit 1
                fi
            '''
        )

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('--image', '-i', required=True, help='Image name')
        parser.add_argument('--wait-time', '-w', default='10', help='Time to wait after which to interrupt the pulling')


class ExtractEnvsFromDockerfileTask(TaskInterface):
    """ Extract environment variables from a Dockerfile """

    def get_name(self) -> str:
        return ':extract-envs-from-dockerfile'

    def get_group_name(self) -> str:
        return ':docker'

    def execute(self, context: ExecutionContext) -> bool:
        out_format = context.args['format']
        file_path = context.args['file']

        if not os.path.isfile(file_path):
            self._io.error_msg('Cannot find Dockerfile at path "%s"' % file_path)
            return False

        with open(file_path, 'rb') as f:
            content = f.read().decode('utf-8')

        out_vars = self.get_envs(content)

        if out_format == 'bash_source':
            self._io.outln('export DOCKERFILE_ENVS=%s' % shlex.quote(json.dumps(out_vars)))
        elif out_format == 'json':
            self._io.outln(json.dumps(out_vars, indent=2, sort_keys=True))
        else:
            for name, out_var in out_vars.items():
                self._io.outln('export %s=%s' % (out_var.name, out_var.value))

        return True

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('--file', '-f', required=True, help='Path to Dockerfile to read as input')
        parser.add_argument('--format', default='json', help='Output format, one of: json, bash_source, env')

    def get_envs(self, content: str):
        by_lines = content.split("\n")
        normalized_lines = list(map(lambda curr: curr.strip(), by_lines))
        pos = -1
        matched_lines = {}

        for line in normalized_lines:
            pos += 1

            # each block that starts with "ENV" can be multi-line, so it will be extracted multi-line
            if line.upper().startswith('ENV'):
                matched_lines = {**matched_lines, **self._parse_lines(self._extract_block(pos, normalized_lines))}

        return matched_lines

    def _parse_lines(self, lines: List[str]) -> Dict[str, EnvironmentVariable]:
        parsed = {}
        comment_buffer = ''

        for line in lines:
            # if that's a comment or a comment continuation, then collect into the buffer
            if line.startswith('#'):
                comment_buffer += line.lstrip('# ') + "\n"
            else:
                # if the comment block ended, or it is not a comment block
                if line.startswith('ENV'):
                    line = line[3:].strip()

                sep = line.split('=', maxsplit=1)

                # potential syntax error
                if len(sep) < 2:
                    self._io.warn('!!! Cannot parse block in line "%s"' % line)
                    continue

                parsed[sep[0].strip()] = EnvironmentVariable(
                    name=sep[0].strip(),
                    value=sep[1].strip(),
                    comment=comment_buffer.strip()
                )
                comment_buffer = ''

        return parsed

    @staticmethod
    def _extract_block(start_pos: int, lines: List[str]) -> list:
        extracted = []
        pos = start_pos
        length = len(lines)

        extracted.append(lines[start_pos].rstrip('\\'))

        while True:
            pos += 1

            if pos > length:
                break

            line = lines[pos]

            if line.endswith('\\') or line.startswith('#'):
                extracted.append(line.rstrip('\\'))
                continue
            else:
                extracted.append(line)
                break

        return extracted
