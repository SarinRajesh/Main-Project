from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users

class UsersAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email','address','home_town','district','state','pincode', 'username', 'user_type')
    search_fields = ('name', 'email', 'username')

admin.site.register(Users, UsersAdmin)



# Unregister the default User and Group models
#admin.site.unregister(User)


