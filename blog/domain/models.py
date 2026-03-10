from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Usuario(models.Model):
    class NivelExperiencia(models.TextChoices):
        BASICO = "basico", "Básico"
        INTERMEDIO = "intermedio", "Intermedio"
        AVANZADO = "avanzado", "Avanzado"

    class UbicacionClimatica(models.TextChoices):
        FRIO = "frio", "Frío"
        TEMPLADO = "templado", "Templado"
        CALIDO = "calido", "Cálido"
        SELVA = "selva", "Selva"
        DESERTICO = "desertico", "Desértico"

    nombre = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    contrasena_hash = models.CharField(max_length=255)
    nivel_experiencia = models.CharField(
        max_length=20,
        choices=NivelExperiencia.choices,
        default=NivelExperiencia.BASICO,
    )
    ubicacion_climatica = models.CharField(
        max_length=20,
        choices=UbicacionClimatica.choices,
    )

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    class TipoProducto(models.TextChoices):
        KIT = "kit", "Kit"
        HERRAMIENTA = "herramienta", "Herramienta"
        BOTIQUIN = "botiquin", "Botiquín"
        MAPA = "mapa", "Mapa"

    class NivelRecomendado(models.TextChoices):
        BASICO = "basico", "Básico"
        INTERMEDIO = "intermedio", "Intermedio"
        AVANZADO = "avanzado", "Avanzado"

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TipoProducto.choices)
    nivel_recomendado = models.CharField(
        max_length=20,
        choices=NivelRecomendado.choices,
        default=NivelRecomendado.BASICO,
    )
    stock = models.PositiveIntegerField(default=0)

    def clean(self):
        if self.precio is None or self.precio <= 0:
            raise ValidationError({"precio": "El precio debe ser mayor que cero."})

    def __str__(self):
        return self.nombre


class KitEspecializado(Producto):
    class Entorno(models.TextChoices):
        MONTANA = "montana", "Montaña"
        SELVA = "selva", "Selva"
        URBANO = "urbano", "Urbano"
        DESIERTO = "desierto", "Desierto"
        NIEVE = "nieve", "Nieve"

    entorno = models.CharField(max_length=20, choices=Entorno.choices)
    lista_items = models.JSONField(default=list, blank=True)

    def clean(self):
        super().clean()
        if self.tipo != Producto.TipoProducto.KIT:
            raise ValidationError({"tipo": "Un kit especializado debe tener tipo 'kit'."})

    def save(self, *args, **kwargs):
        self.tipo = Producto.TipoProducto.KIT
        super().save(*args, **kwargs)


class ReservaKit(models.Model):
    class EstadoReserva(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADA = "confirmada", "Confirmada"
        CANCELADA = "cancelada", "Cancelada"
        FINALIZADA = "finalizada", "Finalizada"

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="reservas_kit"
    )
    kit = models.ForeignKey(
        KitEspecializado,
        on_delete=models.CASCADE,
        related_name="reservas"
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=EstadoReserva.choices,
        default=EstadoReserva.PENDIENTE,
    )

    def clean(self):
        hoy = timezone.localdate()

        if self.fecha_inicio >= self.fecha_fin:
            raise ValidationError(
                {"fecha_fin": "La fecha fin debe ser posterior a la fecha inicio."}
            )

        if self.fecha_inicio < hoy:
            raise ValidationError(
                {"fecha_inicio": "No se permiten reservas en fechas pasadas."}
            )

    def __str__(self):
        return f"{self.usuario.nombre} - {self.kit.nombre} ({self.fecha_inicio} a {self.fecha_fin})"


class Curso(models.Model):
    """Curso disponible para compra por los usuarios."""

    class NivelRecomendado(models.TextChoices):
        BASICO = "basico", "Básico"
        INTERMEDIO = "intermedio", "Intermedio"
        AVANZADO = "avanzado", "Avanzado"

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    nivel_recomendado = models.CharField(
        max_length=20,
        choices=NivelRecomendado.choices,
        default=NivelRecomendado.BASICO,
    )
    duracion_horas = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    def clean(self):
        if self.precio is not None and self.precio < 0:
            raise ValidationError({"precio": "El precio no puede ser negativo."})

    def __str__(self):
        return self.nombre


class CompraCurso(models.Model):
    """Registro de compra de un curso por un usuario."""

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="compras_curso",
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name="compras",
    )
    fecha_compra = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["usuario", "curso"]]

    def __str__(self):
        return f"{self.usuario.nombre} - {self.curso.nombre}"