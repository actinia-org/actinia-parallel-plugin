# actinia-parallel-plugin

This is an example plugin for [actinia-core](https://github.com/mundialis/actinia_core) which adds a "Hello World" endpoint to actinia-core.

You can run actinia-parallel-plugin as an actinia-core plugin.

## Installation
Use docker-compose for installation:
```
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml up -d
```

### Installation hints
* If you get an error like: `ERROR: for docker_redis_1  Cannot start service redis: network xxx not found` you can try the following:
```
docker-compose -f docker/docker-compose.yml down
# remove all custom networks not used by a container
docker network prune
docker-compose -f docker/docker-compose.yml up -d
```

### Requesting helloworld endpoint
You can test the plugin and request the `/helloworld` endpoint, e.g. with:
```
curl -u actinia-gdi:actinia-gdi -X GET http://localhost:8088/api/v3/processing_parallel | jq

curl -u actinia-gdi:actinia-gdi -H 'accept: application/json' -H 'Content-Type: application/json' -X POST http://localhost:8088/api/v3/processing_parallel -d '{"name": "test"}' | jq
```

## DEV setup
For a DEV setup you can use the docker/docker-compose.yml:
```
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml run --rm --service-ports --entrypoint sh actinia

# install the plugin
(cd /src/actinia-parallel-plugin && python3 setup.py install)
# start actinia-core with your plugin
gunicorn -b 0.0.0.0:8088 -w 1 --access-logfile=- -k gthread actinia_core.main:flask_app
```

### Postgis
Connect to postgis DB from actinia-core docker container:
```
psql -U actinia -h postgis -d gis
```

### Hints

* If you have no `.git` folder in the plugin folder, you need to set the
`SETUPTOOLS_SCM_PRETEND_VERSION` before installing the plugin:
```
export SETUPTOOLS_SCM_PRETEND_VERSION=0.0
```
Otherwise you will get an error like this
`LookupError: setuptools-scm was unable to detect version for '/src/actinia-parallel-plugin'.`.

* If you make changes in code and nothing changes you can try to uninstall the plugin:
```
pip3 uninstall actinia-parallel-plugin.wsgi -y
rm -rf /usr/lib/python3.8/site-packages/actinia_parallel_plugin.wsgi-*.egg
```

### Running tests
You can run the tests in the actinia test docker:

```
docker build -f docker/actinia-parallel-plugin-test/Dockerfile -t actinia-parallel-plugin-test .
docker run -it actinia-parallel-plugin-test -i

cd /src/actinia-parallel-plugin/

# run all tests
make test

# run only unittests
make unittest
# run only integrationtests
make integrationtest

# run only tests which are marked for development with the decorator '@pytest.mark.dev'
make devtest
```

##
