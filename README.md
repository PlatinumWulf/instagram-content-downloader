# 📸 Instagram Content Downloader v3.0

> Profesjonalne narzędzie do pobierania zawartości z profili Instagram z pełną obsługą logowania, szyfrowaniem sesji i zaawansowanymi funkcjami.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🌟 Najważniejsze Funkcje

### ✨ Wersja 3.0 - Pełna Refaktoryzacja!

- **🔒 Szyfrowanie sesji** - Bezpieczne przechowywanie danych logowania z szyfrowaniem AES
- **📦 Modułowa architektura** - Czysty, utrzymywalny kod z separacją odpowiedzialności
- **⚙️ Zarządzanie konfiguracją** - Plik `.env` i JSON config dla łatwej personalizacji
- **📊 Progress bary** - Wizualizacja postępu pobierania z tqdm
- **🧠 Adaptive rate limiting** - Inteligentne dostosowywanie opóźnień
- **📝 Proper logging** - Szczegółowe logi do pliku i konsoli
- **🧪 Testy jednostkowe** - Pokrycie kodu testami
- **🌐 Logowanie przez przeglądarkę** - Bezpieczne logowanie z Selenium
- **🔄 Retry logic** - Automatyczne ponowne próby przy błędach

### 📥 Typy Pobieranych Treści

- ✅ **Posty** - Zdjęcia, wideo, rolki
- ✅ **Stories** - Aktywne stories (wymaga logowania)
- ✅ **Highlights** - Zachowane highlights
- ✅ **Tagged Posts** - Posty z oznaczeniem użytkownika
- ✅ **IGTV** - Dłuższe filmy
- ✅ **Metadane** - JSON z pełnymi informacjami o poście

---

## 📋 Spis Treści

