from django.contrib import admin
from .models import Users_table

class UsersAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'username', 'user_type')
    search_fields = ('name', 'email', 'username')

admin.site.register(Users_table, UsersAdmin)
