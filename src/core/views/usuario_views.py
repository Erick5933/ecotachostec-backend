from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
# Modelos y Serializers
from core.models.usuario_models import Usuario
from core.serializers.usuario_serializers import (
    UsuarioCreateSerializer, 
    LoginSerializer, 
    UsuarioSerializer,
    PasswordResetSerializer, 
    SetNewPasswordSerializer
)

# Utils y Auth
from core.utils.jwt_auth import JWTAuthentication, create_jwt_token

# Firebase
from firebase_admin import auth
from core.utils.firebase_app import firebase_admin

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
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token = create_jwt_token(user)
            return Response({"user": UsuarioSerializer(user).data, "token": token})
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
            decoded_token = auth.verify_id_token(id_token)
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
            print(f"ERROR CRÍTICO FIREBASE: {str(e)}") 
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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

    # 🔥 DESACTIVAMOS autenticación SOLO para pruebas
    authentication_classes = []
    permission_classes = []

    def list(self, request):
        return super().list(request)