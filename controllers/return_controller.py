from flask import render_template, request, redirect, url_for, flash, jsonify
from config import app, mysql
from models.returns import Returns
from models.loan import Loan
import logging

@app.route('/returns', methods=['GET'])
def list_returns():
    query = request.args.get('query', '').strip()
    cursor = mysql.connection.cursor()

    if query:
        # Buscar devoluciones relacionadas con el nombre o apellido del estudiante
        cursor.execute("""
            SELECT r.id_return, r.id_loan, s.name, s.lastname,
                   GROUP_CONCAT(b.title SEPARATOR ', ') AS books,
                   r.return_date, r.days_late, r.late_fee
            FROM returns r
            JOIN loans l ON r.id_loan = l.id_loan
            JOIN students s ON l.id_student = s.id_student
            JOIN returned_books rb ON r.id_return = rb.id_return
            JOIN books b ON rb.id_book = b.id_book
            WHERE s.name LIKE %s OR s.lastname LIKE %s
            GROUP BY r.id_return
        """, (f'%{query}%', f'%{query}%'))
        results = cursor.fetchall()
    else:
        # Mostrar una lista vacía si no se realiza una búsqueda
        results = []

    cursor.close()
    return render_template('returns/list.html', returns=results, query=query)

@app.route('/returns/create', methods=['GET', 'POST'])
def create_return():
    if request.method == 'POST':
        # Obtenemos el ID del préstamo (loan) enviado desde el formulario
        id_loan = request.form['id_loan']
        books_to_return = []
        # Iteramos sobre todos los elementos enviados desde el formulario
        for key, value in request.form.items():
            # Verificamos si el campo del formulario se refiere a un libro a devolver
            # 'books_to_return[<book_id>]' y si la cantidad es mayor a 0
            if key.startswith('books_to_return[') and int(value) > 0:
                # Extraemos el 'book_id' del nombre del campo (formato: 'books_to_return[<book_id>]')
                book_id = int(key.split('[')[1].split(']')[0])
                quantity = int(value)
                books_to_return.append((book_id, quantity))
        
        late_fee = float(request.form.get('late_fee', 0))
        
        success, message = Returns.create(id_loan, books_to_return, late_fee)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        
    # Obtener préstamos activos actualizados, tanto para GET como para POST
    active_loans = Loan.get_active_loans()
    return render_template('returns/create.html', loans=active_loans)

@app.route('/returns/get_loan_books/<int:id_loan>')
def get_loan_books(id_loan):
    books = Loan.get_books_for_loan(id_loan)
    return jsonify(books)