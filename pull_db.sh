#!/bin/bash

ssh u48649@u48649.netangels.ru ./scripts/make_db_backup.sh $1
scp u48649@u48649.netangels.ru:~/backups/db_backup.sql ../db_dumps/

source settings.sh
mysql -u $DB_USER -p$DB_PASSWORD << EOF

drop database TBTEST;
create database TBTEST;
use TBTEST;
source ../db_dumps/db_backup.sql;

EOF
