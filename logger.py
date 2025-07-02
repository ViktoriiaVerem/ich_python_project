import logging
import os

# Создание директории для логов, если её нет
os.makedirs('logs', exist_ok=True)

# Настройка логгера
logger = logging.getLogger('project_logger')
logger.setLevel(logging.ERROR)

# Обработчик для записи ошибок в файл logs/log.fail
file_handler = logging.FileHandler('logs/log.fail', encoding='utf-8')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)
