
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.append(CURRENT_DIR + '/../packages/rkt_armutils')
sys.path.append(CURRENT_DIR + '/../packages/rkt_ciutils')
sys.path.append(CURRENT_DIR + '/../packages/rkt_utils')


from rkt_utils.envtojson import EnvToJsonTask
from rkt_ciutils.github import FindClosestReleaseTask, ForEachGithubReleaseTask
from rkt_ciutils.docker import imports as CIDockerImports
from rkt_utils.db import WaitForDatabaseTask
from rkt_armutils.docker import imports as TravisARMImports
from rkt_utils.docker import imports as DockerImports
from rkd_python import imports as PythonImports
from rkd.api.syntax import TaskDeclaration

IMPORTS = [
            TaskDeclaration(EnvToJsonTask()),
            TaskDeclaration(FindClosestReleaseTask()),
            TaskDeclaration(ForEachGithubReleaseTask()),
            TaskDeclaration(WaitForDatabaseTask())
          ] \
          + DockerImports() + CIDockerImports() + PythonImports() + TravisARMImports()

TASKS = []
