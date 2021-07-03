# Create your views here.
from newsfeeds.services import NewsFeedService
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate, TweetSerializerForDetail
from tweets.models import Tweet
from utils.decorators import required_params
from utils.paginations import EndlessPagination
from tweets.services import TweetService

class TweetViewSet(viewsets.GenericViewSet):
    """
    API endpoint that allows user to create, list tweets
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        # <Homework 1> 通过某个 query 参数 with_all_comments 来决定是否需要带上所有comments
        # <Homework 2> 通过某个 query 参数 with_preview_comments 来决定是否需要带上前三条 comments
        serializer = TweetSerializerForDetail(
            self.get_object(),
            context={'request': request},
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        重载 create 方法， 因为需要默认用当前登录用户 作为 tweet.user
        """
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=400)
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        serializer = TweetSerializer(tweet, context={'request': request})
        return Response(serializer.data, status=201)

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).prefetch_related('user')

        cached_tweets = TweetService.get_cached_tweets(user_id)
        page = self.paginator.paginate_cached_list(cached_tweets, request)
        if page is None:
            #这句查询会被翻译为
            #select * from twitter_tweets
            #where user_id = xxx
            # order by created_at desc
            # 这句SQL 查询会用到user 和 created_at 的联合索引
            # 单纯 的user 索引是不够的
            queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
            page = self.paginate_queryset(queryset)
        serializer = TweetSerializer(
            page,
            context={'request': request},
            many=True)
        return self.get_paginated_response(serializer.data)



