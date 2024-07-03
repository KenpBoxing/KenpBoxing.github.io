from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, Pago, Alumno, Clase, Profesor, Contacto
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from .forms import ClaseForm, ContactoForm, PagoForm, ProductoForm, AlumnoForm, ProfesorForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from .utils import remove_html_tags
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from django.shortcuts import redirect
from django.urls import reverse
from datetime import datetime

import json


def home(request):
    return render(request, 'app/home.html')
def contacto(request):

    data = {
        'form' : ContactoForm()
    }

    if request.method == 'POST':
        formulario = ContactoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Informacion Enviada!")
        else:
            data["form"] = formulario

    return render(request, 'app/contacto.html', data)
def galeria(request):
    return render(request, 'app/galeria.html')
def pago(request):
    return render(request, 'app/pago.html')
def productos(request):
    busqueda = request.GET.get("buscar")
    productos = Producto.objects.all()
    precio = request.GET.get("precio")
    page = request.GET.get('page', 1)

    if busqueda:
        productos = Producto.objects.filter(
            Q(nombre__icontains = busqueda) | 
            Q(precio__icontains = busqueda) |
            Q(marca__nombre__icontains=busqueda) 
        ).distinct()

    if precio == 'menor':
        productos = productos.order_by('precio')
    elif precio == 'mayor':
        productos = productos.order_by('-precio')   

    try:
        paginator = Paginator(productos, 6)
        productos = paginator.page(page)
    except:
        raise Http404
 
    data = {
        'entity' : productos,
        'paginator':paginator
    }
    


    return render(request, 'app/productos.html', data)
def clases(request):
    clases = Clase.objects.all()
    profesores = Profesor.objects.all()

    data = {
        'clases' : clases,
        'profesores' : profesores
    }
    return render(request, 'app/clases.html', data)


from datetime import datetime, timedelta
import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import Alumno, Pago

