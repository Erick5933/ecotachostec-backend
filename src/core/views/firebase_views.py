# core/views/firebase_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from core.serializers.firebase_serializers import (
    GoogleLoginSerializer, 
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from core.serializers.usuario_serializers import UsuarioSerializer
from core.utils.jwt_auth import create_jwt_token
from core.firebase_service import FirebaseService
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class GoogleLoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            created = serializer.validated_data.get('created', False)
            
            # Crear token JWT para Django
            token = create_jwt_token(user)
            
            response_data = {
                'user': UsuarioSerializer(user).data,
                'token': token,
                'created': created,
                'message': 'Usuario registrado exitosamente' if created else 'Login exitoso'
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                # 1. Usar Firebase para el enlace de recuperación
                reset_link = FirebaseService.send_password_reset_email(email)
                
                # 2. También enviar email personalizado desde Django
                subject = 'Recuperación de contraseña - Ecotachostec'
                html_message = render_to_string('emails/password_reset.html', {
                    'reset_link': reset_link,
                    'user_email': email,
                })
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                return Response({
                    'message': 'Se ha enviado un correo con instrucciones para recuperar tu contraseña'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendWelcomeEmailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        try:
            subject = '¡Bienvenido a Ecotachostec!'
            html_message = render_to_string('emails/welcome.html', {
                'user_name': user.nombre,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({
                'message': 'Correo de bienvenida enviado exitosamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error al enviar correo: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)