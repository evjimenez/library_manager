from config import mysql
from flask import session
import hashlib

class Employee:
    @staticmethod
    def create(code, first_name, last_name, national_id, address, phone_number, birthdate, email, password, role='librarian'):
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO employees (
                    code, first_name, last_name, national_id, address, 
                    phone_number, birthdate, email, password, role
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (code, first_name, last_name, national_id, address, phone_number, 
                  birthdate, email, password, role))
            
            mysql.connection.commit()
            return True, "Empleado creado exitosamente"
        except Exception as e:
            return False, str(e)
        finally:
            cur.close()

    @staticmethod
    def authenticate(email, password):
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                SELECT id_employee, first_name, last_name, email, password, role, code
                FROM employees 
                WHERE email = %s AND password = %s AND is_active = TRUE
            """, (email, password))
            
            employee = cur.fetchone()
            
            if employee:
                # Guardar en sesión
                session['employee_id'] = employee[0]
                session['employee_name'] = f"{employee[1]} {employee[2]}"
                session['role'] = employee[5]
                session['employee_code'] = employee[6]
                return True, "Login exitoso"
            
            return False, "Credenciales inválidas"
        except Exception as e:
            print(f"Error en autenticación: {str(e)}")
            return False, str(e)
        finally:
            cur.close()

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT * FROM employees WHERE is_active = TRUE ORDER BY id_employee DESC")
            return cur.fetchall()
        finally:
            cur.close()

    @staticmethod
    def get_by_id(id_employee):
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT * FROM employees WHERE id_employee = %s", (id_employee,))
            return cur.fetchone()
        finally:
            cur.close()

    @staticmethod
    def update(id_employee, first_name, last_name, national_id, address, phone_number, birthdate, email, role):
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                UPDATE employees 
                SET first_name = %s, last_name = %s, national_id = %s, 
                    address = %s, phone_number = %s, birthdate = %s, 
                    email = %s, role = %s
                WHERE id_employee = %s
            """, (first_name, last_name, national_id, address, phone_number, 
                  birthdate, email, role, id_employee))
            mysql.connection.commit()
            return True, "Empleado actualizado exitosamente"
        except Exception as e:
            return False, str(e)
        finally:
            cur.close()

    @staticmethod
    def delete(id_employee):
        cur = mysql.connection.cursor()
        try:
            # Soft delete
            cur.execute("UPDATE employees SET is_active = FALSE WHERE id_employee = %s", (id_employee,))
            mysql.connection.commit()
            return True, "Empleado eliminado exitosamente"
        except Exception as e:
            return False, str(e)
        finally:
            cur.close()

    @staticmethod
    def is_authenticated():
        return 'employee_id' in session

    @staticmethod
    def is_manager():
        return session.get('role') == 'manager'
    
    @staticmethod
    def generate_employee_code(first_name, last_name, birthdate):
        from datetime import datetime
        
        # Obtener las iniciales del nombre
        name_initial = first_name[0].upper() if first_name else 'X'
        
        # Obtener las iniciales de los apellidos
        last_initials = ''.join([word[0].upper() for word in last_name.split()])
        
        # Convertir la fecha de string a datetime si es necesario
        if isinstance(birthdate, str):
            birth_date = datetime.strptime(birthdate, '%Y-%m-%d')
        else:
            birth_date = birthdate
            
        # Obtener el año y mes de nacimiento
        birth_year = str(birth_date.year)[-2:]  # Últimos 2 dígitos del año
        birth_month = str(birth_date.month).zfill(2)  # Mes con 2 dígitos
        
        # Construir el código base
        base_code = f"{name_initial}{last_initials}{birth_month}{birth_year}"
        
        # Asegurar que el código no exista
        cur = mysql.connection.cursor()
        counter = 1
        final_code = base_code
        
        while True:
            cur.execute("SELECT COUNT(*) FROM employees WHERE code = %s", (final_code,))
            if cur.fetchone()[0] == 0:
                cur.close()
                return final_code
            # Si existe, agregar un número secuencial
            final_code = f"{base_code}{counter}"
            counter += 1