def consultar_historial(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        rut = data.get('rut')
        try:
            alumno = Alumno.objects.get(rut=rut)
            
            # Obtener la fecha actual
            fecha_actual = datetime.now().date()
            
            # Calcular el primer día del mes actual
            primer_dia_mes_actual = fecha_actual.replace(day=1)
            
            # Calcular el primer día del mes anterior
            primer_dia_mes_anterior = (primer_dia_mes_actual - timedelta(days=1)).replace(day=1)
            
            # Filtrar pagos que estén dentro del mes anterior o del mes actual
            pagos = Pago.objects.filter(
                alumno=alumno, 
                fecha_pago__gte=primer_dia_mes_anterior,
                fecha_pago__lt=(primer_dia_mes_actual + timedelta(days=32)).replace(day=1)
            )
            
            pagos_list = [
                {
                    'fecha_pago': pago.fecha_pago.strftime('%d-%m-%Y'),
                    'monto': pago.monto,
                    'descripcion': pago.descripcion
                } 
                for pago in pagos
            ]
            
            # Calcular los próximos pagos
            proximos_pagos = []
            
            for pago in pagos:
                fecha_proximo_pago = pago.fecha_pago.replace(day=1) + timedelta(days=32)
                fecha_proximo_pago = fecha_proximo_pago.replace(day=1)  # Primer día del mes siguiente
                dias_restantes = (fecha_proximo_pago - fecha_actual).days
                
                proximos_pagos.append({
                    'fecha_proximo_pago': fecha_proximo_pago.strftime('%d-%m-%Y'),
                    'dias_restantes': dias_restantes,
                    'descripcion': pago.descripcion
                })

            return JsonResponse({'exists': True, 'pagos': pagos_list, 'proximos_pagos': proximos_pagos})
        except Alumno.DoesNotExist:
            return JsonResponse({'exists': False})
    return JsonResponse({'exists': False})  



@login_required
def agregar_productos(request):

    data = {
        'form': ProductoForm()
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto Registrado!")
            return redirect(to="listar_producto")
        else:
            data["form"] = formulario

    return render(request, 'app/producto/agregar.html', data)

@login_required
def listar_productos(request):
    productos = Producto.objects.all()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(productos, 5)
        productos = paginator.page(page)
    except:
        raise Http404


    data = {
        'entity' : productos,
        'paginator':paginator
    }

    return render(request, 'app/producto/listar.html', data)

@login_required
def modificar_producto(request, id):

    producto = get_object_or_404(Producto, id=id)

    data = {
        'form': ProductoForm(instance=producto)
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, instance=producto, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Modifciado Correctamente!")
            return redirect(to="listar_producto")
        data["form"] = formulario

    return render(request, 'app/producto/modificar.html', data)

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    messages.success(request, "Eliminado Correctamente!")
    return redirect(to="listar_producto")


@login_required
def agregar_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            alumno = form.save(commit=False)
            # Obtener los valores de región, comuna y dirección
            region = request.POST.get('region', '')
            comuna = request.POST.get('comuna', '')
            direccion = request.POST.get('direccion', '')
            
            # Combinar los valores para formar la dirección completa
            direccion_completa = f"{region}, {comuna}, {direccion}"
            alumno.direccion = direccion_completa
            
            alumno.save()
            form.save_m2m()  # Guardar relaciones ManyToMany
            
            messages.success(request, "Alumno Registrado!")
            return redirect('listar_alumnos')  # Reemplazar por la URL a la que quieras redirigir luego de guardar
    else:
        form = AlumnoForm()
    
    context = {
        'form': form,
        'mensaje': 'Mensaje opcional si lo deseas'
    }
    return render(request, 'app/alumnos/agregar.html', context)

@login_required
def listar_alumnos(request):
    alumnos = Alumno.objects.all()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(alumnos, 5)
        alumnos = paginator.page(page)
    except:
        raise Http404


    data = {
        'entity' : alumnos,
        'paginator':paginator
    }

    return render(request, 'app/alumnos/listar.html', data)
    


@login_required
def modificar_alumno(request, rut):
    alumno = get_object_or_404(Alumno, rut=rut)

    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            alumno = form.save(commit=False)
            # Obtener los valores de región, comuna y dirección
            region = request.POST.get('region', '')
            comuna = request.POST.get('comuna', '')
            direccion = request.POST.get('direccion', '')

            # Combinar los valores para formar la dirección completa
            direccion_completa = f"{region}, {comuna}, {direccion}"
            alumno.direccion = direccion_completa

            alumno.save()
            form.save_m2m()
            messages.success(request, "Modificado Correctamente!")
            return redirect('listar_alumnos')  # O la URL a la que desees redirigir después de guardar
    else:
        form = AlumnoForm(instance=alumno)

    context = {
        'form': form,
        'alumno': alumno
    }
    return render(request, 'app/alumnos/modificar.html', context)
@login_required
def eliminar_alumno(request, rut):
    alumnos = get_object_or_404(Alumno, rut=rut)
    alumnos.delete()
    messages.success(request, "Eliminado Correctamente!")
    return redirect(to="listar_alumnos")






@login_required
def listar_consultas(request):
    estado = request.GET.get('estado')

    if estado == 'resueltas':
        consultas = Contacto.objects.filter(respondida=True)
    elif estado == 'no_resueltas':
        consultas = Contacto.objects.filter(respondida=False)
    else:
        consultas = Contacto.objects.all()

    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(consultas, 5)
        consultas = paginator.page(page)
    except:
        raise Http404

    data = {
        'entity': consultas,
        'paginator': paginator,
        'estado': estado  # Pasamos el estado para mantener el filtro seleccionado
    }

    return render(request, 'app/consultas/listar.html', data)
@login_required
def ver_consulta(request, id):
    consulta = get_object_or_404(Contacto, id=id)
    return render(request, 'app/consultas/ver_consulta.html', {'consulta': consulta})



# views.py

from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import render, redirect
from .forms import ResponderConsultaForm
from .models import Contacto
@login_required
def responder_consulta(request, id):
    consulta = get_object_or_404(Contacto, id=id)

    if request.method == "POST":
        form = ResponderConsultaForm(request.POST)
        if form.is_valid():
            asunto = form.cleaned_data['asunto']
            respuesta = form.cleaned_data['respuesta']

            # Renderizamos la plantilla del correo con la respuesta
            template = render_to_string('email_template.html', {
                'consulta': consulta,
                'respuesta': respuesta,
            })

            # Enviamos el correo electrónico
            email = EmailMessage(
                asunto,
                template,
                settings.EMAIL_HOST_USER,
                [consulta.correo]  # Enviar al correo del usuario que hizo la consulta
            )
            email.content_subtype = "html"  # Configurar el contenido como HTML
            email.send()

            # Marcar la consulta como respondida
            consulta.respondida = True
            consulta.save()

            messages.success(request, 'La respuesta se ha enviado correctamente.')
            return redirect('ver_consulta', id=consulta.id)
    else:
        form = ResponderConsultaForm()

    return render(request, 'app/consultas/responder_consulta.html', {'form': form, 'consulta': consulta})

@login_required
def eliminar_consulta(request, id):
    consultas = get_object_or_404(Contacto, id=id)
    consultas.delete()
    messages.success(request, "Eliminado Correctamente")
    return redirect(to="listar_consultas")

@login_required
def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['correo']
        asunto = request.POST['asunto']
        mensaje = request.POST['mensaje']

        template = render_to_string('email_template.html', {
            'name' : name,
            'email' : email,
            'message' : mensaje
        })

        email = EmailMessage(
            asunto,
            template,
            settings.EMAIL_HOST_USER,
            ['ya.castilla@duocuc.cl']
        )

        email.fail_silently = False
        email.send()

        messages.success(request, 'Se ha enviado tu correo')
        return redirect('listar_consultas')


@login_required
def agregar_profesor(request):
    if request.method == 'POST':
        formulario = ProfesorForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Profesor Registrado correctamente.")
            return redirect('listar_profesor')  # Cambia 'home' por el nombre de la URL a la que deseas redirigir
        else:
            # Si el formulario no es válido, puedes manejar cómo deseas mostrar los errores o mensajes aquí
            messages.error(request, "Error al registrar el profesor. Por favor, corrige los errores.")
    else:
        formulario = ProfesorForm()

    context = {
        'form': formulario,
    }
    return render(request, 'app/profesores/agregar.html', context)


@login_required
def listar_profesor(request):
    profesor = Profesor.objects.all()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(profesor, 5)
        profesor = paginator.page(page)
    except:
        raise Http404


    data = {
        'entity' : profesor,
        'paginator':paginator
    }

    return render(request, 'app/profesores/listar.html', data)


@login_required
def modificar_profesor(request, rut):
    profesor = get_object_or_404(Profesor, rut=rut)

    if request.method == 'POST':
        formulario = ProfesorForm(data=request.POST, instance=profesor, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Modificado Correctamente!")
            return redirect(to="listar_profesor")
        else:
            messages.error(request, "Por favor, corrige los errores.")
    else:
        formulario = ProfesorForm(instance=profesor)

    context = {
        'form': formulario,
        'profesor': profesor
    }
    return render(request, 'app/profesores/modificar.html', context)
@login_required
def eliminar_profesor(request, rut):
    profesor = get_object_or_404(Profesor, rut=rut)
    profesor.delete()
    messages.success(request, "Eliminado Correctamente!")
    return redirect(to="listar_profesor")

@login_required
def agregar_clases(request):

    data = {
        'form': ClaseForm()
    }

    if request.method == 'POST':
        formulario = ClaseForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Clase Registrado!")
            return redirect(to="listar_clase")
        else:
            data["form"] = formulario

    return render(request, 'app/clases/agregar.html', data)

@login_required
def listar_clases(request):
    clases = Clase.objects.all()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(clases, 5)
        clases = paginator.page(page)
    except:
        raise Http404


    data = {
        'entity' : clases,
        'paginator':paginator
    }

    return render(request, 'app/clases/listar.html', data)




@login_required
def modificar_clase(request, id):
    clase = get_object_or_404(Clase, id=id)
    
    

    if request.method == 'POST':
        formulario = ClaseForm(data=request.POST, instance=clase, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Modificado Correctamente!")
            return redirect(to="listar_clases")
    else:
        formulario = ClaseForm(instance=clase)
    
    data = {
        'form': formulario
    }
    
    return render(request, 'app/clases/modificar.html', data)

@login_required
def eliminar_clase(request, id):
    clases = get_object_or_404(Clase, id=id)
    clases.delete()
    messages.success(request, "Eliminado Correctamente!")
    return redirect(to="listar_clases")


from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from .models import Pago, Alumno

@login_required
def listar_pagos(request):
    pagos = Pago.objects.all().order_by('-fecha_pago')  # Ordenar por fecha de pago, el más reciente primero
    page = request.GET.get('page', 1)

    # Obtener todos los RUTs de los alumnos registrados
    ruts_registrados = Alumno.objects.values_list('rut', flat=True).distinct()

    # Filtrar pagos si se ha seleccionado un RUT específico
    filtro = request.GET.get('filtro')
    if filtro and filtro != 'todos':
        pagos = pagos.filter(alumno__rut=filtro)

    # Configurar paginación
    paginator = Paginator(pagos, 5)
    try:
        pagos = paginator.page(page)
    except PageNotAnInteger:
        pagos = paginator.page(1)
    except EmptyPage:
        pagos = paginator.page(paginator.num_pages)

    data = {
        'entity': pagos,
        'ruts_registrados': ruts_registrados,
        'filtro': filtro,
    }

    return render(request, 'app/pagos/listar.html', data)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import PagoForm

@login_required
def agregar_pagos(request):
    if request.method == 'POST':
        formulario = PagoForm(request.POST, request.FILES)
        if formulario.is_valid():
            pago = formulario.save(commit=False)  # Guarda el formulario pero no lo persiste en la BD aún
            # Aquí asegúrate de asignar el alumno correcto a partir del rut
            # Puedes hacer algo como:
            # alumno_rut = formulario.cleaned_data['alumno']
            # alumno = Alumno.objects.get(rut=alumno_rut)
            # pago.alumno = alumno
            pago.save()  # Ahora se guarda el pago en la BD con el alumno asignado
            messages.success(request, "Pago Registrado!")
            return redirect('listar_pagos')
    else:
        formulario = PagoForm()
    
    return render(request, 'app/pagos/agregar.html', {'form': formulario})

from django.http import JsonResponse
from django.db.models import Q  # Importar Q para realizar consultas complejas
from .models import Alumno

def autocomplete_alumno(request):
    term = request.GET.get('term')  # Término de búsqueda desde el frontend
    alumnos = Alumno.objects.filter(
        Q(nombre__icontains=term) |  # Buscar coincidencias en el nombre
        Q(apellido_paterno__icontains=term) |  # Buscar coincidencias en el apellido paterno
        Q(apellido_materno__icontains=term)  # Buscar coincidencias en el apellido materno
    ).values('rut', 'nombre', 'apellido_paterno', 'apellido_materno')  # Incluir los apellidos para mostrar en el resultado
    return JsonResponse(list(alumnos), safe=False)

@login_required
def modificar_pagos(request, id):
    pagos = get_object_or_404(Pago, id=id)
    
    

    if request.method == 'POST':
        formulario = PagoForm(data=request.POST, instance=pagos, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Modificado Correctamente!")
            return redirect(to="listar_pagos")
    else:
        formulario = PagoForm(instance=pagos)
    
    data = {
        'form': formulario
    }
    
    return render(request, 'app/pagos/modificar.html', data)



@login_required
def seleccionar_informe(request):
    
    return render(request, 'app/informes/seleccionar_informe.html')





@login_required
def generar_informe(request):
    if request.method == 'POST':
        tipo_informe = request.POST.get('tipo_informe')
        if tipo_informe == 'total_alumnos':
            return redirect(reverse('informe_total_alumnos'))
        elif tipo_informe == 'pagos_mensuales':
            mes = request.POST.get('mes')
            anio = request.POST.get('anio')
            if mes and anio:
                return redirect(reverse('informe_pagos_mensuales') + f'?mes={mes}&anio={anio}')
            else:
                # Manejar el caso en que no se haya seleccionado mes y año
                # Puedes redirigir de vuelta a la página de selección de informe con un mensaje de error
                return redirect(reverse('seleccionar_informe'))
        elif tipo_informe == 'pagos_atrasados':
            mes = request.POST.get('mes')
            anio = request.POST.get('anio')
            
            return informe_pagos_atrasados(request, mes, anio)
            if mes and anio:
                return redirect(reverse('informe_pagos_atrasados') + f'?mes={mes}&anio={anio}')
            else:
                # Manejar el caso en que no se haya seleccionado mes y año
                # Puedes redirigir de vuelta a la página de selección de informe con un mensaje de error
                return redirect(reverse('seleccionar_informe'))
        # Agrega más opciones según los informes disponibles
    return redirect(reverse('seleccionar_informe'))


@login_required
def informe_total_alumnos(request):

    # Obtener todos los alumnos registrados
    alumnos = Alumno.objects.all()

    # Crear un objeto BytesIO para manejar el PDF en memoria
    buffer = BytesIO()

    # Crear un objeto SimpleDocTemplate
    p = SimpleDocTemplate(buffer, pagesize=A4)

    # Lista para almacenar los datos de la tabla
    data = []
    # Encabezados de la tabla
    headers = ['Rut', 'Nombre', 'Apellidos', 'Correo', 'Clase(s)']
    data.append(headers)

    # Agregar los datos de cada alumno a la tabla
    for alumno in alumnos:
        # Concatenar apellido paterno y materno
        apellidos = f"{alumno.apellido_paterno} {alumno.apellido_materno}"

        # Obtener nombres de las clases asociadas al alumno
        clases = ', '.join([clase.get_tipo_clase_display() for clase in alumno.clases.all()])

        data.append([alumno.rut, alumno.nombre, apellidos, alumno.correo, clases])

    # Crear la tabla
    table = Table(data)

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),  # Fondo gris para el encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Texto blanco para el encabezado
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación centrada para todo
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación vertical centrada
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Borde interno de celda
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Borde exterior de la tabla
    ])

    # Aplicar estilo a la tabla
    table.setStyle(style)

    # Crear una lista de elementos Story y agregar la tabla
    elements = []

    # Agregar título
    styles = getSampleStyleSheet()
    elements.append(Spacer(1, 20))  # Espacio antes del título
    elements.append(Paragraph("Informe de Total de Alumnos Registrados", styles['Title']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))  # Línea horizontal debajo del título
    elements.append(Spacer(1, 20))  # Espacio después de la línea horizontal  # Espacio adicional entre título y contenido

    # Agregar contenido
    elements.append(Paragraph(f"Total de Alumnos Registrados: {alumnos.count()}", styles['BodyText']))
    elements.append(Paragraph("<br/><br/>", styles['Normal'])) 

    # Agregar la tabla a los elementos
    elements.append(table)

    # Cargar la imagen del logo
    logo_path = 'app/static/app/img/logo2.png'  # Ruta correcta de tu imagen
    logo = Image(logo_path, width=100, height=100)
    elements.insert(0, logo)  # Insertar el logo al inicio de la lista de elementos

    # Construir el PDF
    p.build(elements)

    # Obtener el contenido del buffer y devolver la respuesta HTTP
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_total_alumnos.pdf"'
    response.write(pdf)

    return response


@login_required
def informe_pagos_mensuales(request):
    # Obtener los parámetros de mes y año de la URL si están presentes
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')


    # Si no se especifica mes y año, usar el mes y año actuales
    if mes and anio:
        try:
            mes = int(mes)
            anio = int(anio)
        except ValueError:
            mes_actual = datetime.now().month
            anio_actual = datetime.now().year
        else:
            fecha_actual = datetime(anio, mes, 1)
            mes_actual = fecha_actual.month
            anio_actual = fecha_actual.year
    else:
        mes_actual = datetime.now().month
        anio_actual = datetime.now().year

    # Filtrar los pagos del mes y año especificados
    pagos = Pago.objects.filter(fecha_pago__month=mes_actual, fecha_pago__year=anio_actual).order_by('fecha_pago')

    # Calcular el total del monto
    total_monto = sum(pago.monto for pago in pagos)

    # Formatear el total del monto con separación de miles
    total_monto_formateado = "${:,.0f}".format(total_monto)

    # Crear un objeto BytesIO para manejar el PDF en memoria
    buffer = BytesIO()

    # Crear un objeto SimpleDocTemplate
    p = SimpleDocTemplate(buffer, pagesize=A4)

    # Lista para almacenar los datos de la tabla
    data = []
    # Encabezados de la tabla
    headers = ['Fecha', 'Alumno', 'Monto']
    data.append(headers)

    # Agregar los datos de cada pago a la tabla
    for pago in pagos:
        monto_formateado = "${:,.0f}".format(pago.monto)
        data.append([pago.fecha_pago.strftime('%d/%m/%Y'), pago.alumno.rut, monto_formateado])

    # Crear la tabla
    table = Table(data)

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),  # Fondo gris para el encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Texto blanco para el encabezado
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación centrada para todo
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación vertical centrada
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Borde interno de celda
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Borde exterior de la tabla
    ])

    # Aplicar estilo a la tabla
    table.setStyle(style)

    # Crear una lista de elementos Story y agregar la tabla
    elements = []

    # Agregar título
    styles = getSampleStyleSheet()
    elements.append(Spacer(1, 20))  # Espacio antes del título
    elements.append(Paragraph(f"Informe de Pagos Mensuales- {mes}/{anio}", styles['Title']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))  # Línea horizontal debajo del título
    elements.append(Spacer(1, 20))  # Espacio después de la línea horizontal

    elements.append(Paragraph(f"Total recaudado: {total_monto_formateado}", styles['BodyText']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Agregar la tabla a los elementos
    elements.append(table)

    logo_path = 'app/static/app/img/logo2.png'  # Ruta correcta de tu imagen
    logo = Image(logo_path, width=100, height=100)
    elements.insert(0, logo)  # Insertar el logo al inicio de la lista de elementos

    # Construir el PDF
    p.build(elements)

    # Obtener el contenido del buffer y devolver la respuesta HTTP
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_pagos_mensuales.pdf"'
    response.write(pdf)

    return response






@login_required
def informe_pagos_atrasados(request, mes_reporte=None, anio_reporte=None):
    if mes_reporte is None or anio_reporte is None:
        # Obtener el mes y año actuales
        fecha_actual = datetime.now()
        mes_reporte = fecha_actual.month
        anio_reporte = fecha_actual.year

    # Convertir mes_reporte y anio_reporte a enteros para evitar errores de tipo
    mes_reporte = int(mes_reporte)
    anio_reporte = int(anio_reporte)

    # Calcular el mes y año del mes anterior
    if mes_reporte == 1:
        mes_anterior = 12
        anio_anterior = anio_reporte - 1
    else:
        mes_anterior = mes_reporte - 1
        anio_anterior = anio_reporte

    # Obtener la lista de alumnos que no han pagado en el mes y año especificados
    alumnos_sin_pago = Alumno.objects.exclude(pago__fecha_pago__month=mes_reporte, pago__fecha_pago__year=anio_reporte).distinct()

    # Crear un objeto BytesIO para manejar el PDF en memoria
    buffer = BytesIO()

    # Crear un objeto SimpleDocTemplate
    p = SimpleDocTemplate(buffer, pagesize=A4)

    # Lista para almacenar los datos de la tabla
    data = []
    # Encabezados de la tabla
    headers = ['Nombre', 'Apellidos', 'Correo Electrónico', 'Monto por Pagar']
    data.append(headers)

    # Variable para calcular el total del monto por pagar
    total_monto = 0

    # Agregar los datos de cada alumno sin pago a la tabla
    for alumno in alumnos_sin_pago:
        apellidos = f"{alumno.apellido_paterno} {alumno.apellido_materno}"

        # Obtener el total de los pagos del alumno para el mes anterior
        total_alumno_mes_anterior = sum(pago.monto for pago in alumno.pago_set.filter(fecha_pago__month=mes_anterior, fecha_pago__year=anio_anterior))
        monto_formateado = "${:,.0f}".format(total_alumno_mes_anterior)

        data.append([alumno.nombre, apellidos, alumno.correo, monto_formateado])

        # Sumar al total del monto por pagar
        total_monto += total_alumno_mes_anterior

    # Formatear el total del monto con separación de miles
    total_monto_formateado = "${:,.0f}".format(total_monto)

    # Crear la tabla
    table = Table(data)

    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),  # Fondo gris para el encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Texto blanco para el encabezado
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alineación centrada para todo
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alineación vertical centrada
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # Borde interno de celda
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # Borde exterior de la tabla
    ])

    # Aplicar estilo a la tabla
    table.setStyle(style)

    # Crear una lista de elementos Story y agregar la tabla
    elements = []

    # Agregar título
    styles = getSampleStyleSheet()
    elements.append(Spacer(1, 20))  # Espacio antes del título
    elements.append(Paragraph(f"Informe de Alumnos Sin Pago - {mes_reporte}/{anio_reporte}", styles['Title']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))  # Línea horizontal debajo del título
    elements.append(Spacer(1, 20))  # Espacio después de la línea horizontal

    elements.append(Paragraph(f"Total de alumnos sin pago: {len(alumnos_sin_pago)}", styles['BodyText']))
    elements.append(Paragraph(f"Total del monto: {total_monto_formateado}", styles['BodyText']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Agregar la tabla a los elementos
    elements.append(table)

    logo_path = 'app/static/app/img/logo2.png'  # Ruta correcta de tu imagen
    logo = Image(logo_path, width=100, height=100)
    elements.insert(0, logo)  # Insertar el logo al inicio de la lista de elementos

    # Construir el PDF
    p.build(elements)

    # Obtener el contenido del buffer y devolver la respuesta HTTP
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="informe_alumnos_sin_pago_{mes_reporte}_{anio_reporte}.pdf"'
    response.write(pdf)

    return response



















































