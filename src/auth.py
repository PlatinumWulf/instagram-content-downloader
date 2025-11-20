#!/usr/bin/env python3
"""
Moduł autoryzacji - Instagram Content Downloader
Obsługuje logowanie, sesje i bezpieczeństwo
"""

import os
import json
import getpass
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import base64
import hashlib

logger = logging.getLogger(__name__)


class SessionEncryption:
    """
    Klasa do szyfrowania/deszyfrowania plików sesji

    Używa Fernet (symmetric encryption) z kluczem pochodnym hasła użytkownika
    """

    def __init__(self, password: Optional[str] = None):
        """
        Inicjalizacja szyfrowania sesji

        Args:
            password: Hasło do szyfrowania (jeśli None, używa klucza z envs)
        """
        self.key = self._derive_key(password)
        self.fernet = Fernet(self.key)

    def _derive_key(self, password: Optional[str]) -> bytes:
        """
        Tworzy klucz szyfrujący z hasła

        Args:
            password: Hasło użytkownika lub None

        Returns:
            32-bajtowy klucz Fernet
        """
        if password is None:
            # Użyj klucza z zmiennej środowiskowej lub wygeneruj nowy
            env_key = os.getenv('SESSION_ENCRYPTION_KEY')
            if env_key:
                return env_key.encode()
            else:
                # Wygeneruj klucz na podstawie nazwy użytkownika systemu
                system_user = os.getenv('USER') or os.getenv('USERNAME') or 'default'
                password = f"ig_downloader_{system_user}_secret"

        # Użyj PBKDF2 do stworzenia klucza z hasła
        kdf_salt = b'instagram_downloader_salt_v1'  # Stała sól (nie idealne, ale proste)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), kdf_salt, 100000)
        return base64.urlsafe_b64encode(key)

    def encrypt(self, data: str) -> bytes:
        """
        Szyfruje dane

        Args:
            data: Dane do zaszyfrowania (string lub JSON)

        Returns:
            Zaszyfrowane dane (bytes)
        """
        return self.fernet.encrypt(data.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Deszyfruje dane

        Args:
            encrypted_data: Zaszyfrowane dane

        Returns:
            Odszyfrowane dane (string)

        Raises:
            Exception: Jeśli deszyfrowanie się nie powiedzie
        """
        return self.fernet.decrypt(encrypted_data).decode()


class AuthManager:
    """
    Menedżer autoryzacji i sesji Instagram

    Obsługuje:
    - Logowanie przez login/hasło
    - Logowanie przez przeglądarkę
    - Zarządzanie sesjami (zapis/odczyt)
    - Szyfrowanie sesji
    - Wylogowanie
    """

    def __init__(self, loader, session_dir: str = 'data/sessions', encrypt_sessions: bool = True):
        """
        Inicjalizacja menedżera autoryzacji

        Args:
            loader: Instancja instaloader.Instaloader
            session_dir: Katalog do przechowywania sesji
            encrypt_sessions: Czy szyfrować pliki sesji
        """
        self.loader = loader
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.encrypt_sessions = encrypt_sessions

        self.logged_in = False
        self.username: Optional[str] = None
        self.encryption: Optional[SessionEncryption] = None

        # Ustaw uprawnienia katalogu sesji na 700 (rwx------)
        try:
            os.chmod(self.session_dir, 0o700)
        except Exception as e:
            logger.warning(f"Nie można zmienić uprawnień {self.session_dir}: {e}")

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Logowanie do Instagram przez login i hasło

        Args:
            username: Nazwa użytkownika (jeśli None, zapyta)
            password: Hasło (jeśli None, zapyta)

        Returns:
            True jeśli sukces, False jeśli błąd
        """
        try:
            import instaloader.exceptions as ig_exc

            # Najpierw spróbuj załadować zapisaną sesję
            if self._load_session():
                logger.info("Załadowano sesję z pliku")
                print("✅ Zalogowano przy użyciu zapisanej sesji")
                return True

            # Poproś o dane logowania jeśli nie podano
            if not username:
                username = input("📧 Nazwa użytkownika Instagram: ").strip()
            if not password:
                password = getpass.getpass("🔒 Hasło Instagram: ")

            if not username or not password:
                print("❌ Błąd: Nazwa użytkownika i hasło są wymagane")
                return False

            print("🔐 Loguję się do Instagram...")
            self.loader.login(username, password)

            self.logged_in = True
            self.username = username

            # Inicjalizuj szyfrowanie z hasłem użytkownika
            if self.encrypt_sessions:
                self.encryption = SessionEncryption(password)

            # Zapisz sesję
            self._save_session(username)

            print("✅ Pomyślnie zalogowano!")
            logger.info(f"Zalogowano jako {username}")
            return True

        except ig_exc.BadCredentialsException:
            print("❌ Błąd: Nieprawidłowe dane logowania!")
            logger.error("Nieprawidłowe dane logowania")
            return False

        except ig_exc.TwoFactorAuthRequiredException:
            print("🔐 Wymagane uwierzytelnianie dwuskładnikowe")
            code = input("Wprowadź kod 2FA: ").strip()

            try:
                self.loader.two_factor_login(code)
                self.logged_in = True
                self.username = username

                # Inicjalizuj szyfrowanie
                if self.encrypt_sessions and password:
                    self.encryption = SessionEncryption(password)

                self._save_session(username)
                print("✅ Pomyślnie zalogowano z 2FA!")
                logger.info(f"Zalogowano z 2FA jako {username}")
                return True

            except Exception as e:
                print(f"❌ Błąd 2FA: {e}")
                logger.error(f"Błąd 2FA: {e}")
                return False

        except ig_exc.ConnectionException as e:
            print(f"❌ Błąd połączenia: {e}")
            print("💡 Sprawdź połączenie internetowe i spróbuj ponownie")
            logger.error(f"Błąd połączenia podczas logowania: {e}")
            return False

        except Exception as e:
            print(f"❌ Błąd logowania: {e}")
            logger.error(f"Nieoczekiwany błąd logowania: {e}", exc_info=True)
            return False

    def login_browser(self, username: Optional[str] = None) -> bool:
        """
        Logowanie przez przeglądarkę (Selenium)

        Args:
            username: Opcjonalna nazwa użytkownika do wypełnienia

        Returns:
            True jeśli sukces, False jeśli błąd
        """
        try:
            # Import modułu browser_login
            try:
                # Próbuj zaimportować ze starego katalogu (kompatybilność wsteczna)
                import sys
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from browser_login import BrowserLogin
            except ImportError:
                try:
                    # Próbuj z katalogu src
                    from src.browser_auth import BrowserAuth as BrowserLogin
                except ImportError:
                    print("❌ Błąd: Brak modułu browser_login")
                    print("💡 Upewnij się, że plik browser_login.py lub browser_auth.py istnieje")
                    logger.error("Nie można zaimportować modułu browser login")
                    return False

            print("\n🌐 Logowanie przez przeglądarkę")
            print("=" * 60)
            print("✓ Bezpieczniejsze - używa prawdziwej przeglądarki")
            print("✓ Wygodniejsze - graficzny interfejs logowania")
            print("✓ Obsługuje captcha i 2FA automatycznie")
            print("=" * 60)

            # Stwórz instancję browser login
            browser_login = BrowserLogin()

            # Zaloguj się przez przeglądarkę
            result = browser_login.login_via_browser(username)

            if not result:
                print("❌ Logowanie przez przeglądarkę nieudane")
                logger.error("Logowanie przez przeglądarkę nieudane")
                return False

            # Importuj sesję do instaloader
            print("\n🔄 Importuję sesję...")

            # Pobierz sessionid z cookies
            sessionid = None
            for cookie in result.get('cookies', []):
                if cookie['name'] == 'sessionid':
                    sessionid = cookie['value']
                    break

            if not sessionid:
                print("❌ Nie znaleziono sessionid w cookies")
                logger.error("Brak sessionid w cookies z przeglądarki")
                return False

            # Pobierz username z result
            self.username = result.get('username') or username

            if not self.username:
                print("❌ Nie można określić nazwy użytkownika")
                logger.error("Brak username po logowaniu przez przeglądarkę")
                return False

            # WAŻNE: Ustaw wszystkie potrzebne cookies w loaderze
            for cookie in result.get('cookies', []):
                self.loader.context._session.cookies.set(
                    cookie['name'],
                    cookie['value'],
                    domain='.instagram.com'
                )

            # KRYTYCZNE: Ustaw username w context PRZED zapisem sesji
            self.loader.context.username = self.username
            self.logged_in = True

            # Teraz zapisz sesję (loader wie że jest zalogowany)
            self._save_session(self.username)

            print("✅ Pomyślnie zalogowano przez przeglądarkę!")
            logger.info(f"Zalogowano przez przeglądarkę jako {self.username}")
            return True

        except Exception as e:
            print(f"❌ Błąd logowania przez przeglądarkę: {e}")
            logger.error(f"Błąd logowania przez przeglądarkę: {e}", exc_info=True)
            return False

    def _save_session(self, username: str) -> None:
        """
        Zapisuje sesję do pliku

        Args:
            username: Nazwa użytkownika
        """
        try:
            # Przygotuj dane sesji
            session_data = {
                'username': username,
                'timestamp': datetime.now().isoformat(),
                'encrypted': self.encrypt_sessions
            }

            # Zapisz cookies sesji przez instaloader
            session_file_path = self.session_dir / f"session_{username}"
            self.loader.save_session_to_file(str(session_file_path))

            # Jeśli szyfrowanie włączone, zaszyfruj plik
            if self.encrypt_sessions and self.encryption:
                # Przeczytaj plik sesji
                with open(session_file_path, 'rb') as f:
                    session_content = f.read()

                # Zaszyfruj
                encrypted_content = self.encryption.encrypt(session_content.decode('latin-1'))

                # Zapisz zaszyfrowany plik
                with open(session_file_path, 'wb') as f:
                    f.write(encrypted_content)

                logger.info(f"Sesja zaszyfrowana i zapisana: {session_file_path}")

            # Zmień uprawnienia na 600 (rw-------)
            try:
                os.chmod(session_file_path, 0o600)
            except Exception as e:
                logger.warning(f"Nie można zmienić uprawnień pliku sesji: {e}")

            # Zapisz metadane sesji
            metadata_file = self.session_dir / "session.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)

            # Zmień uprawnienia metadanych
            try:
                os.chmod(metadata_file, 0o600)
            except Exception:
                pass

            print(f"💾 Sesja zapisana (będzie ważna przez ok. 90 dni)")
            logger.info(f"Sesja zapisana dla {username}")

        except Exception as e:
            print(f"⚠️  Nie udało się zapisać sesji: {e}")
            logger.error(f"Błąd zapisu sesji: {e}", exc_info=True)

    def _load_session(self) -> bool:
        """
        Ładuje zapisaną sesję

        Returns:
            True jeśli sesja załadowana, False w przeciwnym wypadku
        """
        try:
            metadata_file = self.session_dir / "session.json"

            if not metadata_file.exists():
                logger.debug("Brak pliku metadanych sesji")
                return False

            # Wczytaj metadane
            with open(metadata_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            username = session_data.get('username')
            is_encrypted = session_data.get('encrypted', False)

            if not username:
                logger.warning("Brak username w metadanych sesji")
                return False

            session_file_path = self.session_dir / f"session_{username}"

            if not session_file_path.exists():
                logger.debug(f"Brak pliku sesji dla {username}")
                return False

            # Jeśli sesja jest zaszyfrowana, odszyfruj
            if is_encrypted:
                if not self.encryption:
                    # Inicjalizuj szyfrowanie z domyślnym kluczem
                    self.encryption = SessionEncryption()

                try:
                    # Przeczytaj zaszyfrowany plik
                    with open(session_file_path, 'rb') as f:
                        encrypted_content = f.read()

                    # Odszyfruj
                    decrypted_content = self.encryption.decrypt(encrypted_content)

                    # Tymczasowo zapisz odszyfrowany plik
                    temp_file = session_file_path.with_suffix('.tmp')
                    with open(temp_file, 'w', encoding='latin-1') as f:
                        f.write(decrypted_content)

                    # Załaduj sesję
                    self.loader.load_session_from_file(username, str(temp_file))

                    # Usuń tymczasowy plik
                    temp_file.unlink()

                    logger.info(f"Załadowano zaszyfrowaną sesję dla {username}")
                    print(f"✅ Załadowano sesję użytkownika: {username}")

                except Exception as e:
                    logger.error(f"Błąd deszyfrowania sesji: {e}")
                    print(f"⚠️  Nie można odszyfrować sesji. Zaloguj się ponownie.")
                    return False
            else:
                # Załaduj niezaszyfrowaną sesję
                self.loader.load_session_from_file(username, str(session_file_path))
                logger.info(f"Załadowano niezaszyfrowaną sesję dla {username}")
                print(f"✅ Załadowano sesję użytkownika: {username}")

            self.logged_in = True
            self.username = username
            return True

        except Exception as e:
            logger.debug(f"Nie udało się załadować sesji: {e}")
            return False

    def logout(self) -> None:
        """
        Wylogowuje użytkownika i usuwa pliki sesji
        """
        try:
            # Usuń pliki sesji
            metadata_file = self.session_dir / "session.json"
            if metadata_file.exists():
                metadata_file.unlink()
                logger.info("Usunięto plik metadanych sesji")

            if self.username:
                session_file = self.session_dir / f"session_{self.username}"
                if session_file.exists():
                    session_file.unlink()
                    logger.info(f"Usunięto plik sesji dla {self.username}")

            self.logged_in = False
            self.username = None

            print("✅ Wylogowano i usunięto sesję")
            logger.info("Wylogowano")

        except Exception as e:
            print(f"⚠️  Błąd przy wylogowaniu: {e}")
            logger.error(f"Błąd wylogowania: {e}", exc_info=True)

    def is_logged_in(self) -> bool:
        """
        Sprawdza czy użytkownik jest zalogowany

        Returns:
            True jeśli zalogowany, False w przeciwnym wypadku
        """
        return self.logged_in

    def get_username(self) -> Optional[str]:
        """
        Pobiera nazwę zalogowanego użytkownika

        Returns:
            Nazwa użytkownika lub None
        """
        return self.username
