from rest_framework import serializers


class CrearReservaRequestSerializer(serializers.Serializer):
    kit_id = serializers.IntegerField(min_value=1)
    inicio = serializers.DateField()
    fin = serializers.DateField()


class CrearReservaResponseSerializer(serializers.Serializer):
    reserva_id = serializers.IntegerField(min_value=1)


class VerificarDisponibilidadRequestSerializer(serializers.Serializer):
    kit_id = serializers.IntegerField(min_value=1)
    inicio = serializers.DateField()
    fin = serializers.DateField()


class VerificarDisponibilidadResponseSerializer(serializers.Serializer):
    disponible = serializers.BooleanField()


class CancelarReservaRequestSerializer(serializers.Serializer):
    reserva_id = serializers.IntegerField(min_value=1)


class CancelarReservaResponseSerializer(serializers.Serializer):
    reserva_id = serializers.IntegerField(min_value=1)
    estado = serializers.CharField()


class ReservaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    kit_id = serializers.IntegerField(source="kit.id")
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    estado = serializers.CharField()


class KitSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    descripcion = serializers.CharField()
    precio = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField()
    nivel_recomendado = serializers.CharField()
    entorno = serializers.CharField()
    lista_items = serializers.ListField(child=serializers.CharField(), allow_empty=True)


class UsuarioActualSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    email = serializers.EmailField()
    nivel_experiencia = serializers.CharField()
    ubicacion_climatica = serializers.CharField()


# --- Cursos ---

class CursoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    descripcion = serializers.CharField()
    precio = serializers.DecimalField(max_digits=10, decimal_places=2)
    nivel_recomendado = serializers.CharField()
    duracion_horas = serializers.IntegerField()
    activo = serializers.BooleanField()


class ComprarCursoRequestSerializer(serializers.Serializer):
    curso_id = serializers.IntegerField(min_value=1)


class ComprarCursoResponseSerializer(serializers.Serializer):
    compra_id = serializers.IntegerField(source="id")
    curso_id = serializers.IntegerField(source="curso.id")
    fecha_compra = serializers.DateTimeField()


# --- Foro ---

class PostForoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    titulo = serializers.CharField()
    contenido = serializers.CharField()
    tags = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    es_premium = serializers.BooleanField()
    likes = serializers.IntegerField()
    comentarios_count = serializers.IntegerField()
    creado_en = serializers.DateTimeField()
    autor_nombre = serializers.CharField()
    autor_nivel = serializers.CharField()


class CrearPostRequestSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=200)
    contenido = serializers.CharField()
    tags = serializers.ListField(
        child=serializers.CharField(max_length=40),
        required=False,
        allow_empty=True,
        default=list,
    )
    es_premium = serializers.BooleanField(required=False, default=False)


class CrearPostResponseSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
