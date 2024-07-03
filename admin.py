from django.contrib import admin
from.models import Marca, Producto, Alumno, Pago, Clase, Contacto, Profesor

class ProductoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "precio", "marca"]
    search_fields = ["nombre"]
    list_filter = ["marca"]
    list_per_page = 10

class AlumnosAdmin(admin.ModelAdmin):
    list_display = ["nombre", "rut", "telefono"]
    search_fields = ["nombre"]

class ContactoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "tipo_consulta"]
    search_fields = ["nombre"]
    list_filter = ["tipo_consulta"]
    
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ["nombre", "rut", "clase"]
    search_fields = ["nombre"]
    list_filter = ["rut", "clase"]



admin.site.register(Marca)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Alumno, AlumnosAdmin)
admin.site.register(Pago)
admin.site.register(Clase)
admin.site.register(Contacto, ContactoAdmin)
admin.site.register(Profesor, ProfesorAdmin)
# Register your models here.
