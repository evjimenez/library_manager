from flask import render_template, request, redirect, url_for, flash, session
import json
from config import mysql
from config import app
from models.loan import Loan
from models.student import Student
from models.book import Book
from controllers.validation import validate_loan_days

@app.route('/loans')
def list_loans():
    loans = Loan.get_all()
    return render_template('loans/list.html', loans=loans)

@app.route('/loans/create', methods=['GET', 'POST'])
def create_loan():
    if request.method == 'POST':
        id_student = request.form['id_student']
        print(id_student)
        # Verificar si tiene mora pendiente
        late_fee = Student.get_late_fee(id_student)
        if late_fee > 0:
            flash(f"No se puede realizar el préstamo. El estudiante tiene una mora pendiente de ${late_fee:.2f}", 'error')
            return redirect(url_for('create_loan'))

        loan_days = int(request.form['loan_days'])
        books = json.loads(request.form['selected_books'])
        
        success, result = Loan.create(id_student, loan_days, books)
        
        if success:
            loan_id = result
            flash("Préstamo creado con éxito", 'success')
            return redirect(url_for('loan_preview', loan_id=loan_id))
        else:
            flash(f"Error al crear el préstamo: {result}", 'error')
            return redirect(url_for('create_loan'))
    
    students = Student.get_all()
    return render_template('loans/create.html', students=students)

@app.route('/loans/preview/<int:loan_id>')
def loan_preview(loan_id):
    loan = Loan.get_by_id(loan_id)
    if not loan:
        flash('Préstamo no encontrado', 'error')
        return redirect(url_for('list_loans'))
    
    student = Student.get_by_id(loan[1])
    books = Loan.get_books_for_loan(loan_id)
    
    # Obtener información del empleado que registró el préstamo
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT e.first_name, e.last_name 
            FROM employees e 
            JOIN loans l ON e.id_employee = l.id_employee 
            WHERE l.id_loan = %s
        """, (loan_id,))
        employee = cur.fetchone()
        employee_name = f"{employee[0]} {employee[1]}" if employee else "No registrado"
    finally:
        cur.close()
    
    return render_template('loans/preview.html', 
                         loan=loan, 
                         student=student, 
                         books=books,
                         employee_name=employee_name)

@app.route('/loans/edit/<int:id>', methods=['GET', 'POST'])
def edit_loan(id):
    loan = Loan.get_by_id(id)
    if request.method == 'POST':
        return_date = request.form['return_date']
        renewals = int(request.form['renewals'])
        late_fee = float(request.form['late_fee'])

        
        Loan.update(id, return_date, renewals, late_fee)
        flash('Pretamos editado', 'success')
        return redirect(url_for('list_loans'))
    
    return render_template('loans/edit.html', loan=loan)

@app.route('/loans/delete/<int:id>')
def delete_loan(id):
    success, message = Loan.delete(id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('list_loans'))