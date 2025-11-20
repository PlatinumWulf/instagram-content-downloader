#!/usr/bin/env python3
"""
Testy jednostkowe dla modułu utils
"""

import pytest
from pathlib import Path
from src.utils import (
    validate_username,
    extract_username_from_url,
    format_file_size,
    safe_filename,
    truncate_string,
    calculate_rate_limit_delay,
    parse_profile_list_file
)


class TestValidateUsername:
    """Testy walidacji nazwy użytkownika"""

    def test_valid_username(self):
        """Test poprawnej nazwy użytkownika"""
        assert validate_username("john_doe") == "john_doe"
        assert validate_username("user.name") == "user.name"
        assert validate_username("User123") == "user123"  # lowercase
        assert validate_username("a") == "a"  # min length

    def test_invalid_username_empty(self):
        """Test pustej nazwy"""
        with pytest.raises(ValueError, match="nie może być pusta"):
            validate_username("")
        with pytest.raises(ValueError, match="nie może być pusta"):
            validate_username("   ")

    def test_invalid_username_length(self):
        """Test nieprawidłowej długości"""
        # Za długa nazwa (>30 znaków)
        with pytest.raises(ValueError, match="1-30 znaków"):
            validate_username("a" * 31)

    def test_invalid_username_characters(self):
        """Test nieprawidłowych znaków"""
        with pytest.raises(ValueError, match="niedozwolone znaki"):
            validate_username("user@name")
        with pytest.raises(ValueError, match="niedozwolone znaki"):
            validate_username("user name")  # spacja
        with pytest.raises(ValueError, match="niedozwolone znaki"):
            validate_username("user#name")

    def test_invalid_username_dots(self):
        """Test nazw zaczynających/kończących się kropką"""
        with pytest.raises(ValueError, match="nie może zaczynać"):
            validate_username(".username")
        with pytest.raises(ValueError, match="nie może kończyć"):
            validate_username("username.")


class TestExtractUsernameFromUrl:
    """Testy ekstrakcji nazwy z URL"""

    def test_extract_from_full_url(self):
        """Test ekstrakcji z pełnego URL"""
        assert extract_username_from_url("https://www.instagram.com/username/") == "username"
        assert extract_username_from_url("https://instagram.com/username") == "username"
        assert extract_username_from_url("http://instagram.com/username/") == "username"

    def test_extract_from_partial_url(self):
        """Test ekstrakcji z częściowego URL"""
        assert extract_username_from_url("instagram.com/username/") == "username"
        assert extract_username_from_url("www.instagram.com/username") == "username"

    def test_extract_from_username(self):
        """Test gdy już jest nazwa użytkownika"""
        assert extract_username_from_url("username") == "username"
        assert extract_username_from_url("user_name.123") == "user_name.123"

    def test_extract_from_at_mention(self):
        """Test ekstrakcji z @username"""
        assert extract_username_from_url("@username") == "username"

    def test_extract_invalid_input(self):
        """Test nieprawidłowego input"""
        with pytest.raises(ValueError):
            extract_username_from_url("")
        with pytest.raises(ValueError):
            extract_username_from_url("https://facebook.com/user")


class TestFormatFileSize:
    """Testy formatowania rozmiaru pliku"""

    def test_format_bytes(self):
        """Test formatowania bajtów"""
        assert "B" in format_file_size(100)
        assert "100" in format_file_size(100)

    def test_format_kilobytes(self):
        """Test formatowania kilobajtów"""
        result = format_file_size(1024)
        assert "KB" in result
        assert "1.0" in result

    def test_format_megabytes(self):
        """Test formatowania megabajtów"""
        result = format_file_size(1024 * 1024)
        assert "MB" in result

    def test_format_gigabytes(self):
        """Test formatowania gigabajtów"""
        result = format_file_size(1024 * 1024 * 1024)
        assert "GB" in result


