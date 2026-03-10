from rest_framework import serializers


class CrearReservaRequestSerializer(serializers.Serializer):
    kit_id = serializers.IntegerField(min_value=1)
    inicio = serializers.DateField()
    fin = serializers.DateField()


class CrearReservaResponseSerializer(serializers.Serializer):
    reserva_id = serializers.IntegerField(min_value=1)
