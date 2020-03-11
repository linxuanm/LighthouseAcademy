class BaseConfig:

	SQLALCHEMY_DATABASE_URI = 'sqlite:///lighthouse.db'
	BASE_URL = '0.0.0.0:8000'


class DevelopmentConfig(BaseConfig):

	SQLALCHEMY_ECHO = True
	SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(BaseConfig):

	SQLALCHEMY_TRACK_MODIFICATIONS = False


config = DevelopmentConfig
