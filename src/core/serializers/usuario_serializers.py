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
    canton_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Usuario
        fields = ("id", "nombre", "email", "password", "rol", "telefono", "canton", "canton_id")

    def create(self, validated_data):
        password = validated_data.pop("password")
        # Mapear canton_id si viene desde el cliente
        canton_id = validated_data.pop("canton_id", None)
        if canton_id is not None:
            validated_data["canton_id"] = canton_id

        user = Usuario.objects.create_user(
            password=password,
            **validated_data
        )
        return user

class UsuarioSerializer(serializers.ModelSerializer):
    canton_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    # Mapear is_active del front al campo 'activo' del modelo
    is_active = serializers.BooleanField(required=False, source='activo')
    
    class Meta:
        model = Usuario
        exclude = ("password",)
        # Ocultar 'activo' en la salida para evitar duplicidad; aceptar en entrada si se envía
        extra_kwargs = {
            'activo': {'write_only': True}
        }

    def update(self, instance, validated_data):
        # Extraer canton_id si está presente
        canton_id = validated_data.pop('canton_id', None)
        
        if canton_id is not None:
            try:
                from core.models.ubicacion_models import Canton
                instance.canton_id = canton_id
            except Exception as e:
                raise serializers.ValidationError(f"Cantón no válido: {str(e)}")
        
        # Actualizar otros campos, incluyendo 'activo' si vino desde is_active (source)
        return super().update(instance, validated_data)


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar usuarios - encripta contraseña si se proporciona"""
    password = serializers.CharField(write_only=True, required=False, min_length=6, allow_blank=False)
    canton_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    # Campo del front para estado; mapea a 'activo'
    is_active = serializers.BooleanField(required=False, source='activo')
    
    class Meta:
        model = Usuario
        fields = ("id", "nombre", "email", "password", "rol", "telefono", "canton", "canton_id", "is_active", "created_at", "last_login")
        read_only_fields = ("id", "created_at", "last_login", "canton")
        extra_kwargs = {
            # Ocultar 'activo' para no duplicar con is_active
            'activo': {'write_only': True}
        }

    def update(self, instance, validated_data):
        # Extraer y encriptar contraseña si está presente
        password = validated_data.pop('password', None)
        
        # Extraer canton_id si está presente
        canton_id = validated_data.pop('canton_id', None)
        
        if password:
            instance.set_password(password)
        
        if canton_id is not None:
            try:
                from core.models.ubicacion_models import Canton
                instance.canton_id = canton_id
            except Exception as e:
                raise serializers.ValidationError(f"Cantón no válido: {str(e)}")
        
        # Actualizar otros campos (incluye 'activo' si vino desde is_active)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Usa 'email' ya que USERNAME_FIELD del modelo Usuario es "email"
        user = authenticate(username=data["email"], password=data["password"])

        if not user:
            raise serializers.ValidationError("Credenciales inválidas")

        user.ultimo_login = timezone.now()
        user.save()

        data["user"] = user
        return data

