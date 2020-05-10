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

:utils:env-to-json
------------------

Dumps all environment variables into JSON

.. code:: bash

    rkd :utils:env-to-json

    # parse any JSON value one dimension deep
    rkd :utils:env-to-json --parse-json
