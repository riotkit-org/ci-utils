RiotKit's tools
===============

Set of generic tools dedicated to be used inside of Docker images, in applications deployment and on Continuous Integration systems.
The tools are provided as Python modules runned by RKD - RiotKit Do.

*Previously: RiotKit CI tools*

:github:for-each-release
------------------------

Iterate over recent X github releases and execute a task.

**Examples:**

```bash
# build all versions of File Repository that matches tags v{NUMBER} eg. v3.0.0
# for each version execute: rkd :build --version=%MATCH_0% (it can be any command)

rkd :github:for-each-release \
    --repository=riotkit-org/file-repository \
    --exec 'rkd :build --version=%MATCH_0%' \
    --dest-docker-repo quay.io/riotkit/file-repository \
    --allowed-tags-regexp 'v([0-9.]+)'
```

:github:find-closest-release
----------------------------

Finds a release number closest to specified.

**Examples:**

```bash
rkd :github:find-closest-release --repository riotkit-org/file-repository -c 1.3
```
