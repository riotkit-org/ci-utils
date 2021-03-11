from rkd.api.syntax import TaskDeclaration

from .http import WaitForHttpTask
from .db import WaitForDatabaseTask
from .docker import TagImageTask, PushTask
from .envtojson import EnvToJsonTask


def imports():
    return [
        TaskDeclaration(WaitForHttpTask()),
        TaskDeclaration(WaitForDatabaseTask()),
        TaskDeclaration(TagImageTask()),
        TaskDeclaration(PushTask()),
        TaskDeclaration(EnvToJsonTask())
    ]
