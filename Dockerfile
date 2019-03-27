FROM ubuntu:18.04
LABEL MAINTAINER="Alaska Satellite Facility"

COPY snap_install.varfile /usr/local/etc/snap_install.varfile
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable && \
    apt-get update && \
    apt-get install -y gdal-bin wget && \
    wget --no-verbose --directory-prefix=/usr/local/etc/ http://step.esa.int/downloads/6.0/installers/esa-snap_sentinel_unix_6_0.sh && \
    sh /usr/local/etc/esa-snap_sentinel_unix_6_0.sh -q -varfile /usr/local/etc/snap_install.varfile && \
    rm /usr/local/etc/esa-snap_sentinel_unix_6_0.sh && \
    mkdir /output

COPY gpt.vmoptions /usr/local/snap/bin/gpt.vmoptions
COPY rtc.sh /usr/local/sbin/

ENTRYPOINT ["/usr/local/sbin/rtc.sh"]
