from django.db import models
from .validators import validar_rut
from django.db.models.signals import pre_delete, m2m_changed
from django.dispatch import receiver
import os

# Create your models here.

class Marca(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField()
    stock = models.IntegerField(default=0)
    descripcion = models.TextField()
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT)
    imagen = models.ImageField(upload_to="productos", null=True)



    def __str__(self):
        return self.nombre
    

class Alumno(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ] #para que pueda escoger solo esas opciones predefindias
    rut = models.CharField(max_length=12, primary_key=True, validators=[validar_rut])
    nombre = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    correo = models.EmailField(max_length=254, unique=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)  
    telefono = models.CharField(max_length=15)  
    direccion = models.TextField() 

    clases = models.ManyToManyField('Clase', related_name='alumnos')

    def __str__(self):
        return self.rut
    

    
class Clase(models.Model):
    CLASES_CHOICES = [
        ('0', 'Boxeo'),
        ('1', 'Boxeo Niños'),
        ('2', 'Fight Do'),
        ('3', 'Karate Kenpo'),
        ('4', 'Kick Boxing'),
        ('5', 'Pesas'),
        ('6', 'Tae Kwondo'),
        ('7', 'Zumba'),
    ]
    tipo_clase = models.CharField(max_length=1,choices=CLASES_CHOICES)
    cupos = models.IntegerField()
    precio = models.IntegerField()
    horario_inicio = models.TimeField()
    horario_fin = models.TimeField()
    descripcion = models.TextField(default="Descripcion no disponible")

    def __str__(self):
        return self.get_tipo_clase_display()



class Pago(models.Model):
    
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    fecha_pago = models.DateField()
    monto = models.IntegerField()
    descripcion = models.TextField()
    

    def __str__(self):
        return f"Pago de {self.alumno.nombre} el {self.fecha_pago}"
    

opciones_consulta = [
    [0, "consulta"],
    [1, "reclamo"],
    [2, "felicitaciones"]
]

class Contacto(models.Model):
    nombre = models.CharField(max_length=50)
    correo = models.EmailField()
    tipo_consulta = models.IntegerField(choices=opciones_consulta)
    mensaje = models.TextField()
    respondida = models.BooleanField(default=False)  # Nuevo campo para marcar si ha sido respondida

    def __str__(self):
        return self.nombre
    
    

class Profesor(models.Model):
    rut = models.CharField(max_length=12, primary_key=True, validators=[validar_rut])
    nombre = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50)
    correo = models.EmailField()
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="profesores", null=True)

    def __str__(self):
        return self.nombre
    
@receiver(pre_delete, sender=Profesor)
def eliminar_imagen_profesor(sender, instance, **kwargs):
    # Obtener la ruta de la imagen
    ruta_imagen = instance.imagen.path
    # Verificar si la imagen existe y eliminarla
    if os.path.exists(ruta_imagen):
        os.remove(ruta_imagen)
    
@receiver(m2m_changed, sender=Alumno.clases.through)
def aumentar_cupos(sender, instance, action, **kwargs):
    if action == 'post_remove' or action == 'post_clear':  # Verificar si se removió un alumno de una clase o se borraron todas las relaciones
        clases = instance.clases.all()  # Obtener todas las clases del alumno
        for clase in clases:
            clase.cupos += 1  # aumenta en uno el cupo de la clase
            clase.save()  # Guardar el cambio en la base de datos

    

    


