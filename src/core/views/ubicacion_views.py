from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from core.models.ubicacion_models import Provincia, Ciudad, Canton
from core.serializers.ubicacion_serializers import ProvinciaSerializer, CiudadSerializer, CantonSerializer

class ProvinciaViewSet(viewsets.ModelViewSet):
    queryset = Provincia.objects.all()
    serializer_class = ProvinciaSerializer

class CiudadViewSet(viewsets.ModelViewSet):
    queryset = Ciudad.objects.all()
    serializer_class = CiudadSerializer

class CantonViewSet(viewsets.ModelViewSet):
    queryset = Canton.objects.all()
    serializer_class = CantonSerializer


# ==================== ENDPOINTS INTELIGENTES ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def autocompletar_provincia(request):
    """
    Busca provincias que coincidan con lo que escribe
    GET /api/ubicaciones/autocompletar-provincia/?q=pich
    """
    q = request.query_params.get('q', '').strip()
    
    if len(q) < 2:
        return Response({'provincias': []})
    
    provincias = Provincia.objects.filter(
        nombre__icontains=q,
        activo=True
    ).values_list('nombre', flat=True)[:10]
    
    return Response({'provincias': list(provincias)})


@api_view(['GET'])
@permission_classes([AllowAny])
def autocompletar_ciudad(request):
    """
    Busca ciudades por provincia
    GET /api/ubicaciones/autocompletar-ciudad/?provincia=Pichincha&q=quit
    """
    provincia_nombre = request.query_params.get('provincia', '').strip()
    q = request.query_params.get('q', '').strip()
    
    if len(q) < 2 or not provincia_nombre:
        return Response({'ciudades': []})
    
    try:
        provincia = Provincia.objects.get(nombre__iexact=provincia_nombre, activo=True)
        ciudades = Ciudad.objects.filter(
            provincia=provincia,
            nombre__icontains=q,
            activo=True
        ).values_list('nombre', flat=True)[:10]
        
        return Response({'ciudades': list(ciudades)})
    except Provincia.DoesNotExist:
        return Response({'ciudades': []})


@api_view(['GET'])
@permission_classes([AllowAny])
def autocompletar_canton(request):
    """
    Busca cantones por ciudad
    GET /api/ubicaciones/autocompletar-canton/?provincia=Pichincha&ciudad=Quito&q=cay
    """
    provincia_nombre = request.query_params.get('provincia', '').strip()
    ciudad_nombre = request.query_params.get('ciudad', '').strip()
    q = request.query_params.get('q', '').strip()
    
    if len(q) < 2 or not ciudad_nombre:
        return Response({'cantones': []})
    
    try:
        provincia = Provincia.objects.get(nombre__iexact=provincia_nombre, activo=True)
        ciudad = Ciudad.objects.get(
            nombre__iexact=ciudad_nombre,
            provincia=provincia,
            activo=True
        )
        cantones = Canton.objects.filter(
            ciudad=ciudad,
            nombre__icontains=q,
            activo=True
        ).values_list('nombre', flat=True)[:10]
        
        return Response({'cantones': list(cantones)})
    except (Provincia.DoesNotExist, Ciudad.DoesNotExist):
        return Response({'cantones': []})


@api_view(['POST'])
@permission_classes([AllowAny])
def guardar_ubicacion_smart(request):
    """
    Guarda Provincia, Ciudad y Cantón con lógica inteligente.
    
    Enviar:
    {
        "provincia": "Pichincha",
        "ciudad": "Quito",
        "canton": "Cayambe"
    }
    
    Lógica:
    - Si provincia NO existe → crear
    - Si ciudad existe pero no ciudad → crear
    - Si ambas existen → solo guardar cantón
    """
    try:
        provincia_nombre = request.data.get('provincia', '').strip().capitalize()
        ciudad_nombre = request.data.get('ciudad', '').strip().capitalize()
        canton_nombre = request.data.get('canton', '').strip().capitalize()
        
        if not provincia_nombre or not ciudad_nombre:
            return Response(
                {'success': False, 'error': 'Provincia y Ciudad son requeridas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 🔹 Obtener o crear PROVINCIA
        provincia, _ = Provincia.objects.get_or_create(
            nombre__iexact=provincia_nombre,
            defaults={'nombre': provincia_nombre}
        )
        
        # 🔹 Obtener o crear CIUDAD
        ciudad, _ = Ciudad.objects.get_or_create(
            nombre__iexact=ciudad_nombre,
            provincia=provincia,
            defaults={'nombre': ciudad_nombre, 'provincia': provincia}
        )
        
        # 🔹 Obtener o crear CANTÓN
        canton = None
        if canton_nombre:
            canton, _ = Canton.objects.get_or_create(
                nombre__iexact=canton_nombre,
                ciudad=ciudad,
                defaults={'nombre': canton_nombre, 'ciudad': ciudad}
            )
        
        return Response({
            'success': True,
            'message': 'Ubicación guardada correctamente',
            'data': {
                'provincia': {
                    'id': provincia.id,
                    'nombre': provincia.nombre
                },
                'ciudad': {
                    'id': ciudad.id,
                    'nombre': ciudad.nombre
                },
                'canton': {
                    'id': canton.id,
                    'nombre': canton.nombre
                } if canton else None
            }
        })
    
    except Exception as e:
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
