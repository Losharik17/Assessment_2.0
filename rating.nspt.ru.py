from app import create_app, db
from app.models import User, Expert, Grade


app = create_app()
app.logger.info('123')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Expert': Expert, 'Grade': Grade}

if __name__ == "__main__":
	app.run(host='0.0.0.0')

