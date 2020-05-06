RiotKit's tools
===============

Set of generic tools dedicated to be used inside of Docker images, in
applications deployment and on Continuous Integration systems. The tools
are provided as Python modules runned by RKD - RiotKit Do.

*Previously: RiotKit CI tools*

rkt_utils package
==================

Main package of RiotKit Tools, contains various tools.

:github:for-each-release
------------------------

Iterate over recent X github releases and execute a task.

**Examples:**

.. code:: bash

    # build all versions of File Repository that matches tags v{NUMBER} eg. v3.0.0
    # for each version execute: rkd :build --version=%MATCH_0% (it can be any command)

    rkd :github:for-each-release \
        --repository=riotkit-org/file-repository \
        --exec 'rkd :build --version=%MATCH_0%' \
        --dest-docker-repo quay.io/riotkit/file-repository \
        --allowed-tags-regexp 'v([0-9.]+)'

:github:find-closest-release
----------------------------

Finds a release number closest to specified.

**Examples:**

.. code:: bash

    rkd :github:find-closest-release --repository riotkit-org/file-repository -c 1.3

:utils:env-to-json
------------------

Dumps all environment variables into JSON

.. code:: bash

    rkd :utils:env-to-json

    # parse any JSON value one dimension deep
    rkd :utils:env-to-json --parse-json

:docker:tag-exists
------------------

Checks if a docker image has a tag. Requires docker client, daemon and
permissions to the daemon.

**Examples:**

.. code:: bash

    # will result in a success
    sudo rkd :docker:tag-exists -i alpine:latest

    # will result in a failure
    sudo rkd :docker:tag-exists -i alpine:not-existing

:docker:extract-envs-from-dockerfile
------------------------------------

Extract list of environment variables, their descriptions and example
values from a Dockerfile.

.. code:: bash

    rkd :docker:extract-envs-from-dockerfile -f ~/Projekty/riotkit/riotkit/docker-taiga/Dockerfile --format bash_source

:docker:generate-readme
-----------------------

Generates a README.md file from README.md.j2 template, considering
environment variables from a Dockerfile.

.. code:: bash

    rkd :docker:generate-readme --template docker-taiga/README.md.j2 --dockerfile docker-taiga/Dockerfile

.. code:: bash

    #### Configuration reference

    List of all environment variables that could be used.

    {% for env_var, attrs in DOCKERFILE_ENVS.items() %}{% if attrs[2] %}# {{ attrs[2] }}{% endif %}
    - {{ attrs[0] }} # (default: {{ attrs[1] }})

    {% endfor %}

:db:wait-for
------------

Wait for database to be up and running, and the contents will be
present.

Supports: PostgreSQL, MySQL

**Examples:**

.. code:: bash

    rkd :db:wait-for \
        --host=postgres \
        --username=riotkit \
        --password=some \
        --port 5432 \
        --timeout 25 \
        --db-name=humhub \
        --type=postgres

    rkd :db:wait-for \
        --host=mysql \
        --port=3306 \
        --type=mysql

rkt\_armutils package
=====================

Consists of ARM-related tools, includes QEMU binaries required for
cross-compilation and running of ARM binaries on x86\_64.

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
