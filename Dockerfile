FROM python:3.8-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

COPY docker-entrypoint.sh /opt/
COPY src /opt/src
RUN cd /opt/src \
    && pip install -r ./requirements.txt

RUN chmod +x opt/docker-entrypoint.sh
ENTRYPOINT ["opt/docker-entrypoint.sh"]