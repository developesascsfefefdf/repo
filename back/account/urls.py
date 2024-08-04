from django.urls import path
from account.views import SendPasswordResetEmailView, UserChangePasswordView, UserLoginView, UserProfileView, UserPasswordResetView
from .views import UserListView, UserDetailView
from account.views import SendInviteLinkView, RegisterUserView




urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
     path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
        path('send-invite/', SendInviteLinkView.as_view(), name='send-invite'),



]