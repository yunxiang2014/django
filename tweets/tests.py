from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from testing.testcases import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import Tweet
from tweets.models import TweetPhoto
from utils.time_helpers import utc_now


# Create your tests here.


class TweetTests(TestCase):

    def setUp(self):
        self.linghu = self.create_user(username='linghu')
        self.tweet = self.create_tweet(self.linghu, content='Jiuzhang dafa good')

    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_create_photo(self):
        photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.linghu,
        )
        self.assertEqual(photo.user, self.linghu)
        self.assertEqual(photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(self.tweet.tweetphoto_set.count(), 1)
