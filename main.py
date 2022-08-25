from app import create_app, db
from app.models import User, Expert, Grade
from app.main.functions import delete_timer


app = create_app()

#delete_timer()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Expert': Expert, 'Grade': Grade}
