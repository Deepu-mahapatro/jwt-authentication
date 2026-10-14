# Import Django's URL routing function.
from django.urls import path

# Import the registration view from views.py.
from .views import register_user, login_user, profile_user, logout_user

from rest_framework_simplejwt.views import TokenRefreshView

# Define the URLs available in the authentication app.
urlpatterns = [
    # Route registration requests to the register_user view.
    path("register/", register_user, name="register"),
    # Login endpoint.
    path("login/", login_user, name="login"),
    #profile endpoint 
    path("profile/", profile_user, name="profile"),
    #get new access token (refresh token)
    path(
    "token/refresh/",
    TokenRefreshView.as_view(),
    name="token_refresh",
    ),
    #logout endpoint
    path("logout/", logout_user, name="logout"),
]
