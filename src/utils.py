#!/usr/bin/env python3
"""
Moduł funkcji pomocniczych - Instagram Content Downloader
Zawiera funkcje walidacji, formatowania i inne narzędzia
"""

import re
import os
import time
import logging
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def validate_username(username: str) -> str:
    """
    Waliduje nazwę użytkownika Instagram

    Instagram usernames:
    - Długość: 1-30 znaków
    - Dozwolone znaki: a-z, A-Z, 0-9, _, .
    - Nie może zaczynać się od kropki
    - Nie może kończyć się kropką

    Args:
        username: Nazwa użytkownika do walidacji

    Returns:
        Zwalidowana nazwa użytkownika (lowercase)

    Raises:
        ValueError: Jeśli nazwa użytkownika jest nieprawidłowa
    """
    if not username:
        raise ValueError("Nazwa użytkownika nie może być pusta")

    # Usuń białe znaki
    username = username.strip()

    # Sprawdź długość
    if len(username) < 1 or len(username) > 30:
        raise ValueError(f"Nazwa użytkownika musi mieć 1-30 znaków (podano: {len(username)})")

    # Sprawdź dozwolone znaki
    if not re.match(r'^[a-zA-Z0-9._]+$', username):
        raise ValueError(
            f"Nazwa użytkownika zawiera niedozwolone znaki: '{username}'\n"
            "Dozwolone: a-z, A-Z, 0-9, _, ."
        )

    # Sprawdź czy nie zaczyna/kończy się kropką
    if username.startswith('.'):
        raise ValueError("Nazwa użytkownika nie może zaczynać się od kropki")
    if username.endswith('.'):
        raise ValueError("Nazwa użytkownika nie może kończyć się kropką")

    # Instagram usernames są case-insensitive
    return username.lower()


def extract_username_from_url(url: str) -> str:
    """
    Wyciąga nazwę użytkownika z URL Instagram

    Obsługiwane formaty:
    - https://www.instagram.com/username/
    - https://instagram.com/username
    - instagram.com/username/
    - @username
    - username

    Args:
        url: URL lub nazwa użytkownika

    Returns:
        Nazwa użytkownika

    Raises:
        ValueError: Jeśli nie można wyciągnąć nazwy użytkownika
    """
    # Usuń białe znaki
    url = url.strip()

    # Przypadek 1: Już jest nazwą użytkownika (bez http//@)
    if not url.startswith('http') and not url.startswith('@') and '/' not in url:
        return validate_username(url)

    # Przypadek 2: Zaczyna się od @
    if url.startswith('@'):
        return validate_username(url[1:])

    # Przypadek 3: Pełny URL
    if url.startswith('http'):
        parsed = urlparse(url)
        path = parsed.path.strip('/')

        # instagram.com/username/ → username
        # instagram.com/username/tagged/ → username
        if path:
            parts = path.split('/')
            if parts:
                return validate_username(parts[0])

    # Przypadek 4: URL bez http (instagram.com/username)
    if 'instagram.com' in url:
        parts = url.split('instagram.com/')
        if len(parts) > 1:
            username = parts[1].split('/')[0]
            if username:
                return validate_username(username)

    # Nie udało się wyciągnąć
    raise ValueError(f"Nie można wyciągnąć nazwy użytkownika z: '{url}'")


