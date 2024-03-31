from rest_framework import serializers


from .models import Book , Category , Comment , Cart , CartItem , Customer , Order , OrderItem

from django.utils.text import slugify
from django.conf import settings
from django.db import transaction


from decimal import Decimal


class BookSerializer(serializers.ModelSerializer):
    unit_price_after_tax = serializers.SerializerMethodField()
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
    class Meta:
        model = Book
        fields = ['id', 'name' , 'description' , 'unit_price_after_tax', 'inventory' ,'image','category' , 'price' ]



    def validate(self, data):
        if(len(data['name'])<6):
            raise serializers.ValidationError('Your name is less 6 charecters')
        return data

    def get_unit_price_after_tax(self , book):
          return round(book.unit_price * Decimal(1.09) , 2)


    def create(self, validated_data):
        book = Book(**validated_data)
        book.slug = slugify(book.name)
        book.save()
        return book




class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title' ]

    def create(self, validated_data):
        category = Category(**validated_data)
        category.save()
        return category



class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id' ,'name' , 'body' ]


    def create(self, validated_data):
        book_pk = self.context['book_pk']
        return Comment.objects.create(**validated_data , book_id = book_pk )



class CartBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields =['id' , 'name' , 'unit_price' , 'unit_price_after_tax']



class UpdateItemCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = [ 'quantity' , ]



class AddCartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields =['id' , 'quantity' , 'book']
        read_only_fields = ['id',]


    def create(self, validated_data):
        cart_pk = self.context['cart_pk']
        book = validated_data.get('book')
        quantity = validated_data.get('quantity')
        try:
            cart_item = CartItem.objects.get(cart__id = cart_pk , book_id = book.id)
            cart_item.quantity+=quantity
            cart_item.save()

        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id = cart_pk , **validated_data)


        return cart_item


class CartItemSerializer(serializers.ModelSerializer):

    book = CartBookSerializer()
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields =['id',  'book' ,'quantity' , 'item_total']


    def get_item_total(self , cart_item):
        return cart_item.quantity * cart_item.book.unit_price






class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True , read_only=True)
    cart_total = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id' , 'created_at' , 'items' , 'cart_total']
        read_only_fields = ['id',]


    def get_cart_total(self , cart_id):
        return [item.quanity * item.book.unit_price for item in cart_id.items.all]



class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['id' , 'user' , 'birth_date']
        read_only_fields = ['users',]



class OrderCustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=60 , source='user.first_name')
    last_name = serializers.CharField(max_length=60 , source='user.last_name')
    email = serializers.CharField(max_length=60 , source = 'user.email')

    class Meta:
        model = Customer
        fields = ['id' , 'first_name' , 'last_name' , 'email']



class OrderItemBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = [ 'id' , 'name' ,'slug']



class OrderItemSerializer(serializers.ModelSerializer):

    book = OrderItemBookSerializer()

    class Meta:
        model = OrderItem
        fields = ['id' , 'order' , 'book' , 'quantity' , 'unit_price']



class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id' , 'status' , 'items']




class OrderForAdminSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True)
    customer = OrderCustomerSerializer()
    class Meta:
        model = Order
        fields = ['id' , 'customer', 'status' , 'items']



class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status',]



class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self , cart_id):

        if not Cart.objects.filter(id = cart_id).exists():
            raise serializers.ValidationError("There's no cart!!?")


        if  CartItem.objects.filter(cart_id = cart_id).count()==0 :
            raise  serializers.ValidationError('You cart is empty!!!')

        return cart_id



    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            customer = Customer.objects.get(user_id = user_id)
            order = Order()
            order.customer = customer
            order.save()

            cart_items = CartItem.objects.select_related('book').filter(cart_id = cart_id)

            order_items = []
            for cart_item in cart_items:
                order_item = OrderItem()
                order_item.order = order
                order_item.book_id = cart_item.book_id
                order_item.unit_price = cart_item.book.unit_price
                order_item.quantity = cart_item.quantity

                order_items.append(order_item)


            OrderItem.objects.bulk_create(order_items)

            Cart.objects.get(id = cart_id).delete()

            return order






