from rest_framework import serializers
from core.models.usuario_models import Usuario
from django.contrib.auth import authenticate

class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Usuario
        fields = ("id", "nombre", "email", "password", "rol", "telefono", "provincia", "canton")

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
        email = data.get("email")
        password = data.get("password")
        user = authenticate(username=email, password=password)
        
        if not user:
            raise serializers.ValidationError("Credenciales inválidas")

        if not user.activo:
            raise serializers.ValidationError("Usuario inactivo")

        data["user"] = user
        return data
