import re
import json

from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.forms.models import model_to_dict

from APPS.bms.models import Student, Book, BorrowLog
from APPS.utils.http import JsonResponse
from APPS.bms.BMSResponseState import AccountResponseState, BMSResponseState, ResponseState
from APPS.utils.validator import BaseValidator
from APPS.bms.decorator import login_required, manager_required


class UsernameValidator(BaseValidator):

    @classmethod
    def validate(cls, username, *args, **kwargs):
        if len(username) < 1:
            return AccountResponseState.USERNAME_TOO_SHORT_ERROR
        if len(username) > 30:
            return AccountResponseState.USERNAME_TOO_LONG_ERROR
        if re.search(r'[^A-Za-z0-9_]', username):
            return AccountResponseState.USERNAME_FORMAT_ERROR

        return ResponseState.VALIDATE_OK


class PWDValidator(BaseValidator):
    @classmethod
    def validate(cls, password, *args, **kwargs):
        if len(password) < 6:
            return AccountResponseState.PASSWORD_TOO_SHORT_ERROR
        if len(password) > 20:
            return AccountResponseState.PASSWORD_TOO_LONG_ERROR
        if not all(32 < ord(c) < 128 for c in password):
            return AccountResponseState.PASSWORD_FORMAT_ERROR
        if not re.search(r'[0-9]', password):
            return AccountResponseState.PASSWORD_LACK_NUMBER_ERROR
        if not re.search(r'[A-Za-z]', password):
            return AccountResponseState.PASSWORD_LACK_LETTER_ERROR

        return ResponseState.VALIDATE_OK


class PcodeValidator(BaseValidator):
    @classmethod
    def validate(cls, p_code, *args, **kwargs):
        if len(p_code) != 11 or not re.match("[0-9]+", p_code):
            return AccountResponseState.PCODE_FORMAT_ERROR
        if Student.objects.filter(student_id=p_code).exists():
            return AccountResponseState.USER_EXISTED_ERROR
        return ResponseState.VALIDATE_OK


class JsonDataValidator(BaseValidator):
    """
    required_fields: [(field_name: str, type)]
    """

    @classmethod
    def validate(cls, data, *args, **kwargs):
        required_fields = kwargs["required_fields"]
        for field in required_fields:
            field_name = field[0]
            field_type = field[1]
            if field_name not in data:
                return ResponseState.PARAMETER_LACK_ERROR
            if not isinstance(data[field_name], field_type):
                return ResponseState.PARAMETER_TYPE_ERROR
        return ResponseState.VALIDATE_OK


class StrLenValidator(BaseValidator):

    @classmethod
    def validate(cls, raw_string, *args, **kwargs):
        if "max_length" in kwargs.keys():
            max_length = kwargs["max_length"]
        else:
            max_length = 256
        return len(raw_string) <= max_length


def login(request):
    if request.method == "POST":
        json_data = json.loads(request.body.decode("utf-8"))
        p_code = json_data["name"]
        pwd = json_data["pwd"]

        state = PWDValidator.validate(pwd)
        if state != ResponseState.VALIDATE_OK:
            return JsonResponse(state)

        if not Student.objects.filter(student_id=p_code).exists():
            return JsonResponse(AccountResponseState.PCODE_NOT_EXISTED_ERROR)

        stu = Student.objects.get(student_id=p_code)
        if not check_password(pwd, stu.student_pwd):
            return JsonResponse(AccountResponseState.PASSWORD_NOT_MATCH_ERROR)
        data = {
            "data": {
                "username": stu.student_name,
                "userid": stu.student_id,
                "is_manager": stu.is_manager
            }
        }
        request.session["id"] = p_code
        request.session["manager"] = stu.is_manager
        return JsonResponse(ResponseState.OK, data)
    else:
        return JsonResponse(ResponseState.REQUEST_METHOD_ERROR)


