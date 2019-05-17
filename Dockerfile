FROM ubuntu:18.04
LABEL MAINTAINER="Alaska Satellite Facility"

COPY snap_install.varfile /usr/local/etc/snap_install.varfile
RUN apt-get update && \
    apt-get install -y software-properties-common python3 python3-pip git wget && \
    add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable && \
    apt-get update && \
    apt-get install -y gdal-bin python-gdal python3-gdal && \
    wget --no-verbose --directory-prefix=/usr/local/etc/ http://step.esa.int/downloads/6.0/installers/esa-snap_sentinel_unix_6_0.sh && \
    sh /usr/local/etc/esa-snap_sentinel_unix_6_0.sh -q -varfile /usr/local/etc/snap_install.varfile && \
    rm /usr/local/etc/esa-snap_sentinel_unix_6_0.sh && \
    pip3 install requests jinja2 lxml boto3 shapely && \
    git clone --single-branch --branch python3 https://github.com/asfadmin/hyp3-lib.git /usr/local/etc/hyp3-lib && \
    mkdir /output /work && \
    chmod 777 /output /work

COPY gpt.vmoptions /usr/local/snap/bin/gpt.vmoptions
ENV PATH=$PATH:/usr/local/snap/bin
ENV PYTHONPATH=$PYTHONPATH:/usr/local/etc/hyp3-lib/src
ENV HOME=/work
WORKDIR $HOME
COPY src $HOME
COPY get_dem.py.cfg /usr/local/etc/hyp3-lib/config/get_dem.py.cfg

ENTRYPOINT ["python3", "-u", "rtc.py"]
