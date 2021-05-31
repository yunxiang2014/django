from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer()
    user = UserSerializer()
    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'user', 'tweet')
