from app.utilities.environment import Environment

class Configuration(object):
    env = Environment.__instance__()
    DEBUG = env.get['APP_DEBUG']
    CSRF_ENABLED = env.get['APP_CSRF_ENABLED']
    SECRET_KEY = env.get['APP_SECRET']

    SQLALCHEMY_DATABASE_URI = '{db_type}+{db_dialect}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'.format(db_type=env.get['DB_TYPE'], db_dialect=env.get['DB_DIALECT'], db_user=env.get['DB_USER'], db_pass=env.get['DB_PASS'], db_host=env.get['DB_HOST'], db_port=env.get['DB_PORT'], db_name=env.get['DB_NAME'])
    SQLALCHEMY_TRACK_MODIFICATIONS = env.get['DB_TRACK_MODIFICATIONS']
