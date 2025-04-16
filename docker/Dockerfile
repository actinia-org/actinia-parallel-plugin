FROM mundialis/actinia-core:latest

# pwgen is needed for the tests
RUN pip3 install pwgen

COPY docker/actinia.cfg /etc/default/actinia
COPY src /src/actinia-parallel-plugin/src/
COPY setup.cfg /src/actinia-parallel-plugin/
COPY setup.py /src/actinia-parallel-plugin/

RUN pip3 uninstall actinia-parallel-plugin.wsgi -y
# SETUPTOOLS_SCM_PRETEND_VERSION is only needed if in the plugin folder is no
# .git folder
ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.0
RUN (cd /src/actinia-parallel-plugin && pip3 install .)
