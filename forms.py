from django import forms
from .models import Clase, Contacto, Producto,Alumno, Profesor, Pago
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from .validators import validar_rut
import re
from dal import autocomplete  

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = '__all__'
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'class': 'datepicker form-control'}),
            'alumno': autocomplete.ModelSelect2(
                url='autocomplete-alumno',
                attrs={'class': 'form-control', 'data-placeholder': 'Selecciona un alumno'},
            ),
        }
        
class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ['nombre', 'correo', 'tipo_consulta', 'mensaje', 'respondida']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'campo-texto'}),
            'correo': forms.EmailInput(attrs={'class': 'campo-correo'}),
            'mensaje': forms.Textarea(attrs={'class': 'campo-mensaje'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'nombre',
            'correo',
            'tipo_consulta',
            'mensaje',
            Field('respondida', type='hidden'),  # Ocultar el campo respondida con una clase d-none
            Submit('submit', 'Enviar', css_class='btn btn-primary')
        )


class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = '__all__'

class ClaseForm(forms.ModelForm):
    class Meta:
        model = Clase
        fields = '__all__'



class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['rut', 'nombre', 'apellido_paterno', 'apellido_materno', 'correo', 'genero', 'telefono', 'clases']  # Incluye el campo 'clases'
        
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if rut:
            # Validar el formato del RUT (aceptar puntos y guion)
            if not re.match(r'^\d{1,2}(\.\d{3}){2}-[\dK]$', rut.upper()):
                raise forms.ValidationError('El RUT debe contener solo números, puntos y guion en el formato 11.111.111-K.')

            # Llamar a la función de validación
            validar_rut(rut.replace('.', '').replace('-', ''))
        return rut


class ProfesorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rut'].widget.attrs.update({'name': 'rut', 'placeholder': 'Ej. 12.345.678-K'})

    class Meta:
        model = Profesor
        fields = '__all__'

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if rut:
            # Validar el formato del RUT (aceptar puntos y guion)
            if not re.match(r'^\d{1,2}(\.\d{3}){2}-[\dK]$', rut.upper()):
                raise forms.ValidationError('El RUT debe contener solo números, puntos y guion en el formato 11.111.111-K.')

            # Llamar a la función de validación
            validar_rut(rut.replace('.', '').replace('-', ''))
        return rut

class ResponderConsultaForm(forms.Form):
    asunto =  forms.CharField(max_length=100, label='Asunto')
    respuesta = forms.CharField(widget=forms.Textarea,label='Respuesta')































