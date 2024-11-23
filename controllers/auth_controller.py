from flask import render_template, request, redirect, url_for, flash, session
from config import app
from models.employee import Employee
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not Employee.is_authenticated():
            flash('Por favor inicie sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not Employee.is_authenticated() or not Employee.is_manager():
            flash('No tiene permisos para acceder a esta página', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        success, message = Employee.authenticate(email, password)
        if success:
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash(message, 'error')
    return render_template('auth/login.html')  # Cambié la ruta aquí

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

# Ejemplo de ruta protegida para managers
@app.route('/admin/dashboard')
@manager_required
def admin_dashboard():
    return render_template('admin/dashboard.html')