:docker:inject-qemu-bins
------------------------

Injects QEMU binaries into a docker image required to run ARM binaries
on x86\_64 processors.

**NOTICE: This operation is flattening the docker layers by doing export
and import**

**Importing in makefile.py:**

.. code:: python

    from rkd.syntax import TaskDeclaration
    from rkt_armutils.docker import InjectQEMUBinaryIntoContainerTask

    # ...
    IMPORTS += [TaskDeclaration(InjectQEMUBinaryIntoContainerTask)]

**Importing in makefile.yaml:**

.. code:: yaml

    imports:
        - rkt_armutils.docker
        # or
        - rkt_armutils.docker.InjectQEMUBinaryIntoContainerTask


**Examples:**

.. code:: bash

    rkd :docker:inject-qemu-bins --image=arm32v7/php:7.2-fpm

:travis:use-experimental-docker
-------------------------------

Turns on experimental features in Docker client. **NOTICE: Overrides
~/.docker/config.json - but useful on CI**

**Importing in makefile.py:**

.. code:: python

    from rkd.syntax import TaskDeclaration
    from rkt_armutils.docker import UseExperimentalDockerTask

    # ...
    IMPORTS += [TaskDeclaration(UseExperimentalDockerTask)]

**Importing in makefile.yaml:**

.. code:: yaml

    imports:
        - rkt_armutils.docker
        # or
        - rkt_armutils.docker.UseExperimentalDockerTask

:travis:configure-qemu
----------------------

Configures Travis-CI to use QEMU for building docker containers.

**Importing in makefile.py:**

.. code:: python

    from rkd.syntax import TaskDeclaration
    from rkt_armutils.docker import ConfigureTravisBuildTask

    # ...
    IMPORTS += [TaskDeclaration(ConfigureTravisBuildTask)]

**Importing in makefile.yaml:**

.. code:: yaml

    imports:
        - rkt_armutils.docker
        # or
        - rkt_armutils.docker.ConfigureTravisBuildTask
