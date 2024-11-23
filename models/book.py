from config import mysql
from datetime import date
import random, datetime, string

class Book:
    def __init__(self, title, author, materia, code, acquisition_date, status, quantity):
        self.title = title
        self.code = code
        self.author = author
        self.materia = materia
        self.acquisition_date = acquisition_date
        self.status = status
        self.quantity = quantity
        self.stock = quantity

    '''@staticmethod
    def create(title, author, materia, code, acquisition_date, quantity, status='AVAILABLE'):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO books (title, author, materia, code, acquisition_date, quantity, stock, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                    (title, author, materia, code, acquisition_date, quantity, quantity, status))
        mysql.connection.commit()
        cur.close()'''

    @staticmethod
    def create(title, author, materia, code, acquisition_date, quantity, status='AVAILABLE'):
        # creando book_id para generar el codigo automatico en la consulta -- Victor Orellana
        code = Book.generate_book_id(title.upper())
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO books (title, author, materia, code, acquisition_date, quantity, stock, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (title, author, materia, code, acquisition_date, quantity, quantity, status))
        mysql.connection.commit()
        book_id = cur.lastrowid  # Obtén el ID del último libro insertado
        cur.close()
        return book_id


    # se ha cambiado la logica para iniciar el libro en caso de que se inicie con un numero -- Victor Orellana
    @staticmethod
    def generate_book_id(bookname):
        # Crear variable para manejar la fecha
        current_date = datetime.datetime.now()

        # Obtener año, mes y día
        year_two_digit = str(current_date.year)[-2:]
        month_two_digit = current_date.strftime("%m")
        day_one_digit = current_date.day

        # Obtener las iniciales del libro, omitiendo números si el libro comienza con uno
        words = bookname.split()
        initials_book_ = ''

        for word in words:
            if word[0].isalpha():  # Solo tomamos la inicial si la palabra empieza con una letra
                initials_book_ += word[0].upper()

            if len(initials_book_) >= 2:  # Solo tomamos las primeras dos iniciales
                break

        # Si no hay suficientes iniciales alfabéticas, tomamos los primeros caracteres alfabéticos disponibles
        if not initials_book_:
            initials_book_ = ''.join(c.upper() for c in bookname if c.isalpha())[:2]

        # Conectar a la base de datos
        cur = mysql.connection.cursor()

        # Generar el código único para el libro
        while True:
            # Generar 3 dígitos aleatorios
            random_digits = ''.join(random.choices(string.digits, k=3))

            # Crear el código con las iniciales, los dígitos aleatorios y la fecha
            code = f"{initials_book_}{random_digits}{day_one_digit}{month_two_digit}{year_two_digit}"

            # Verificar si el código ya existe en la base de datos
            cur.execute("SELECT COUNT(1) FROM books WHERE id_book = %s", (code,))
            if cur.fetchone()[0] == 0:
                cur.close()
                return code
            #hasta aca se ha modificado el ingreso de titulo de libro -- Victor Orellana

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM books")
        books = cur.fetchall()
        cur.close()
        return books

    @staticmethod
    def get_by_id(id_book):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM books WHERE id_book = %s", (id_book,))
        book = cur.fetchone()
        cur.close()
        return book

    @staticmethod
    def update(id_book, title, author, materia, code, acquisition_date, status, quantity):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE books SET title = %s, author = %s, materia = %s, code = %s, acquisition_date = %s, quantity = %s, status = %s  WHERE id_book = %s",
                    (title, author, materia, code, acquisition_date, quantity, status, id_book))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def is_borrowed(id_book):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) 
            FROM loan_books lb
            JOIN loans l ON lb.id_loan = l.id_loan
            WHERE lb.id_book = %s AND l.return_date >= %s
        """, (id_book, date.today()))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0

    @staticmethod
    def delete(id_book):
        if Book.is_borrowed(id_book):
            return False, "No se puede eliminar un libro que está prestado."
        
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM books WHERE id_book = %s", (id_book,))
        mysql.connection.commit()
        cur.close()
        return True, "Libro eliminado con éxito."
    
 # se ha modificado el archivado de libros -- Victor Orellana
    @staticmethod
    def archive(id_book):
     cur = mysql.connection.cursor()

    # Verificar si el libro tiene la misma cantidad de stock que la cantidad disponible
     cur.execute("SELECT stock, quantity FROM books WHERE id_book = %s", (id_book,))
     result = cur.fetchone()
    
     if not result:
        cur.close()
        return False, "El libro no existe en la base de datos."
    
     stock, quantity = result

     # Si la cantidad total (stock) no es igual a la cantidad disponible (quantity), no se puede archivar
     if stock != quantity:
        cur.close()
        return False, "No puedes archivar un libro que tiene un préstamo vigente."

    # Verificar si el libro está prestado actualmente (tiene préstamos no devueltos)
     cur.execute("""
        SELECT COUNT(*)
        FROM loan_books lb
        JOIN loans l ON lb.id_loan = l.id_loan
        WHERE lb.id_book = %s AND (l.return_date IS NULL OR l.return_date >= %s)
    """, (id_book, date.today()))
    
     count = cur.fetchone()[0]

    # Si hay préstamos activos, no se puede archivar el libro
     if count > 0:
        cur.close()
        return False, "No se puede archivar un libro que tiene un préstamo vigente."

    # Si no hay préstamos activos, proceder a archivar el libro
     cur.execute("UPDATE books SET status = 'OBSOLETO' WHERE id_book = %s", (id_book,))
     mysql.connection.commit()
     cur.close()
 
     return True, "Libro archivado exitosamente."
    
    #recuperar libro -- Victor Orellana
    
    @staticmethod
    def recover(id_book):
        cur = mysql.connection.cursor()
        
        # Verificar el estado del libro
        cur.execute("SELECT status FROM books WHERE id_book = %s", (id_book,))
        status = cur.fetchone()[0]
        
        # Verificar si hay libros prestados
        cur.execute("""
            SELECT SUM(quantity) 
            FROM loan_books 
            WHERE id_book = %s AND return_date >= %s
        """, (id_book, date.today()))
        quantity_borrowed = cur.fetchone()[0] or 0
        
        if status == 'DISPONIBLE' or quantity_borrowed > 0:
            cur.close()
            return False, "No se puede recuperar un libro obsoleto"
        
        cur.execute("UPDATE books SET status = 'DISPONIBLE' WHERE id_book = %s", (id_book,))
        mysql.connection.commit()
        cur.close()
        return True, "Libro recuperado exitosamente."
    # hasta aca es el metodo de recuperar libro -- Victor Orellana
   
    @staticmethod
    def get_available():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM books WHERE quantity > 0")
        available_books = cur.fetchall()
        cur.close()
        return available_books
    
    @staticmethod
    def get_total_stock(id_book):
        cur = mysql.connection.cursor()
        cur.execute("SELECT stock FROM books WHERE id_book = %s", (id_book,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else 0 
    
    @staticmethod
    def get_available_books(id_book):
        cur = mysql.connection.cursor()
        cur.execute("SELECT quantity FROM books WHERE quantity > 0 and id_book = %s", (id_book,))
        available_books = cur.fetchone()
        cur.close()
        return available_books[0] if available_books else 0
    
    @staticmethod
    def get_total_borrowed(id_book):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT lb.quantity
            FROM loan_books lb
            INNER JOIN books b ON lb.id_book = b.id_book
            WHERE b.id_book = %s
        """, (id_book,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else 0

    @staticmethod
    def decrease_quantity(id_book):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id_book = %s AND quantity > 0", (id_book,))
        affected_rows = cur.rowcount
        mysql.connection.commit()
        cur.close()
        return affected_rows > 0

    @staticmethod
    def increase_quantity(id_book, quantity=1):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE books SET quantity = quantity + %s WHERE id_book = %s", (quantity, id_book))
        mysql.connection.commit()
        cur.close()