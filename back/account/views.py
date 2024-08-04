from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from account.models import User, InviteToken
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from smtplib import SMTP


from rest_framework.permissions import IsAdminUser



class SendInviteLinkView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'User already registered'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check if an invite token already exists for the given email
            invite_token = InviteToken.objects.filter(email=email).first()
            if invite_token:
                # Optionally delete the existing token
                invite_token.delete()
            
            # Create a new invite token
            token = get_random_string(64)
            InviteToken.objects.create(email=email, token=token)
            link = f"{settings.FRONTEND_URL}/register?token={token}"
            
            send_mail(
                'Your Registration Link',
                f'Click the link to register: {link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return Response({'msg': 'Invite link sent'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]  # Only admin can list users

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]  


# Generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterUserView(APIView):
    def post(self, request):
        token = request.data.get('token')
        invite = InviteToken.objects.filter(token=token, is_used=False).first()
        
        if not invite:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            invite.is_used = True
            invite.save()
            return Response({'msg': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)
