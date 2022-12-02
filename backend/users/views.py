import logging

from django.contrib.auth import login, logout
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.request import Request

from users.serilizers import (
    LoginSerializer, UserSerializer, UserRegisterSerializer
)
from users.models import User

logger_info = logging.getLogger('root')
logger_warning = logging.getLogger('main-warning')


class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request, *args, **kwargs) -> Response:
        logger_info.info(f'Login: {request.user}')

        serializer = LoginSerializer(
            data=self.request.data,
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(
            {
                'id': user.id,
                'username': user.username
            },
            status=status.HTTP_202_ACCEPTED
        )


class LogoutView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request: Request, *args, **kwargs) -> Response:
        if request.user.is_anonymous:
            logger_warning.warning(f'Logout: {request.user}')
        else:
            logger_info.info(f'Logout: {request.user}')
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = ()


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request: Request, *args, **kwargs) -> Response:
        return self.list(request, *args, **kwargs)


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request: Request, *args, **kwargs) -> Response:
        return self.retrieve(request, *args, **kwargs)
