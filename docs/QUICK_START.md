# Quick Start Guide

## Szybki start w 3 krokach

### 1. Instalacja
```bash
pip install instaloader
```

### 2. Uruchom skrypt
```bash
python instagram_downloader.py
```

### 3. Postępuj zgodnie z menu

```
============================================================
MENU GŁÓWNE
============================================================
1. Pobierz profil (bez logowania)
2. Zaloguj się przez przeglądarkę 🌐 (POLECANE)
3. Zaloguj się (login/hasło)
4. Pobierz profil (zalogowany)
5. Konfiguracja pobierania
6. Wyloguj się
0. Wyjście
============================================================
```

## Scenariusze użycia

### Scenariusz 1: Szybkie pobieranie bez logowania
**Cel:** Pobrać posty z publicznego profilu

1. Uruchom: `python instagram_downloader.py username`
2. Poczekaj na zakończenie
3. Znajdź pliki w folderze `username/`

**Ograniczenia:** Możliwe rate limity, brak dostępu do stories

---

### Scenariusz 2: Pełne pobieranie z logowaniem (polecane)
**Cel:** Pobrać wszystko (posty, stories, highlights) bez rate limitów

**Metoda A: Przez przeglądarkę (łatwiejsza):**
1. Uruchom: `python instagram_downloader.py`
2. Wybierz opcję `2` (Zaloguj się przez przeglądarkę)
3. Zaloguj się w przeglądarce jak zwykle
4. Naciśnij Enter w terminalu
5. Wybierz opcję `4` (Pobierz profil zalogowany)
6. Podaj nazwę profilu
7. Wybierz `4` (Wszystko)

**Metoda B: Przez terminal:**
1. Uruchom: `python instagram_downloader.py`
2. Wybierz opcję `3` (Zaloguj się login/hasło)
3. Podaj login i hasło Instagram
4. Wybierz opcję `4` (Pobierz profil zalogowany)
5. Podaj nazwę profilu
6. Wybierz `4` (Wszystko)

**Zalety:**
- Brak rate limitów
- Dostęp do stories i highlights
- Sesja zapisana na 90 dni
- Metoda przez przeglądarkę bezpieczniejsza

---

### Scenariusz 3: Pobieranie własnego profilu
**Cel:** Backup własnego konta Instagram

1. Uruchom: `python instagram_downloader.py -l`
2. Zaloguj się na swoje konto
3. Uruchom ponownie: `python instagram_downloader.py`
4. Wybierz `3`, podaj swoją nazwę użytkownika
5. Wybierz `4` (Wszystko)

---

## Częste komendy

| Komenda | Opis |
|---------|------|
| `python instagram_downloader.py` | Tryb interaktywny |
| `python instagram_downloader.py -l` | Tylko logowanie |
| `python instagram_downloader.py -h` | Pomoc |
| `python instagram_downloader.py username` | Szybkie pobieranie |

## Rozwiązywanie problemów - TL;DR

| Problem | Rozwiązanie |
|---------|-------------|
| 403/401 błędy | Zaloguj się opcją `-l` |
| Rate limit | Zwiększ sleep_time w konfiguracji (opcja 4) |
| Profil prywatny | Zaloguj się kontem które go obserwuje |
| Brak stories | Stories wymagają zalogowania |

## Tips & Tricks

1. **Zaloguj się raz** - sesja będzie ważna przez 90 dni
2. **Zwiększ sleep_time do 5-10s** dla dużych profili (1000+ postów)
3. **Ctrl+C bezpiecznie przerywa** - możesz wznowić później
4. **Już pobrane pliki są pomijane** - bezpieczne ponowne uruchomienie

## Następne kroki

Przeczytaj pełny [README.md](README.md) aby poznać wszystkie funkcje.
