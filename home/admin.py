from django.contrib import admin
from .models import Users, UserType, Feedback, Consultation, Product, Design, Amount,Cart

class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'address', 'home_town', 'district', 'state', 'pincode', 'username', 'photo', 'user_type_id')
    search_fields = ('name', 'email', 'username')

class UserTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_type')
    search_fields = ('user_type',)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'feedback')
    search_fields = ('feedback',)

class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'designer_id', 'design_id', 'date_time', 'consultation_status', 'feedback', 'proposal')
    search_fields = ('customer_id', 'designer_id', 'consultation_status')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'amount', 'category', 'image')
    search_fields = ('name', 'category')

class DesignAdmin(admin.ModelAdmin):
    list_display = ('id', 'designer_id', 'name', 'description', 'amount', 'image')
    search_fields = ('name', 'designer_id')

class AmountAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount')
    search_fields = ('amount',)


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'product_id', 'quantity', 'amount', 'status')
   
    search_fields = ('user_id__username', 'user_id__email', 'product_id__name')


# ... existing code ...

admin.site.register(Cart, CartAdmin)
admin.site.register(Users, UsersAdmin)
admin.site.register(UserType, UserTypesAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Consultation, ConsultationAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Design, DesignAdmin)
admin.site.register(Amount, AmountAdmin)
