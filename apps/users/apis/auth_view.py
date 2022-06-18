# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.serializers import RegisterUserSerializer, VerifyOTPRequestSerializer
from uno import settings


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class AuthView(viewsets.ViewSet):
    model = User
    permission_classes = [AllowAny]
    serializer_class = RegisterUserSerializer
    queryset = model.objects.all()

    @action(methods=['POST'], detail=False)
    def register(self, request):
        print(settings.AUTH_USER_MODEL)
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            otp = user.send_otp()
            return Response({
                "token": token,
                "otp": otp,
                "message": "Registration successfull"
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def verify(self, request):

        serializer = VerifyOTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            id=request.user.id
        ).first()

        print("this is user", user)

        otp = serializer.validated_data['otp'] if 'otp' in serializer.validated_data else None

        if not user:
            raise AuthenticationFailed('User does not exist.')

        is_verified = user.verify_otp_or_mpin(supplied_otp=otp,)
        print("this is verified", is_verified)
        if not is_verified:
            error_message = "please enter valid otp"
            return Response(
                {"message": error_message}
            )

        response = Response()
        refresh = RefreshToken.for_user(user)
        response.data = {
            "status": "success",
            "jwt": str(refresh.access_token)
        }
        return response






# @action(methods=["POST"], detail=False)
# def send_otp(self, request):
#     serializer = SendOTPRequestSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#
#     mobile = serializer.validated_data['mobile']
#     user = self.model.objects.filter(mobile=mobile).first()
#     send_on_email = request.query_params.get('send_on_email')
#
#     if user is None:
#         raise AuthenticationFailed('User does not exist.')
#
#     user.send_otp(send_on_email=send_on_email)
#
#     return Response(data={
#         'message': 'Otp Sent Successfully'
#     })
#
# @action(methods=["POST"], detail=False)
# def verify(self, request):
#     # validate request
#     serializer = VerifyOTPRequestSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#
#     mobile = serializer.validated_data['mobile']
#     otp = serializer.validated_data['otp'] if 'otp' in serializer.validated_data else None
#     mpin = serializer.validated_data['mpin'] if 'mpin' in serializer.validated_data else None
#
#     user = self.model.objects.filter(mobile=mobile).first()
#
#     if not user:
#         raise AuthenticationFailed('User does not exist.')
#
#     is_verified = user.verify_otp_or_mpin(supplied_otp=otp, supplied_mpin=mpin)
#     if not is_verified:
#         if otp is not None:
#             error_message = 'Invalid OTP'
#         else:
#             error_message = 'Invalid MPIN'
#         raise ValidationError(error_message)
#
#     response = Response()
#     refresh = RefreshToken.for_user(user)
#     response.data = {
#         "status": "success",
#         "jwt": str(refresh.access_token)
#     }
#     return response
#
# @action(methods=["POST"], detail=False)
# def create_user(self, request):
#     serializer = UserCreateSerializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#
#     user = self.model.objects.filter(mobile=serializer.validated_data.get('mobile')).first()
#
#     if user is not None and not user.is_mobile_verified:
#         serializer = UserCreateSerializer(data=request.data, instance=user)
#         serializer.is_valid(raise_exception=True)
#
#     user = serializer.save()
#
#     return Response({
#         'user_id': user.id
#     }, status=HTTPStatus.CREATED)
