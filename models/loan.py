from config import mysql
from datetime import datetime, timedelta
from models.book import Book
from models.student import Student
import logging

class Loan:
    def __init__(self, id_student, loan_date, return_date, loan_days, renewals=0, late_fee=0.00):
        self.id_student = id_student
        self.loan_date = loan_date
        self.return_date = return_date
        self.loan_days = loan_days
        self.renewals = renewals
        self.late_fee = late_fee

    @staticmethod
    def create(id_student, loan_days, books):
        logging.info(f"Creating loan: student={id_student}, days={loan_days}, books={books}")
        
        # Validar que el estudiante existe
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_student FROM students WHERE id_student = %s", (id_student,))
        if not cur.fetchone():
            return False, "Estudiante no encontrado"
        
        # Validar que la lista de libros no esté vacía
        if not books:
            return False, "No se han seleccionado libros"
        
        # Validar la estructura de cada libro
        for book in books:
            if not isinstance(book, dict) or 'id' not in book or 'quantity' not in book:
                return False, "Formato de libros inválido"
        
        try:
            loan_date = datetime.now().date()
            return_date = loan_date + timedelta(days=loan_days)
            
            # Verificar si el estudiante ya tiene el máximo de libros prestados
            current_loans = Student.get_borrowed_books_count(id_student)
            total_books = sum(book['quantity'] for book in books)
            logging.info(f"prestamo actual: {current_loans}, Total libros nuevos: {total_books}")
            
            if current_loans + total_books > 3:
                logging.warning("maximo 3")
                return False, "El estudiante no puede prestar más de 3 libros en total."

            # Insertar el nuevo préstamo
            cur.execute("INSERT INTO loans (id_student, loan_date, return_date, loan_days) VALUES (%s, %s, %s, %s)",
                        (id_student, loan_date, return_date, loan_days))
            id_loan = cur.lastrowid
            
            # Asociar cada libro al préstamo
            for book in books:
                book_id = book['id']
                quantity = book['quantity']
                
                # Verificar disponibilidad
                cur.execute("SELECT quantity FROM books WHERE id_book = %s", (book_id,))
                result = cur.fetchone()
                if not result:
                    raise Exception(f"Libro con ID {book_id} no encontrado")
                    
                available = result[0]
                if available < quantity:
                    raise Exception(f"No hay suficientes copias disponibles del libro con ID {book_id}")

                # Insertar en loan_books
                cur.execute("INSERT INTO loan_books (id_loan, id_book, quantity, return_date) VALUES (%s, %s, %s, %s)",
                            (id_loan, book_id, quantity, return_date))
                
                # Actualizar cantidad del libro
                cur.execute("UPDATE books SET quantity = quantity - %s WHERE id_book = %s", (quantity, book_id))

            # Incrementar libros prestados del estudiante
            Student.increment_borrowed_books(id_student, total_books)

            mysql.connection.commit()
            return True, id_loan
        
        except Exception as e:
            mysql.connection.rollback()
            logging.error(f"Error en create_loan: {str(e)}")
            return False, str(e)
        finally:
            cur.close()

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                SELECT l.*, s.name, s.lastname, 
                    GROUP_CONCAT(DISTINCT b.title SEPARATOR ', ') as books,
                    CASE 
                        WHEN l.status = 'returned' THEN 'Devuelto'
                        ELSE 'Activo'
                    END as loan_status
                FROM loans l
                JOIN students s ON l.id_student = s.id_student
                LEFT JOIN loan_books lb ON l.id_loan = lb.id_loan
                LEFT JOIN books b ON lb.id_book = b.id_book
                GROUP BY l.id_loan
                ORDER BY l.loan_date DESC
            """)
            loans = cur.fetchall()
            return loans
        except Exception as e:
            print(f"Error al obtener los préstamos: {e}")
            return []
        finally:
            cur.close()
            
    @staticmethod
    def get_active_loans():
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                SELECT l.*, s.name, s.lastname, 
                    GROUP_CONCAT(DISTINCT b.title SEPARATOR ', ') as books,
                    SUM(lb.quantity) as total_borrowed,
                    COALESCE(SUM(rb.quantity), 0) as total_returned
                FROM loans l
                JOIN students s ON l.id_student = s.id_student
                JOIN loan_books lb ON l.id_loan = lb.id_loan
                JOIN books b ON lb.id_book = b.id_book
                LEFT JOIN returns r ON l.id_loan = r.id_loan
                LEFT JOIN returned_books rb ON r.id_return = rb.id_return AND rb.id_book = lb.id_book
                GROUP BY l.id_loan
                HAVING total_borrowed > total_returned
                ORDER BY l.loan_date DESC
            """)
            active_loans = cur.fetchall()
            return active_loans
        finally:
            cur.close()

    @staticmethod
    def get_by_id(id_loan):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM loans WHERE id_loan = %s", (id_loan,))
        loan = cur.fetchone()
        cur.close()
        return loan

    @staticmethod
    def get_books_for_loan(id_loan):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT b.id_book, b.title, lb.return_date, lb.quantity
            FROM loan_books lb
            JOIN books b ON lb.id_book = b.id_book
            WHERE lb.id_loan = %s AND lb.quantity > 0
        """, (id_loan,))
        books = cur.fetchall()
        cur.close()
        return [{'id_book': book[0], 'title': book[1], 'return_date': book[2], 'quantity': book[3]} for book in books]
    
    @staticmethod
    def update(id_loan, return_date, renewals, late_fee):
        #todo: autoincrementar las renovaciones, calcular la fecha de devolucion
        cur = mysql.connection.cursor()
        cur.execute("UPDATE loans SET return_date = %s, renewals = %s, late_fee = %s WHERE id_loan = %s",
                    (return_date, renewals, late_fee, id_loan))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def delete(id_loan):
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_book FROM loan_books WHERE id_loan = %s", (id_loan,))
        book_ids = [row[0] for row in cur.fetchall()]
        
        for book_id in book_ids:
            Book.increase_quantity(book_id)
        
        cur.execute("DELETE FROM loan_books WHERE id_loan = %s", (id_loan,))
        cur.execute("DELETE FROM loans WHERE id_loan = %s", (id_loan,))
        mysql.connection.commit()
        cur.close()