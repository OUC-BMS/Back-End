import re
import json
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.forms.models import model_to_dict

from models import Student, Book

from APPS.utils.http import JsonResponse
from BMSResponseState import AccountResponseState, BMSResponseState
from APPS.utils.validator import BaseValidator


class UsernameValidator(BaseValidator):

    @classmethod
    def validate(cls, username, *args, **kwargs):
        if len(username) < 4:
            return AccountResponseState.USERNAME_TOO_SHORT_ERROR
        if len(username) > 30:
            return AccountResponseState.USERNAME_TOO_LONG_ERROR
        if re.search(r'[^A-Za-z0-9_]', username):
            return AccountResponseState.USERNAME_FORMAT_ERROR

        return AccountResponseState.VALIDATE_OK


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

        return AccountResponseState.VALIDATE_OK


class PcodeValidator(BaseValidator):
    @classmethod
    def validate(cls, p_code, *args, **kwargs):
        if len(p_code) != 11 or not re.match("[0-9]+", p_code):
            return AccountResponseState.PCODE_FORMAT_ERROR

        return AccountResponseState.VALIDATE_OK


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
                return BMSResponseState.PARAMETER_LACK_ERROR
            if not isinstance(data[field_name], field_type):
                return BMSResponseState.PARAMETER_TYPE_ERROR
        return BMSResponseState.VALIDATE_OK


def login(request):
    p_code = request.POST.get("pcode")
    pwd = request.POST.get("password")

    state = PcodeValidator.validate(p_code)
    if state != AccountResponseState.VALIDATE_OK:
        return JsonResponse(state)

    state = PWDValidator.validate(pwd)
    if state != AccountResponseState.VALIDATE_OK:
        return JsonResponse(state)

    if not Student.objects.exists(student_id=p_code):
        return JsonResponse(AccountResponseState.PCODE_NOT_EXISTED_ERROR)

    stu = Student.objects.get(student_id=p_code)
    if not check_password(pwd, stu.student_pwd):
        return JsonResponse(AccountResponseState.PASSWORD_NOT_MATCH_ERROR)
    data = {
        "data": {
            "username": stu.student_name,
            "userid": stu.student_id
        }
    }
    request.session["id"] = p_code
    return JsonResponse(AccountResponseState.OK, data)


def register(request):
    username = request.POST.get("name")
    p_code = request.POST.get("userid")
    pwd = request.POST.get("password")

    state = UsernameValidator.validate(username)
    if state != AccountResponseState.VALIDATE_OK:
        return JsonResponse(state)
    state = PWDValidator.validate(pwd)
    if state != AccountResponseState.VALIDATE_OK:
        return JsonResponse(state)
    state = PcodeValidator.validate(p_code)
    if state != AccountResponseState.VALIDATE_OK:
        return JsonResponse(state)
    usr = Student(student_id=p_code,
                  student_name=username,
                  student_pwd=make_password(pwd))
    usr.save()
    return JsonResponse(AccountResponseState.OK)


def bms(request):
    if request.method == "GET":
        query = request.GET.get("search")
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
            book_data = model_to_dict(q)
            data["data"]["result"].append(book_data)
        return JsonResponse(BMSResponseState.OK, data)

    elif request.method == "POST":
        request_data = request.body
        request_dict = json.loads(request_data.decode('utf-8'))
        required_fields = [
            ("name", str),
            ("author", str),
            ("press", str)
        ]
        state = JsonDataValidator.validate(request_dict, required_fields=required_fields)
        if state != BMSResponseState.VALIDATE_OK:
            book = Book(press=request_dict["press"],
                        book_name=request_dict["name"],
                        author=request_dict["author"])
            book.save()
            return JsonResponse(BMSResponseState.OK)
        else:
            return JsonResponse(state)

    elif request.method == "DELETE":
        pass

    elif request.method == "PUT":
        pass
    else:
        return JsonResponse(AccountResponseState.REQUEST_METHOD_ERROR)
