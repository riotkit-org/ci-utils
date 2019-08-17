RiotKit's Continuous Integration Utils
======================================

Set of scripts commonly used on CI.

Works with any CI, incl. Travis CI, Jenkins, Circle CI, Gitlab CI.

### Usage

```bash
mkdir -p /opt/riotkit/utils
wget https://github.com/riotkit-org/ci-utils/archive/master.zip -O /tmp/ci-utils.zip
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

Tools
=====

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
