"""
Главный файл приложения String Storage API
"""

import logging
import sys
from flask import Flask
from routes import api_bp
from config import get_config
from database import DatabaseManager


def create_app(config_name: str = None) -> Flask:
    """
    Фабрика приложений Flask
    
    Args:
        config_name: Имя конфигурации
        
    Returns:
        Настроенное Flask приложение
    """
    app = Flask(__name__)
    
    # Загружаем конфигурацию
    config = get_config(config_name)
    
    # Настраиваем логирование
    setup_logging(config.LOG_LEVEL, config.LOG_FORMAT)
    
    # Регистрируем Blueprint с API маршрутами
    app.register_blueprint(api_bp)
    
    # Сохраняем конфигурацию в контексте приложения
    app.config.update(config.get_config_dict())
    
    return app


def setup_logging(log_level: str, log_format: str) -> None:
    """
    Настройка системы логирования
    
    Args:
        log_level: Уровень логирования
        log_format: Формат сообщений
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Неверный уровень логирования: {log_level}')
    
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )


def print_startup_info(config) -> None:
    """
    Вывод информации о запуске приложения
    
    Args:
        config: Объект конфигурации
    """
    print("=" * 50)
    print("String Storage")
    print("=" * 50)
    print(f"База данных: {config.DATABASE_PATH}")
    print(f"Режим отладки: {'Включен' if config.DEBUG else 'Отключен'}")
    print(f"Адрес сервера: http://{config.HOST}:{config.PORT}")


def main():
    """Главная функция для запуска приложения"""
    # Создаем приложение
    app = create_app()
    config = get_config()
    
    # Инициализируем базу данных
    db_manager = DatabaseManager(config.DATABASE_PATH)
    
    # Выводим информацию о запуске
    print_startup_info(config)
    
    # Настраиваем логгер
    logger = logging.getLogger(__name__)
    logger.info("Запуск String Storage API")
    logger.info(f"Конфигурация: {config.__class__.__name__}")
    logger.info(f"База данных: {config.DATABASE_PATH}")
    
    try:
        # Запускаем приложение
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG
        )
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()