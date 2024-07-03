import re
from django.core.exceptions import ValidationError

def validar_rut(value):
    # Eliminar puntos y guion del RUT
    rut = value.replace('.', '').replace('-', '')
    # Extraer el dígito verificador
    dv = rut[-1].upper()
    # Extraer el cuerpo del RUT
    rut = rut[:-1]
    
    # Validar el formato del RUT
    if not re.match(r'^\d+$', rut):
        raise ValidationError('El RUT debe contener solo números, puntos y guion.')

    # Calcular el dígito verificador
    reverse_rut = rut[::-1]
    factors = [2, 3, 4, 5, 6, 7]
    total = 0
    for i, digit in enumerate(reverse_rut):
        total += int(digit) * factors[i % 6]
    remainder = 11 - (total % 11)
    calculated_dv = '0' if remainder == 11 else 'K' if remainder == 10 else str(remainder)
    
    # Validar el dígito verificador
    if dv != calculated_dv:
        raise ValidationError('El RUT ingresado no es válido213123123.')
