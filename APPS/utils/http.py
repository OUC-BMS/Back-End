from django.http import HttpResponse
import json


class JsonResponse(HttpResponse):

    def __init__(self, state, data=None, **kwargs):
        if data is None:
            data = {}
        kwargs.setdefault('content_type', 'application/json')
        data["code"] = state[0]
        data["msg"] = state[1]
        data = json.dumps(data)
        super().__init__(content=data, **kwargs)