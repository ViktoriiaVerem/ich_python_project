import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()


class Settings:
    """
    Класс настроек приложения, загружает параметры из переменных окружения.
    """
    # Настройки MongoDB (для логов и статистики)
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
    MONGO_COLLECTION_NAME = os.getenv('MONGO_COLLECTION_NAME')

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
    def get_mongo_connection_string(cls) -> str:
        """
        Вернуть строку подключения к MongoDB из переменной окружения.
        :return: str
        """
        return cls.MONGO_URI

    @classmethod
    def get_mysql_config(cls) -> dict:
        """
        Получить конфиг для подключения к MySQL.
        :return: dict
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