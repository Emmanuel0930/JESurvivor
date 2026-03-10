# Generated manually for Curso and CompraCurso

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Curso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=200)),
                ("descripcion", models.TextField()),
                ("precio", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "nivel_recomendado",
                    models.CharField(
                        choices=[("basico", "Básico"), ("intermedio", "Intermedio"), ("avanzado", "Avanzado")],
                        default="basico",
                        max_length=20,
                    ),
                ),
                ("duracion_horas", models.PositiveIntegerField(default=0)),
                ("activo", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="CompraCurso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha_compra", models.DateTimeField(auto_now_add=True)),
                (
                    "curso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="compras",
                        to="blog.curso",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="compras_curso",
                        to="blog.usuario",
                    ),
                ),
            ],
            options={
                "unique_together": {("usuario", "curso")},
            },
        ),
    ]