def format_file_size(size_bytes: int) -> str:
    """
    Formatuje rozmiar pliku do czytelnej postaci

    Args:
        size_bytes: Rozmiar w bajtach

    Returns:
        Sformatowany string (np. "1.5 MB", "230 KB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Upewnia się, że katalog istnieje (tworzy jeśli nie istnieje)

    Args:
        path: Ścieżka do katalogu

    Returns:
        Path object do katalogu

    Raises:
        OSError: Jeśli nie można utworzyć katalogu
    """
    path = Path(path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError as e:
        logger.error(f"Nie można utworzyć katalogu {path}: {e}")
        raise


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Tworzy bezpieczną nazwę pliku (usuwa niedozwolone znaki)

    Args:
        filename: Oryginalna nazwa pliku
        max_length: Maksymalna długość nazwy (domyślnie: 255)

    Returns:
        Bezpieczna nazwa pliku
    """
    # Usuń/zamień niedozwolone znaki
    # Windows: < > : " / \ | ? *
    # Unix: /
    invalid_chars = r'[<>:"/\\|?*]'
    safe_name = re.sub(invalid_chars, '_', filename)

    # Usuń białe znaki z początku/końca
    safe_name = safe_name.strip()

    # Ogranicz długość
    if len(safe_name) > max_length:
        # Zachowaj rozszerzenie pliku
        name, ext = os.path.splitext(safe_name)
        max_name_length = max_length - len(ext)
        safe_name = name[:max_name_length] + ext

    return safe_name


def sleep_with_progress(seconds: int, message: str = "Czekam") -> None:
    """
    Śpi z wyświetlaniem postępu

    Args:
        seconds: Liczba sekund do czekania
        message: Wiadomość do wyświetlenia
    """
    if seconds <= 0:
        return

    try:
        from tqdm import tqdm
        for _ in tqdm(range(seconds), desc=message, unit="s", leave=False):
            time.sleep(1)
    except ImportError:
        # Fallback jeśli tqdm nie jest zainstalowany
        print(f"{message} {seconds}s...", end='', flush=True)
        time.sleep(seconds)
        print(" ✓")


def format_timestamp(timestamp: float) -> str:
    """
    Formatuje timestamp do czytelnej daty

    Args:
        timestamp: Unix timestamp

    Returns:
        Sformatowana data (YYYY-MM-DD HH:MM:SS)
    """
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def calculate_rate_limit_delay(
    error_count: int,
    base_delay: float = 3.0,
    multiplier: float = 1.5,
    max_delay: float = 300.0
) -> float:
    """
    Oblicza opóźnienie dla rate limiting (exponential backoff)

    Args:
        error_count: Liczba kolejnych błędów
        base_delay: Bazowe opóźnienie w sekundach
        multiplier: Mnożnik dla exponential backoff
        max_delay: Maksymalne opóźnienie w sekundach

    Returns:
        Obliczone opóźnienie w sekundach
    """
    delay = base_delay * (multiplier ** error_count)
    return min(delay, max_delay)


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Obcina string do maksymalnej długości z dodaniem suffixu

    Args:
        text: Tekst do obcięcia
        max_length: Maksymalna długość
        suffix: Suffix do dodania (np. "...")

    Returns:
        Obcięty tekst
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def parse_profile_list_file(file_path: Union[str, Path]) -> list[str]:
    """
    Parsuje plik z listą profili

    Format pliku:
    - Jeden profil na linię
    - Linie zaczynające się od # są komentarzami
    - Puste linie są ignorowane

    Args:
        file_path: Ścieżka do pliku z listą profili

    Returns:
        Lista zwalidowanych nazw użytkowników

    Raises:
        FileNotFoundError: Jeśli plik nie istnieje
        ValueError: Jeśli plik jest pusty lub zawiera nieprawidłowe nazwy
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Plik nie istnieje: {file_path}")

    profiles = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # Usuń białe znaki
            line = line.strip()

            # Pomiń puste linie i komentarze
            if not line or line.startswith('#'):
                continue

            # Wyciągnij nazwę użytkownika (obsługuje URL i @)
            try:
                username = extract_username_from_url(line)
                profiles.append(username)
            except ValueError as e:
                logger.warning(f"Linia {line_num}: Pominięto nieprawidłową nazwę: {line} ({e})")

    if not profiles:
        raise ValueError(f"Plik {file_path} nie zawiera żadnych prawidłowych profili")

    return profiles


def get_terminal_width() -> int:
    """
    Pobiera szerokość terminala

    Returns:
        Szerokość terminala (domyślnie: 80)
    """
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def print_separator(char: str = "=", width: Optional[int] = None) -> None:
    """
    Wyświetla separator w terminalu

    Args:
        char: Znak do użycia jako separator
        width: Szerokość (None = szerokość terminala)
    """
    if width is None:
        width = get_terminal_width()
    print(char * width)


def print_header(text: str, char: str = "=") -> None:
    """
    Wyświetla sformatowany nagłówek

    Args:
        text: Tekst nagłówka
        char: Znak do ramki
    """
    width = get_terminal_width()
    print_separator(char, width)
    print(text.center(width))
    print_separator(char, width)
