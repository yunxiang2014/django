# django
provision commnet sql install part, perform it inside image.
add django admin user, run django_user.sh

avaialble reference for guide
https://www.django-rest-framework.org/


use database;
show tables;
explan

pip freeze > requirements.txt

start memcached
/usr/bin/memcached -u memcache -m 1024 -p 11222 -l 0.0.0.0 -d start

unsync task
pip install celery
prerequirment: redis or rabbitmq was installed on OS


# Hbase       path: cd /home/vagrant/hbase-2.3.5
sudo bash bin/start-hbase.sh
# Hbase thrift     path:  /home/vagrant/hbase-2.3.5
sudo bin/hbase-deamon.sh start thrift


# git usage
git checkout -b "branchname"
git add .
git commit - m "message"
git push origin -u branchname