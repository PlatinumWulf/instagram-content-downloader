#!/usr/bin/env python3
"""
Moduł konfiguracji logowania - Instagram Content Downloader
Konfiguruje logowanie do pliku i konsoli
"""

import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    max_size: int = 10485760,  # 10 MB
    backup_count: int = 5,
    console: bool = True
) -> logging.Logger:
    """
    Konfiguruje system logowania

    Args:
        log_level: Poziom logowania (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ścieżka do pliku logu (None = tylko konsola)
        max_size: Maksymalny rozmiar pliku logu (bajty)
        backup_count: Liczba backupów pliku logu
        console: Czy logować również do konsoli

    Returns:
        Skonfigurowany logger
    """
    # Pobierz poziom logowania
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Stwórz główny logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Usuń istniejące handlery (żeby nie duplikować)
    logger.handlers = []

    # Format logów
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler do pliku (z rotacją)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Handler do konsoli
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Tylko ostrzeżenia i błędy do konsoli

        # Prostszy format dla konsoli
        console_formatter = logging.Formatter(
            fmt='%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


def setup_logging_from_env() -> logging.Logger:
    """
    Konfiguruje logowanie na podstawie zmiennych środowiskowych

    Używa zmiennych:
    - LOG_LEVEL (domyślnie: INFO)
    - LOG_FILE (domyślnie: logs/instagram_downloader.log)
    - LOG_MAX_SIZE (domyślnie: 10485760 = 10MB)
    - LOG_BACKUP_COUNT (domyślnie: 5)

    Returns:
        Skonfigurowany logger
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'logs/instagram_downloader.log')
    max_size = int(os.getenv('LOG_MAX_SIZE', '10485760'))
    backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))

    return setup_logging(
        log_level=log_level,
        log_file=log_file if log_file else None,
        max_size=max_size,
        backup_count=backup_count,
        console=True
    )