def register(request):
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        required_fields = [
            ("name", str),
            ("userid", str),
            ("pwd", str)
        ]
        state = JsonDataValidator.validate(json_data, required_fields=required_fields)
        if state != ResponseState.VALIDATE_OK:
            return JsonResponse(state)
        username = json_data["name"]
        p_code = json_data["userid"]
        pwd = json_data["pwd"]
        state = UsernameValidator.validate(username)
        if state != ResponseState.VALIDATE_OK:
            return JsonResponse(state)
        state = PWDValidator.validate(pwd)
        if state != ResponseState.VALIDATE_OK:
            return JsonResponse(state)
        state = PcodeValidator.validate(p_code)
        if state != ResponseState.VALIDATE_OK:
            return JsonResponse(state)

        usr = Student.objects.create(student_id=p_code,
                                     student_name=username,
                                     student_pwd=make_password(pwd))
        usr.save()
        return JsonResponse(ResponseState.OK)
    else:
        return JsonResponse(ResponseState.REQUEST_METHOD_ERROR)


@login_required
def bms(request):
    if request.method == "GET":
        query = request.GET.get("search")
        if not query:
            return JsonResponse(BMSResponseState.QUERY_EMPTY_ERROR)
        queried_books = Book.objects.filter(Q(book_name__contains=query)
                                            | Q(author__contains=query)
                                            | Q(press__contains=query))
        data = {
            "data": {
                "total_num": 0,
                "result": [],
            },
        }
        data["data"]["total_num"] = len(queried_books)
        for q in queried_books:
            book_data = model_to_dict(q, exclude=["id", "borrow_status"])
            data["data"]["result"].append(book_data)
        return JsonResponse(ResponseState.OK, data)

    elif request.method == "POST":
        request_data = request.body
        request_dict = json.loads(request_data.decode('utf-8'))
        required_fields = [
            ("name", str),
            ("author", str),
            ("press", str)
        ]
        state = JsonDataValidator.validate(request_dict, required_fields=required_fields)
        if state == ResponseState.VALIDATE_OK:
            book = Book(press=request_dict["press"],
                        book_name=request_dict["name"],
                        author=request_dict["author"])
            book.save()
            return JsonResponse(ResponseState.OK)
        else:
            return JsonResponse(state)
    else:
        return JsonResponse(ResponseState.REQUEST_METHOD_ERROR)


@login_required
def u_info(request):
    if request.method == "GET":
        u_id = request.session.get("id")
        stu = Student.objects.get(student_id=u_id)
        data = {
            "data": model_to_dict(stu, exclude=["student_pwd", "id"])
        }
        return JsonResponse(ResponseState.OK, data)
    else:
        return JsonResponse(ResponseState.REQUEST_METHOD_ERROR)


@login_required
def book_checkout(request):
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        required_fields = [
            ("book_id", str),
        ]
        state = JsonDataValidator.validate(json_data, required_fields=required_fields)
        if state == ResponseState.VALIDATE_OK:
            user_id = request.session.get("id")
            book_id = json_data["book_id"]
            user = Student.objects.get(student_id=user_id)
            if user.borrow_now == user.borrow_max:
                return JsonResponse(BMSResponseState.BOOK_BORROW_NUM_EXCEEDED_ERROR)
            if not Book.objects.filter(book_id=book_id).exists():
                return JsonResponse(BMSResponseState.INVALID_BOOK_BORROW_ERROR)

            # 合法的数据
            book = Book.objects.get(book_id=book_id)
            if book.available == 0:
                return JsonResponse(BMSResponseState.NOT_ENOUGH_BOOK_ERROR)
            user.borrow_now += 1
            book.available -= 1
            user.save()
            book.save()
            if BorrowLog.objects.filter(student=user, book=book, status=0).exists():
                # 曾经预约过, 更新状态
                book_log = BorrowLog.objects.get(student=user, book=book, status=0)
                book_log.status = 1
                book_log.borrow_time = timezone.now()
                book_log.save()
            else:
                new_borrow_log = BorrowLog.objects.create(
                    student=user,
                    book=book,
                    status=1,
                    borrow_time=timezone.now()
                )
                new_borrow_log.save()
            return JsonResponse(ResponseState.OK)
        else:
            return JsonResponse(state)
    else:
        return JsonResponse(ResponseState.REQUEST_METHOD_ERROR)


