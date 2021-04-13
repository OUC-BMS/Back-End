from enum import Enum


class ResponseState(Enum):
    DEBUG = (10000, 'Debug')
    OK = (20000, '成功')
    FORBIDDEN = (50403, 'Forbidden')
    UNEXPECTED_ERROR = (50000, '意外错误')
    REQUEST_METHOD_ERROR = (40000, '请求方法错误')
    JSON_DECODE_ERROR = (40001, 'JSON 解析错误')
    NOT_LOGIN = (44001, '未登陆')
