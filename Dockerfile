# Switch to the target image
FROM alpine:3.12.7

ENV IP		    0.0.0.0
ENV PORT		  1688
ENV EPID		  ""
ENV LCID		  1033
ENV SQLITE    false
ENV HWID		  "364F463A8863D35F"
ENV LOGLEVEL	ERROR
ENV LOGFILE   /var/log/pykms_logserver.log
ENV LOGSIZE	  ""
ENV CLIENT_COUNT	26
ENV ACTIVATION_INTERVAL	120
ENV RENEWAL_INTERVAL	10080
ENV PYKMS_DB      /db/pykms_database.db
ENV UID       ""
ENV GID       ""

COPY docker/docker-py3-kms/start.sh /usr/bin/start.sh
COPY py-kms /home/py-kms

#hadolint ignore=DL3013,DL3018
RUN apk add --no-cache --update \
    bash \
    git \
    py3-argparse \
    py3-flask \
    py3-pygments \
    python3-tkinter \
    sqlite-libs \
    py3-pip \
    shadow && \
    git clone https://github.com/coleifer/sqlite-web.git /tmp/sqlite_web && \
    mv /tmp/sqlite_web/sqlite_web /home/ && \
    rm -rf /tmp/sqlite_web && \
    pip3 install --no-cache-dir peewee tzlocal pysqlite3 && \
    mkdir /db/ && \
    chmod a+x /usr/bin/start.sh && \
    apk del git && \
    adduser -S py-kms -G users

WORKDIR /home/py-kms

EXPOSE ${PORT}/tcp
EXPOSE 8080

ENTRYPOINT ["/usr/bin/start.sh"]
