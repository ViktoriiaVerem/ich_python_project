# Главный модуль приложения
from ui import (
    show_menu, get_menu_choice, get_search_keyword, get_genre_and_year_range,
    display_film, display_films, display_popular_queries, show_exit_message, get_first_letter
)
from db import (
    find_films_by_keyword, find_films_by_criteria,
    close_all_connections, find_films_by_first_letter
)
from settings import settings


def main():
    """
    Основной цикл приложения.
    Управляет меню, обработкой пользовательского ввода и вызовом функций поиска.
    """
    while True:
        show_menu()
        choice = get_menu_choice()

        if choice == "1":
            # Поиск по ключевому слову
            keyword = get_search_keyword()
            films = find_films_by_keyword(keyword)
            display_films(films)

        elif choice == "2":
            # Поиск по жанру и диапазону годов
            criteria = get_genre_and_year_range()
            films = find_films_by_criteria(
                genre=criteria['genre'],
                year_from=criteria['year_from'],
                year_to=criteria['year_to']
            )
            display_films(films)

        elif choice == "3":
            # Просмотр популярных запросов
            display_popular_queries()

        elif choice == "4":
            # Поиск по первой букве
            letter = get_first_letter()
            films = find_films_by_first_letter(letter)
            display_films(films)

        elif choice == "9":
            # Выход
            break

    # Закрытие соединений с БД при выходе
    show_exit_message()
    close_all_connections()


if __name__ == "__main__":
    main()