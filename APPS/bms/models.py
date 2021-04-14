from django.db import models

# Create your models here.


class Student(models.Model):
    student_id = models.CharField(max_length=30, verbose_name="学号", unique=True)
    student_name = models.CharField(max_length=30, verbose_name="姓名")
    student_pwd = models.CharField(max_length=30, verbose_name="密码")
    borrow_max = models.IntegerField(verbose_name="最大借阅数", default=30)
    borrow_now = models.IntegerField(verbose_name="已借阅数", default=0)


class Book(models.Model):
    book_name = models.CharField(max_length=256, verbose_name="书名")
    author = models.CharField(max_length=256, verbose_name="作者")
    press = models.CharField(max_length=256, verbose_name="出版社")
    borrow_status = models.BooleanField(verbose_name="借阅状态", default=1)


class BorrowLog(models.Model):
    state = (
        (0, "预约"),
        (1,  "已借阅"),
        (2, "已归还")
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.SmallIntegerField(verbose_name="借阅状态", choices=state, default=0)
    order_time = models.DateField(verbose_name="预约时间")
    borrow_time = models.DateField(verbose_name="借阅时间")
    giveback_time = models.DateField(verbose_name="归还时间")


class Manager(models.Model):
    manager_id = models.CharField(max_length=12, verbose_name="工号")
    manager_name = models.CharField(max_length=12, verbose_name="管理员姓名")
    authority = models.SmallIntegerField(verbose_name="权限等级")
