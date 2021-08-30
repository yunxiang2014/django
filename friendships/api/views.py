from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from friendships.api.serializers import FollowerSerializer, FriendshipSerializerForCreate, FollowingSerializer
from friendships.models import HBaseFollower, HBaseFollowing, Friendship
from friendships.services import FriendshipService
from gatekeeper.models import GateKeeper
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from utils.paginations import EndlessPagination


class FriendshipViewSet(viewsets.GenericViewSet):
    # 我们希望 post /api/friendships/1/follow  是去 follow user_id = 1 的用户
    # 因此 这里 queryset 需要是 user.objects.all()
    # 如果是 friendships.objects.all 的话 会出现 404 not found
    # 因为detail=True 的action 会默认去调用 get_object() 也就是
    # queryset.filer(pk=1) 查询一下这个object 在不在
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()
    # 一般来说，不同的 views 所需要的 pagination 规则肯定是不同的，因此一般都需要自定义
    pagination_class = EndlessPagination

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followers(self, request, pk):
        # get /api/friendships/1/followers/
        # get http://172.24.76.93:8000/api/friendships/3/followers/
        if GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            page = self.paginator.paginate_hbase(HBaseFollower, (pk,), request)
        else:
            friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
            page = self.paginate_queryset(friendships)

        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followings(self, request, pk):
        if GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            page = self.paginator.paginate_hbase(HBaseFollowing, (pk,), request)
        else:
            friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
            page = self.paginate_queryset(friendships)

        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.paginator.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def follow(self, request, pk):
        # check i fuser with id=pk exists
        # self.get_object()
        # 特殊判断重复 follow 的情况 （比如前端猛点多次follow）
        # 静默处理， 不报错， 因为这类重复操作 因为网络延迟的原因会比较多， 没必要当做错误处理
        if FriendshipService.has_followed(request.user.id, int(pk)):
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)
        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response({'success': True}, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def unfollow(self, request, pk):
        # check user is exists, raise 404 if no user id == pk  http://172.24.76.93:8000/api/friendships/6/unfollow/
        unfollow_user = self.get_object()
        # self.get_object()
        # 注意 pk 的类型是str, 所以要做类型转换
        if request.user.id == unfollow_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        deleted = FriendshipService.unfollow(request.user.id, int(pk))

        return Response({'success': True, 'deleted': deleted})

    def list(selfself, request):
        return Response({
            'message': 'this is friendships home page',
        })
