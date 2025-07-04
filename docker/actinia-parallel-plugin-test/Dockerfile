FROM mundialis/actinia-core:latest as actinia_test

LABEL authors="Carmen Tawalika,Anika Weinmann"
LABEL maintainer="tawalika@mundialis.de,weinmann@mundialis.de"

ENV ACTINIA_CUSTOM_TEST_CFG /etc/default/actinia-parallel-plugin-test

# TODO do not set DEFAULT_CONFIG_PATH if this is fixed
ENV DEFAULT_CONFIG_PATH /etc/default/actinia-parallel-plugin-test

# install things only for tests
RUN apk add valkey valkey-cli
RUN pip3 install iniconfig colorlog pwgen pytest pytest-cov

ENTRYPOINT ["/bin/sh"]
CMD ["/src/start.sh"]

# add data for tests
RUN wget --quiet https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_micro.zip && \
  unzip nc_spm_08_micro.zip && \
  rm -f nc_spm_08_micro.zip && \
  mv nc_spm_08_micro /actinia_core/grassdb/nc_spm_08

# copy needed files and configs for test
COPY docker/actinia-parallel-plugin-test/actinia-parallel-plugin-test.cfg /etc/default/actinia
COPY docker/actinia-parallel-plugin-test/actinia-parallel-plugin-test.cfg /etc/default/actinia-parallel-plugin-test
COPY . /src/actinia-parallel-plugin/

WORKDIR /src/actinia-parallel-plugin/

RUN pip install .

ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.0

COPY docker/actinia-parallel-plugin-test/run_integration_tests.sh /usr/bin/run_integration_tests.sh
RUN chmod a+x /usr/bin/run_integration_tests.sh
COPY docker/actinia-parallel-plugin-test/run_unittests.sh /usr/bin/run_unittests.sh
RUN chmod a+x /usr/bin/run_unittests.sh

# RUN make test
