import re

#A partir de aqui son validaciones para el formulario LIBROS
def validate_title(title):
    if len(title) > 150:
        return False, "El límite de título es de 150 caracteres."
    if not title or not re.match(r'^[A-Za-záéíóúÁÉÍÓÚÑñ\w\s]+$', title):
        return False, 'El título es obligatorio y no puede contener caracteres especiales.'
    return True, ''

def validate_author(author):
    if len(author) > 50:
        return False, "El límite del autor es de 50 caracteres."
    if not author or not re.match(r'^[A-Za-záéíóúÁÉÍÓÚÑñ\s]+$', author):
        return False, 'El autor es obligatorio y no puede contener numeros ni caracter especial'
    return True, ''

def validate_materia(materia):
    if len(materia) > 20:
        return False, "El límite de materia es de 20 caracteres."
    if not materia or not re.match(r'^[A-Za-záéíóúÁÉÍÓÚÑñ\w\s]+$', materia):
        return False, 'La materia es obligatoria y no puede contener números ni caracteres especiales.'
    return True, ''
# aumento el code a 15 para quitar la validacion al editar libro -- Victor Orellana
def validate_code(code):
    if len(code) >= 15:
        return False, "El limite de codigo es de 10 digitos"
    if not code or not re.match(r'^[\w\s]+$', code):
        return False, 'El código es obligatorio.'
    return True, ''

#todo: esto se puede hacer en html
def validate_acquisition_date(acquisition_date):
    if not acquisition_date:
        return False, 'La fecha de ingreso es obligatoria'
    return True,''

def validate_quantity(quantity):
    try:
        quantity = int(quantity)
        return True, quantity
    except ValueError:
        return False, 'La cantidad debe ser un número entero.'
    
    #A partir de aqui son validaciones para el formulario ESTUDIANTE
def validate_name(name):
    if len(name) > 50:
        return False, 'El limite de nombre es de 50 caracteres'
    if not name or not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚÑñ\s]+$', name):
        return False, 'El nombre no puede contener numeros ni caracteres especiales'
    return True, ''

def validate_lastname(lastname):
    if len(lastname) > 50:
        return False, 'El limite de nombre es de 50 caracteres'
    if not lastname or not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚÑñ\s]+$', lastname):
        return False, 'El nombre no puede contener numeros ni caracteres especiales'
    return True, ''

#todo: esta validacion no debe ir, el código debe ser automatico
def validate_student_id(student_id):
    if len(student_id) > 10:
        return False, 'El limite de codigo es de 10 digitos'
    if not student_id or not re.match(r'^[\w\s]+$', student_id):
        return False, 'El Codigo estudiante es obligatorio y no puede contener caracteres especiales'
    return True, ''

def validate_grade(grade):
    if len(grade) > 20:
        return False, 'El limite de grado es de 20 digitos'
    if not grade or not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚÑñ\s]+$', grade):
        return False, 'El grado es obligatorio y no puede contener numero ni caracter especial'
    return True, ''

def validate_section(section):
    if len(section) > 10:
        return False, 'el limite de seccion es de 10 digitos'
    if not section or not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚÑñ\s]+$', section):
        return False, 'La seccion es obligatorio y no puede contener numero ni caracter especial'
    return True, ''

#aqui vamos a validar el fprmulario prestamo.

def validate_loan_days(loan_days):
    try:
        loan_days = int(loan_days)
        return True, loan_days
    except ValueError:
        return False, 'La cantidad debe ser un número entero.'
    

# Nuevas validaciones para empleados
def validate_national_id(national_id):
    if len(national_id) != 10:
        return False, "El DUI debe tener 10 dígitos."
    if not national_id or not re.match(r'^\d{8}-?\d$', national_id):
        return False, 'El formato del DUI no es válido'
    return True, ''

def validate_phone(phone):
    if len(phone) > 15:
        return False, "El número de teléfono no puede exceder 15 caracteres."
    if not phone or not re.match(r'^[0-9-+\s]+$', phone):
        return False, 'El formato del teléfono no es válido'
    return True, ''

def validate_age(age):
    try:
        age = int(age)
        if age < 18 or age > 100:
            return False, 'La edad debe estar entre 18 y 100 años'
        return True, age
    except ValueError:
        return False, 'La edad debe ser un número entero'

def validate_email(email):
    if len(email) > 100:
        return False, "El correo no puede exceder 100 caracteres."
    if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return False, 'El formato del correo electrónico no es válido'
    return True, ''

def validate_address(address):
    if len(address) > 150:
        return False, "La dirección no puede exceder 150 caracteres."
    if not address or not address.strip():
        return False, 'La dirección es obligatoria'
    return True, ''

def validate_password(password):
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    if len(password) > 50:
        return False, "La contraseña no puede exceder 50 caracteres"
    if not password or not re.match(r'^[\w@#$%^&+=]+$', password):
        return False, 'La contraseña contiene caracteres no permitidos'
    return True, ''    