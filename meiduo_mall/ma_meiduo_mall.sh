#! /bin/bash
mysql.server start
sudo redis-server /etc/redis/redis.conf
python manage.py runserver