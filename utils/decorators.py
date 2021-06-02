from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def required_params(method='GET', params=None):
    if params is None:
        params = []

    def decorator(view_func):   # view_func 待装饰的函数
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs): # 被装饰函数，由于被装饰函数需要调用待装函数的parameter, 所以声明
            #data = getattr(request, request_attr)
            if method.lower() == 'get':
                data = request.query_params
            else:
                data = request.data
            missing_params = [
                param for param in params if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message': u'missing {} in request'.format(params_str),
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)
            return view_func(instance, request, *args, **kwargs)  # 返回待装饰函数

        return _wrapped_view  # 返回被装饰函数

    return decorator  # 返回decorator
