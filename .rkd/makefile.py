
from rkt_utils.envtojson import EnvToJsonTask
from rkt_utils.github import FindClosestReleaseTask, ForEachGithubReleaseTask
from rkt_utils.docker import DockerTagExistsTask
from rkd.syntax import TaskDeclaration
from rkd.standardlib.docker import imports as DockerImports
from rkd.standardlib.python import imports as PythonImports

IMPORTS = [
            TaskDeclaration(EnvToJsonTask()),
            TaskDeclaration(FindClosestReleaseTask()),
            TaskDeclaration(ForEachGithubReleaseTask()),
            TaskDeclaration(DockerTagExistsTask())
          ] \
          + DockerImports() + PythonImports()

TASKS = []
