import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基本配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///data_value_assessment.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 最大上传限制

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 在生产环境中使用更安全的设置
    SECRET_KEY = os.environ.get('SECRET_KEY')  # 必须在环境变量中设置

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'