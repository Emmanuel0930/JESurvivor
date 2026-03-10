from django.contrib import admin
from blog.domain.models import Usuario, Producto, KitEspecializado, ReservaKit

admin.site.register(Usuario)
admin.site.register(Producto)
admin.site.register(KitEspecializado)
admin.site.register(ReservaKit)