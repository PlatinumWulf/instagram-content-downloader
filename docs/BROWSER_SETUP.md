# Instalacja Logowania przez Przeglądarkę

Przewodnik po instalacji Selenium i WebDriver dla funkcji logowania przez przeglądarkę.

## Krok 1: Zainstaluj Selenium

```bash
pip install selenium
```

## Krok 2: Wybierz i zainstaluj WebDriver

### Opcja A: Chrome (Polecane)

**Automatyczna instalacja:**
```bash
pip install chromedriver-autoinstaller
```

Następnie uruchom w Pythonie jeden raz:
```python
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
```

**Ręczna instalacja:**

1. Sprawdź wersję Chrome:
   - Otwórz Chrome
   - Wejdź na `chrome://settings/help`
   - Zanotuj numer wersji (np. 120.0.6099.109)

2. Pobierz odpowiedni ChromeDriver:
   - https://chromedriver.chromium.org/downloads
   - Pobierz wersję pasującą do twojego Chrome

3. Rozpakuj i dodaj do PATH:
   - **Windows:** Skopiuj `chromedriver.exe` do `C:\Windows\System32\`
   - **Linux/Mac:** Przenieś do `/usr/local/bin/` i ustaw uprawnienia: `chmod +x chromedriver`

### Opcja B: Firefox

**Automatyczna instalacja:**
```bash
pip install webdriver-manager
```

**Ręczna instalacja:**

1. Pobierz GeckoDriver:
   - https://github.com/mozilla/geckodriver/releases
   - Pobierz najnowszą wersję dla twojego systemu

2. Rozpakuj i dodaj do PATH:
   - **Windows:** Skopiuj `geckodriver.exe` do `C:\Windows\System32\`
   - **Linux/Mac:** Przenieś do `/usr/local/bin/` i ustaw uprawnienia: `chmod +x geckodriver`

## Krok 3: Testuj instalację

Uruchom skrypt testowy:

```bash
python browser_login.py
```

Jeśli przeglądarka się otworzy, instalacja jest poprawna!

## Rozwiązywanie problemów

### Problem: "chromedriver not found"

**Rozwiązanie:**
```bash
pip install chromedriver-autoinstaller
python -c "import chromedriver_autoinstaller; chromedriver_autoinstaller.install()"
```

### Problem: "Chrome version mismatch"

**Rozwiązanie:**
- Zaktualizuj Chrome do najnowszej wersji
- Pobierz odpowiedni ChromeDriver dla twojej wersji Chrome
- Lub użyj Firefox zamiast Chrome

### Problem: "selenium module not found"

**Rozwiązanie:**
```bash
pip install --upgrade selenium
```

### Problem: Przeglądarka nie otwiera się

**Rozwiązanie:**
1. Sprawdź czy Chrome/Firefox jest zainstalowany
2. Spróbuj użyć drugiej przeglądarki
3. Użyj tradycyjnego logowania (opcja 3 w menu)

## Alternatywa: Logowanie bez przeglądarki

Jeśli nie możesz zainstalować Selenium, użyj:

**Opcja 1:** Tradycyjne logowanie (opcja 3 w menu)
```bash
python instagram_downloader.py
# Wybierz opcję 3
```

**Opcja 2:** Wersja bez logowania (wolniejsza)
```bash
python instagram_downloader_nologin.py username
```

## Testowanie

Po instalacji, przetestuj:

```bash
python instagram_downloader.py
# Wybierz opcję 2 (Zaloguj się przez przeglądarkę)
```

Jeśli przeglądarka się otworzy i możesz się zalogować - instalacja OK!

## Często zadawane pytania

**Q: Czy muszę instalować Selenium?**
A: Nie, możesz używać opcji 3 (tradycyjne logowanie) lub wersji nologin.

**Q: Która przeglądarka jest lepsza?**
A: Chrome jest bardziej stabilny i częściej testowany.

**Q: Czy logowanie przez przeglądarkę jest bezpieczne?**
A: Tak, skrypt używa prawdziwej przeglądarki i oficjalnego Instagram. Twoje dane nie są nigdzie wysyłane oprócz Instagram.

**Q: Czy muszę być zalogowany?**
A: Nie dla publicznych profili, ale logowanie zapobiega rate limitom (błędy 403/401).

## Dodatkowe zasoby

- Dokumentacja Selenium: https://selenium-python.readthedocs.io/
- ChromeDriver: https://chromedriver.chromium.org/
- GeckoDriver: https://github.com/mozilla/geckodriver
