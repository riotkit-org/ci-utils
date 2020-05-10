RiotKit's tools
===============

Set of generic tools dedicated to be used inside of Docker images, in
applications deployment and on Continuous Integration systems. The tools
are provided as Python modules runned by RKD - RiotKit Do.

Tools are split into modules by usage type to reduce the size of fetched package - main reason is usage inside of Docker containers.

*Previously: RiotKit CI tools*

rkt_utils package
==================

Contains various tools to work with applications and with environment. rkt_utils have minimal requirements, so it can be
used inside of a docker container to eg. wait for database to get up before application will be started.

> Browse rkt_utils_ documentation
---------------------------------

.. code:: bash

    # with PIP
    pip install rkt-utils==3.0.0     # replace with a preferred version
    # or with PipEnv
    pipenv install rkt-utils==3.0.0

**Check available releases there:** https://pypi.org/project/rkt-utils/#history

.. _rkt_utils: packages/rkt_utils/README.rst

rkt_armutils package
=====================

Consists of ARM-related tools, includes QEMU binaries required for
cross-compilation and running of ARM binaries on x86\_64.

> Browse rkt_armutils_ documentation
------------------------------------

.. code:: bash

    # with PIP
    pip install rkt-armutils==3.0.0     # replace with a preferred version
    # or with PipEnv
    pipenv install rkt-armutils==3.0.0

**Check available releases there:** https://pypi.org/project/rkt-armutils/#history

.. _rkt_armutils: packages/rkt_armutils/README.rst

rkt_ciutils package
===================

Continuous Integration tools, and tools for local builds, publishing, building docker images.

> Browse rkt_ciutils_ documentation
-----------------------------------

.. code:: bash

    # with PIP
    pip install rkt-ciutils==3.0.0     # replace with a preferred version
    # or with PipEnv
    pipenv install rkt-ciutils==3.0.0

**Check available releases there:** https://pypi.org/project/rkt-ciutils/#history

.. _rkt_ciutils: packages/rkt_ciutils/README.rst

From authors
===================

We are grassroot activists for social change, so we created RKD especially in mind for those fantastic initiatives:

- RiotKit (https://riotkit.org)
- International Workers Association (https://iwa-ait.org)
- Anarchistyczne FAQ (http://anarchizm.info) a translation of Anarchist FAQ (https://theanarchistlibrary.org/library/the-anarchist-faq-editorial-collective-an-anarchist-faq)
- Federacja Anarchistyczna (http://federacja-anarchistyczna.pl)
- Związek Syndykalistów Polski (https://zsp.net.pl) (Polish section of IWA-AIT)
- Komitet Obrony Praw Lokatorów (https://lokatorzy.info.pl)
- Solidarity Federation (https://solfed.org.uk)
- Priama Akcia (https://priamaakcia.sk)
