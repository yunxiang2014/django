from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    """
    这个permission 负责检查 obj.user 是不是 == request.user
    之恶个类比较通用的， 今后如果有其他也用到这个类的地方， 可以将文件放到一个共享的位置
    permission 会一个个被执行
    如果 detail = false 的action ， 只检测 has_permission
    如果 detail = True 的action. 同时检测has_permission 和 has_object_permission
    如果出错的时候， 默认的错误信息会显示 IsObjectOwner.message 中的内容
    """
    message = "you do not have permission to access this object"

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user

