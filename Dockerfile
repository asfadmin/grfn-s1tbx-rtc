FROM ubuntu:18.04
LABEL MAINTAINER="Alaska Satellite Facility"

COPY snap_install.varfile /usr/local/etc/snap_install.varfile
RUN apt-get update && \
    apt-get install -y software-properties-common python3 python3-pip && \
    add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable && \
    apt-get update && \
    apt-get install -y gdal-bin wget && \
    wget --no-verbose --directory-prefix=/usr/local/etc/ http://step.esa.int/downloads/6.0/installers/esa-snap_sentinel_unix_6_0.sh && \
    sh /usr/local/etc/esa-snap_sentinel_unix_6_0.sh -q -varfile /usr/local/etc/snap_install.varfile && \
    rm /usr/local/etc/esa-snap_sentinel_unix_6_0.sh && \
    pip3 install requests jinja2 lxml && \
    mkdir /output

COPY gpt.vmoptions /usr/local/snap/bin/gpt.vmoptions
ENV PATH=$PATH:/usr/local/snap/bin
ENV HOME=/root
WORKDIR $HOME
COPY src $HOME

ENTRYPOINT ["python3", "-u", "rtc.py"]
