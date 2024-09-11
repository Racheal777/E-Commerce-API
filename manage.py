from flask_migrate import Migrate
from flask_script import Manager
from src import create_app, db

app = create_app()
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db')

if __name__ == '__main__':
    manager.run()