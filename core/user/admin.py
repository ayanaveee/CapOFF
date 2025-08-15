from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser

class MyUserAdmin(UserAdmin):
    model = MyUser
    list_display = ('email', 'username', 'phone_number', 'is_admin')
    list_filter = ('is_admin',)
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('phone_number', 'avatar', 'address')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'phone_number', 'avatar', 'address', 'is_admin'),
        }),
    )

    filter_horizontal = ()

admin.site.register(MyUser, MyUserAdmin)
