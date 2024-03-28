from rest_framework_nested import routers

from . import views


router = routers.DefaultRouter()
router.register('books' , views.BookViewSet  , basename='book_viewset')
router.register('categories' , views.CategoryViewSet , basename = 'category_viewset')
router.register('cart' , views.CartViewSet , basename = 'cart')
router.register('customer' , views.CustomerViewSet , basename = 'customer')
router.register('order' , views.OrderViewSet , basename = 'order')

book_router = routers.NestedSimpleRouter(router , 'books' , lookup = 'book' )
book_router.register('comments' , views.CommentViewSet , basename = 'book_comments')

cart_router = routers.NestedSimpleRouter(router , 'cart' , lookup='cart')
cart_router.register('items' , views.CartViewSet , basename='cart_items')

urlpatterns = router.urls + book_router.urls + cart_router.urls