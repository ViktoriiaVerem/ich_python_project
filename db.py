import pymysql
from pymongo import MongoClient
from settings import settings
from datetime import datetime
import json
from logger import logger

# Глобальные переменные для кэширования соединений
_mongo_client = None
_mongo_db = None
_mysql_connection = None


def initialize_mongo():
    """
    Инициализация соединения с MongoDB для логов и статистики с кэшированием.
    """
    global _mongo_client, _mongo_db
    if _mongo_client is not None and _mongo_db is not None:
        try:
            _mongo_client.admin.command('ping')
            return _mongo_db
        except Exception:
            _mongo_client = None
            _mongo_db = None
    # Создаём новое соединение
    connection_string = settings.get_mongo_connection_string()
    _mongo_client = MongoClient(connection_string)
    _mongo_db = _mongo_client[settings.MONGO_DB_NAME]
    return _mongo_db


def initialize_mysql():
    """
    Инициализация соединения с MySQL для фильмов с кэшированием.
    """
    global _mysql_connection
    if _mysql_connection is not None:
        try:
            _mysql_connection.ping(reconnect=True)
            return _mysql_connection
        except Exception:
            _mysql_connection = None
    config = settings.get_mysql_config()
    _mysql_connection = pymysql.connect(**config)
    return _mysql_connection


def close_all_connections():
    """
    Закрыть все соединения с базами данных и очистить кэш.
    """
    global _mongo_client, _mongo_db, _mysql_connection
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
    if _mysql_connection:
        _mysql_connection.close()
        _mysql_connection = None

# =====================================================
# ФУНКЦИИ ДЛЯ MONGODB (Логи и статистика)
# =====================================================

def log_search_query(query, search_type, results_count):
    """
    Логировать поисковый запрос в MongoDB для сбора статистики.
    
    Args:
        query (str): Поисковый текст запроса
        search_type (str): Тип поиска (ключевое слово, жанр_год)
        results_count (int): Количество найденных результатов
    """
    try:
        mongo_db = initialize_mongo()
        collection = mongo_db[settings.MONGO_COLLECTION_NAME]
        
        log_entry = {
            'query': query,
            'search_type': search_type,
            'timestamp': datetime.utcnow(),
            'results_count': results_count
        }
        
        collection.insert_one(log_entry)
        
    except Exception as e:
        print(f"Ошибка при логировании запроса: {e}")
        logger.error(f"Ошибка при логировании запроса: {e}")

