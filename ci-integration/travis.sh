#!/bin/bash

echo " >> Installing RiotKit CI-Utils on this Travis-CI build"
mkdir -p /opt/riotkit/utils
test -f /tmp/ci-utils.zip || wget https://github.com/riotkit-org/ci-utils/archive/master.zip -O /tmp/ci-utils.zip
unzip /tmp/ci-utils.zip -d /opt/riotkit/utils
mv /opt/riotkit/utils/ci-utils*/* /opt/riotkit/utils/
rm -rf /opt/riotkit/utils/ci-utils*/
rm /tmp/ci-utils.zip

export export PATH="/opt/riotkit/utils:$PATH"
