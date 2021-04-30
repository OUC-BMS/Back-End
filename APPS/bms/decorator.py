from functools import wraps
from APPS.utils.http import JsonResponse
from APPS.bms.BMSResponseState import ResponseState


def login_required(func):

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('id', None) is None:
            return JsonResponse(ResponseState.NOT_LOGIN)

        # 正常处理
        return func(request, *args, **kwargs)

    return wrapper


def allowed_method(methods):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return JsonResponse(ResponseState.REQUEST_METHOD_ERROR)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
