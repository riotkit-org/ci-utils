
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.append(CURRENT_DIR + '/../packages/rkt_armutils/src')
sys.path.append(CURRENT_DIR + '/../packages/rkt_ciutils/src')
sys.path.append(CURRENT_DIR + '/../packages/rkt_utils/src')


from rkt_utils.envtojson import EnvToJsonTask
from rkt_ciutils.github import FindClosestReleaseTask, ForEachGithubReleaseTask
from rkt_ciutils.docker import DockerTagExistsTask, ExtractEnvsFromDockerfileTask, GenerateReadmeTask
from rkt_utils.db import WaitForDatabaseTask
from rkt_armutils.docker import imports as TravisARMImports
from rkd.standardlib.docker import imports as DockerImports
from rkd.standardlib.python import imports as PythonImports

IMPORTS = [
            TaskDeclaration(EnvToJsonTask()),
            TaskDeclaration(FindClosestReleaseTask()),
            TaskDeclaration(ForEachGithubReleaseTask()),
            TaskDeclaration(DockerTagExistsTask()),
            TaskDeclaration(ExtractEnvsFromDockerfileTask()),
            TaskDeclaration(GenerateReadmeTask()),
            TaskDeclaration(WaitForDatabaseTask())
          ] \
          + DockerImports() + PythonImports() + TravisARMImports()

TASKS = []
