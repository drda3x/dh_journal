#!/bin/bash

# Удаляем пики
echo Чистка пиков
find $1 -name *.pyc -delete

#Создаем архив
echo Создание архива
catalog=pwd
cd $1
tar -czf $1/app.tar.gz application
cd $catalog

# Копируем исходники на сервак
echo Копирование файлов на сервер
scp $1/app.tar.gz u48649@u48649.netangels.ru:~/buffer/

# Перезапись исходников
echo Распаковка файлов и перезапуск сервера
ssh u48649@u48649.netangels.ru << EOF
rm -rf ~/dev.teacher.dancehustle.ru/www/application
tar -xf ~/buffer/app.tar.gz -C ~/dev.teacher.dancehustle.ru/www
rm -rf ~/buffer/*
rm -rf ~/dev.teacher.dancehustle.ru/www/static/*
# Запуск сервера
source ~/python/bin/activate
python ~/dev.teacher.dancehustle.ru/www/manage.py collectstatic --noinput
python ~/dev.teacher.dancehustle.ru/www/manage.py migrate
pkill -u u48649 -f django-wrapper.fcgi
exit
EOF

#Удаляем архив
rm app.tar.gz

echo Обновление прошло
