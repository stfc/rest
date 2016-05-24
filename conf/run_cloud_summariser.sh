#!/bin/bash

# Stop the dbloader
/sbin/service apeldbloader-cloud stop

# Wait to ensure dbloader has stopped
sleep 5

# Run the summariser
su apel -c 'python /usr/bin/apelsummariser -d /etc/apel/clouddb.cfg -c /etc/apel/cloudsummariser.cfg'

# Wait to ensure summariser has stopped
sleep 5

# Start the dbloader
/sbin/service apeldbloader-cloud start

