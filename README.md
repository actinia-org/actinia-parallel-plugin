# actinia-parallel-plugin

This is the actinia-parallel-plugin for [actinia-core](https://github.com/mundialis/actinia_core) which adds parallel processing endpoints to actinia.

You can run actinia-parallel-plugin as an actinia-core plugin.

## Installation
Use docker compose for installation:
```
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d
```

### Installation hints
* If you get an error like: `ERROR: for docker_kvdb_1  Cannot start service valkey: network xxx not found` you can try the following:
```
docker compose -f docker/docker-compose.yml down
# remove all custom networks not used by a container
docker network prune
docker compose -f docker/docker-compose.yml up -d
```

## DEV setup
For a DEV setup you can use the docker/docker-compose.yml:
```
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm --service-ports --entrypoint sh actinia

# install the plugin
(cd /src/actinia-parallel-plugin && pip3 install .)
# start actinia-core with your plugin
gunicorn -b 0.0.0.0:8088 -w 1 --access-logfile=- -k gthread actinia_core.main:flask_app

# or for debugging in one line with reset
reset && (cd /src/actinia-parallel-plugin && pip3 install .) && gunicorn -b 0.0.0.0:8088 -w 3 --access-logfile=- -k gthread actinia_core.main:flask_app
```

### PostGIS
Connect to PostGIS DB from actinia-core docker container:
```
psql -U actinia -h postgis -d gis
```

### Hints

* If you have no `.git` folder in the plugin folder, you need to set the
`SETUPTOOLS_SCM_PRETEND_VERSION` before installing the plugin:
```
export SETUPTOOLS_SCM_PRETEND_VERSION=0.0
```
Otherwise you will get an error like this:
`LookupError: setuptools-scm was unable to detect version for '/src/actinia-parallel-plugin'.`.

* If you make changes in code and nothing changes you can try to uninstall the plugin:
```
pip3 uninstall actinia-parallel-plugin.wsgi -y
rm -rf /usr/lib/python3.8/site-packages/actinia_parallel_plugin.wsgi-*.egg
```

### Running tests
You can run the tests in the actinia test docker:

```
docker compose -f docker/docker-compose-test.yml build
docker compose -f docker/docker-compose-test.yml up -d

# exec docker and run tests manually
docker exec -it docker_actinia-test_1 sh

# run all tests
make test

# run only unittests
make unittest
# run only integrationtests
make integrationtest

# or run tests outside of docker container
docker exec -it docker_actinia-test_1 sh /usr/bin/run_integration_tests.sh
docker exec -it docker_actinia-test_1 sh /usr/bin/run_unittests.sh

docker compose -f docker/docker-compose-test.yml down
```

You can also run the tests in the GHA workflows locally via [act](https://github.com/nektos/act).
To run docker compose inside a workflow [act_base](https://github.com/lucasctrl/act_base) can be used.
With these you can run the following to run the tests:
```
# list all workflows
act -l

# run workflow
act -j integration-tests -P ubuntu-latest=lucasalt/act_base:latest
act -j unittests -P ubuntu-latest=lucasalt/act_base:latest
```


## Examples

### Requesting batch job and job endpoints
```
# request batch job
curl -u actinia-gdi:actinia-gdi -X GET http://localhost:8088/api/v3/resources/actinia-gdi/batches/1 | jq
# request job
curl -u actinia-gdi:actinia-gdi -X GET http://localhost:8088/api/v3/resources/actinia-gdi/batches/1/jobs/1 | jq
```

### Start parallel batch job
#### Ephemeral processing
You can start a parallel **ephemeral** batch job via:
```
# parallel ephemeral processing
curl -u actinia-gdi:actinia-gdi -X POST -H 'Content-Type: application/json' -d @test_postbodies/parallel_ephemeral_processing.json http://localhost:8088/api/v3/projects/nc_spm_08_grass7_root/processing_parallel | jq
```
Attention:
* The individual process chains must be "independent" of each other, since
  createBatch is designed as an ephemeral process.

TODOs:
* exporter in PC
* using stdout/export in PC of next block
