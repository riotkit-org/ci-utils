:docker:inject-qemu-bins
------------------------

Injects QEMU binaries into a docker image required to run ARM binaries
on x86\_64 processors.

**NOTICE: This operation is flattening the docker layers by doing export
and import**

**Examples:**

.. code:: bash

    rkd :docker:inject-qemu-bins --image=arm32v7/php:7.2-fpm

**Class name to import:** rkt_armutils.docker.InjectQEMUBinaryIntoContainerTask [see how to import_]

:travis:use-experimental-docker
-------------------------------

Turns on experimental features in Docker client. **NOTICE: Overrides
~/.docker/config.json - but useful on CI**

**Class name to import:** rkt_armutils.docker.UseExperimentalDockerTask [see how to import_]

:travis:configure-qemu
----------------------

Configures Travis-CI to use QEMU for building docker containers.

**Class name to import:** rkt_armutils.docker.ConfigureTravisBuildTask [see how to import_]

.. _import: https://riotkit-do.readthedocs.io/en/latest/usage/importing-tasks.html
