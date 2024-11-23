import logging
from config import mysql
import datetime
import random
import string

class Student:
    def __init__(self, name, lastname, student_id, grade, section):
        self.name = name
        self.lastname = lastname
        self.student_id = student_id
        self.grade = grade
        self.section = section

    @staticmethod
    def generate_student_id(lastname):
        current_year = datetime.datetime.now().year
        year_suffix = str(current_year)[-2:]
        
        # Obtener las iniciales de todos los apellidos (lastname)
        initials = ''.join([word[0].upper() for word in lastname.split()])
        initials = initials.ljust(2, 'X')[:2]  # Asegurar que tengamos 2 caracteres, rellenando con 'X' si es necesario
        
        cur = mysql.connection.cursor()
        while True:
            # Generar 4 dígitos aleatorios
            random_digits = ''.join(random.choices(string.digits, k=4))
            
            # Construir el student_id
            student_id = f"{initials}{random_digits}{year_suffix}"
            
            # Verificar si ya existe
            cur.execute("SELECT COUNT(*) FROM students WHERE student_id = %s", (student_id,))
            if cur.fetchone()[0] == 0:
                cur.close()
                return student_id
            
    @staticmethod
    def create(name, lastname, grade, section):
        student_id = Student.generate_student_id(lastname)
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO students (name, lastname, student_id, grade, section)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, lastname, student_id, grade, section))
            mysql.connection.commit()
            return True, "Estudiante creado con éxito.", student_id
        except Exception as e:
            mysql.connection.rollback()
            return False, f"Error al crear el estudiante: {str(e)}", None
        finally:
            cur.close()


    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                SELECT id_student, name, lastname, student_id, 
                       grade, section, books_borrowed,
                       COALESCE(late_fee, 0) as late_fee 
                FROM students
            """)
            students = cur.fetchall()
            return students
        finally:
            cur.close()
            
    @staticmethod
    def get_by_id(id_student):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE id_student = %s", (id_student,))
        student = cur.fetchone()
        cur.close()
        print(student)
        return student

    @staticmethod
    def update(id_student, name, lastname, student_id, grade, section):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET name = %s, lastname = %s, student_id = %s, grade = %s, section = %s WHERE id_student = %s",
                    (name, lastname, student_id, grade, section, id_student))
        mysql.connection.commit()
        cur.close()

    def delete(id_student):
        """
        Intenta eliminar un estudiante. Si tiene préstamos, no permite la eliminación.
        """
        if Student.has_loans(id_student):
            return False, "No se puede eliminar el estudiante porque tiene préstamos registrados."
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("DELETE FROM students WHERE id_student = %s", (id_student,))
            mysql.connection.commit()
            return True, "Estudiante eliminado."
        except Exception as e:
            mysql.connection.rollback()
            return False, f"Error al eliminar el estudiante: {str(e)}"
        finally:
            cur.close()


    #funciones para obtener la cantidad de libros prestamos por alumno

    @staticmethod
    def increment_borrowed_books(id_student, num_books):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET books_borrowed = books_borrowed + %s WHERE id_student = %s", (num_books, id_student))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def decrement_borrowed_books(id_student):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET books_borrowed = books_borrowed - 1 WHERE id_student = %s", (id_student,))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def decrement_borrowed_books_multiple(id_student, books_returned):
        """
        Disminuye el número de libros prestados de un estudiante por la cantidad especificada.
        """
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE students 
            SET books_borrowed = books_borrowed - %s 
            WHERE id_student = %s
        """, (books_returned, id_student))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_borrowed_books_count(id_student):
        cur = mysql.connection.cursor()
        cur.execute("SELECT books_borrowed FROM students WHERE id_student = %s", (id_student,))
        count = cur.fetchone()[0]
        cur.close()
        return count
    
    #metodo para validar si tiene historico de prestamos

    @staticmethod
    def has_loans(id_student):
        """
        Verifica si un estudiante tiene préstamos (históricos o activos).
        """
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM loans WHERE id_student = %s", (id_student,))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0
    

    @staticmethod
    def has_late_fee(id_student):
        """Verifica si el estudiante tiene mora pendiente"""
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT late_fee FROM students WHERE id_student = %s", (id_student,))
            result = cur.fetchone()
            if result is None:
                return False
            return result[0] is not None and float(result[0]) > 0
        except Exception as e:
            logging.error(f"Error verificando mora: {str(e)}")
            return False
        finally:
            cur.close()

    @staticmethod
    def get_late_fee(id_student):
        """Obtiene el monto de la mora del estudiante"""
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT COALESCE(late_fee, 0) FROM students WHERE id_student = %s", (id_student,))
            result = cur.fetchone()
            return float(result[0]) if result else 0.0
        finally:
            cur.close()        

    @staticmethod
    def clear_late_fee(id_student):
        """Limpia la mora del estudiante"""
        cur = mysql.connection.cursor()
        try:
            cur.execute("UPDATE students SET late_fee = 0 WHERE id_student = %s", (id_student,))
            mysql.connection.commit()
            return True, "Mora limpiada exitosamente"
        except Exception as e:
            mysql.connection.rollback()
            return False, f"Error al limpiar la mora: {str(e)}"
        finally:
            cur.close()