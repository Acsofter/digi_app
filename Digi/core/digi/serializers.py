
from rest_framework import serializers
from .models import User
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    # token = serializers.CharField(max_length=255, read_only=True)
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    roles = serializers.SerializerMethodField(read_only=True)

    def get_roles(self, obj):
        return obj.get_roles()
    

    class Meta:
        model = User
        fields = ['id', 'username', 'is_active', 'company', 'password', 'roles', ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        return super().validate(attrs)

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.get('password', None)
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'token']

    def create(self, validated_data):
        print("validate data from register: " )
        return User.objects.create_user(**validated_data)

class RegistrationSuperUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'token']

    def create(self, validated_data):
        return User.objects.create_superuser(**validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username:
            raise serializers.ValidationError('Especificar el usuario')
        if not password:
            raise serializers.ValidationError('Especificar la contraseña')

        user = get_object_or_404(User, username=username)
        
        if not user.check_password(password):
            raise serializers.ValidationError('Credenciales incorrectas')

        if not user.is_active:
            raise serializers.ValidationError('Este usuario se encuentra suspendido')

        return {
            'username': user.username,
            'token': user.token,
            'email': user.email,
            'company': user.company,
            'id': user.id
        }