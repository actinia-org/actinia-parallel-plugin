FROM mundialis/actinia-core:latest as actinia_test

LABEL authors="Carmen Tawalika,Anika Weinmann"
LABEL maintainer="tawalika@mundialis.de,weinmann@mundialis.de"

ENV ACTINIA_CUSTOM_TEST_CFG /etc/default/actinia-parallel-plugin-test

# TODO do not set DEFAULT_CONFIG_PATH if this is fixed
ENV DEFAULT_CONFIG_PATH /etc/default/actinia-parallel-plugin-test

# install things only for tests
RUN apk add redis postgresql
RUN pip3 install iniconfig colorlog pwgen

# COPY docker/actinia-parallel-plugin-test/start.sh /src/start.sh

ENTRYPOINT ["/bin/sh"]
CMD ["/src/start.sh"]

# # add data for tests
# RUN wget --quiet https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_micro.zip && \
#   unzip nc_spm_08_micro.zip && \
#   rm -f nc_spm_08_micro.zip && \
#   mv nc_spm_08_micro /actinia_core/grassdb/nc_spm_08
# RUN grass -e -c 'EPSG:4326' /actinia_core/grassdb/latlong_wgs84

# copy needed files and configs for test
COPY docker/actinia-parallel-plugin-test/actinia-parallel-plugin-test.cfg /etc/default/actinia
COPY docker/actinia-parallel-plugin-test/actinia-parallel-plugin-test.cfg /etc/default/actinia-parallel-plugin-test
COPY . /src/actinia-parallel-plugin/

WORKDIR /src/actinia-parallel-plugin/

RUN chmod a+x tests_with_redis.sh
RUN make install

# RUN make test
