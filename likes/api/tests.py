from rest_framework.test import APIClient

from testing.testcases import TestCase

LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'

class LikeApiTests(TestCase):

    def setUp(self):
        self.linghu, self.linghu_client = self.create_user_and_client('linghu')
        self.dongxie, self.dongxie_client = self.create_user_and_client('dongxie')
        self.anonymous_client = APIClient()

    def test_tweet_likes(self):
        tweet = self.create_tweet(self.linghu)
        data = {'content_type': 'tweet', 'object_id': tweet.id}

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        #get is not allowed
        response = self.linghu_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # post success
        response = self.linghu_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        # duplicate likes
        self.linghu_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.dongxie_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_comment_likes(self):
        tweet = self.create_tweet(self.linghu)
        comment = self.create_comment(self.dongxie, tweet, 'original')
        data = {'content_type': 'comment', 'object_id': comment.id}

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # get is not allowed
        response = self.linghu_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        #wrong content_type
        response = self.linghu_client.post(LIKE_BASE_URL, {
            'content_type': 'coment',
            'object_id': comment.id,
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        #wrong object_id
        response = self.linghu_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id' in response.data['errors'], True)

        # post success
        response = self.linghu_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        # duplicate likes
        response = self.linghu_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)
        self.dongxie_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)

    def test_cancel(self):
        tweet = self.create_tweet(self.linghu)
        comment = self.create_comment(self.dongxie, tweet)
        like_tweet_data = {'content_type': 'tweet', 'object_id': tweet.id}
        like_comment_data = {'content_type': 'comment', 'object_id': comment.id}
        self.linghu_client.post(LIKE_BASE_URL, like_comment_data)
        self.dongxie_client.post(LIKE_BASE_URL, like_tweet_data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # login required
        response = self.anonymous_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 403)

        # get is not allowed
        response = self.linghu_client.get(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 405)

        #wrong content_type
        response = self.linghu_client.post(LIKE_CANCEL_URL, {
            'content_type': 'wrong',
            'object_id': 1,
        })
        self.assertEqual(response.status_code, 400)

        #wrong object_id
        response = self.linghu_client.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)

        #dongxie has not liked before
        response = self.dongxie_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # successful canceled
        response = self.linghu_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        # linghu has not like before
        response = self.linghu_client.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        #dongxie like has been cancled
        response = self.dongxie_client.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 0)
        self.assertEqual(comment.like_set.count(), 0)





