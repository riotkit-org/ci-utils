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
