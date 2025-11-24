from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from core.serializers.usuario_serializers import UsuarioCreateSerializer, LoginSerializer, UsuarioSerializer
from rest_framework.permissions import IsAuthenticated
from core.utils.jwt_auth import JWTAuthentication, create_jwt_token
from core.models.usuario_models import Usuario

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
