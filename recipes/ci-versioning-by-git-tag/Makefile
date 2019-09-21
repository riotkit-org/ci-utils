.SILENT:
.PHONY: help

SUDO = sudo
QUAY_REPO=quay.io/riotkit/infracheck

help:
	@grep -E '^[a-zA-Z\-\_0-9\.@]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build: ## Build and push (args: PUSH, ARCH, GIT_TAG)
	set -e; DOCKER_TAG="latest-dev-${ARCH}"; \
	\
	if [[ "${GIT_TAG}" != '' ]]; then \
		DOCKER_TAG=${GIT_TAG}-${ARCH}; \
	fi; \
	\
	${SUDO} docker build . -f ./.infrastructure/${ARCH}.Dockerfile -t ${QUAY_REPO}:$${DOCKER_TAG}; \
	${SUDO} docker tag ${QUAY_REPO}:$${DOCKER_TAG} ${QUAY_REPO}:$${DOCKER_TAG}-$$(date '+%Y-%m-%d'); \
	\
	if [[ "${PUSH}" == "true" ]]; then \
		${SUDO} docker push ${QUAY_REPO}:$${DOCKER_TAG}-$$(date '+%Y-%m-%d'); \
		${SUDO} docker push ${QUAY_REPO}:$${DOCKER_TAG}; \
	fi
