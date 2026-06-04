import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('DEBUG', False) == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # AI Model selection
    AI_MODEL = os.getenv('AI_MODEL', 'openai')  # 'openai' or 'gemini'
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///chatbot.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Voice Configuration
    ENABLE_VOICE = os.getenv('ENABLE_VOICE', 'True') == 'True'
    VOICE_RATE = int(os.getenv('VOICE_RATE', 150))
    
    # Server Configuration
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Chat Configuration
    MAX_CHAT_HISTORY = 50
    MAX_MESSAGE_LENGTH = 1000
    
    # OpenAI Model
    OPENAI_MODEL = 'gpt-3.5-turbo'
    OPENAI_TEMPERATURE = 0.7
    MAX_TOKENS = 500

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///test_chatbot.db'
    OPENAI_API_KEY = 'test-key'
    GEMINI_API_KEY = 'test-key'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
