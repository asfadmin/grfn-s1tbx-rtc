FROM ubuntu:18.04
LABEL MAINTAINER="Alaska Satellite Facility"

COPY snap_install.varfile /usr/local/etc/snap_install.varfile
RUN apt-get update && \
    apt-get install -y software-properties-common python3 python3-pip python python-pip python-gdal && \
    add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable && \
    apt-get update && \
    apt-get install -y gdal-bin wget && \
    wget --no-verbose --directory-prefix=/usr/local/etc/ http://step.esa.int/downloads/6.0/installers/esa-snap_sentinel_unix_6_0.sh && \
    sh /usr/local/etc/esa-snap_sentinel_unix_6_0.sh -q -varfile /usr/local/etc/snap_install.varfile && \
    rm /usr/local/etc/esa-snap_sentinel_unix_6_0.sh && \
    pip3 install requests jinja2 lxml && \
    pip install boto3 lxml && \
    wget --no-verbose --directory-prefix=/usr/local/etc/ https://github.com/asfadmin/hyp3-lib/archive/v0.8.tar.gz && \
    tar xvzf /usr/local/etc/v0.8.tar.gz -C /usr/local/etc/ && \
    mkdir /output /root/.aws

COPY gpt.vmoptions /usr/local/snap/bin/gpt.vmoptions
ENV PATH=$PATH:/usr/local/snap/bin
ENV PYTHONPATH=$PYTHONPATH:/usr/local/etc/hyp3-lib-0.8/src
ENV HOME=/root
WORKDIR $HOME
COPY src $HOME
COPY get_dem.py.cfg /usr/local/etc/hyp3-lib-0.8/config/get_dem.py.cfg
COPY credentials /root/.aws/credentials

ENTRYPOINT ["python3", "-u", "rtc.py"]
