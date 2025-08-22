from django.urls import path
from .views import UserListCreateAPIView, UserRetrieveUpdateAPIView, MyLoginAPIView, MyRegisterAPIView

urlpatterns = [
    path("users/", UserListCreateAPIView.as_view(), name="users-list-create"),
    path("users/<int:pk>/", UserRetrieveUpdateAPIView.as_view(), name="users-detail"),

    # Auth JWT
    path("auth/login/", MyLoginAPIView.as_view(), name="login"),
    path("auth/register/", MyRegisterAPIView.as_view(), name="register"),
]
