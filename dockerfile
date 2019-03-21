FROM ubuntu:18.04
LABEL MAINTAINER="Alaska Satellite Facility"

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
RUN apt-get update && \
    apt-get install -y gdal-bin wget

RUN wget --no-verbose --directory-prefix=/usr/local/etc/ http://step.esa.int/downloads/5.0/installers/esa-snap_sentinel_unix_5_0.sh
COPY snap_install.varfile /usr/local/etc/snap_install.varfile
RUN sh /usr/local/etc/esa-snap_sentinel_unix_5_0.sh -q -varfile /usr/local/etc/snap_install.varfile
COPY gpt.vmoptions /usr/local/snap/bin/gpt.vmoptions
RUN rm /usr/local/etc/esa-snap_sentinel_unix_5_0.sh

RUN mkdir /output

COPY rtc.sh /usr/local/sbin/

ENTRYPOINT ["/usr/local/sbin/rtc.sh"]
