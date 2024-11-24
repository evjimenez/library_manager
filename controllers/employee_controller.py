from flask import render_template, request, redirect, url_for, flash
from config import app
from models.employee import Employee
from controllers.auth_controller import manager_required
from controllers.validation import validate_name, validate_lastname, validate_phone, validate_email, validate_birthdate

@app.route('/employees')
@manager_required
def list_employees():
    employees = Employee.get_all()
    return render_template('employees/list.html', employees=employees)

@app.route('/employees/create', methods=['GET', 'POST'])
@manager_required
def create_employee():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        national_id = request.form.get('national_id')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        birthdate = request.form.get('birthdate')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # Validaciones
        is_valid, message = validate_name(first_name)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_employee'))

        is_valid, message = validate_lastname(last_name)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_employee'))

        is_valid, message = validate_phone(phone_number)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_employee'))
        
        is_valid, message = validate_birthdate(birthdate)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_employee'))

        is_valid, message = validate_email(email)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_employee'))

        # Generar código único para el empleado
        code = Employee.generate_employee_code(first_name, last_name, birthdate)

        success, message = Employee.create(code, first_name, last_name, national_id, 
                                        address, phone_number, birthdate, email, password, role)
        
        if success:
            flash(f"{message} Código del empleado: {code}", 'success')
            return redirect(url_for('list_employees'))
        else:
            flash(message, 'error')

    return render_template('employees/create.html')

@app.route('/employees/edit/<int:id>', methods=['GET', 'POST'])
@manager_required
def edit_employee(id):
    employee = Employee.get_by_id(id)
    if not employee:
        flash('Empleado no encontrado.', 'error')
        return redirect(url_for('list_employees'))

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        national_id = request.form.get('national_id')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        birthdate = request.form.get('birthdate')
        email = request.form.get('email')
        role = request.form.get('role')

        success, message = Employee.update(id, first_name, last_name, national_id, 
                                        address, phone_number, birthdate, email, role)
        if success:
            flash('Empleado actualizado con éxito', 'success')
            return redirect(url_for('list_employees'))
        else:
            flash(message, 'error')

    return render_template('employees/edit.html', employee=employee)

@app.route('/employees/delete/<int:id>')
@manager_required
def delete_employee(id):
    success, message = Employee.delete(id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('list_employees'))