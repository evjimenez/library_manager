from config import mysql
from datetime import date
from models.loan import Loan
from models.book import Book
from models.student import Student
import logging

class Returns:
    @staticmethod
    def calculate_days_late(expected_date, actual_date):
        if actual_date > expected_date:
            return (actual_date - expected_date).days
        return 0

    @staticmethod
    def update_book_inventory(id_loan, books_to_return):
        cur = mysql.connection.cursor()
        try:
            for book_id in books_to_return:
                Book.increase_quantity(book_id)
            return len(books_to_return)
        finally:
            cur.close()


    @staticmethod
    def create(id_loan, books_to_return, late_fee=0.00):
        cur = mysql.connection.cursor()
        try:
            # Obtener información del préstamo
            cur.execute("SELECT id_student, return_date FROM loans WHERE id_loan = %s", (id_loan,))
            loan_info = cur.fetchone()
            if not loan_info:
                return False, "Préstamo no encontrado."

            id_student, expected_return_date = loan_info
            actual_return_date = date.today()

            # Calcular días de retraso
            days_late = Returns.calculate_days_late(expected_return_date, actual_return_date)
            late_fee = days_late * 0.50  # $0.50 por día

            # Si hay retraso, actualizar la mora del estudiante
            if days_late > 0:
                cur.execute("""
                    UPDATE students 
                    SET late_fee = late_fee + %s 
                    WHERE id_student = %s
                """, (late_fee, id_student))

            # Registrar la devolución
            cur.execute("""
                INSERT INTO returns (id_loan, return_date, days_late, late_fee)
                VALUES (%s, %s, %s, %s)
            """, (id_loan, actual_return_date, days_late, late_fee))
            id_return = cur.lastrowid

            # Actualizar el inventario y registrar los libros devueltos
            for book_id, quantity_returned in books_to_return:
                # Obtener la cantidad prestada originalmente
                cur.execute("SELECT quantity FROM loan_books WHERE id_loan = %s AND id_book = %s", (id_loan, book_id))
                quantity_borrowed = cur.fetchone()[0]

                if quantity_returned > quantity_borrowed:
                    raise ValueError(f"No se pueden devolver más libros ({quantity_returned}) que los prestados ({quantity_borrowed}) para el libro ID {book_id}")

                # Actualizar la cantidad en loan_books
                new_quantity = quantity_borrowed - quantity_returned
                if new_quantity > 0:
                    cur.execute("""
                        UPDATE loan_books 
                        SET quantity = %s 
                        WHERE id_loan = %s AND id_book = %s
                    """, (new_quantity, id_loan, book_id))
                else:
                    cur.execute("""
                        DELETE FROM loan_books 
                        WHERE id_loan = %s AND id_book = %s
                    """, (id_loan, book_id))

                # Aumentar la cantidad disponible del libro
                Book.increase_quantity(book_id, quantity_returned)

                # Registrar los libros devueltos
                cur.execute("""
                    INSERT INTO returned_books (id_return, id_book, quantity)
                    VALUES (%s, %s, %s)
                """, (id_return, book_id, quantity_returned))

            # Verificar si todos los libros han sido devueltos
            cur.execute("SELECT COUNT(*) FROM loan_books WHERE id_loan = %s", (id_loan,))
            remaining_books = cur.fetchone()[0]

            if remaining_books == 0:
                # Todos los libros han sido devueltos, marcar el préstamo como completado
                cur.execute("UPDATE loans SET status = 'returned' WHERE id_loan = %s", (id_loan,))
                message = "Devolución completa registrada con éxito. El préstamo ha sido marcado como devuelto."
            else:
                message = f"Devolución parcial registrada con éxito. Quedan {remaining_books} libros por devolver."

            # Actualizar el contador de libros prestados del estudiante
            cur.execute("SELECT id_student FROM loans WHERE id_loan = %s", (id_loan,))
            id_student = cur.fetchone()[0]
            Student.decrement_borrowed_books_multiple(id_student, sum(quantity for _, quantity in books_to_return))

            mysql.connection.commit()
            mensaje_mora = f" Días de retraso: {days_late}. Mora generada: ${late_fee:.2f}" if days_late > 0 else ""
            return True, f"Devolución registrada exitosamente.{mensaje_mora}"
        except Exception as e:
            mysql.connection.rollback()
            return False, f"Error al registrar la devolución: {str(e)}"
        finally:
            cur.close()

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                SELECT r.*, l.id_loan, l.id_student, s.name, s.lastname,
                    GROUP_CONCAT(DISTINCT b.title SEPARATOR ', ') as returned_books,
                    CASE 
                        WHEN l.status = 'returned' THEN 'Completa'
                        ELSE 'Parcial'
                    END as return_status
                FROM returns r
                JOIN loans l ON r.id_loan = l.id_loan
                JOIN students s ON l.id_student = s.id_student
                JOIN returned_books rb ON r.id_return = rb.id_return
                JOIN books b ON rb.id_book = b.id_book
                GROUP BY r.id_return
                ORDER BY r.return_date DESC
            """)
            returns = cur.fetchall()
            print(f"Devoluciones recuperadas: {returns}")  # Depuración
            return returns
        except Exception as e:
            print(f"Error al obtener las devoluciones: {e}")
            return []
        finally:
            cur.close()