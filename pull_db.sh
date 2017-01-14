#!/bin/bash

ssh u48649@u48649.netangels.ru ./scripts/make_db_backup.sh
scp u48649@u48649.netangels.ru:~/backups/db_backup.sql ../db_dumps/

mysql -u tbtest -ptest << EOF

drop database TBTEST;
create database TBTEST;
use TBTEST;
source ../db_dumps/db_backup.sql;

EOF
