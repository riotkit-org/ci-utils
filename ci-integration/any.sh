#!/bin/bash

RIOTKIT_UTILS_VERSION=${RIOTKIT_UTILS_VERSION:-""}
CONFIGURE_PROFILE=${CONFIGURE_PROFILE:-True}
FORCE_INSTALL=${FORCE_INSTALL:-False}
INSTALL_DIR=${INSTALL_DIR:-/opt/riotkit/utils}

URL_VERSION="${RIOTKIT_UTILS_VERSION}"

if [[ -d "${INSTALL_DIR}/ci-utils-${RIOTKIT_UTILS_VERSION}" ]] && [[ "${FORCE_INSTALL}" == "False" ]]; then
    echo " >> RiotKit Utils v${RIOTKIT_UTILS_VERSION} already installed, skipping."
    exit 0
fi

if [[ "${RIOTKIT_UTILS_VERSION}" == "" ]]; then
    echo " >> Please provide 'RIOTKIT_UTILS_VERSION' environment variable"
    exit 1
fi

if [[ "${RIOTKIT_UTILS_VERSION}" == "master" ]]; then
    echo " >> WARNING: Using 'master' version is very dangerous. Please set a fixed version soon."
else
    URL_VERSION="v${URL_VERSION}"
fi

set -xe
wget "https://github.com/riotkit-org/ci-utils/archive/${URL_VERSION}.zip" -O /tmp/ci-utils.zip
mkdir -p "${INSTALL_DIR}"
unzip -o /tmp/ci-utils.zip -d "${INSTALL_DIR}"

echo " >> Exporting PATH"
export PATH="${INSTALL_DIR}/ci-utils-${RIOTKIT_UTILS_VERSION}/bin/:$PATH"

# export PATH for every user in the system
if [[ "${CONFIGURE_PROFILE}" == "True" ]]; then
    [[ ! "$(cat /etc/profile)" != *"riotkit"* ]] || echo "export PATH=\"${INSTALL_DIR}/ci-utils-${RIOTKIT_UTILS_VERSION}/bin/:\$PATH\"" >> /etc/profile;
fi
