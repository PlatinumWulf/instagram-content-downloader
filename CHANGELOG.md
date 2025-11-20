# Changelog

Wszystkie istotne zmiany w projekcie Instagram Content Downloader.

Format oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.0.0/).

## [3.0.0] - 2024-11-20

### 🎉 Pełna Refaktoryzacja Projektu

### Dodano
- **Modułowa architektura** - Kod rozdzielony na moduły w katalogu `src/`
  - `config.py` - Zarządzanie konfiguracją
  - `auth.py` - Autoryzacja i sesje
  - `downloader.py` - Główna logika pobierania
  - `batch.py` - Pobieranie wsadowe
  - `utils.py` - Funkcje pomocnicze
  - `logger_setup.py` - Konfiguracja logowania

- **Bezpieczeństwo**
  - Szyfrowanie plików sesji (Fernet/AES)
  - Automatyczne uprawnienia 600 dla wrażliwych plików
  - Walidacja nazw użytkowników
  - Usunięcie wrażliwych danych z repozytorium

- **Konfiguracja**
  - Plik `.env` dla zmiennych środowiskowych
  - `.env.example` z pełną dokumentacją opcji
  - `config/config.json` dla dodatkowej konfiguracji
  - Priorytet: `.env` > `config.json` > domyślne

- **Progress & UX**
  - Progress bary z `tqdm` dla wszystkich operacji pobierania
  - Adaptive rate limiting z exponential backoff
  - Lepsze komunikaty błędów
  - Kolorowe emoji dla lepszej czytelności

- **Logging**
  - Proper logging system z `logging` module
  - Logi do pliku (`logs/instagram_downloader.log`)
  - Rotacja plików logu
  - Poziomy: DEBUG, INFO, WARNING, ERROR, CRITICAL

- **Error Handling**
  - Specific exception handling zamiast generic `Exception`
  - Osobne obsługi dla:
    - `ProfileNotExistsException`
    - `LoginRequiredException`
    - `ConnectionException`
    - `TooManyRequestsException`
    - `QueryReturnedNotFoundException`

- **CLI**
  - Nowy interfejs z `argparse`
  - Argumenty: `--posts`, `--stories`, `--highlights`, `--tagged`, `--igtv`, `--all`
  - Tryb batch: `-b/--batch`
  - Opcje logowania: `-l/--login`, `--browser-login`
  - Wyświetlanie konfiguracji: `--config`

- **Testy**
  - Testy jednostkowe z `pytest`
  - `test_config.py` - Testy konfiguracji
  - `test_utils.py` - Testy funkcji pomocniczych
  - Coverage reports z `pytest-cov`

- **Dokumentacja**
  - Nowy README.md po polsku z pełną dokumentacją
  - Sekcje: Instalacja, Konfiguracja, Użycie, FAQ, Troubleshooting
  - Badges (Python, License, Code Style)
  - Emoji dla lepszej czytelności

- **Instalacja**
  - `setup.py` - Instalacja jako pakiet Python
  - Entry points: `ig-downloader`, `instagram-downloader`
  - Wsparcie dla `pip install -e .`

### Zmieniono
- **Struktura projektu**
  ```
  Przed: Wszystkie pliki w root
  Po:    Modułowa struktura (src/, tests/, config/, docs/, data/)
  ```

- **Zarządzanie sesjami**
  - Sesje są teraz szyfrowane
  - Przechowywane w `data/sessions/` zamiast w root
  - Bezpieczniejsze uprawnienia plików

- **Rate limiting**
  - Z fixed delay na adaptive rate limiting
  - Automatyczne zwiększanie opóźnień przy błędach
  - Exponential backoff dla rate limit errors

- **Logging**
  - Z `print()` na proper `logging` module
  - Logi zapisywane do pliku z rotacją
  - Poziomy logowania konfigurowane przez `.env`

### Poprawiono
- **Bezpieczeństwo**
  - Usunięto `browser_session.json` z repozytorium (zawierał prawdziwą sesję!)
  - Dodano szyfrowanie wszystkich plików sesji
  - Poprawiono uprawnienia plików (600 dla sesji, 700 dla katalogów)

- **Error handling**
  - Lepsze obsługa wyjątków Instagram API
  - Graceful degradation przy błędach
  - Informacyjne komunikaty dla użytkownika

- **Walidacja**
  - Walidacja nazw użytkowników (długość, znaki, format)
  - Ekstrakcja username z różnych formatów URL
  - Walidacja plików konfiguracyjnych

### Usunięto
- Generic exception handling
- Hardcoded wartości konfiguracyjnych
- Duplikacja kodu między modułami
- Nieużywane funkcje i komentarze

### Techniczne
- **Nowe zależności:**
  - `python-dotenv` - Zmienne środowiskowe
  - `cryptography` - Szyfrowanie sesji
  - `tqdm` - Progress bary
  - `pytest` - Testy jednostkowe
  - `pytest-cov` - Coverage reports

- **Python version:** 3.8+

---

## [2.0] - 2024-11

### Dodano
- Logowanie przez przeglądarkę (Selenium)
- Pobieranie stories
- Pobieranie highlights
- Pobieranie tagged posts
- Pobieranie IGTV
- Tryb interaktywny z menu
- Konfigurowalny rate limiting
- Obsługa 2FA
- Wznawianie przerwanych pobierań

---

## [1.0] - 2024-10

### Dodano
- Podstawowe pobieranie postów z Instagram
- Logowanie przez login/hasło
- Zapisywanie metadanych do JSON
- Obsługa video i zdjęć
- CLI interface

---

## Legenda

- **Dodano** - Nowe funkcje
- **Zmieniono** - Zmiany w istniejących funkcjach
- **Poprawiono** - Bugfixy
- **Usunięto** - Usunięte funkcje
- **Bezpieczeństwo** - Poprawki bezpieczeństwa
- **Techniczne** - Zmiany techniczne/infrastrukturalne
