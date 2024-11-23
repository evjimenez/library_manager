from flask import render_template, request, redirect, url_for, flash
from config import app
from models.student import Student
from flask import jsonify
from config import mysql
from controllers.validation import validate_name, validate_lastname, validate_grade, validate_section

@app.route('/students/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        grade = request.form['grade']
        section = request.form['section']

        #Aqui validamos los campos a partir de validation.py
        is_valid, message = validate_name(name)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_student'))
        
        is_valid, message = validate_lastname(lastname)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_student'))
        
        is_valid, message = validate_grade(grade)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_student'))
        
        is_valid, message = validate_section(section)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_student'))

        success, message, student_id = Student.create(name, lastname, grade, section)
        if success:
            flash(f"{message} Carné del estudiante: {student_id}", 'success')
            return redirect(url_for('list_students'))
        else:
            flash(message, 'error')
    
    return render_template('students/create.html')

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.get_by_id(id)
    if not student:
        flash('Estudiante no encontrado.', 'error')
        return redirect(url_for('list_students'))

    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        student_id = request.form['student_id']
        grade = request.form['grade']
        section = request.form['section']

        fields = {
            'name': name,
            'lastname': lastname,
            'student_id': student_id,
            'grade': grade,
            'section': section,
        }

        for field_name, field_value in fields.items():
            validator = globals().get(f'validate_{field_name}')
            if validator:
                is_valid, message = validator(field_value)
                if not is_valid:
                    flash(message, 'error')
                    return redirect(url_for('edit_student', id=id))

        Student.update(id, name, lastname, student_id, grade, section)
        flash('Alumno editado con éxito', 'success')
        return redirect(url_for('list_students'))

    return render_template('students/edit.html', student=student)

@app.route('/students/delete/<int:id>')
def delete_student(id):
    success, message = Student.delete(id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('list_students'))



#busqueda por alumno

@app.route('/students/search')
def search_students():
    query = request.args.get('query', '')
    print(f"Searching for student: {query}")
    
    cur = mysql.connection.cursor()
    sql_query = """
        SELECT s.id_student, s.name, s.lastname, s.student_id, s.books_borrowed, s.late_fee
        FROM students s
        WHERE s.name LIKE %s OR s.lastname LIKE %s OR s.student_id LIKE %s
        LIMIT 10
    """
    
    search_term = f'%{query}%'
    cur.execute(sql_query, (search_term, search_term, search_term))
    students = cur.fetchall()
    cur.close()
    
    result = [{
        'id': student[0],
        'name': f"{student[1]} {student[2]}",
        'student_id': student[3],
        'books_borrowed': student[4],
        'late_fee': float(student[5]) if student[5] else 0.00
    } for student in students]
    
    return jsonify(result)

@app.route('/students/clear_late_fee/<int:id>')
def clear_student_late_fee(id):
    success, message = Student.clear_late_fee(id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('list_students'))