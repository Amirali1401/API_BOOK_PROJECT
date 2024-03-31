from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Prefetch

from rest_framework.viewsets import ModelViewSet , GenericViewSet
from rest_framework.generics import CreateAPIView , ListCreateAPIView , ListAPIView , RetrieveAPIView , GenericAPIView
from rest_framework.mixins import RetrieveModelMixin , CreateModelMixin , DestroyModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser , AllowAny


from .models import Book , Category ,Comment , Cart , CartItem , Customer , Order , OrderItem
from .serializers import BookSerializer , CategorySerializer , CommentSerializer ,CartSerializer , CartItemSerializer , AddCartItemSerializer , UpdateItemCartSerializer , CustomerSerializer , OrderSerializer , OrderForAdminSerializer , OrderCreateSerializer , OrderUpdateSerializer
from .permissions import SendPrivateEmailToCustomerPermission

# Create your views here.



class BookViewSet(ModelViewSet):
    queryset = Book.objects.select_related('category').all()
    serializer_class = BookSerializer

    def get_serializer_context(self):
        return {'request':self.request}




class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.prefetch_related('books').all()
    serializer_class = CategorySerializer

    def get_serializer_context(self):
        return {'request':self.request}



class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        book_pk = self.kwargs['book__pk']
        return Comment.objects.filter(book__id = book_pk).all()


    def get_serializer_context(self):
        return {'book_pk':self.kwargs['book__pk']}



class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        cart_pk = self.kwargs['cart__pk']
        return CartItem.objects.select_related('book').filter(cart__id = cart_pk).all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer

        elif self.request.method == 'PATCH':
            return UpdateItemCartSerializer

        return CartItemSerializer



    def get_serializer_context(self):
        return {'cart_pk':self.kwargs['cart__pk']}




class CartViewSet(RetrieveModelMixin, CreateModelMixin , DestroyModelMixin, GenericViewSet ):
    queryset = Cart.objects.prefetch_related('items').all()
    serializer_class = CartSerializer





class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser , ]

    @action(detail=False, methods=['GET' , 'PUT'] , permission_classes=[IsAuthenticated,])
    def me(self , request):
        user_id = request.user.id
        customer = Customer.objects.get(user__id = user_id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(data = serializer.data)

        elif request.method =='PUT':
            serializer = CustomerSerializer(customer , data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data = serializer.data)


    @action(detail=True , permission_classes=[SendPrivateEmailToCustomerPermission,])
    def send_private_email(self , request , pk):
        return Response(f'sending private email : {pk=}')





class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated,]
    def get_queryset(self):
        queryset = Order.objects.prefetch_related(
            Prefetch(
                'items',
                queryset = OrderItem.objects.select_related('book'),
            )
        ).select_related('customer__user').all()

        user = self.request.user
        if user.is_staff:
            return queryset

        return queryset.filter(customer__user__id = self.request.user.id)


    def get_serializer_class(self):

        if self.request.method == 'POST':
            return OrderCreateSerializer

        if self.request.method =='PATCH':
            return OrderUpdateSerializer

        if self.request.user.is_staff :
            return OrderForAdminSerializer

        return OrderSerializer


    def get_serializer_context(self):
        return {'user_id':self.request.user.id}


    def create(self, request, *args, **kwargs):
        create_order_serializer = OrderCreateSerializer(data = request.data , context={'user_id':self.request.user.id})
        create_order_serializer.is_valid(raise_exception=True)
        created_order = create_order_serializer.save()

        serializer = OrderSerializer(created_order)
        return Response(data = serializer.data)


