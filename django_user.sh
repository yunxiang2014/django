#!/usr/bin/env bash
# superuser名字
USER="admin"
# superuser密码
PASS="admin"
# superuser邮箱
MAIL="admin@twitter.com"
script="
from django.contrib.auth.models import User;
username = '$USER';
password = '$PASS';
email = '$MAIL';
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password);
    print('Superuser created.');
else:
    print('Superuser creation skipped.');
"
printf "$script" | python manage.py shell

# 如果想直接进入/vagrant路径下
# 请输入vagrant ssh命令进入
# 手动输入
# 输入ls -a
# 输入 vi .bashrc
# 在最下面，添加cd /vagrant

echo 'All Done!'

