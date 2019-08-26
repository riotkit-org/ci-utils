RiotKit's Continuous Integration Utils
======================================

Set of scripts commonly used on CI.

Works with any CI, incl. Travis CI, Jenkins, Circle CI, Gitlab CI.

### Usage

Just download and unpack.

```bash
mkdir -p /opt/riotkit/utils
wget https://github.com/riotkit-org/ci-utils/archive/v1.0.3.zip -O /tmp/ci-utils.zip
unzip /tmp/ci-utils.zip -d /opt/riotkit/utils
mv /opt/riotkit/utils/ci-utils*/* /opt/riotkit/utils/
rm -rf /opt/riotkit/utils/ci-utils*/
rm /tmp/ci-utils.zip

export PATH="/opt/riotkit/utils:$PATH"
```

### Usage on Travis

```yaml
- curl "https://raw.githubusercontent.com/riotkit-org/ci-utils/master/ci-integration/travis.sh" -s | bash
```

#### Stability

It is not recommended to use `master`. Please use a recent release instead. `master` will always contain changes backwards incompatible, the releases are snapshots of master.

Tools
=====

### docker-generate-readme

Generates a README.md basing on the Dockerfile envs.

```bash
DOCKERFILE_PATH=Dockerfile README_TEMPLATE_PATH=README.md.j2 README_PATH=README.md RIOTKIT_PATH=./bin ./bin/docker-generate-readme
```

Example README.md:
```jinja2
Configuration reference
-----------------------

List of all environment variables that could be used.

```yaml
{% for env_var, attrs in DOCKERFILE_ENVS.items() %}{% if attrs[2] %}# {{ attrs[2] }}{% endif %}
- {{ attrs[0] }} # (example value: {{ attrs[1] }})

{% endfor %}
```

### for-each-github-release

Iterate over a github project tags and execute a specified build command

```bash
./bin/for-each-github-release --repo-name phpbb/phpbb --dest-docker-repo quay.io/riotkit/phpbb --allowed-tags-regexp="(stable|release)-([0-9\.]+)$" --release-tag-template="%MATCH_1%" --exec "echo \"%GIT_TAG% - %RELEASE_TAG%\""
release-3.2.7 - 3.2.7
release-3.2.6 - 3.2.6
release-3.2.5 - 3.2.5
release-3.2.4 - 3.2.4
release-3.2.3 - 3.2.3
```

### env-to-json

Dumps environment variables of current shell scope into the json.

```bash
./bin/env-to-json parse_json # will also parse into native json all variable values that are json
./bin/env-to-json
```

### extract-envs-from-dockerfile

Extracts defined environment variables from Dockerfile (with comments). Supports multi-line environment variable blocks.

```bash
cat Dockerfile | ./extract-envs-from-dockerfile bash_source > some.env
cat Dockerfile | ./extract-envs-from-dockerfile json > some.json
cat Dockerfile | ./extract-envs-from-dockerfile bash | bash
```

### docker-hub-tag-exists

Checks if a specific tag exists in docker registry.

**NOTICE: May require root privileges!**

Scenarios:
a) When image is from quay.io and we did not force using manifest, then a docker pull will be made with a timeout
b) When we call with second parameter "using_manifest", then a `docker manifest inspect` will be used (requires experimental docker features enabled)

```bash
./bin/docker-hub-tag-exists php:7.3
./bin/docker-hub-tag-exists php:7.3 using_manifest
./bin/docker-hub-tag-exists quay.io/riotkit/php-app:7.3-x86_64
```

### use-experimental-docker

Sets the local docker client to use experimental features.

```bash
./bin/use-experimental-docker
```

### wait-for-mysql-to-be-ready

Waits for the MySQL server to be up and running. When only host specified, then only port will be pinged.
When specified valid username and password, then a login attempt and `SELECT 1;` will be attempted.

**Requirements:**
- nc
- mysql shell client (optional, but good to have)

```bash
# wait 5 seconds or less
./bin/wait-for-mysql-to-be-ready --host db_mysql --port 3306 --username root --password root --timeout 5
```
