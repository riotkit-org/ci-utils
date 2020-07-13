:db:wait-for
------------

Wait for database to be up and running, and the contents will be present.

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

**Class name to import:** rkt_utils.db.WaitForDatabaseTask [see how to import_]

:utils:env-to-json
------------------

Dumps all environment variables into JSON

.. code:: bash

    rkd :utils:env-to-json

    # parse any JSON value one dimension deep
    rkd :utils:env-to-json --parse-json

**Class name to import:** rkt_utils.envtojson.EnvToJsonTask [see how to import_]

.. _import: https://riotkit-do.readthedocs.io/en/latest/usage/importing-tasks.html

:docker:tag
-----------

Re-tag images to propagate version tags in docker-like format eg. 1.0.1 -> 1.0 -> 1 -> latest

Examples:
    1.0.0 -> 1.0 -> 1 -> latest
    1.0.0-RC1 -> 1.0.0-latest-rc


.. code:: bash

    # simple propagate tags 1.2.23 -> 1.2 -> 1
    rkd :docker:tag --image my-image:1.2.23 --propagate

    # advanced usage
    rkd :docker:tag --image my-image:1.2.23 --propagate --allowed-meta=rc,alpha,stable,dev,prod,test,beta,build,b

:docker:push
------------

Push all re-tagged imagges by **:docker:tag**

.. code:: bash

    rkd @ --image my-image:1.2.23 --propagate :docker:tag :docker:push

