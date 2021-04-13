import re
from django.contrib.auth.hashers import make_password, check_password
from models import Student

from APPS.utils.http import JsonResponse
from BMSResponseState import AccountResponseState
from APPS.utils.validator import BaseValidator


class UsernameValidator(BaseValidator):

    @classmethod
    def validate(cls, username):
        if len(username) < 4:
            return AccountResponseState.USERNAME_TOO_SHORT_ERROR
        if len(username) > 30:
            return AccountResponseState.USERNAME_TOO_LONG_ERROR
        if re.search(r'[^A-Za-z0-9_]', username):
            return AccountResponseState.USERNAME_FORMAT_ERROR

        return AccountResponseState.VALIDATE_OK


class PWDValidator(BaseValidator):
    @classmethod
    def validate(cls, password):
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
    def validate(cls, p_code):
        if len(p_code) != 11 or not re.match("[0-9]+", p_code):
            return AccountResponseState.PCODE_FORMAT_ERROR

        return AccountResponseState.VALIDATE_OK


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

    request.session["id"] = p_code
    return JsonResponse(AccountResponseState.OK)


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
    pass
