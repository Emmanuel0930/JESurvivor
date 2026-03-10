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
    compra_id = serializers.IntegerField()
    curso_id = serializers.IntegerField(source="curso.id")
    fecha_compra = serializers.DateTimeField()
