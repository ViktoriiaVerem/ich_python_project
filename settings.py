import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()


class Settings:
    """
    Класс настроек приложения, загружает параметры из переменных окружения.
    """
    # Настройки MongoDB (для логов и статистики)
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'film_logs')
    MONGO_USERNAME = os.getenv('MONGO_USERNAME', '')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '')

    # Настройки MySQL (для фильмов)
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    MYSQL_DB_NAME = os.getenv('MYSQL_DB_NAME', 'films_database')
    MYSQL_USERNAME = os.getenv('MYSQL_USERNAME', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')

    # Прочие настройки приложения
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

    @classmethod
    def get_mongo_connection_string(cls):
        """
        Сформировать строку подключения к MongoDB на основе настроек.
        """
        if cls.MONGO_USERNAME and cls.MONGO_PASSWORD:
            return f'mongodb://{cls.MONGO_USERNAME}:{cls.MONGO_PASSWORD}@{cls.MONGO_HOST}:{cls.MONGO_PORT}/'
        return f'mongodb://{cls.MONGO_HOST}:{cls.MONGO_PORT}/'

    @classmethod
    def get_mysql_config(cls):
        """
        Получить конфиг для подключения к MySQL.
        """
        return {
            'host': cls.MYSQL_HOST,
            'port': cls.MYSQL_PORT,
            'user': cls.MYSQL_USERNAME,
            'password': cls.MYSQL_PASSWORD,
            'database': cls.MYSQL_DB_NAME,
            'charset': 'utf8mb4',
            'autocommit': True
        }

# Экземпляр настроек
settings = Settings()