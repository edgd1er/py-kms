#!/bin/bash
# EN: Start daemons
# RU: Запуск демонов
set -x
SUDO="sudo -u py-kms "

if [[ ${#UID} -gt 1 ]]; then
  #set docker py-kms user with UID number
  echo "py-kms has now ${UID} as UID"
  usermod -u ${UID} py-kms
fi

if [[ ${#GID} -gt 1 ]]; then
  # set container py-kms group with GID number
  echo "users group has now ${GID} as group id"
  groupmod -g ${GID} py-kms
fi

cd /home/py-kms

CMD1="/usr/bin/python3 pykms_Server.py ${IP} ${PORT} -l ${LCID} -c ${CLIENT_COUNT} -a ${ACTIVATION_INTERVAL} -r ${RENEWAL_INTERVAL} -w ${HWID} -V ${LOGLEVEL}"

[[ "$SQLITE" != false ]] && PYARGS+=" -s ${PYKMS_DB}"

[ "$EPID" != "" ] && PYARGS+=" -e ${EPID}"

[ "$LOGSIZE" == "" ] && PYARGS+= " -S ${LOGSIZE}"

CMDALL="${CMD1} ${PYARGS}"

if [ "${SQLITE}" != false ]; then
  ${SUDO} /bin/bash -c "$CMDALL &"
  sleep 5
  ${SUDO} /usr/bin/python3 pykms_Client.py ${IP} ${PORT} -m Windows10 &
  ${SUDO} /usr/bin/python3 /home/sqlite_web/sqlite_web.py -H ${IP} -x ${PYKMS_DB} --read-only
else
  ${SUDO}  $CMDALL
fi
