from rest_framework import serializers

from accounts.api.serializers import UserSerializer
from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer()
    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'tweet')