@login_required
def book_appointment(request):
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        required_fields = [
            ("book_id", str),
        ]
        state = JsonDataValidator.validate(json_data, required_fields=required_fields)
        if state == ResponseState.VALIDATE_OK:
            user_id = request.session.get("id")
            book_id = json_data["book_id"]
            user = Student.objects.get(student_id=user_id)
            if not Book.objects.filter(book_id=book_id).exists():
                return JsonResponse(BMSResponseState.INVALID_BOOK_ORDER_ERROR)

            book = Book.objects.get(book_id=book_id)
            new_borrow_log = BorrowLog.objects.create(
                student=user,
                book=book,
                order_time=timezone.now()
            )
            new_borrow_log.save()
            return JsonResponse(ResponseState.OK)
        else:
            return JsonResponse(state)
    else:
        return JsonResponse(ResponseState.REQUEST_METHOD_ERROR)


@login_required
def book_return(request):
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        required_fields = [
            ("book_id", str),
        ]
        state = JsonDataValidator.validate(json_data, required_fields=required_fields)
        if state == ResponseState.VALIDATE_OK:
            user_id = request.session.get("id")
            book_id = json_data["book_id"]
            user = Student.objects.get(student_id=user_id)
            if not BorrowLog.objects.filter(book__book_id=book_id, student=user, status=1).exists():
                return JsonResponse(BMSResponseState.INVALID_BOOK_RETURN_ERROR)

            book = Book.objects.get(book_id=book_id)
            user.borrow_now -= 1
            book.available += 1
            user.save()
            book.save()
            BorrowLog.objects.filter(book__book_id=book_id, student=user, status=1) \
                .update(giveback_time=timezone.now(), status=2)
            return JsonResponse(ResponseState.OK)
        else:
            return JsonResponse(state)
    else:
        return JsonResponse(ResponseState.REQUEST_METHOD_ERROR)


@manager_required
def book_add(request):
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        if "book_id" not in json_data.keys():
            return JsonResponse(BMSResponseState.INVALID_BOOK_ADD_ERROR)
        else:
            book_id = json_data["book_id"]
            if Book.objects.filter(book_id=book_id).exists():
                book = Book.objects.get(book_id=book_id)
                required_fields = [
                    ("book_num", int),
                ]
                state = JsonDataValidator.validate(json_data, required_fields=required_fields)
                if state != ResponseState.VALIDATE_OK:
                    return JsonResponse(state)
                book_num = max(json_data["book_num"], 0)
                book_num = min(book_num, 65536)
                book.available += (book_num - book.stock)
                book.stock = book_num
                book.save()
                return JsonResponse(ResponseState.OK)
            else:
                required_fields = [
                    ("book_name", str),
                    ("book_author", str),
                    ("book_press", str),
                    ("book_num", int),
                ]
                state = JsonDataValidator.validate(json_data, required_fields=required_fields)
                if state != ResponseState.VALIDATE_OK:
                    return JsonResponse(state)
                book_name = json_data["book_name"]
                book_author = json_data["book_author"]
                book_press = json_data["book_press"]
                book_num = min(json_data["book_num"], 65536)
                book_id = json_data["book_id"]

                if len(book_name) > 256 \
                        or len(book_author) > 256 \
                        or len(book_press) > 256 \
                        or len(book_id) > 256:
                    return JsonResponse(BMSResponseState.INVALID_BOOK_ADD_ERROR)

                new_book = Book.objects.create(
                    book_id=book_id,
                    book_name=book_name,
                    press=book_press,
                    stock=book_num,
                    author=book_author,
                    available=book_num
                )
                new_book.save()
                return JsonResponse(ResponseState.OK)
    else:
        return JsonResponse(ResponseState.REQUEST_METHOD_ERROR)


@login_required
def borrow_log(request):
    if request.method == "GET":
        user_id = request.session.get("id")
        borrows = BorrowLog.objects.filter(student__student_id=user_id)
        history_list = []
        for one in borrows:
            history_list.append(
                {
                    "book_id": one.book.book_id,
                    "book_name": one.book.book_name,
                    "press": one.book.press,
                    "author": one.book.author,
                    "status": one.status,
                    "order_time": str(one.order_time),
                    "borrow_time": str(one.borrow_time),
                    "giveback_time": str(one.giveback_time)
                }
            )
        history = {
            "data": {
                "num": len(borrows),
                "result": history_list
            }
        }

        return JsonResponse(ResponseState.OK, data=history)
    else:
        return JsonResponse(ResponseState.REQUEST_METHOD_ERROR)
