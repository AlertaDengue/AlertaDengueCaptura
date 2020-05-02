#!/bin/bash

# Basic if statement
if [ -z ${HOST_UID} ]
  then
    useradd --shell=/bin/bash --home=/srv/alertadengue/ --create-home alertadengue
  else
    groupadd --gid ${HOST_GID} alertadengue # we need the same GID as the host.
    useradd --shell=/bin/bash --home=/srv/alertadengue/ --create-home alertadengue -u ${HOST_UID} -g ${HOST_GID}
fi;
