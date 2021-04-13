from functools import wraps
from APPS.utils.http import JsonResponse
from BMSResponseState import AccountResponseState


def login_required(func):

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('id', None) is None:
            return JsonResponse(AccountResponseState.NOT_LOGIN)

        # 正常处理
        return func(request, *args, **kwargs)

    return wrapper


def allowed_method(methods):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return JsonResponse(AccountResponseState.REQUEST_METHOD_ERROR)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
