from django.contrib import admin
from django.db.models import Count

from .models import Book , Category , Comment , Customer , Cart , CartItem

from . import models

# Register your models here.

admin.site.register(Book)
admin.site.register(Category)
admin.site.register(Comment)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name' ,'last_name' , 'email']
    list_per_page = 10
    ordering = ['user__last_name' , 'user__first_name']
    search_fields = ['user__first_name__istartswith' , 'user__last_name__istartswith']

    def first_name(self , customer):
        return customer.user.first_name

    def last_name(self , customer):
        return customer.user.last_name


    def email(self , customer):
        return customer.user.email





class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    fields = ['book', 'quantity', 'unit_price']
    extra = 0
    min_num = 1


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'num_of_items']
    list_editable = ['status']
    list_per_page = 10
    # ordering = ['-datetime_created']
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return super() \
                .get_queryset(request) \
                .prefetch_related('items') \
                .annotate(
                    items_count=Count('items')
                )

    @admin.display(ordering='items_count', description='# items')
    def num_of_items(self, order):
        return order.items_count



class CartItemAdmin(admin.TabularInline):
    model = models.CartItem
    fields = ['id' , 'book' , 'quantity']
    extra = 0
    min_num = 1



@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id' , 'created_at']
    inlines = [CartItemAdmin,]