class TestSafeFilename:
    """Testy tworzenia bezpiecznej nazwy pliku"""

    def test_safe_filename_valid(self):
        """Test poprawnej nazwy"""
        assert safe_filename("normal_file.txt") == "normal_file.txt"

    def test_safe_filename_with_invalid_chars(self):
        """Test nazwy z niedozwolonymi znakami"""
        assert safe_filename("file:name.txt") == "file_name.txt"
        assert safe_filename("file<name>.txt") == "file_name_.txt"
        assert safe_filename('file"name".txt') == "file_name_.txt"

    def test_safe_filename_max_length(self):
        """Test ograniczenia długości"""
        long_name = "a" * 300 + ".txt"
        result = safe_filename(long_name, max_length=255)
        assert len(result) <= 255
        assert result.endswith(".txt")  # Rozszerzenie zachowane


class TestTruncateString:
    """Testy obcinania stringów"""

    def test_truncate_short_string(self):
        """Test krótkiego stringa (nie obcina)"""
        assert truncate_string("short", max_length=50) == "short"

    def test_truncate_long_string(self):
        """Test długiego stringa"""
        result = truncate_string("very long string here", max_length=10)
        assert len(result) == 10
        assert result.endswith("...")

    def test_truncate_custom_suffix(self):
        """Test własnego suffixu"""
        result = truncate_string("long string", max_length=10, suffix=">>")
        assert result.endswith(">>")


class TestCalculateRateLimitDelay:
    """Testy obliczania opóźnienia rate limit"""

    def test_zero_errors(self):
        """Test bez błędów - bazowe opóźnienie"""
        assert calculate_rate_limit_delay(0, base_delay=3.0) == 3.0

    def test_one_error(self):
        """Test jednego błędu"""
        delay = calculate_rate_limit_delay(1, base_delay=3.0, multiplier=1.5)
        assert delay == 4.5

    def test_multiple_errors(self):
        """Test wielu błędów (exponential backoff)"""
        delay = calculate_rate_limit_delay(3, base_delay=3.0, multiplier=2.0)
        assert delay == 24.0  # 3 * 2^3

    def test_max_delay_limit(self):
        """Test limitu maksymalnego opóźnienia"""
        delay = calculate_rate_limit_delay(10, base_delay=3.0, multiplier=2.0, max_delay=100.0)
        assert delay <= 100.0
        assert delay == 100.0  # Powinien osiągnąć max


class TestParseProfileListFile:
    """Testy parsowania pliku z listą profili"""

    def test_parse_valid_file(self, tmp_path):
        """Test parsowania poprawnego pliku"""
        # Utwórz tymczasowy plik
        test_file = tmp_path / "profiles.txt"
        test_file.write_text("""
# Komentarz
username1
https://instagram.com/username2/
@username3

# Kolejny komentarz
        """)

        profiles = parse_profile_list_file(test_file)
        assert len(profiles) == 3
        assert "username1" in profiles
        assert "username2" in profiles
        assert "username3" in profiles

    def test_parse_empty_file(self, tmp_path):
        """Test pustego pliku"""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("# Tylko komentarze\n\n")

        with pytest.raises(ValueError, match="nie zawiera żadnych"):
            parse_profile_list_file(test_file)

    def test_parse_nonexistent_file(self):
        """Test nieistniejącego pliku"""
        with pytest.raises(FileNotFoundError):
            parse_profile_list_file("nonexistent.txt")

    def test_parse_with_invalid_names(self, tmp_path):
        """Test pliku z nieprawidłowymi nazwami (pomija je)"""
        test_file = tmp_path / "profiles.txt"
        test_file.write_text("""
valid_username
invalid@username
another_valid
        """)

        # Powinien pominąć invalid@username i zwrócić tylko valid
        profiles = parse_profile_list_file(test_file)
        assert "valid_username" in profiles
        assert "another_valid" in profiles
        # invalid@username powinien być pominięty (warning w logach)
