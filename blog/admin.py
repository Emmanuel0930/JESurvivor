from django.contrib import admin
from blog.domain.models import (
    CompraCurso,
    Curso,
    KitEspecializado,
    Producto,
    ReservaKit,
    Usuario,
)

admin.site.register(Usuario)
admin.site.register(Producto)
admin.site.register(KitEspecializado)
admin.site.register(ReservaKit)
admin.site.register(Curso)
admin.site.register(CompraCurso)