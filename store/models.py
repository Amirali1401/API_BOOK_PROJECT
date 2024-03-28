from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from uuid import uuid4


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=250)
    top_book = models.ForeignKey('Book' , on_delete = models.CASCADE ,null = True , blank = True  , related_name="+")

    def __str__(self):
        return self.title



class Discount(models.Model):
    discount = models.FloatField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return f'{str(self.discount)} | {self.description}'




class Book(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    category = models.ForeignKey('Category' , on_delete = models.CASCADE , related_name = 'books')
    slug  = models.SlugField()
    inventory = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=6 , decimal_places=2)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    # discount = models.ManyToManyField(Discount)

    def __str__(self):
        return self.name



class CommentManger(models.Manager):
    def get_approved(self):
        return self.get_queryset().filter(status=Comment.COMMENT_STATUS_APPROVED)


class ApprovedCommentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Comment.COMMENT_STATUS_APPROVED)


class Comment(models.Model):
    COMMENT_STATUS_WAITING = 'w'
    COMMENT_STATUS_APPROVED = 'a'
    COMMENT_STATUS_NOT_APPROVED = 'na'
    COMMENT_STATUS = [
        (COMMENT_STATUS_WAITING, 'Waiting'),
        (COMMENT_STATUS_APPROVED, 'Approved'),
        (COMMENT_STATUS_NOT_APPROVED, 'Not Approved'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=255)
    body = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=COMMENT_STATUS, default=COMMENT_STATUS_WAITING)

    objects = CommentManger()
    approved = ApprovedCommentManager()



class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL , on_delete = models.CASCADE)
    phone_number = models.CharField(max_length=50)
    birth_date = models.DateField(null = True , blank = True)

    def __str__(self):
        return f'{self.user} : {self.phone_number}'

    @property
    def full_name(self):
        return f'{self.user.first_name}  {self.user.last_name}'

    @property
    def first_name(self):
        return self.user.first_name


    @property
    def last_name(self):
        return self.user.last_name

    class Meta:
        permissions = [
            ('send_private_email' , 'Can send Private email by user that you build' )
        ]



class UnpaidOrderManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.ORDER_STATUS_UNPAID)


class Order(models.Model):
    ORDER_STATUS_PAID = 'p'
    ORDER_STATUS_UNPAID = 'u'
    ORDER_STATUS_CANCELED = 'c'
    ORDER_STATUS = [
        (ORDER_STATUS_PAID, 'Paid'),
        (ORDER_STATUS_UNPAID, 'Unpaid'),
        (ORDER_STATUS_CANCELED, 'Canceled'),
    ]
    customer = models.ForeignKey(Customer , on_delete=models.CASCADE , related_name='customer_orders')
    # datetime_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1 , choices=ORDER_STATUS , default=ORDER_STATUS_UNPAID)

    objects = models.Manager()
    unpaid_order = UnpaidOrderManger()

    def __str__(self):
        return f'Order id={self.id}'




class OrderItem(models.Model):
    order = models.ForeignKey(Order , on_delete=models.CASCADE , related_name ='items')
    book = models.ForeignKey(Book , on_delete = models.CASCADE , related_name ='order_items')
    quantity = models.SmallIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=6 ,  decimal_places=2)

    class Meta:
        unique_together = [['order', 'book']]




class Cart(models.Model):
    id = models.UUIDField(primary_key=True , default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)




class CartItem(models.Model):
    cart = models.ForeignKey(Cart , on_delete = models.CASCADE , related_name = 'items')
    book = models.ForeignKey(Book , on_delete = models.CASCADE , related_name = 'book_items')
    quantity = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = [['cart' ,'book']]
