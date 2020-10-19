#!/bin/bash
# EN: Start daemons
# RU: Запуск демонов
set -x

cd /home/py-kms

CMD1="/usr/bin/python3 pykms_Server.py ${IP} ${PORT} -l ${LCID} -c ${CLIENT_COUNT} -a ${ACTIVATION_INTERVAL} -r ${RENEWAL_INTERVAL} -w ${HWID} -V ${LOGLEVEL}"

[[ "$SQLITE" != false ]] && PYARGS+=" -s ${PYKMS_DB}"

[ "$EPID" != "" ] && PYARGS+=" -e ${EPID}"

[ "$LOGSIZE" == "" ] && PYARGS+= " -S ${LOGSIZE}"

CMDALL="${CMD1} ${PYARGS}"

if [ "${SQLITE}" != false ]; then
  /bin/bash -c "$CMDALL &"
  sleep 5
  /usr/bin/python3 pykms_Client.py ${IP} ${PORT} -m Windows10 &
  /usr/bin/python3 /home/sqlite_web/sqlite_web.py -H ${IP} -x ${PYKMS_DB} --read-only
else
  $CMDALL
fi
