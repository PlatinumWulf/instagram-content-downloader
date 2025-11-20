# 🚀 Szybka Instalacja - Instagram Content Downloader v3.0

## Krok 1: Zainstaluj zależności

```bash
# Podstawowa instalacja
pip install -r requirements.txt

# Lub ręcznie:
pip install instaloader python-dotenv cryptography tqdm selenium pytest pytest-cov
```

## Krok 2: Konfiguracja (Opcjonalna)

```bash
# Skopiuj przykładowy plik .env
cp .env.example .env

# Edytuj .env (opcjonalnie)
nano .env  # Lub inny edytor
```

**Uwaga:** NIE musisz edytować .env - domyślne ustawienia działają od razu!

## Krok 3: Pierwsze uruchomienie

```bash
# Tryb interaktywny
python3 main.py

# Lub szybkie pobieranie
python3 main.py username

# Pomoc
python3 main.py --help
```

## Instalacja jako pakiet (Opcjonalnie)

```bash
# Instalacja w trybie development
pip install -e .

# Teraz możesz uruchomić z dowolnego miejsca:
ig-downloader
instagram-downloader
```

## Testowanie

```bash
# Uruchom testy
pytest

# Z pokryciem kodu
pytest --cov=src

# Verbose
pytest -v
```

## Troubleshooting

### ModuleNotFoundError

```bash
# Upewnij się że zainstalowałeś zależności:
pip install -r requirements.txt

# Lub zainstaluj jako pakiet:
pip install -e .
```

### Permission denied

```bash
# Dodaj uprawnienia wykonywania:
chmod +x main.py

# Uruchom:
./main.py
```

## Gotowe!

Wszystko działa. Sprawdź [README.md](README.md) dla pełnej dokumentacji.

---

**Szybki start:** `python3 main.py -i`
