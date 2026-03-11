from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from blog.domain.models import (
    CompraCurso,
    Curso,
    KitEspecializado,
    Producto,
    ReservaKit,
    Usuario,
)


class Command(BaseCommand):
    help = "Crea datos mock (usuarios, kits, cursos) para probar endpoints."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding mock data..."))

        # Usuarios (modelo de dominio)
        usuarios = [
            Usuario.objects.get_or_create(
                email="basico@jesurvivor.local",
                defaults={
                    "nombre": "Usuario Básico",
                    "contrasena_hash": "hash",
                    "nivel_experiencia": Usuario.NivelExperiencia.BASICO,
                    "ubicacion_climatica": Usuario.UbicacionClimatica.TEMPLADO,
                },
            )[0],
            Usuario.objects.get_or_create(
                email="intermedio@jesurvivor.local",
                defaults={
                    "nombre": "Usuario Intermedio",
                    "contrasena_hash": "hash",
                    "nivel_experiencia": Usuario.NivelExperiencia.INTERMEDIO,
                    "ubicacion_climatica": Usuario.UbicacionClimatica.FRIO,
                },
            )[0],
            Usuario.objects.get_or_create(
                email="avanzado@jesurvivor.local",
                defaults={
                    "nombre": "Usuario Avanzado",
                    "contrasena_hash": "hash",
                    "nivel_experiencia": Usuario.NivelExperiencia.AVANZADO,
                    "ubicacion_climatica": Usuario.UbicacionClimatica.SELVA,
                },
            )[0],
        ]

        # Kits
        kits = [
            KitEspecializado.objects.get_or_create(
                nombre="Kit Montaña Básico",
                defaults={
                    "descripcion": "Kit básico para montaña.",
                    "precio": 59.99,
                    "tipo": Producto.TipoProducto.KIT,
                    "nivel_recomendado": Producto.NivelRecomendado.BASICO,
                    "stock": 10,
                    "entorno": KitEspecializado.Entorno.MONTANA,
                    "lista_items": ["Linterna", "Cuerda", "Manta térmica"],
                },
            )[0],
            KitEspecializado.objects.get_or_create(
                nombre="Kit Selva Intermedio",
                defaults={
                    "descripcion": "Kit para supervivencia en selva.",
                    "precio": 89.99,
                    "tipo": Producto.TipoProducto.KIT,
                    "nivel_recomendado": Producto.NivelRecomendado.INTERMEDIO,
                    "stock": 5,
                    "entorno": KitEspecializado.Entorno.SELVA,
                    "lista_items": ["Machete", "Repelente", "Filtro de agua"],
                },
            )[0],
            KitEspecializado.objects.get_or_create(
                nombre="Kit Nieve Avanzado",
                defaults={
                    "descripcion": "Kit avanzado para clima extremo (nieve).",
                    "precio": 129.99,
                    "tipo": Producto.TipoProducto.KIT,
                    "nivel_recomendado": Producto.NivelRecomendado.AVANZADO,
                    "stock": 2,
                    "entorno": KitEspecializado.Entorno.NIEVE,
                    "lista_items": ["Piolet", "Crampones", "Saco -10°C"],
                },
            )[0],
        ]

        # Cursos
        cursos = [
            Curso.objects.get_or_create(
                nombre="Supervivencia 101",
                defaults={
                    "descripcion": "Introducción a supervivencia: agua, fuego, refugio.",
                    "precio": 19.99,
                    "nivel_recomendado": Curso.NivelRecomendado.BASICO,
                    "duracion_horas": 6,
                    "activo": True,
                },
            )[0],
            Curso.objects.get_or_create(
                nombre="Navegación y orientación",
                defaults={
                    "descripcion": "Brújula, mapa y orientación en terreno.",
                    "precio": 29.99,
                    "nivel_recomendado": Curso.NivelRecomendado.INTERMEDIO,
                    "duracion_horas": 8,
                    "activo": True,
                },
            )[0],
            Curso.objects.get_or_create(
                nombre="Operaciones avanzadas en clima extremo",
                defaults={
                    "descripcion": "Técnicas avanzadas para nieve y rescate básico.",
                    "precio": 49.99,
                    "nivel_recomendado": Curso.NivelRecomendado.AVANZADO,
                    "duracion_horas": 10,
                    "activo": True,
                },
            )[0],
        ]

        # Compra curso (ejemplo)
        CompraCurso.objects.get_or_create(
            usuario=usuarios[0],
            curso=cursos[0],
        )

        # Reserva ejemplo (para tener un solapamiento observable)
        inicio = date.today() + timedelta(days=2)
        fin = date.today() + timedelta(days=4)
        ReservaKit.objects.get_or_create(
            usuario=usuarios[1],
            kit=kits[0],
            fecha_inicio=inicio,
            fecha_fin=fin,
            defaults={"estado": ReservaKit.EstadoReserva.PENDIENTE},
        )

        self.stdout.write(self.style.SUCCESS("Mock data creado correctamente."))
        self.stdout.write(
            "Usuarios: "
            + ", ".join([f"{u.id}:{u.email}" for u in usuarios])
        )
        self.stdout.write(
            "Kits: " + ", ".join([f"{k.id}:{k.nombre}" for k in kits])
        )
        self.stdout.write(
            "Cursos: " + ", ".join([f"{c.id}:{c.nombre}" for c in cursos])
        )

