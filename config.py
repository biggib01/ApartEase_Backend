import os


basedir = os.path.abspath(os.path.dirname(__file__))

class ConfigPG(object):
    # ...
    # connect route to your database here
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        ''
        # set up postgresql database first then input the required parameter in "{}"
        # postgresql://{user name}:{password}@{url}:{port}/{db name}
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = 'd9874b1c9d7d19b255c72a8096ecbd331f6885e9'

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
        'sqlite:///' + os.path.join(basedir, 'test_api.db')
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
