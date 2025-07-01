# Модуль пользовательского интерфейса (UI)

menu = {
    "1": "Поиск по ключевому слову",
    "2": "Поиск по жанру и диапазону годов",
    "3": "Посмотреть популярные запросы",
    "9": "Выход"
}


def show_menu():
    """Вывести главное меню пользователю."""
    print("\nВыберите действие:")
    for key, value in menu.items():
        print(f"{key}. {value}")


def get_menu_choice():
    """Получить выбор пользователя из меню с валидацией."""
    while True:
        choice = input("\nВведите номер действия: ").strip()
        if choice in menu:
            return choice
        print("Неверный ввод. Попробуйте снова.")


def get_search_keyword():
    """Запросить у пользователя ключевое слово для поиска."""
    keyword = input("Введите ключевое слово для поиска: ").strip()
    if not keyword:
        print("Ключевое слово не может быть пустым!")
        return get_search_keyword()
    return keyword


def get_genre_and_year_range():
    """Запросить у пользователя жанр и диапазон годов для поиска."""
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
    """Преобразовать строку года в int, если возможно."""
    if year_str:
        try:
            return int(year_str)
        except ValueError:
            print(f"Неверный {label} год. Используется значение по умолчанию.")
    return None


def display_film(film):
    """Вывести информацию об одном фильме."""
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
    """Вывести список фильмов."""
    if not films:
        print("\nФильмы не найдены.")
        return
    print(f"\nНайдено {len(films)} фильм(ов):")
    for i, film in enumerate(films, 1):
        print(f"\n{i}. {film.get('title', 'Не указано')} ({film.get('year', 'Не указан')})")
        print(f"   Жанр: {film.get('genre', 'Не указан')}")
        print(f"   Рейтинг: {film.get('rating', 'Не указан')}")


def display_popular_queries():
    """Вывести популярные и последние поисковые запросы из MongoDB."""
    from db import get_popular_queries, get_recent_queries
    print("\n" + "=" * 60)
    print("СТАТИСТИКА ПОИСКОВЫХ ЗАПРОСОВ")
    print("=" * 60)
    # Популярные запросы
    print("\nТоп-5 популярных запросов:")
    popular = get_popular_queries(5)
    if popular:
        for i, query in enumerate(popular, 1):
            print(f"{i}. '{query['_id']}' - {query['count']} раз(а)")
            print(f"   Тип: {query['search_type']}, Последний поиск: {query['last_searched'].strftime('%Y-%m-%d %H:%M')}")
    else:
        print("   Нет данных о популярных запросах")
    # Последние запросы
    print("\nПоследние 5 запросов:")
    recent = get_recent_queries(5)
    if recent:
        for i, query in enumerate(recent, 1):
            print(f"{i}. '{query['query']}' - {query['timestamp'].strftime('%Y-%m-%d %H:%M')}")
            print(f"   Тип: {query['search_type']}, Результатов: {query['results_count']}")
    else:
        print("   Нет данных о последних запросах")
    print("=" * 60)
    input("\nНажмите Enter для продолжения...")


def show_exit_message():
    """Вывести сообщение о завершении работы."""
    print("\nЗакрытие соединения с базой данных...")
    print("До свидания!")


def ask_continue():
    """Спросить пользователя, хочет ли он продолжить просмотр результатов."""
    choice = input("\nПоказать больше результатов? (y/n): ").strip().lower()
    return choice in ['y', 'yes', 'да', 'д']
