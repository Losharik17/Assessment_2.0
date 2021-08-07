from app import create_app, db
from app.models import User, Expert, Grade


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Expert': Expert, 'Grade': Grade}

# для виртуальной среды
# C:\Users\tanku\AppData\Local\Programs\Python\Python37\python.exe C:\Users\tanku\AppData\Local\Programs\Python\Python37\Lib\site-packages\pip\_internal\utils\virtualenv.py venv
# venv\Scripts\activate
# set FLASK_APP=main.py
