#!/bin/bash

# Удаляем пики
echo Чистка пиков
find /home/da3x/freelance/teacher_book/ -name *.pyc -delete

#Создаем архив
echo Создание архива
catalog=pwd
cd ~/freelance/teacher_book
tar -czf ~/freelance/teacher_book/app.tar.gz application
cd $catalog

# Копируем исходники на сервак
echo Копирование файлов на сервер
scp ~/freelance/teacher_book/app.tar.gz u48649@u48649.netangels.ru:~/buffer/

# Перезапись исходников
echo Распаковка файлов и перезапуск сервера
ssh u48649@u48649.netangels.ru << EOF
rm -rf ~/teacher.dancehustle.ru/www/application
tar -xf ~/buffer/app.tar.gz -C ~/teacher.dancehustle.ru/www
rm -rf ~/buffer/*
# Запуск сервера
python ~/teacher.dancehustle.ru/www/manage.py migrate
pkill -u u48649 -f django-wrapper.fcgi
exit
EOF

#Удаляем архив
rm app.tar.gz

echo Обновление прошло