
from rkt_utils.envtojson import EnvToJsonTask
from rkt_utils.github import FindClosestReleaseTask
from rkd.syntax import TaskDeclaration
from rkd.standardlib.docker import imports as DockerImports
from rkd.standardlib.python import imports as PythonImports

IMPORTS = [
            TaskDeclaration(EnvToJsonTask()),
            TaskDeclaration(FindClosestReleaseTask())
          ] \
          + DockerImports() + PythonImports()

TASKS = []
