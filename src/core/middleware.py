"""
Middleware de seguridad para encabezados HTTP
"""
from django.conf import settings
from django.http import HttpResponseForbidden

class SecurityHeadersMiddleware:
    """Agrega encabezados de seguridad a todas las respuestas"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy
        # Política estricta por defecto (sin 'unsafe-inline')
        csp_strict = (
            "default-src 'self'; "
            "script-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com; "
            "style-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; "
            "font-src 'self' data: fonts.gstatic.com cdnjs.cloudflare.com; "
            "img-src 'self' data: https://cdn.jsdelivr.net https://roboflow.com https://serverless.roboflow.com; "
            "connect-src 'self' https://api.roboflow.com https://serverless.roboflow.com https://cdn.jsdelivr.net https://firebase.googleapis.com https://identitytoolkit.googleapis.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        ).replace("  ", " ")

        # Excepción solo para la página de OAuth de Swagger (requiere inline)
        csp_relaxed = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; "
            "font-src 'self' data: fonts.gstatic.com cdnjs.cloudflare.com; "
            "img-src 'self' data: https://cdn.jsdelivr.net https://roboflow.com https://serverless.roboflow.com; "
            "connect-src 'self' https://api.roboflow.com https://serverless.roboflow.com https://cdn.jsdelivr.net https://firebase.googleapis.com https://identitytoolkit.googleapis.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        ).replace("  ", " ")

        if request.path.endswith('/oauth2-redirect.html') or (
            request.path.startswith('/static/drf-yasg/swagger-ui-dist') and request.path.endswith('oauth2-redirect.html')
        ):
            response['Content-Security-Policy'] = csp_relaxed
        else:
            response['Content-Security-Policy'] = csp_strict
        
        # X-Content-Type-Options: previene MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options: previene clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection: protección contra XSS
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions-Policy (Feature-Policy)
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), '
            'gyroscope=(), magnetometer=(), microphone=(), '
            'payment=(), usb=()'
        )
        
        # 🔒 HSTS (HTTP Strict Transport Security)
        # Fuerza HTTPS en futuras conexiones (máximo 1 año)
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # 🔒 Cache-Control para APIs (no cachear datos sensibles)
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        # 🔒 OCULTAR INFORMACIÓN DEL SERVIDOR
        # Remover header Server si existe
        if 'Server' in response:
            del response['Server']
        
        # Establecer un header genérico
        response['Server'] = 'WebServer'
        
        return response


class StaticFilesSecurityMiddleware:
    """
    Middleware para asegurar que los archivos estáticos tengan headers de seguridad.
    Esto es especialmente importante para archivos que podrían ser servidos por 
    whitenoise o directamente por Django en desarrollo.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Aplicar headers de seguridad a archivos estáticos
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            # X-Content-Type-Options para prevenir MIME sniffing
            response['X-Content-Type-Options'] = 'nosniff'
            
            # X-Frame-Options para prevenir clickjacking
            response['X-Frame-Options'] = 'DENY'
            
            # Content Security Policy para archivos HTML estáticos
            if request.path.endswith('.html'):
                csp = (
                    "default-src 'self'; "
                    "script-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com; "
                    "style-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; "
                    "font-src 'self' fonts.gstatic.com cdnjs.cloudflare.com; "
                    "img-src 'self' data: https://cdn.jsdelivr.net https://roboflow.com https://serverless.roboflow.com; "
                    "connect-src 'self' https://api.roboflow.com https://serverless.roboflow.com https://cdn.jsdelivr.net https://firebase.googleapis.com https://identitytoolkit.googleapis.com; "
                    "frame-ancestors 'none'; "
                    "base-uri 'self'; "
                    "form-action 'self'"
                ).replace("  ", " ")
                response['Content-Security-Policy'] = csp
                # Garantizar X-Frame-Options para archivos HTML
                response['X-Frame-Options'] = 'DENY'
            
            # Cache para archivos estáticos (1 año)
            response['Cache-Control'] = 'public, max-age=31536000, immutable'
            
            # Ocultar servidor
            if 'Server' in response:
                del response['Server']
            response['Server'] = 'WebServer'
        
        return response


def whitenoise_add_headers(headers, path, url):
    """
    Función para WhiteNoise: agrega encabezados de seguridad a archivos estáticos.
    Se aplica especialmente a HTML (incluye CSP compatible con Swagger oauth redirect).
    """
    # Encabezados comunes
    headers['X-Content-Type-Options'] = 'nosniff'
    headers['X-Frame-Options'] = 'DENY'
    headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    headers['Permissions-Policy'] = (
        'accelerometer=(), camera=(), geolocation=(), '
        'gyroscope=(), magnetometer=(), microphone=(), '
        'payment=(), usb=()'
    )
    headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    # Ocultar información del servidor
    headers['Server'] = 'WebServer'

    # CSP para todas las respuestas estáticas (incluye .html, .xml, etc.)
    csp_strict = (
        "default-src 'self'; "
        "script-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com; "
        "style-src 'self' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; "
        "font-src 'self' data: fonts.gstatic.com cdnjs.cloudflare.com; "
        "img-src 'self' data: https://cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    ).replace("  ", " ")
    csp_relaxed = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; "
        "font-src 'self' data: fonts.gstatic.com cdnjs.cloudflare.com; "
        "img-src 'self' data: https://cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    ).replace("  ", " ")

    if url.endswith('oauth2-redirect.html'):
        headers['Content-Security-Policy'] = csp_relaxed
    else:
        headers['Content-Security-Policy'] = csp_strict


class IPWhitelistMiddleware:
    """
    Restringe el acceso a rutas sensibles para usuarios NO autenticados
    basado en una lista blanca de IPs (configurable por entorno).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_ips = set(getattr(settings, 'TRUSTED_IP_WHITELIST', []))
        self.path_prefixes = getattr(settings, 'IP_WHITELIST_PATH_PREFIXES', ['/admin/', '/swagger/', '/redoc/'])

    def __call__(self, request):
        # Si no hay lista blanca configurada, no hace nada
        if not self.allowed_ips:
            return self.get_response(request)

        path = request.path or ''
        applies = any(path.startswith(prefix) for prefix in self.path_prefixes)

        if applies and not getattr(request, 'user', None) or (getattr(request, 'user', None) and not request.user.is_authenticated):
            # Obtener IP del cliente (considerando proxies)
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
            if ip not in self.allowed_ips:
                return HttpResponseForbidden('Acceso restringido por IP')

        return self.get_response(request)
