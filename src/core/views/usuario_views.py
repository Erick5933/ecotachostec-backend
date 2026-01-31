from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
# Modelos y Serializers
from core.models.usuario_models import Usuario
from core.serializers.usuario_serializers import (
    UsuarioCreateSerializer, 
    LoginSerializer, 
    UsuarioSerializer,
    UsuarioUpdateSerializer,
    PasswordResetSerializer, 
    SetNewPasswordSerializer
)

# Utils y Auth
from core.utils.jwt_auth import JWTAuthentication, create_jwt_token
from core.permissions import IsAdmin

# Firebase - Inicializar primero
from core.utils import firebase_app
from firebase_admin import auth

# Para el correo
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMessage  # Cambiado a EmailMessage
from django.conf import settings


# -------------------- REGISTRO Y LOGIN NORMAL --------------------

class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UsuarioCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = create_jwt_token(user)
            return Response({"user": UsuarioSerializer(user).data, "token": token})
        return Response(serializer.errors, status=400)


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print(f"📋 Datos recibidos: {request.data}")
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token = create_jwt_token(user)
            print(f"✅ Login exitoso para: {user.email}")
            return Response({"user": UsuarioSerializer(user).data, "token": token})
        print(f"❌ Errores de validación: {serializer.errors}")
        return Response(serializer.errors, status=400)


# -------------------- LOGIN CON GOOGLE --------------------

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print("--------------- DEBUG INICIO ---------------")
        print(f"BODY RECIBIDO: {request.data}")
        
        id_token = request.data.get('token')
        
        if not id_token:
            print("ERROR: El campo 'token' es None o vacío.")
            return Response({'error': 'No se proporcionó token'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            print("Verificando token con Firebase Admin...")
            # clock_skew_seconds=10 tolera desajustes de reloj de hasta 10 segundos
            decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=10)
            print(f"Token verificado. Email: {decoded_token.get('email')}")
            
            email = decoded_token.get('email')
            name = decoded_token.get('name', '')

            if not email:
                return Response({'error': 'Token inválido (sin email)'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                user = Usuario.objects.create_user(
                    email=email,
                    nombre=name,
                    password=None,
                    rol='user'
                )

            token = create_jwt_token(user)
            return Response({
                "user": UsuarioSerializer(user).data,
                "token": token
            })

        except Exception as e:
            error_msg = str(e)
            print(f"ERROR CRÍTICO FIREBASE: {error_msg}") 
            
            # Si es error de configuración de Firebase, proporcionar instrucciones claras
            if "project ID" in error_msg.lower():
                return Response({
                    'error': 'Firebase no configurado. Necesitas:',
                    'instrucciones': [
                        '1. Crear archivo firebase_credentials.json en src/',
                        '2. O configurar variables de entorno: GOOGLE_CLOUD_PROJECT, FIREBASE_PRIVATE_KEY, etc.',
                        '3. Consulta .env.example para más detalles'
                    ]
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)


# -------------------- RECUPERACIÓN DE CONTRASEÑA --------------------

class RequestPasswordResetEmail(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            email = request.data['email']
            
            if Usuario.objects.filter(email=email).exists():
                user = Usuario.objects.get(email=email)
                
                # Generar tokens
                uidb64 = urlsafe_base64_encode(force_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                
                # Crear link
                current_site = settings.FRONTEND_URL 
                absurl = f"{current_site}/reset-password/{uidb64}/{token}" 
                
                # Preparamos los datos
                # Ahora podemos usar "Contraseña" ya que usamos UTF-8
                email_subject = 'Restablecer Contraseña - EcoTachos'
                email_body = f'Hola {user.nombre},\n\nUsa el siguiente enlace para restablecer tu contraseña:\n{absurl}'
                
                try:
                    # --- CONFIGURACIÓN EXPLÍCITA DE UTF-8 ---
                    email_msg = EmailMessage(
                        subject=email_subject,
                        body=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[user.email]
                    )
                    
                    # Forzamos la codificación UTF-8 para soportar caracteres especiales
                    email_msg.encoding = 'utf-8' 
                    
                    email_msg.send(fail_silently=False)
                    # -----------------------------------------------------------

                    return Response({'success': 'Correo enviado'}, status=status.HTTP_200_OK)
                except Exception as e:
                    print(f"❌ ERROR SMTP DETALLADO: {repr(e)}") # Imprime el error técnico exacto
                    return Response({'error': f'Error enviando correo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Por seguridad, respondemos OK aunque el email no exista
            return Response({'success': 'Si el correo existe, se ha enviado un enlace'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def patch(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'success': True, 'message': 'Contraseña restablecida correctamente'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------- PERFIL Y VIEWSET --------------------

class ProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)

    def put(self, request):
        serializer = UsuarioSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    # ✅ Solo admins autenticados pueden acceder
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def perform_destroy(self, instance):
        """Eliminado lógico: marcar usuario como inactivo en lugar de borrar"""
        instance.activo = False
        instance.save()

    def get_serializer_class(self):
        """Usa UsuarioCreateSerializer para crear y actualizar, UsuarioSerializer para leer"""
        if self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            # Para PUT/PATCH, usa un serializer que maneje contraseña opcional
            return UsuarioUpdateSerializer
        return UsuarioSerializer

    def list(self, request):
        return super().list(request)

    @action(detail=True, methods=["post", "patch"], url_path="reactivar")
    def reactivar(self, request, pk=None):
        """Reactivar usuario (soft-undelete)"""
        user = self.get_object()
        user.activo = True
        user.save()
        serializer = self.get_serializer(user)
        return Response(serializer.data)