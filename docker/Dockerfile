# Switch to the target image
FROM alpine:3.20 as minimal

ARG BUILD_COMMIT=unknown
ARG BUILD_BRANCH=unknown

ENV IP ::
ENV DUALSTACK 1
ENV PORT 1688
ENV EPID ""
ENV LCID 1033
ENV CLIENT_COUNT 26
ENV ACTIVATION_INTERVAL 120
ENV RENEWAL_INTERVAL 10080
ENV HWID RANDOM
ENV LOGLEVEL INFO
ENV LOGFILE STDOUT
ENV LOGSIZE ""
ENV TZ America/Chicago
ENV WEBUI 0

COPY py-kms /home/py-kms/
COPY docker/entrypoint.py /usr/bin/entrypoint.py
COPY docker/start.py /usr/bin/start.py
COPY LICENSE /LICENSE



#hadolint ignore=DL3013,DL3018,SC2261
RUN apk add --no-cache --update \
  python3 \
  py3-pip \
  sqlite-libs \
  ca-certificates \
  tzdata \
  shadow \
  netcat-openbsd \
  #minimal
  py3-dnspython>=2.4.2 py3-tzlocal>=5.1 \
  && mkdir /db/ \
  && adduser -S py-kms -G users -s /bin/bash \
  && chown py-kms:users /home/py-kms \
  # Fix undefined timezone, in case the user did not mount the /etc/localtime
  && ln -sf /usr/share/zoneinfo/UTC /etc/localtime \
  # Web-interface specifics
  && echo "$BUILD_COMMIT" > /VERSION \
  && echo "$BUILD_BRANCH" >> /VERSION \
  && chmod 755 /usr/bin/entrypoint.py

WORKDIR /home/py-kms

EXPOSE ${PORT}/tcp
EXPOSE 8080/tcp

HEALTHCHECK --interval=5m --timeout=3s --start-period=10s --retries=4 CMD echo | nc -z ${IP%% *} ${PORT} || exit 1

ENTRYPOINT [ "/usr/bin/python3", "-u", "/usr/bin/entrypoint.py" ]

FROM minimal as gui

#gui
#hadolint ignore=DL3013,DL3018,SC2261
RUN apk add --no-cache --update py3-flask>=2.3.3 py3-gunicorn>=21.2.0