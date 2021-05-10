from django.contrib import admin
from APPS.bms.models import Student, Book, BorrowLog


class StudentAdmin(admin.ModelAdmin):
    pass


class BookAdmin(admin.ModelAdmin):
    pass


class BorrowLogAdmin(admin.ModelAdmin):
    pass


admin.site.register(Book, BookAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(BorrowLog, BorrowLogAdmin)
