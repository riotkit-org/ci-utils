
from abc import ABC
from argparse import ArgumentParser
from rkd.contract import TaskInterface, ExecutionContext
from rkd.standardlib.shell import BaseShellCommandWithArgumentParsingTask


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

