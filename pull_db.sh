#!/bin/bash

mkdir $PWD/db_dumps

ssh u48649@u48649.netangels.ru ./scripts/make_db_backup.sh $1
scp u48649@u48649.netangels.ru:~/backups/db_backup.sql $PWD/db_dumps/

source settings.sh
mysql -u $DB_USER -p$DB_PASSWORD << EOF

drop database TBTEST;
create database TBTEST;
use TBTEST;
source $PWD/db_dumps/db_backup.sql;

EOF

rm -rf $PWD/db_dumps/db_backup.sql
