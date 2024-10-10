
from django.contrib import admin
from .models import Users, UserType, Feedback, Consultation, Product, Design, Amount, Cart, Order, Payment_Type, ConsultationDate, ChatMessage,MoodBoard, MoodBoardItem
# ... (keep existing admin classes) ...
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'address', 'home_town', 'district', 'state', 'pincode', 'username', 'status', 'user_type_id', 'deactivation_reason')
    search_fields = ('name', 'email', 'username')

class UserTypesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_type')
    search_fields = ('user_type',)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'feedback')
    search_fields = ('feedback',)

class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'designer_id', 'design_id', 'date_time', 'consultation_status', 'room_length', 'room_width', 'room_height','design_preferences','feedback', 'proposal','payment_type','payment_status','amount')
    search_fields = ('customer_id__username', 'designer_id__username', 'consultation_status')
  

    fieldsets = (
        ('Basic Information', {
            'fields': ('customer_id', 'designer_id', 'design_id', 'date_time', 'consultation_status', 'proposal')
        }),
        ('Room Details', {
            'fields': ('room_type', 'room_length', 'room_width', 'room_height')
        }),
        ('Additional Information', {
            'fields': ('feedback', 'design_preferences')
        }),
    )
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'amount', 'category', 'image','stock','color')
    search_fields = ('name', 'category')

class DesignAdmin(admin.ModelAdmin):
    list_display = ('id', 'designer_id', 'name', 'description', 'amount', 'image','category')
    search_fields = ('name', 'designer_id')

class AmountAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount')
    search_fields = ('amount',)


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'product_id', 'quantity', 'amount', 'status')
   
    search_fields = ('user_id__username', 'user_id__email', 'product_id__name')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'amount', 'order_date', 'order_status', 'payment_type', 'payment_status','delivery_date')
    search_fields = ('user__username', 'user__email', 'product__name', 'order_status', 'payment_status')
    list_filter = ('order_status', 'payment_status', 'payment_type')

class Payment_TypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_type')
    search_fields = ('payment_type',)
# ... existing code ...

class ConsultationDateAdmin(admin.ModelAdmin):
    list_display = ('designer', 'date_time', 'is_booked')
    list_filter = ('is_booked', 'date_time')
    search_fields = ('designer__username', 'date_time')
    date_hierarchy = 'date_time'

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'design', 'content', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp', 'design')
    search_fields = ('sender__username', 'receiver__username', 'content', 'design__name')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)

    fieldsets = (
        ('Message Details', {
            'fields': ('sender', 'receiver', 'design', 'content', 'is_read')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )

from django.contrib import admin
from .models import Users, UserType, Feedback, Consultation, Product, Design, Amount, Cart, Order, Payment_Type, ConsultationDate, ChatMessage, Review

# ... (keep existing admin classes) ...

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'content_preview','rating', 'created_at')
    list_filter = ('product', 'created_at')
    search_fields = ('product__name', 'user__username', 'content')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
class MoodBoardItemInline(admin.TabularInline):
    model = MoodBoardItem
    extra = 1

class MoodBoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name','image', 'description_preview', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    inlines = [MoodBoardItemInline]
    
    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description Preview'

class MoodBoardItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'mood_board', 'caption', 'position_x', 'position_y')
    list_filter = ('mood_board',)
    search_fields = ('mood_board__name', 'caption')

# ... (keep existing admin registrations) ...

admin.site.register(MoodBoard, MoodBoardAdmin)
admin.site.register(MoodBoardItem, MoodBoardItemAdmin)

admin.site.register(Review, ReviewAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)

admin.site.register(ConsultationDate, ConsultationDateAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Users, UsersAdmin)
admin.site.register(UserType, UserTypesAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Consultation, ConsultationAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Design, DesignAdmin)
admin.site.register(Amount, AmountAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment_Type, Payment_TypeAdmin)