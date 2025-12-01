from rest_framework import serializers
from core.models.usuario_models import Usuario
from django.contrib.auth import authenticate
from django.utils import timezone

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

