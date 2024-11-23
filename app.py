from flask import Flask
from config import app, mysql
from controllers import student_controller, book_controller
import logging

app.secret_key = 'admin' 


if __name__ == '__main__':
    app.run(debug=True)




logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='library_app.log',
                    filemode='a')    