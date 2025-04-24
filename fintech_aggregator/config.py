
import os

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get(SECRET_KEY, your_secret_key)
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(DATABASE_URL, postgresql://user:password@localhost:5432/fintech_dev)

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(DATABASE_URL_TEST, postgresql://user:password@localhost:5432/fintech_test)

class ProductionConfig(Config):
    """Production configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get(DATABASE_URL, postgresql://user:password@localhost:5432/fintech_prod)

config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

