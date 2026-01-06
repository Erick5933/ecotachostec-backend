from rest_framework import serializers
from core.models.usuario_models import Usuario
from django.contrib.auth import authenticate
from django.utils import timezone

    
# Agrega estos imports arriba
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, write_only=True)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            
            id = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("El enlace de reseteo es inválido o ha expirado", 401)
            
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise serializers.ValidationError("Token inválido", 401)
        
        
class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Usuario
        fields = ("id", "nombre", "email", "password", "rol", "telefono", "canton")

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Usuario.objects.create_user(
            password=password,
            **validated_data
        )
        return user

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        exclude = ("password",)



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["email"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Credenciales inválidas")

        user.ultimo_login = timezone.now()
        user.save()

        data["user"] = user
        return data

