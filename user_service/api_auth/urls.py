from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api_auth.views import (
    LogOutView,
    MyTokenObtainPairView,
    UserCreateView,
    UserExistenceCheckView,
)
from custom_simplejwt.views import CustomTokenRefreshView, CustomTokenVerifyView

router = DefaultRouter()
router.register(r"crud-user", UserCreateView, basename="crud-user")


urlpatterns = [
    # get the access token
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    # provide user details with refresh token to get new access token
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    # Logout endpoint
    path("logout/", LogOutView.as_view(), name="logout"),
    path(
        "user-exists/",
        UserExistenceCheckView.as_view(),
        name="user-exists",
    ),
    path(
        "get-api-user-id-for-user/",
        UserCreateView.as_view({"post": "get_api_user_id_for_user"}),
        name="get_api_user_id_for_user",
    ),
] + [path("", include(router.urls))]
