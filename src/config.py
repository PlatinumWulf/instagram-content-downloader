#!/usr/bin/env python3
"""
Moduł zarządzania konfiguracją - Instagram Content Downloader
Obsługuje ładowanie konfiguracji z .env i plików JSON
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Załaduj zmienne środowiskowe z pliku .env
load_dotenv()


class ConfigManager:
    """
    Menedżer konfiguracji aplikacji

    Ładuje ustawienia z:
    1. Pliku .env (zmienne środowiskowe)
    2. Pliku config.json (jeśli istnieje)
    3. Wartości domyślne

    Priorytet: .env > config.json > domyślne
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Inicjalizacja menedżera konfiguracji

        Args:
            config_path: Opcjonalna ścieżka do pliku config.json
        """
        self.config_path = Path(config_path) if config_path else Path("config/config.json")
        self.config = self._load_config()

    def _default_config(self) -> Dict[str, Any]:
        """
        Zwraca domyślną konfigurację aplikacji

        Returns:
            Słownik z domyślnymi ustawieniami
        """
        return {
            # Opcje pobierania mediów
            'download_videos': True,
            'download_thumbnails': True,
            'download_geotags': False,
            'download_comments': False,
            'save_metadata': True,
            'compress_json': False,

            # Opcje połączenia i limitów
            'max_attempts': 3,
            'request_timeout': 300.0,
            'sleep_time': 5,  # WAŻNE: Instagram agresywnie blokuje, używaj ≥5s

            # Typy zawartości do pobrania
            'download_posts': True,
            'download_stories': False,
            'download_highlights': False,
            'download_tagged': False,
            'download_igtv': False,

            # Katalogi
            'download_dir': 'data/downloads',
            'session_dir': 'data/sessions',

            # Rate limiting
            'min_sleep_time': 2,
            'max_sleep_time': 10,
            'rate_limit_backoff_multiplier': 1.5,
        }

    def _load_from_env(self) -> Dict[str, Any]:
        """
        Ładuje konfigurację ze zmiennych środowiskowych (.env)

        Returns:
            Słownik z ustawieniami ze zmiennych środowiskowych
        """
        env_config = {}

        # Funkcja pomocnicza do konwersji wartości boolean
        def get_bool(key: str, default: bool = None) -> Optional[bool]:
            value = os.getenv(key)
            if value is None:
                return default
            return value.lower() in ('true', '1', 'yes', 'tak')

        # Funkcja pomocnicza do konwersji wartości int
        def get_int(key: str, default: int = None) -> Optional[int]:
            value = os.getenv(key)
            if value is None:
                return default
            try:
                return int(value)
            except ValueError:
                return default

        # Funkcja pomocnicza do konwersji wartości float
        def get_float(key: str, default: float = None) -> Optional[float]:
            value = os.getenv(key)
            if value is None:
                return default
            try:
                return float(value)
            except ValueError:
                return default

        # Ładuj ustawienia ze zmiennych środowiskowych
        if get_bool('DOWNLOAD_VIDEOS') is not None:
            env_config['download_videos'] = get_bool('DOWNLOAD_VIDEOS')
        if get_bool('DOWNLOAD_THUMBNAILS') is not None:
            env_config['download_thumbnails'] = get_bool('DOWNLOAD_THUMBNAILS')
        if get_bool('DOWNLOAD_GEOTAGS') is not None:
            env_config['download_geotags'] = get_bool('DOWNLOAD_GEOTAGS')
        if get_bool('DOWNLOAD_COMMENTS') is not None:
            env_config['download_comments'] = get_bool('DOWNLOAD_COMMENTS')
        if get_bool('SAVE_METADATA') is not None:
            env_config['save_metadata'] = get_bool('SAVE_METADATA')
        if get_bool('COMPRESS_JSON') is not None:
            env_config['compress_json'] = get_bool('COMPRESS_JSON')

        if get_int('MAX_ATTEMPTS') is not None:
            env_config['max_attempts'] = get_int('MAX_ATTEMPTS')
        if get_float('REQUEST_TIMEOUT') is not None:
            env_config['request_timeout'] = get_float('REQUEST_TIMEOUT')
        if get_int('SLEEP_TIME') is not None:
            env_config['sleep_time'] = get_int('SLEEP_TIME')

        if get_bool('DOWNLOAD_POSTS') is not None:
            env_config['download_posts'] = get_bool('DOWNLOAD_POSTS')
        if get_bool('DOWNLOAD_STORIES') is not None:
            env_config['download_stories'] = get_bool('DOWNLOAD_STORIES')
        if get_bool('DOWNLOAD_HIGHLIGHTS') is not None:
            env_config['download_highlights'] = get_bool('DOWNLOAD_HIGHLIGHTS')
        if get_bool('DOWNLOAD_TAGGED') is not None:
            env_config['download_tagged'] = get_bool('DOWNLOAD_TAGGED')
        if get_bool('DOWNLOAD_IGTV') is not None:
            env_config['download_igtv'] = get_bool('DOWNLOAD_IGTV')

        if os.getenv('DOWNLOAD_DIR'):
            env_config['download_dir'] = os.getenv('DOWNLOAD_DIR')
        if os.getenv('SESSION_DIR'):
            env_config['session_dir'] = os.getenv('SESSION_DIR')

        if get_int('MIN_SLEEP_TIME') is not None:
            env_config['min_sleep_time'] = get_int('MIN_SLEEP_TIME')
        if get_int('MAX_SLEEP_TIME') is not None:
            env_config['max_sleep_time'] = get_int('MAX_SLEEP_TIME')
        if get_float('RATE_LIMIT_BACKOFF_MULTIPLIER') is not None:
            env_config['rate_limit_backoff_multiplier'] = get_float('RATE_LIMIT_BACKOFF_MULTIPLIER')

        return env_config

    def _load_from_file(self) -> Dict[str, Any]:
        """
        Ładuje konfigurację z pliku JSON

        Returns:
            Słownik z ustawieniami z pliku lub pusty słownik
        """
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️  Ostrzeżenie: Błąd parsowania {self.config_path}: {e}")
            return {}
        except Exception as e:
            print(f"⚠️  Ostrzeżenie: Nie można załadować {self.config_path}: {e}")
            return {}

    def _load_config(self) -> Dict[str, Any]:
        """
        Ładuje pełną konfigurację z wszystkich źródeł

        Priorytet: .env > config.json > domyślne

        Returns:
            Słownik z finalną konfiguracją
        """
        # Zacznij od wartości domyślnych
        config = self._default_config()

        # Nadpisz wartościami z pliku config.json
        file_config = self._load_from_file()
        config.update(file_config)

        # Nadpisz wartościami ze zmiennych środowiskowych
        env_config = self._load_from_env()
        config.update(env_config)

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Pobiera wartość z konfiguracji

        Args:
            key: Klucz konfiguracji
            default: Wartość domyślna jeśli klucz nie istnieje

        Returns:
            Wartość konfiguracji lub default
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Ustawia wartość w konfiguracji (tylko w pamięci)

        Args:
            key: Klucz konfiguracji
            value: Nowa wartość
        """
        self.config[key] = value

    def save_to_file(self, path: Optional[str] = None) -> None:
        """
        Zapisuje bieżącą konfigurację do pliku JSON

        Args:
            path: Opcjonalna ścieżka do pliku (domyślnie: self.config_path)
        """
        save_path = Path(path) if path else self.config_path

        # Utwórz katalog jeśli nie istnieje
        save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✓ Konfiguracja zapisana do {save_path}")
        except Exception as e:
            print(f"❌ Błąd zapisu konfiguracji: {e}")

    def get_instagram_credentials(self) -> tuple[Optional[str], Optional[str]]:
        """
        Pobiera dane logowania Instagram ze zmiennych środowiskowych

        Returns:
            Tuple (username, password) lub (None, None)
        """
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        return username, password

    def __repr__(self) -> str:
        """Reprezentacja tekstowa konfiguracji"""
        return f"ConfigManager({len(self.config)} opcji)"

    def __str__(self) -> str:
        """Ładny wydruk konfiguracji"""
        lines = ["Aktualna konfiguracja:"]
        for key, value in sorted(self.config.items()):
            # Ukryj potencjalnie wrażliwe dane
            if 'password' in key.lower() or 'secret' in key.lower():
                value = '***'
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)


# Funkcja pomocnicza do szybkiego ładowania konfiguracji
def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Funkcja pomocnicza do szybkiego załadowania konfiguracji

    Args:
        config_path: Opcjonalna ścieżka do pliku config.json

    Returns:
        Słownik z konfiguracją
    """
    manager = ConfigManager(config_path)
    return manager.config
