# core/utils/jwt_auth.py

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model

Usuario = get_user_model()

JWT_ALGORITHM = "HS256"
JWT_EXP_DAYS = getattr(settings, "JWT_EXP_DAYS", 7)


def create_jwt_token(user):
    """
    Genera un JWT con payload básico (user_id, email, exp).
    """
    exp = datetime.utcnow() + timedelta(days=JWT_EXP_DAYS)
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": exp,
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)

    # PyJWT < 2.0 devolvía bytes, por si acaso:
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token


def decode_jwt_token(token):
    """
    Decodifica y valida un JWT.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed("Token expirado")

    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed("Token inválido")


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Autenticación personalizada para DRF:
    Authorization: Bearer <token>
    """

    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()

        if not auth_header:
            return None

        if len(auth_header) != 2:
            raise exceptions.AuthenticationFailed("Authorization header inválido")

        prefix = auth_header[0].decode()
        token = auth_header[1].decode()

        if prefix != self.keyword:
            return None

        payload = decode_jwt_token(token)

        try:
            user = Usuario.objects.get(id=payload.get("user_id"))
        except Usuario.DoesNotExist:
            raise exceptions.AuthenticationFailed("Usuario no existe")

        if hasattr(user, "activo") and not user.activo:
            raise exceptions.AuthenticationFailed("Usuario inactivo")

        return (user, token)
