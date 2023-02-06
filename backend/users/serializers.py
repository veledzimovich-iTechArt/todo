from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import password_validation

from rest_framework import serializers

from users.models import User


class LoginSerializer(serializers.Serializer):
    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs: dict) -> dict:
        # Take username and password from request
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(
                request=self.context.get('request'),
                username=username, password=password
            )
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'phone', 'email'
        ]


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(trim_whitespace=False, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']

    def validate_password(self, value: str) -> str:
        password_validation.validate_password(value, self.instance)
        return value

    def create(self, validated_data: dict) -> User:
        user = super().create(validated_data)

        user.set_password(validated_data['password'])
        user.save(update_fields=('password',))
        request = self.context.get('request')
        user = authenticate(
            request=request,
            username=validated_data['username'],
            password=validated_data['password']
        )
        login(request, user)
        return user
