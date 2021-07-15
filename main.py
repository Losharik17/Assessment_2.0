from app import current_app, db
from app.models import User


@current_app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

# для виртуальной среды
# C:\Users\tanku\PycharmProjects\pythonProject\venv\Scripts\python.exe C:\Users\tanku\PycharmProjects\pythonProject\venv\Lib\site-packages\pip\_internal\utils\virtualenv.py venv
# venv\Scripts\activate
# set FLASK_APP=main.py
