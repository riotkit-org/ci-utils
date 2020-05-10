:docker:inject-qemi-bins
------------------------

Injects QEMU binaries into a docker image required to run ARM binaries
on x86\_64 processors.

**NOTICE: This operation is flattening the docker layers by doing export
and import**

**Examples:**

.. code:: bash

    rkd :docker:inject-qemi-bins --image=arm32v7/php:7.2-fpm

:travis:use-experimental-docker
-------------------------------

Turns on experimental features in Docker client. **NOTICE: Overrides
~/.docker/config.json - but useful on CI**

:travis:configure-qemu
----------------------

Configures Travis-CI to use QEMU for building docker containers.
