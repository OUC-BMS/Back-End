# -*- coding:utf-8 -*-

from django.http import QueryDict
from django.utils.deprecation import MiddlewareMixin


class HttpOtherMethodMiddleware(MiddlewareMixin):

    def process_request(self, request):

        """
        可以继续添加 HEAD, PATCH, OPTIONS以及自定义方法
        :param request: 经过原生中间件处理过后的请求
        :return:
        """
        try:
            http_method = request.META['REQUEST_METHOD']
            if http_method.upper() not in ('GET', 'POST'):
                setattr(request, http_method.upper(), QueryDict(request.body))
        except Exception:
            pass
        finally:
            return
