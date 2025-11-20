#!/usr/bin/env python3
"""
Testy jednostkowe dla modułu config
"""

import os
import json
import pytest
from pathlib import Path
from src.config import ConfigManager, load_config


class TestConfigManager:
    """Testy menedżera konfiguracji"""

    def test_default_config(self):
        """Test domyślnej konfiguracji"""
        config = ConfigManager()

        assert config.get('download_videos') == True
        assert config.get('download_thumbnails') == True
        assert config.get('sleep_time') == 3
        assert config.get('download_posts') == True
        assert config.get('max_attempts') == 3

    def test_get_with_default(self):
        """Test pobierania z wartością domyślną"""
        config = ConfigManager()

        # Klucz nie istnieje - zwróci default
        assert config.get('nonexistent_key', 'default_value') == 'default_value'

        # Klucz istnieje - zwróci wartość
        assert config.get('sleep_time', 999) == 3

    def test_set_config_value(self):
        """Test ustawiania wartości"""
        config = ConfigManager()

        config.set('sleep_time', 10)
        assert config.get('sleep_time') == 10

        config.set('custom_key', 'custom_value')
        assert config.get('custom_key') == 'custom_value'

    def test_load_from_json_file(self, tmp_path):
        """Test ładowania z pliku JSON"""
        # Utwórz tymczasowy plik config
        config_file = tmp_path / "config.json"
        config_data = {
            'sleep_time': 5,
            'download_videos': False,
            'custom_option': 'test_value'
        }

        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        # Załaduj konfigurację
        config = ConfigManager(config_path=str(config_file))

        # Wartości z pliku powinny nadpisać domyślne
        assert config.get('sleep_time') == 5
        assert config.get('download_videos') == False
        assert config.get('custom_option') == 'test_value'

        # Wartości domyślne które nie są w pliku
        assert config.get('download_thumbnails') == True  # Domyślna

    def test_load_from_env(self, monkeypatch):
        """Test ładowania ze zmiennych środowiskowych"""
        # Ustaw zmienne środowiskowe
        monkeypatch.setenv('SLEEP_TIME', '7')
        monkeypatch.setenv('DOWNLOAD_VIDEOS', 'false')
        monkeypatch.setenv('DOWNLOAD_GEOTAGS', 'true')
        monkeypatch.setenv('MAX_ATTEMPTS', '5')

        config = ConfigManager()

        # Zmienne środowiskowe powinny nadpisać domyślne
        assert config.get('sleep_time') == 7
        assert config.get('download_videos') == False
        assert config.get('download_geotags') == True
        assert config.get('max_attempts') == 5

    def test_env_overrides_file(self, tmp_path, monkeypatch):
        """Test że .env ma priorytet nad plikiem JSON"""
        # Plik JSON
        config_file = tmp_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump({'sleep_time': 3}, f)

        # Zmienna środowiskowa
        monkeypatch.setenv('SLEEP_TIME', '10')

        config = ConfigManager(config_path=str(config_file))

        # Zmienna środowiskowa powinna wygrać
        assert config.get('sleep_time') == 10

    def test_save_to_file(self, tmp_path):
        """Test zapisywania do pliku"""
        config = ConfigManager()
        config.set('sleep_time', 15)
        config.set('custom_value', 'test')

        save_path = tmp_path / "saved_config.json"
        config.save_to_file(str(save_path))

        # Sprawdź czy plik został utworzony
        assert save_path.exists()

        # Załaduj i sprawdź zawartość
        with open(save_path) as f:
            saved_data = json.load(f)

        assert saved_data['sleep_time'] == 15
        assert saved_data['custom_value'] == 'test'

    def test_get_instagram_credentials(self, monkeypatch):
        """Test pobierania danych logowania z .env"""
        monkeypatch.setenv('INSTAGRAM_USERNAME', 'test_user')
        monkeypatch.setenv('INSTAGRAM_PASSWORD', 'test_pass')

        config = ConfigManager()
        username, password = config.get_instagram_credentials()

        assert username == 'test_user'
        assert password == 'test_pass'

    def test_get_instagram_credentials_empty(self):
        """Test gdy brak danych logowania"""
        config = ConfigManager()
        username, password = config.get_instagram_credentials()

        # Powinny być None jeśli nie ustawione
        assert username is None or username == ''
        assert password is None or password == ''

    def test_invalid_json_file(self, tmp_path):
        """Test obsługi nieprawidłowego pliku JSON"""
        # Utwórz plik z nieprawidłowym JSON
        config_file = tmp_path / "invalid.json"
        config_file.write_text("{ invalid json }")

        # Nie powinno wywołać wyjątku - załaduje domyślne
        config = ConfigManager(config_path=str(config_file))

        # Powinna załadować domyślną konfigurację
        assert config.get('sleep_time') == 3

    def test_repr_and_str(self):
        """Test reprezentacji tekstowej"""
        config = ConfigManager()

        repr_str = repr(config)
        assert "ConfigManager" in repr_str
        assert "opcji" in repr_str

        str_repr = str(config)
        assert "konfiguracja" in str_repr.lower()
        assert "sleep_time" in str_repr


class TestLoadConfigFunction:
    """Testy funkcji load_config"""

    def test_load_config_default(self):
        """Test funkcji load_config bez argumentów"""
        config_dict = load_config()

        assert isinstance(config_dict, dict)
        assert 'sleep_time' in config_dict
        assert 'download_videos' in config_dict

    def test_load_config_with_file(self, tmp_path):
        """Test funkcji load_config z plikiem"""
        config_file = tmp_path / "test_config.json"
        test_data = {'sleep_time': 99}

        with open(config_file, 'w') as f:
            json.dump(test_data, f)

        config_dict = load_config(str(config_file))

        assert config_dict['sleep_time'] == 99
