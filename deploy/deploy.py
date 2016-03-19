# -*- coding:utf-8 -*-

# BEFORE START!!!!!!
# Create file named "config.py"
# set there the HOST_NAME, USER_NAME and PASSWORD variables

import config
from paramiko import AutoAddPolicy
from paramiko.client import SSHClient

client = SSHClient()
client.set_missing_host_key_policy(AutoAddPolicy())
client.connect(hostname=config.HOST_NAME, username=config.USER_NAME, password=config.PASSWORD)

# Передача файлов
sftp = client.open_sftp()
if sftp:
	sftp.put('hw.txt', '~')

stdin, stdout, stderr = client.exec_command('pkill -u u48649 -f django-wrapper.fcgi')

for line in stdout:
    print line.strip('\n')
    
client.close()