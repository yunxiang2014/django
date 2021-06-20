from django.contrib.auth.models import User
from friendships.api.paginations import FriendshipPagination
from friendships.api.serializers import FollowerSerializer, FriendshipSerializerForCreate, FollowingSerializer
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


class FriendshipViewSet(viewsets.GenericViewSet):
    # 我们希望 post /api/friendships/1/follow  是去 follow user_id = 1 的用户
    # 因此 这里 queryset 需要是 user.objects.all()
    # 如果是 friendships.objects.all 的话 会出现 404 not found
    # 因为detail=True 的action 会默认去调用 get_object() 也就是
    # queryset.filer(pk=1) 查询一下这个object 在不在
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()
    # 一般来说，不同的 views 所需要的 pagination 规则肯定是不同的，因此一般都需要自定义
    pagination_class = FriendshipPagination

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # get /api/friendships/1/followers/
        # get http://172.24.76.93:8000/api/friendships/3/followers/
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # check i fuser with id=pk exists
        # self.get_object()
        # 特殊判断重复 follow 的情况 （比如前端猛点多次follow）
        # 静默处理， 不报错， 因为这类重复操作 因为网络延迟的原因会比较多， 没必要当做错误处理
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
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
        # https://docs.djangoproject.com/en/3.1/ref/models/quersets/#delete
        # Queryset 的 delete 操作返回两个值， 一个是删除多少数据， 一个是具体每种类型删除了多少
        # 为什么会出现多种类型数据的删除？ 因为可以因为 foreign key 设置了 cascade 出现级联
        # 删除， 也就是 比如 A model 的某个属性是 B model 的 foreign key, 并且设置了 on_delete=models.CASCADE,
        # 那么当 B 的 莫格数据删除的时候， A 中的关联也会被删除。
        # 所以 CASCADE 是很危险的， 我们一般最好不用。 而是用 on_delete=models.set_null
        # 取而代之， 这样至少可以避免误删除带来的多米诺效应
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=unfollow_user,
        ).delete()

        return Response({'success': True, 'deleted': deleted})

    def list(selfself, request):
        return Response({
            'message': 'this is friendships home page',
        })
