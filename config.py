import os


basedir = os.path.abspath(os.path.dirname(__file__))

class ConfigPG(object):
    # ...
    # connect route to your database here
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:1234@localhost:5432/test'
        # set up postgresql database first then input the required parameter in "{}"
        # postgresql://{user name}:{password}@{url}:{port}/{db name}
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = 'd9874b1c9d7d19b255c72a8096ecbd331f6885e9'



    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))  # Use 587 for TLS
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEBUG = True  # Enable debugging for Flask-Mail

    AZURE_CONNECTION_STRING = os.environ.get('AZURE_CONNECTION_STRING')
    CONTAINER_NAME = os.environ.get('CONTAINER_NAME')
    AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME')
    AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY')

    print(f"MAIL_SERVER: {MAIL_SERVER}, MAIL_PORT: {MAIL_PORT}, MAIL_USE_TLS: {MAIL_USE_TLS}, MAIL_USE_SSL: {MAIL_USE_SSL}, MAIL_USERNAME: {MAIL_USERNAME}")
    print(f"AZURE_CONNECTION_STRING: {AZURE_CONNECTION_STRING}")


# not usable for current backend version.
class ConfigSL(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'api.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'd9874b1c9d7d19b255c72a8096ecbd331f6885e9'

class TestingConfig(ConfigSL):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:1234@localhost:5647/test2'
    TESTING = True
class StagingConfig(ConfigSL):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'staging_api.db')


app_config = {
    'testing': TestingConfig,
    'staging': StagingConfig,
    'defaultPG': ConfigPG,
    'defaultSL': ConfigSL
}
