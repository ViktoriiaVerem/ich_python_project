# Модуль пользовательского интерфейса (UI)
from prettytable import PrettyTable

menu = {
    "1": "Поиск по ключевому слову",
    "2": "Поиск по жанру и диапазону годов",
    "3": "Посмотреть популярные запросы",
    "4": "Поиск по первой букве названия",
    "9": "Выход"
}


def show_menu():
    """
    Выводит главное меню для пользователя.
    Перечисляет все доступные действия.
    """
    print("\nВыберите действие:")
    for key, value in menu.items():
        print(f"{key}. {value}")


def get_menu_choice():
    """
    Запрашивает у пользователя выбор пункта меню.
    Проверяет корректность ввода.
    Возвращает выбранный пункт как строку.
    """
    while True:
        choice = input("\nВведите номер действия: ").strip()
        if choice in menu:
            return choice
        print("Неверный ввод. Попробуйте снова.")


def get_search_keyword():
    """
    Запрашивает у пользователя ключевое слово для поиска фильмов.
    Не допускает пустой ввод.
    Возвращает строку-ключевое слово.
    """
    keyword = input("Введите ключевое слово для поиска: ").strip()
    if not keyword:
        print("Ключевое слово не может быть пустым!")
        return get_search_keyword()
    return keyword


def get_genre_and_year_range():
    """
    Запрашивает у пользователя жанр и диапазон годов для поиска фильмов.
    Возвращает словарь с ключами 'genre', 'year_from', 'year_to'.
    """
    print("\nПоиск по жанру и диапазону годов:")
    genre = input("Введите жанр (или нажмите Enter для пропуска): ").strip()
    year_from = input("Введите начальный год (или нажмите Enter для пропуска): ").strip()
    year_to = input("Введите конечный год (или нажмите Enter для пропуска): ").strip()

    # Валидация годов
    year_from = _parse_year(year_from, "начальный")
    year_to = _parse_year(year_to, "конечный")

    return {
        'genre': genre if genre else None,
        'year_from': year_from,
        'year_to': year_to
    }


def _parse_year(year_str, label):
    """
    Преобразует строку в число (год).
    Если ввод некорректен — возвращает None и выводит предупреждение.
    """
    if year_str:
        try:
            return int(year_str)
        except ValueError:
            print(f"Неверный {label} год. Используется значение по умолчанию.")
    return None


def display_film(film):
    """
    Выводит подробную информацию об одном фильме.
    Если фильм не найден — сообщает об этом.
    """
    if not film:
        print("Фильм не найден.")
        return
    print("\n" + "=" * 50)
    print(f"Название: {film.get('title', 'Не указано')}")
    print(f"Год: {film.get('year', 'Не указан')}")
    print(f"Жанр: {film.get('genre', 'Не указан')}")
    print(f"Рейтинг: {film.get('rating', 'Не указан')}")
    print(f"Описание: {film.get('description', 'Не указано')}")
    print("=" * 50)


def display_films(films):
    """
    Выводит список фильмов в виде таблицы.
    Если фильмов нет — сообщает об этом.
    """
    if not films:
        print("\nФильмы не найдены.")
        return
    print(f"\nНайдено {len(films)} фильм(ов):")
    table = PrettyTable()
    # Определяем заголовки по ключам первого фильма
    headers = []
    if films:
        sample = films[0]
        # Для совместимости с разными структурами
        if 'title' in sample and 'description' in sample:
            headers = ['№', 'Название', 'Описание']
        elif 'title' in sample and 'release_year' in sample and 'genre' in sample:
            headers = ['№', 'Название', 'Год', 'Жанр']
        else:
            headers = ['№'] + list(sample.keys())
    table.field_names = headers
    for i, film in enumerate(films, 1):
        if 'title' in film and 'description' in film:
            table.add_row([i, film.get('title', 'Не указано'), film.get('description', 'Не указано')])
        elif 'title' in film and 'release_year' in film and 'genre' in film:
            table.add_row([i, film.get('title', 'Не указано'), film.get('release_year', 'Не указан'), film.get('genre', 'Не указан')])
        else:
            table.add_row([i] + [film.get(k, 'Не указано') for k in film.keys()])
    print(table)


def display_popular_queries():
    """
    Выводит популярные и последние поисковые запросы из MongoDB в виде таблицы.
    Если данных нет — сообщает об этом.
    """
    from db import get_popular_queries, get_recent_queries
    print("\n" + "=" * 60)
    print("СТАТИСТИКА ПОИСКОВЫХ ЗАПРОСОВ")
    print("=" * 60)
    print("\nТоп-5 популярных запросов:")
    popular = get_popular_queries(5)
    if popular:
        table = PrettyTable()
        table.field_names = ["№", "Запрос", "Тип", "Кол-во", "Последний поиск"]
        for i, query in enumerate(popular, 1):
            last = query.get('last_searched')
            last_str = last.strftime('%Y-%m-%d %H:%M') if last else '-'
            table.add_row([
                i,
                query.get('_id', '-'),
                query.get('search_type', '-'),
                query.get('count', 0),
                last_str
            ])
        print(table)
    else:
        print("   Нет данных о популярных запросах")
    print("\nПоследние 5 запросов:")
    recent = get_recent_queries(5)
    if recent:
        table = PrettyTable()
        table.field_names = ["№", "Запрос", "Тип", "Результатов", "Время"]
        for i, query in enumerate(recent, 1):
            ts = query.get('timestamp')
            ts_str = ts.strftime('%Y-%m-%d %H:%M') if ts else '-'
            table.add_row([
                i,
                query.get('query', '-'),
                query.get('search_type', '-'),
                query.get('results_count', 0),
                ts_str
            ])
        print(table)
    else:
        print("   Нет данных о последних запросах")
    print("=" * 60)
    input("\nНажмите Enter для продолжения...")


def show_exit_message():
    """
    Выводит сообщение о завершении работы приложения.
    """
    print("\nЗакрытие соединения с базой данных...")
    print("До свидания!")


def ask_continue():
    """
    Спрашивает пользователя, хочет ли он продолжить просмотр результатов.
    Возвращает True, если пользователь согласен, иначе False.
    """
    choice = input("\nПоказать больше результатов? (y/n): ")

    return choice in ['y', 'yes', 'да', 'д']


def get_first_letter():
    """
    Запрашивает у пользователя первую букву для поиска фильмов по названию.
    Проверяет, что введена одна английская буква.
    Возвращает букву в верхнем регистре.
    """
    while True:
        letter = input("Введите первую букву (A-Z): ").strip().upper()
        if len(letter) == 1 and letter.isalpha():
            return letter
        print("Введите одну английскую букву!")
