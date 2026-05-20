from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_add_curso_compra_curso"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostForo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("titulo", models.CharField(max_length=200)),
                ("contenido", models.TextField()),
                ("tags", models.JSONField(blank=True, default=list)),
                ("es_premium", models.BooleanField(default=False)),
                ("likes", models.PositiveIntegerField(default=0)),
                ("comentarios_count", models.PositiveIntegerField(default=0)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posts_foro",
                        to="blog.usuario",
                    ),
                ),
            ],
            options={
                "ordering": ["-creado_en"],
            },
        ),
    ]
