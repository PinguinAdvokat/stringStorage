"""
Конфигурация приложения String Storage API
"""

import os
from typing import Dict, Any


class Config:
    """Базовый класс конфигурации"""
    
    # Настройки Flask
    DEBUG = True
    TESTING = False
    
    # Настройки сервера
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Настройки базы данных
    DATABASE_PATH = 'strings.db'
    
    # Настройки логирования
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """
        Возвращает словарь с конфигурацией
        
        Returns:
            Dict с параметрами конфигурации
        """
        return {
            'debug': cls.DEBUG,
            'testing': cls.TESTING,
            'host': cls.HOST,
            'port': cls.PORT,
            'database_path': cls.DATABASE_PATH,
            'log_level': cls.LOG_LEVEL,
            'log_format': cls.LOG_FORMAT
        }


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    
    DEBUG = True
    DATABASE_PATH = 'dev_strings.db'
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Конфигурация для production"""
    
    DEBUG = False
    HOST = '127.0.0.1'  # Более безопасный хост для production
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'prod_strings.db')
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Конфигурация для тестирования"""
    
    TESTING = True
    DEBUG = True
    DATABASE_PATH = ':memory:'  # Использование в памяти для тестов
    LOG_LEVEL = 'DEBUG'


# Словарь доступных конфигураций
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """
    Получение конфигурации по имени
    
    Args:
        config_name: Имя конфигурации ('development', 'production', 'testing')
        
    Returns:
        Класс конфигурации
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    return config_map.get(config_name, DevelopmentConfig)