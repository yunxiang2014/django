from comments.models import Comment
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase as DjangoTestCase
from likes.models import Like
from tweets.models import Tweet


class TestCase(DjangoTestCase):

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'
            # 不能 写成 user.onjects.create()
            # 因为password 需要被加密， username 和 email 需要进行一些 normalize 处理
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user, content=content)

    def create_comment(self, user, tweet, content=None):
        return Comment.objects.create(user=user, tweet=tweet, content=content)

    def create_like(self, user, target):
        # target is comment or tweet
        instance, _ = Like.objects.get_or_create(
            # 使用__class__, 去找 database 里面的model
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        )
        return instance