- [Wymagania](#-wymagania)
- [Instalacja](#-instalacja)
- [Konfiguracja](#%EF%B8%8F-konfiguracja)
- [Użycie](#-użycie)
- [Funkcje](#-funkcje)
- [Bezpieczeństwo](#-bezpieczeństwo)
- [FAQ](#-faq)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Licencja](#-licencja)

---

## 🔧 Wymagania

- **Python 3.8+**
- Połączenie z internetem
- (Opcjonalnie) Konto Instagram dla pełnej funkcjonalności
- (Opcjonalnie) Chrome/Firefox dla logowania przez przeglądarkę

---

## 📦 Instalacja

### Metoda 1: Klonowanie repozytorium (zalecana)

```bash
# Sklonuj repozytorium
git clone https://github.com/yourusername/instagram-content-downloader.git
cd instagram-content-downloader

# Utwórz wirtualne środowisko (opcjonalne, ale zalecane)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate     # Windows

# Zainstaluj zależności
pip install -r requirements.txt
```

### Metoda 2: Instalacja jako pakiet

```bash
# Instalacja w trybie development
pip install -e .

# Lub bezpośrednia instalacja
pip install .

# Teraz możesz uruchomić z dowolnego miejsca:
ig-downloader
instagram-downloader
```

### Dodatkowe kroki (opcjonalne)

#### Dla logowania przez przeglądarkę (Selenium):

**Chrome (zalecane):**
```bash
# Pobierz ChromeDriver: https://chromedriver.chromium.org/
# Lub użyj automatycznego instalatora:
pip install webdriver-manager
```

**Firefox:**
```bash
pip install webdriver-manager
```

---

## ⚙️ Konfiguracja

### 1. Plik `.env` (Zmienne Środowiskowe)

Skopiuj przykładowy plik i dostosuj:

```bash
cp .env.example .env
nano .env  # lub edytor tekstowy
```

Przykładowa zawartość `.env`:

```bash
# Podstawowa konfiguracja
DOWNLOAD_VIDEOS=true
DOWNLOAD_THUMBNAILS=true
SAVE_METADATA=true

# Rate limiting
SLEEP_TIME=3
MIN_SLEEP_TIME=2
MAX_SLEEP_TIME=30

# Katalogi
DOWNLOAD_DIR=data/downloads
SESSION_DIR=data/sessions

# Logowanie
LOG_LEVEL=INFO
LOG_FILE=logs/instagram_downloader.log
```

**Uwaga:** NIE przechowuj hasła w pliku `.env`! Loguj się interaktywnie lub przez przeglądarkę.

### 2. Plik `config/config.json` (Opcjonalny)

```json
{
  "download_videos": true,
  "download_thumbnails": true,
  "save_metadata": true,
  "sleep_time": 3,
  "download_posts": true,
  "download_stories": false,
  "download_highlights": false
}
```

### 3. Lista profili `config/profiles.txt`

```
# Przykładowa lista profili do pobrania
username1
https://instagram.com/username2/
@username3

# Możesz dodać komentarze
another_profile
```

---

## 🚀 Użycie

### Tryb Interaktywny (Zalecany)

Uruchom bez argumentów, aby otworzyć interaktywne menu:

```bash
python main.py
```

**Menu:**
```
═══════════════════════════════════════════════════════════
                        MENU GŁÓWNE
═══════════════════════════════════════════════════════════
1. Pobierz profil (bez logowania)
2. Zaloguj się przez przeglądarkę 🌐 (POLECANE)
3. Zaloguj się (login/hasło)
4. Pobierz profil (zalogowany)
5. Pobieranie wsadowe z pliku
6. Konfiguracja
7. Wyloguj się
0. Wyjście
═══════════════════════════════════════════════════════════
```

### Tryb CLI (Szybkie Pobieranie)

```bash
# Podstawowe użycie - pobierz profil
python main.py username

# Pobierz z URL
python main.py https://instagram.com/username/

# Pobierz wszystko (posty, stories, highlights, igtv, tagged)
python main.py username --all

# Pobierz tylko stories i highlights
python main.py username --stories --highlights

# Pobieranie wsadowe z pliku
python main.py -b config/profiles.txt

# Tylko zaloguj się
python main.py --login

# Zaloguj przez przeglądarkę
python main.py --browser-login

# Pokaż konfigurację
python main.py --config

# Pomoc
python main.py --help
```

### Przykłady Zaawansowane

```bash
# Pobierz profil ze stories i highlights (wymaga logowania)
python main.py --login  # Najpierw zaloguj się
python main.py username --stories --highlights

# Pobieranie wsadowe z własnym opóźnieniem
python main.py -b my_profiles.txt  # Domyślnie 60s między profilami

# Tryb interaktywny
python main.py -i

# Sprawdź wersję
python main.py --version
```

---

## 🎯 Funkcje

### 1. 🔐 Bezpieczne Logowanie

#### Metoda A: Logowanie przez przeglądarkę (ZALECANE)

```bash
python main.py --browser-login
```

**Zalety:**
- ✅ Najbezpieczniejsza metoda
- ✅ Automatyczna obsługa captcha
- ✅ Automatyczna obsługa 2FA
- ✅ Wizualne potwierdzenie logowania

#### Metoda B: Logowanie tradycyjne (login/hasło)

```bash
python main.py --login
```

**Uwaga:** Hasło wprowadzane jest bezpiecznie (nie jest wyświetlane).

### 2. 📊 Inteligentny Rate Limiting

System automatycznie dostosowuje opóźnienia:
- 🟢 **Sukces** → Stopniowo skraca opóźnienia
- 🔴 **Błąd rate limit** → Podwaja opóźnienie (exponential backoff)
- ⚠️ **Inny błąd** → Lekko zwiększa opóźnienie

### 3. 🔒 Szyfrowanie Sesji

Wszystkie pliki sesji są:
- ✅ Szyfrowane algorytmem Fernet (AES)
- ✅ Przechowywane z uprawnieniami 600 (tylko właściciel)
- ✅ Automatycznie deszyfrowane przy ładowaniu

### 4. 📦 Pobieranie Wsadowe

Pobierz wiele profili z pliku:

```bash
# Utwórz plik profiles.txt
echo "username1
username2
username3" > profiles.txt

# Pobierz wszystkie
python main.py -b profiles.txt
```

Nieudane profile są zapisywane do `failed_profiles.txt` do późniejszej próby.

### 5. 📝 Logowanie

Szczegółowe logi zapisywane do pliku:

```bash
# Domyślnie: logs/instagram_downloader.log
tail -f logs/instagram_downloader.log

# Zmień poziom logowania w .env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 6. 🔄 Wznowienie Pobierania

Instaloader automatycznie pomija już pobrane pliki:

```bash
# Przerwij (Ctrl+C) i uruchom ponownie - kontynuuje od miejsca przerwania
python main.py username
# (przerwij)
python main.py username  # Kontynuuje
```

---

## 🛡️ Bezpieczeństwo

### Dobre Praktyki

✅ **Zawsze:**
- Używaj pliku `.env` dla konfiguracji
- Upewnij się że `.env` jest w `.gitignore`
- Używaj logowania przez przeglądarkę zamiast hasła
- Trzymaj pliki sesji poza repozytorium
- Regularnie aktualizuj zależności

❌ **Nigdy:**
- Nie commituj pliku `.env` do repozytorium
- Nie udostępniaj plików sesji
- Nie przechowuj hasła w kodzie/plikach
- Nie wyłączaj szyfrowania sesji

### Ochrona Danych

1. **Pliki sesji** - Szyfrowane i z uprawnieniami 600
2. **Hasła** - Nigdy nie są zapisywane (tylko sesje)
3. **Logi** - Nie zawierają wrażliwych danych
4. **.gitignore** - Chroni wrażliwe pliki przed przypadkowym commitem

### Uprawnienia Plików

```bash
# Automatycznie ustawiane przez aplikację:
chmod 600 data/sessions/*     # Tylko właściciel
chmod 700 data/sessions/      # Tylko właściciel
```

---

## ❓ FAQ

### 1. Czy to legalne?

✅ Pobieranie publicznych treści dla osobistego użytku jest legalne.
⚠️ Zawsze przestrzegaj [Terms of Service Instagram](https://help.instagram.com/581066165581870).

### 2. Czy potrzebuję konta Instagram?

**⚠️ WAŻNE: Instagram bardzo agresywnie blokuje pobieranie BEZ logowania (403 Forbidden)!**

- Dla **publicznych profili** - **ZALECANE LOGOWANIE** (bez logowania: max 10-20 postów, potem blokada)
- Dla **prywatnych profili** - **TAK** (musisz obserwować)
- Dla **stories/highlights** - **TAK** (zawsze wymaga logowania)

**Najlepsze rozwiązanie:** Zawsze loguj się przed pobieraniem!

### 3. Jak uniknąć blokady?

- ✅ Loguj się przed pobieraniem
- ✅ Używaj rozsądnych opóźnień (≥3s)
- ✅ Nie pobieraj zbyt wielu profili naraz
- ✅ Korzystaj z logowania przez przeglądarkę

### 4. Czy hasło jest bezpieczne?

**TAK!**
- Hasło wprowadzane jest przez `getpass` (ukryte)
- Nigdy nie jest zapisywane do pliku
- Tylko sesja (cookie) jest zapisywana (zaszyfrowana)

### 5. Jak długo ważna jest sesja?

Sesja Instagram jest ważna przez **~90 dni**. Po tym czasie musisz się zalogować ponownie.

### 6. Co oznacza "rate limit"?

Instagram ogranicza liczbę requestów. Aplikacja automatycznie:
- Wykrywa rate limiting
- Zwiększa opóźnienia
- Czeka przed kolejnymi próbami

---

## 🔧 Troubleshooting

### Błąd: "ProfileNotExistsException"

**Przyczyna:** Profil nie istnieje lub nazwa jest nieprawidłowa.

**Rozwiązanie:**
- Sprawdź poprawność nazwy użytkownika
- Upewnij się że profil istnieje (otwórz w przeglądarce)

### Błąd: "LoginRequiredException"

**Przyczyna:** Treść wymaga zalogowania (profil prywatny lub stories).

**Rozwiązanie:**
```bash
python main.py --browser-login  # Zaloguj się
python main.py username --stories  # Teraz zadziała
```

### Błąd: "403 Forbidden" lub "JSON Query to graphql/query"

**Przyczyna:** Instagram zablokował requesty (najczęstszy problem!).

**To oznacza:**
- Pobierasz bez logowania
- Instagram wykrył podejrzaną aktywność
- Za szybkie requesty

**Rozwiązanie (w kolejności):**
```bash
# 1. NAJWAŻNIEJSZE: Zaloguj się!
python3 main.py --browser-login  # Najlepsze
# lub
python3 main.py --login

# 2. Zwiększ opóźnienia w .env:
SLEEP_TIME=7
MIN_SLEEP_TIME=5
MAX_SLEEP_TIME=120

# 3. Poczekaj 15-30 minut przed następną próbą
# Instagram czasowo blokuje IP

# 4. Teraz spróbuj ponownie (jako zalogowany!)
python3 main.py username
```

**Ważne:** Bez logowania możesz pobrać max 10-20 postów, potem Instagram blokuje!

### Błąd: "ConnectionException" lub "TooManyRequestsException"

**Przyczyna:** Rate limiting Instagram.

**Rozwiązanie:**
```bash
# W .env zwiększ opóźnienia:
SLEEP_TIME=7
MIN_SLEEP_TIME=5
MAX_SLEEP_TIME=120
```

### Błąd: "No module named 'src'"

**Przyczyna:** Uruchomiłeś z niewłaściwego katalogu.

**Rozwiązanie:**
```bash
cd /path/to/instagram-content-downloader
python main.py
```

### Selenium nie działa

**Rozwiązanie:**
```bash
# Zainstaluj WebDriver Manager
pip install webdriver-manager

# Lub pobierz ręcznie ChromeDriver
# https://chromedriver.chromium.org/
```

### Błędy importu po instalacji

**Rozwiązanie:**
```bash
# Przeinstaluj w trybie edytowalnym
pip install -e .

# Lub dodaj do PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/instagram-content-downloader"
```

---

## 📁 Struktura Projektu

```
instagram-content-downloader/
├── src/                      # Kod źródłowy
│   ├── __init__.py
│   ├── config.py             # Zarządzanie konfiguracją
│   ├── auth.py               # Logowanie i sesje
│   ├── downloader.py         # Główna logika pobierania
│   ├── batch.py              # Pobieranie wsadowe
│   ├── utils.py              # Funkcje pomocnicze
│   ├── logger_setup.py       # Konfiguracja logowania
│   └── browser_auth.py       # Logowanie przez przeglądarkę (legacy)
│
├── tests/                    # Testy jednostkowe
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_downloader.py
│   └── test_utils.py
│
├── config/                   # Pliki konfiguracyjne
│   ├── config.example.json
│   └── profiles.example.txt
│
├── docs/                     # Dokumentacja
│   ├── QUICK_START.md
│   └── BROWSER_SETUP.md
│
├── data/                     # Dane (w .gitignore)
│   ├── downloads/            # Pobrane pliki
│   └── sessions/             # Pliki sesji (WRAŻLIWE!)
│
├── logs/                     # Logi (w .gitignore)
│
├── main.py                   # Główny plik programu
├── setup.py                  # Instalator pakietu
├── requirements.txt          # Zależności
├── .env.example              # Przykładowy plik .env
├── .gitignore
├── README.md                 # Ten plik
└── LICENSE
```

---

## 🧪 Testy

Uruchom testy jednostkowe:

```bash
# Wszystkie testy
pytest

# Z pokryciem kodu
pytest --cov=src --cov-report=html

# Tylko konkretny test
pytest tests/test_config.py

# Verbose mode
pytest -v
```

---

## 🤝 Contributing

Chcesz pomóc? Świetnie!

1. Fork projektu
2. Stwórz branch: `git checkout -b feature/amazing-feature`
3. Commit zmian: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Otwórz Pull Request

### Guidelines

- Kod w języku angielskim (komentarze i docstringi w polsku)
- Testy dla nowych funkcji
- Dokumentacja zmian w README
- PEP 8 style guide

---

## 📝 Changelog

### v3.0.0 (2024-11-20)
- 🎉 **Pełna refaktoryzacja projektu**
- 🔒 Dodano szyfrowanie plików sesji
- 📦 Nowa modułowa architektura
- ⚙️ Obsługa .env i JSON config
- 📊 Progress bary z tqdm
- 🧠 Adaptive rate limiting
- 📝 Proper logging system
- 🧪 Testy jednostkowe
- 📚 Kompletna dokumentacja PL

### v2.0 (2024-11)
- 🌐 Logowanie przez przeglądarkę
- 📱 Pobieranie stories i highlights
- 🔄 Tryb interaktywny
- ⚙️ Konfigurowalny rate limiting

### v1.0 (wcześniej)
- Podstawowe pobieranie postów

---

## 📄 Licencja

Ten projekt jest na licencji MIT. Zobacz plik [LICENSE](LICENSE) dla szczegółów.

```
MIT License - możesz swobodnie używać, modyfikować i dystrybuować.
```

---

## 🙏 Podziękowania

- [Instaloader](https://instaloader.github.io/) - świetna biblioteka do Instagram API
- [Selenium](https://selenium.dev/) - automatyzacja przeglądarki
- [tqdm](https://github.com/tqdm/tqdm) - piękne progress bary

---

## ⚠️ Disclaimer

To narzędzie jest przeznaczone wyłącznie do **edukacyjnych i osobistych** celów.

Użytkownicy są odpowiedzialni za przestrzeganie:
- [Terms of Service Instagram](https://help.instagram.com/581066165581870)
- Lokalnych praw autorskich
- Prywatności innych użytkowników

Autor nie ponosi odpowiedzialności za niewłaściwe użycie tego narzędzia.

---

## 📧 Kontakt

Jeśli masz pytania lub sugestie:

- 🐛 **Zgłoś błąd:** [GitHub Issues](https://github.com/yourusername/instagram-content-downloader/issues)
- 💡 **Propozycja funkcji:** [GitHub Discussions](https://github.com/yourusername/instagram-content-downloader/discussions)
- 📧 **Email:** your.email@example.com

---

<div align="center">

**Zrobione z ❤️ w Polsce**

⭐ Jeśli projekt Ci się podoba, zostaw gwiazdkę na GitHub!

</div>
