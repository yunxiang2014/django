from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from testing.testcases import TestCase
from tweets.constants import TweetPhotoStatus
from tweets.models import Tweet
from tweets.models import TweetPhoto
from utils.time_helpers import utc_now
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer


# Create your tests here.


class TweetTests(TestCase):

    def setUp(self):
        self.clear_cache()
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

    def test_cache_tweet_in_redis(self):
        tweet = self.create_tweet(self.linghu)
        conn = RedisClient.get_connection()
        serialized_data = DjangoModelSerializer.serialize(tweet)
        conn.set(f'tweet:{tweet.id}', serialized_data)
        data = conn.get(f'tweet:not_exists')
        self.assertEqual(data, None)

        data = conn.get(f'tweet:{tweet.id}')
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(tweet, cached_tweet)
