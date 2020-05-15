Github
======

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

**Class name to import:** rkt_ciutils.github.ForEachGithubReleaseTask [see how to import_]

:github:find-closest-release
----------------------------

Finds a release number closest to specified.

**Examples:**

.. code:: bash

    rkd :github:find-closest-release --repository riotkit-org/file-repository -c 1.3

**Class name to import:** rkt_ciutils.github.FindClosestReleaseTask [see how to import_]

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

**Class name to import:** rkt_ciutils.docker.DockerTagExistsTask [see how to import_]

Docker
======

:docker:extract-envs-from-dockerfile
------------------------------------

Extract list of environment variables, their descriptions and example
values from a Dockerfile.

.. code:: bash

    rkd :docker:extract-envs-from-dockerfile -f ~/Projekty/riotkit/riotkit/docker-taiga/Dockerfile --format bash_source

**Class name to import:** rkt_ciutils.docker.ExtractEnvsFromDockerfileTask [see how to import_]

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

**Class name to import:** rkt_ciutils.docker.GenerateReadmeTask [see how to import_]

.. _import: https://riotkit-do.readthedocs.io/en/latest/usage/importing-tasks.html


Boat-CI
=======

Provides Continuous Integration tasks designed to build docker images. Boat-CI is focusing on packaging existing applications, that are released on Github in separate repositories.
The CI is customizable with environment variables and commandline switches.

**Example scenario:**

.. code:: cucumber

    GIVEN we have project taigaio/taiga-back that is a backend application
    AND there is a separate frontend application at taigaio/taiga-front-dist
    AND we have THIS Boat-CI repository named riotkit-org/taiga-docker
    WHEN we want to build docker image for each new release of Taiga (backend + frontend is a complete setup)
    THEN on each pushed tag in riotkit-org/taiga-docker we run Boat-CI to produce images eg. taiga:5.0.1-D1.0, taiga:4.9-D1.0


**Concept:**

- The CI+Dockerfile is placed in a separate repository (application is in a separate repository, probably it can be configured differently)
- SNAPSHOT on master/commit is a tag in the docker registry that overwrites all the time eg. taiga:4.1.5-SNAPSHOT, taiga:4.1.6-SNAPSHOT (SNAPSHOT means that CI+docker version is LATEST for given application version)
- [customization] SNAPSHOT can consider ci+docker next version eg. taiga:4.1.5-D1.0.1-SNAPSHOT by using --dev-version-template="%MATCH_0%-D%NEXT_VERSION%-SNAPSHOT"
- SNAPSHOT tags are not propagated by default, so no 1.0.1 -> 1.0 -> 1 -> latest re-tagging of docker image

**Naming convention:**

    - TAG is the CI+Dockerfile repository git tag, not application repository tag
    - Application version is the tag in application repository

**Example:**

.. code:: yaml

    version: org.riotkit.rkd/0.3
    imports:
        - rkd.standardlib.python
        - rkd.standardlib.docker
        - rkt_ciutils.boatci

    tasks:
        :build-all-versions:
            description: Build all versions of Taiga
            arguments:
                "--commit-msg":
                  required: True
            steps: |
                export GITHUB_REPOSITORY=taigaio/taiga-back
                export ALLOWED_TAGS_REGEXP="([0-9\.]+)$"
                export DEST_DOCKER_REPO=quay.io/riotkit/taiga

                # == OPTIONAL, ADVANCED EXAMPLE ==
                # Given we build backend from taigaio/taiga-back
                # and the frontend is in separate repository - we try to find closest version of frontend
                # to match our backend eg. 5.0.1 backend + 5.0.0 frontend (frontend didn't get the patch version released yet)
                export DOCKER_BUILD_OPTS="--build-arg FRONTEND_VERSION=%FIND_CLOSEST_RELEASE(taigaio/taiga-front-dist)%"

                echo " > Starting CI"
                rkd --no-ui :boat-ci:process \
                    --commit-message="${ARG_COMMIT_MSG}"


:boat-ci:process
----------------

Takes incoming request from the CI.

Responsibility:

    - Decide about the destination version number and format
    - Decide if we REBUILD existing tags or not (release enforces this)

Behavior:

    - When "@force-rebuild" in commit message, then rebuild existing images (in case of "moving tags" - bad practice, but can happen, we handle such emergency case)
    - When "@force-rebuild-last-tag" is in commit message, rebuild previous tag's images, warning: dangerous, use with caution
    - When is on TAG in current docker repository - build last X versions of application, set double version (app + docker)
    - When is on branch/commit in current docker repository - build a snapshot of last X versions of application #TODO VERIFY