def get_popular_queries(limit=5):
    """
    Получить самые популярные поисковые запросы из MongoDB.
    
    Args:
        limit (int): Максимальное количество запросов для возврата
    
    Returns:
        list: Список популярных запросов с количеством
    """
    try:
        mongo_db = initialize_mongo()
        collection = mongo_db[settings.MONGO_COLLECTION_NAME]
        
        # Конвейер агрегации для подсчета запросов по тексту
        pipeline = [
            {
                '$group': {
                    '_id': '$query',
                    'count': {'$sum': 1},
                    'search_type': {'$first': '$search_type'},
                    'last_searched': {'$max': '$timestamp'}
                }
            },
            {
                '$sort': {'count': -1}
            },
            {
                '$limit': limit
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        return results
        
    except Exception as e:
        print(f"Ошибка при получении популярных запросов: {e}")
        logger.error(f"Ошибка при получении популярных запросов: {e}")
        return []

def get_recent_queries(limit=5):
    """
    Получить последние поисковые запросы из MongoDB.
    
    Args:
        limit (int): Максимальное количество запросов для возврата
    
    Returns:
        list: Список последних запросов
    """
    try:
        mongo_db = initialize_mongo()
        collection = mongo_db[settings.MONGO_COLLECTION_NAME]
        
        results = list(collection.find()
                      .sort('timestamp', -1)
                      .limit(limit))
        return results
        
    except Exception as e:
        print(f"Ошибка при получении последних запросов: {e}")
        logger.error(f"Ошибка при получении последних запросов: {e}")
        return []

# =====================================================
# ФУНКЦИИ ДЛЯ MYSQL (Данные о фильмах)
# =====================================================

def find_films_by_keyword(keyword, limit=10, skip=0):
    """
    Найти фильмы по ключевому слову в MySQL.
    
    Args:
        keyword (str): Ключевое слово для поиска
        limit (int): Максимальное количество результатов
        skip (int): Количество результатов для пропуска (для пагинации)
    
    Returns:
        list: Список словарей с фильмами
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        sql = (
            """
            SELECT title, description
            FROM film_text
            WHERE title LIKE %s
            LIMIT %s OFFSET %s
            """
        )
        
        search_pattern = f"%{keyword}%"
        cursor.execute(sql, (search_pattern, limit, skip))
        
        results = cursor.fetchall()
        cursor.close()
        
        # Логируем поиск
        log_search_query(keyword, 'keyword', len(results))
        
        return results
        
    except Exception as e:
        print(f"Ошибка поиска фильмов по ключевому слову '{keyword}': {e}")
        logger.error(f"Ошибка поиска фильмов по ключевому слову '{keyword}': {e}")
        return []

def find_films_by_criteria(genre=None, year_from=None, year_to=None, limit=10, skip=0):
    """
    Найти фильмы по жанру и/или диапазону годов в MySQL.
    
    Args:
        genre (str): Жанр фильма для поиска
        year_from (int): Минимальный год
        year_to (int): Максимальный год
        limit (int): Максимальное количество результатов
        skip (int): Количество результатов для пропуска (для пагинации)
    
    Returns:
        list: Список словарей с фильмами
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        if genre and year_from and year_to:
            # найти фильмы по жанру и диапазону годов
            sql = (
                """
                SELECT f.title, f.release_year, c.name AS genre
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE c.name = %s AND f.release_year BETWEEN %s AND %s
                LIMIT %s OFFSET %s
                """
            )
            cursor.execute(sql, (genre, year_from, year_to, limit, skip))
            
        elif genre:
            # найти первые 10 фильмов по жанру (например 'Comedy')
            sql = (
                """
                SELECT f.title, f.release_year, c.name AS genre
                FROM film f
                JOIN film_category fc ON f.film_id = fc.film_id
                JOIN category c ON fc.category_id = c.category_id
                WHERE c.name = %s
                LIMIT %s OFFSET %s
                """
            )
            cursor.execute(sql, (genre, limit, skip))
            
        elif year_from and year_to:
            # найти первые 10 фильмов по диапазону годов (например 2005-2012)
            sql = (
                """
                SELECT title, release_year
                FROM film
                WHERE release_year BETWEEN %s AND %s
                LIMIT %s OFFSET %s
                """
            )
            cursor.execute(sql, (year_from, year_to, limit, skip))
            
        else:
            # если никаких критериев не указано, возвращаем пустой результат
            return []
        
        results = cursor.fetchall()
        cursor.close()
        
        # Логируем поиск
        search_criteria = f"genre:{genre}, years:{year_from}-{year_to}"
        log_search_query(search_criteria, 'genre_year', len(results))
        
        return results
        
    except Exception as e:
        print(f"Ошибка поиска фильмов по критериям: {e}")
        logger.error(f"Ошибка поиска фильмов по критериям: {e}")
        return []

def get_all_genres():
    """
    Получить все уникальные жанры из таблицы MySQL.
    
    Returns:
        list: Список уникальных жанров
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor()
        
        # вывести все категории
        sql = """
        SELECT name AS genre
        FROM category
        """
        cursor.execute(sql)
        
        results = cursor.fetchall()
        cursor.close()
        
        # Извлекаем названия жанров из кортежей
        genres = [row[0] for row in results]
        return genres
        
    except Exception as e:
        print(f"Ошибка получения жанров: {e}")
        logger.error(f"Ошибка получения жанров: {e}")
        return []

def get_year_range():
    """
    Получить минимальный и максимальный год из таблицы фильмов MySQL.
    
    Returns:
        dict: Словарь с 'min_year' и 'max_year'
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor()
        
        # вывести мин и мах года выпуска фильма
        sql = """
        SELECT MIN(release_year) AS min_year, MAX(release_year) AS max_year
        FROM film
        """
        cursor.execute(sql)
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                'min_year': result[0],
                'max_year': result[1]
            }
        else:
            return {'min_year': None, 'max_year': None}
            
    except Exception as e:
        print(f"Ошибка получения диапазона лет: {e}")
        logger.error(f"Ошибка получения диапазона лет: {e}")
        return {'min_year': None, 'max_year': None}

def find_film_by_key(key: str):
    """
    Найти фильм по ключу (ID или названию) в MySQL.
    
    Args:
        key (str): Ключ фильма для поиска.
    
    Returns:
        dict: Документ фильма если найден, иначе None.
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Сначала пытаемся найти по ID, затем по названию
        sql = "SELECT * FROM films WHERE id = %s OR title = %s LIMIT 1"
        cursor.execute(sql, (key, key))
        
        result = cursor.fetchone()
        cursor.close()
        
        return result
        
    except Exception as e:
        print(f"Ошибка поиска фильма по ключу '{key}': {e}")
        logger.error(f"Ошибка поиска фильма по ключу '{key}': {e}")
        return None

def find_films_by_first_letter(letter, limit=20, skip=0):
    """
    Найти фильмы, название которых начинается с заданной буквы.
    """
    try:
        connection = initialize_mysql()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        sql = (
            """
            SELECT title, description
            FROM film_text
            WHERE title LIKE %s
            LIMIT %s OFFSET %s
            """
        )
        search_pattern = f"{letter.upper()}%"
        cursor.execute(sql, (search_pattern, limit, skip))
        results = cursor.fetchall()
        cursor.close()
        return results
    except Exception as e:
        print(f"Ошибка поиска фильмов по первой букве: {e}")
        logger.error(f"Ошибка поиска фильмов по первой букве: {e}")
        return []

# Синоним для обратной совместимости
close_db_connection = close_all_connections

