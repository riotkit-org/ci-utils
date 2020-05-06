
import os
from argparse import ArgumentParser
from rkd.standardlib.shell import BaseShellCommandWithArgumentParsingTask
from rkd.syntax import TaskDeclaration


class InjectQEMUBinaryIntoContainerTask(BaseShellCommandWithArgumentParsingTask):
    def __init__(self):
        script_path = os.path.dirname(os.path.realpath(__file__))

        def handle_args(parser: ArgumentParser):
            parser.add_argument('--image', '-i', required=True, help='Image name with tag')

        super().__init__(
            name=':inject-qemu-bins',
            group=':docker',
            description='Injects QEMU binaries for emulation on x86_64 platform',
            arguments_definition=handle_args,
            command='''
echo " >> Injecting qemu arm binaries into ${ARG_IMAGE}"
set -xe

docker rm -f tmp_qemu_container 2>/dev/null > /dev/null || true
docker pull ${ARG_IMAGE}
docker create --name tmp_qemu_container ${ARG_IMAGE}
docker cp "${''' + script_path + '''}/arm/usr" tmp_qemu_container:/
docker export tmp_qemu_container > /tmp/tmp_qemu_container.tar.gz
cat /tmp/tmp_qemu_container.tar.gz | docker import - ${ARG_IMAGE}
rm /tmp/tmp_qemu_container.tar.gz
docker rm -f tmp_qemu_container 2>/dev/null > /dev/null || true
            '''
        )


class UseExperimentalDockerTask(BaseShellCommandWithArgumentParsingTask):
    def __init__(self):
        super().__init__(
            name=':use-experimental-docker',
            group=':travis',
            description='Turn on experimental docker client',
            command='''
echo " >> Using experimental docker version"
echo '{"experimental": "enabled"}' > ~/.docker/config.json
cat ~/.docker/config.json
            '''
        )


class ConfigureTravisBuildTask(BaseShellCommandWithArgumentParsingTask):
    def __init__(self):
        super().__init__(
            name=':configure-qemu',
            description='Configure TravisCI for ARM builds',
            group=':travis',
            command='''
echo " >> Configuring Travis build to be able to build Docker ARM images"
set -x

docker --version  # document the version Travis is using (currently 17.x, which is way too old)
echo '{"experimental":true}' | sudo tee /etc/docker/daemon.json
mkdir -p $HOME/.docker
echo '{"experimental":"enabled"}' | tee $HOME/.docker/config.json # needed to use docker manifest
service docker restart
docker run --rm --privileged multiarch/qemu-user-static:register --reset
            '''
        )


def imports():
    return [
        TaskDeclaration(InjectQEMUBinaryIntoContainerTask()),
        TaskDeclaration(UseExperimentalDockerTask()),
        TaskDeclaration(UseExperimentalDockerTask())
    ]
