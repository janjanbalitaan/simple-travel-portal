from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.utilities.environment import Environment
from app.utilities.configuration import Configuration

env = Environment.__instance__()

app = Flask(__name__, static_url_path=env.get['APP_STATIC_URL'], static_folder=env.get['APP_STATIC'])
app.config.from_object(Configuration)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import api, utilities, models
from app.models.user import User

User.create_user(email="admin@company.com", role=1, password=User.generate_password('p@ssw0rd'), status=1, first_name='Juan', last_name='Dela Cruz', uid=User.generate_uid())
User.create_user(email="finance_manager@company.com", role=2, password=User.generate_password('p@ssw0rd'), status=1, first_name='Jemployee', last_name='Marcos', uid=User.generate_uid())
User.create_user(email="manager@company.com", role=3, password=User.generate_password('p@ssw0rd'), status=1, first_name='Manaroger', last_name='Sison', uid=User.generate_uid())
User.create_user(email="employee@company.com", role=4, password=User.generate_password('p@ssw0rd'), status=1, first_name='Josefinance', last_name='Quezon', uid=User.generate_uid())

