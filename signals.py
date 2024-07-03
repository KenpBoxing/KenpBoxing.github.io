from django.db.models.signals import post_delete, post_save, m2m_changed
from django.dispatch import receiver
from .models import Alumno, Clase

@receiver(post_delete, sender='app.Profesor')
def eliminar_imagen_profesor(sender, instance, **kwargs):
    if instance.imagen:
        instance.imagen.delete(save=False)



@receiver(m2m_changed, sender=Alumno.clases.through)
def actualizar_cupos_al_agregar_alumno(sender, instance, action, **kwargs):
    if action == 'post_add':  # Verificar si se agregó un alumno a una clase
        clases = instance.clases.all()  # Obtener todas las clases del alumno
        for clase in clases:
            clase.cupos -= 1  # Reducir en uno el cupo de la clase
            clase.save()  # Guardar el cambio en la base de datos

    elif action == 'post_remove' or action == 'post_clear':  # Verificar si se removió un alumno de una clase o se borraron todas las relaciones
        clases_afectadas = kwargs.get('pk_set', [])  # Obtener los IDs de las clases afectadas
        for clase_id in clases_afectadas:
            clase = Clase.objects.get(pk=clase_id)  # Obtener la instancia de la clase
            clase.cupos += 1  # Aumentar en uno el cupo de la clase
            clase.save()  # Guardar el cambio en la base de datos

@receiver(m2m_changed, sender=Alumno.clases.through)
def aumentar_cupos(sender, instance, action, **kwargs):
    if action == 'post_remove' or action == 'post_clear':  # Verificar si se removió un alumno de una clase o se borraron todas las relaciones
        clases = instance.clases.all()  # Obtener todas las clases del alumno
        for clase in clases:
            clase.cupos += 1  # aumenta en uno el cupo de la clase
            clase.save()  # Guardar el cambio en la base de datos



