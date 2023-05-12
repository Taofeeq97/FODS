from rest_framework.urls import path
from . import views


urlpatterns =[
    path('food-list/', views.FoodListAPIVIew.as_view(), name='food'),
    path('food_list/search', views.FoodSearchAPIView.as_view(), name='food-search'),
    path('food-list/<int:pk>/', views.DetailAPIView.as_view(), name='food-detail'),
    path('food-list/tags/', views.TagListAPIview.as_view(), name='tag'),
    path('food-list/tags/<int:pk>/', views.TagDetailUpdateDeleteAPIView.as_view(), name='tag-detail'),
    path('food-list/optional_items', views.OptionalItemListAPIView.as_view(), name='optional-items'),
    path('food-list/optional_items/<int:pk>/', views.OptionalItemDetailUpdateDeleteAPIView.as_view(), name='optionalitem-detail'),
    path('food-list/foods', views.FoodListCreateUpdateDeleteAPIView.as_view(), name='food'),
    path('cart/', views.FoodCartAPIView.as_view(), name='foodcart-detail'),
    path('cart/<int:ordered_food_id>/delete', views.RemoveFoodCartItemAPIView.as_view(), name='remove-foodcart-item'),
    path('cart/<int:food_cart_id>/place_order', views.PlaceFoodOrderAPIView.as_view(), name='place-order'),
    path('user_dashboard/', views.UserDashboardAPIView.as_view(), name='users-dashboard'),
    path('<int:pk>/user_accept_delivery/', views.UserAcceptDeliveryAPIView.as_view(), name='user-accept-delivery'),
    path('<int:pk>/admin_accept_order/', views.AdminAcceptOrderAPIView.as_view(), name='admin-accept-order'),
    path('ongoing_order/', views.OngoingOrderListAPIView.as_view(), name='ongoing-order'),
    path('ongoing_order/<int:pk>/', views.OngoingOrderDetailAPIView.as_view(), name='ongoingorder-detail'),
    path('ongoing_order/<int:pk>/cancel/', views.CancelOngoingOrderAPIView.as_view(), name='onging-order-cancel'),
    path('accounts/customer_register/', views.CustomerRegistrationAPIView.as_view(), name='register'),
    path('accounts/delivery_person_register',views.DeliveryPersonCreateAccountAPIView.as_view(), name='delivery_person_register'),
    path('accounts/customer_login', views.CustomerLoginAPIView.as_view(), name='customer-login'),
    path('accounts/customer_update_details', views.CustomerDetailsUpdateAPIView.as_view(), name='customer-details-update')
]