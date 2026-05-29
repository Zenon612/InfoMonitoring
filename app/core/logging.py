import logging
import logging.handlers
import os
from pathlib import Path

logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Конфигурация логирования
def setup_logging() -> None:
    """Инициализация логирования для всего приложения."""
    
    # Корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Формат логов
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler для файла (все логи)
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Handler для ошибок в отдельный файл
    error_handler = logging.handlers.RotatingFileHandler(
        "logs/errors.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    root_logger.addHandler(error_handler)
    
    # Console handler (только для WARNING и выше)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
