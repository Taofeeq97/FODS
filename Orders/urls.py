from django.urls import path
from . import views

urlpatterns = [
    path('', views.FoodListView.as_view(), name='foods'),
    path('<int:pk>/', views.detail_view, name='food_detail'),
    path('cart/',views.CartView.as_view(), name='cart'),
    path('cart/remove/<int:food_id>/<int:cart_id>/', views.RemoveFoodCartItemView.as_view(), name='remove_food_cart_item'),
    path('pickup/<int:cart_id>/', views.PickupView.as_view(), name='pickup'),
    path('delivery/<int:cart_id>/', views.DeliveryView.as_view(), name='delivery'),
    path('user_dashboard/', views.UserDashboardView.as_view(), name='user-dashboard'),
    path('<int:pk>/order_confirm', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('create-food',views.FoodCreateView.as_view(), name='create-food'),
    path('admin_list/', views.FoodAdminListView.as_view(), name='admin-list'),
    path('admin_order_management', views.AdminOrderManagementView.as_view(), name='admin_order_management'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('delivery/create/', views.DeliveryEntityCreateView.as_view(), name='create_delivery_entity'),
    path('delivery/<int:pk>/update/', views.DeliveryEntityUpdateView.as_view(), name='delivery-update'),
    path('delivery/<int:pk>/delete/', views.DeliveryEntityDeleteView.as_view(), name='delivery-delete'),
    path('ongoing-orders/', views.OngoingOrderListView.as_view(), name='ongoing_orders'),
    path('ongoing-order/<int:pk>/', views.OngoingOrderDetailView.as_view(), name='ongoing_order_detail'),
    path('ongoing-order/<int:pk>/cancel/', views.CancelOrderView.as_view(), name='cancel_order'),
    path('create-tag/', views.CreateFoodTagView.as_view(), name='create-tag'),
    path('create_optional_item/', views.CreateFoodOptionalItemView.as_view(), name='create-optionalitem'),
    # path('map/', views.save_location, name='save_location'),
    path('delivery/<int:cart_id>/save-location/', views.save_location, name='save_location'),
]


