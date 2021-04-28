from enum import Enum

from APPS.utils import ResponseState


class AccountResponseState(Enum):
    # 枚举类继承存在问题
    DEBUG = (10000, 'Debug')
    OK = (20000, '成功')
    FORBIDDEN = (50403, 'Forbidden')
    UNEXPECTED_ERROR = (50000, '意外错误')
    REQUEST_METHOD_ERROR = (40000, '请求方法错误')
    JSON_DECODE_ERROR = (40001, 'JSON 解析错误')
    PARAMETER_LACK_ERROR = (46001, '缺少参数')
    PARAMETER_TYPE_ERROR = (46002, '参数类型错误')
    NOT_LOGIN = (44001, '未登陆')


    VALIDATE_OK = (20000, '验证通过')

    USERNAME_REQUIRED_ERROR = (41002, '缺少用户名')
    PASSWORD_REQUIRED_ERROR = (41003, '缺少密码')
    EMAIL_REQUIRED_ERROR = (41004, '缺少邮箱')

    USERNAME_TOO_SHORT_ERROR = (42001, '用户名应不少于 2 位')
    USERNAME_TOO_LONG_ERROR = (42002, '用户名应不多于 20 位')
    USERNAME_FORMAT_ERROR = (42003, '用户名仅能含有字母、数字和下划线')
    PASSWORD_TOO_SHORT_ERROR = (42004, '密码应不少于 6 位')
    PASSWORD_TOO_LONG_ERROR = (42005, '密码应不多于 20 位')
    PASSWORD_FORMAT_ERROR = (42006, '密码应仅包含合法字符')
    PASSWORD_LACK_NUMBER_ERROR = (42007, '密码必须包含数字')
    PASSWORD_LACK_LETTER_ERROR = (42008, '密码必须包含字母')

    USER_EXISTED_ERROR = (43001, '用户名已存在')
    EMAIL_EXISTED_ERROR = (43002, '邮箱已存在')

    USER_NOT_EXISTED_ERROR = (43003, '用户名不存在')
    PASSWORD_NOT_MATCH_ERROR = (43004, '密码错误')

    PCODE_NOT_EXISTED_ERROR = (43005, '学号未注册')
    PCODE_FORMAT_ERROR = (43006, '学号格式错误')


class BMSResponseState(Enum):

    DEBUG = (10000, 'Debug')
    OK = (20000, '成功')
    FORBIDDEN = (50403, 'Forbidden')
    UNEXPECTED_ERROR = (50000, '意外错误')
    REQUEST_METHOD_ERROR = (40000, '请求方法错误')
    JSON_DECODE_ERROR = (40001, 'JSON 解析错误')
    PARAMETER_LACK_ERROR = (46001, '缺少参数')
    PARAMETER_TYPE_ERROR = (46002, '参数类型错误')
    NOT_LOGIN = (44001, '未登陆')

    VALIDATE_OK = (20000, '验证通过')

    BOOK_BORROW_NUM_EXCEEDED_ERROR = (46000, "超过最大借阅书籍数")
    NOT_ENOUGH_BOOK_ERROR = (46006, "没有可借阅的书籍")
    INVALID_BOOK_BORROW_ERROR = (46001, "无效的借阅操作")
    INVALID_BOOK_RETURN_ERROR = (46002, "无效的归还操作")
    INVALID_BOOK_ORDER_ERROR = (46003, "无效的预约操作")
    INVALID_BOOK_ADD_ERROR = (46004, "无效的增加操作")
    INVALID_BOOK_DELETE_ERROR = (46005, "无效的删除操作")

