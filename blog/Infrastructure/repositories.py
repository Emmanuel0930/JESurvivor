from blog.domain.models import CompraCurso, Curso, KitEspecializado, ReservaKit


class KitRepository:
    def obtener_por_id(self, kit_id):
        return KitEspecializado.objects.get(id=kit_id)

    def listar_kits(self, solo_con_stock=False):
        qs = KitEspecializado.objects.all().order_by("nombre")
        if solo_con_stock:
            qs = qs.filter(stock__gt=0)
        return qs


class ReservaRepository:
    def existe_solapamiento(self, kit, fecha_inicio, fecha_fin):
        return ReservaKit.objects.filter(
            kit=kit,
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
        ).exists()

    def guardar(self, reserva):
        reserva.save()
        return reserva

    def obtener_por_id(self, reserva_id):
        return ReservaKit.objects.get(id=reserva_id)

    def listar_por_usuario(self, usuario):
        return ReservaKit.objects.filter(usuario=usuario).order_by("fecha_inicio")


class CursoRepository:
    def obtener_por_id(self, curso_id):
        return Curso.objects.get(id=curso_id)

    def listar_cursos(self, solo_activos=True):
        qs = Curso.objects.all().order_by("nombre")
        if solo_activos:
            qs = qs.filter(activo=True)
        return qs


class CompraCursoRepository:
    def guardar(self, compra):
        compra.save()
        return compra

    def existe_compra(self, usuario, curso):
        return CompraCurso.objects.filter(usuario=usuario, curso=curso).exists()

    def listar_por_usuario(self, usuario):
        return CompraCurso.objects.filter(usuario=usuario).select_related("curso").order_by("-fecha_compra")
