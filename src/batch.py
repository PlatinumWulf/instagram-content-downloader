#!/usr/bin/env python3
"""
Moduł pobierania wsadowego - Instagram Content Downloader
Obsługuje pobieranie wielu profili z listy
"""

import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from src.downloader import InstagramDownloader
from src.config import ConfigManager
from src.utils import parse_profile_list_file, print_header, print_separator

logger = logging.getLogger(__name__)


class BatchDownloader:
    """
    Klasa do pobierania wsadowego wielu profili

    Obsługuje:
    - Pobieranie z pliku tekstowego
    - Tracking niepowodzeń
    - Zapisywanie stanu (możliwość wznowienia)
    - Statystyki
    """

    def __init__(self, downloader: InstagramDownloader, delay_between: int = 60):
        """
        Inicjalizacja batch downloadera

        Args:
            downloader: Instancja InstagramDownloader
            delay_between: Opóźnienie między profilami (sekundy)
        """
        self.downloader = downloader
        self.delay_between = delay_between
        self.failed_profiles: List[tuple] = []  # (username, error)
        self.stats = {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'skipped': 0
        }

    def download_from_file(
        self,
        file_path: str,
        download_options: Optional[Dict[str, bool]] = None,
        save_failed: bool = True
    ) -> Dict[str, Any]:
        """
        Pobiera profile z pliku tekstowego

        Args:
            file_path: Ścieżka do pliku z listą profili
            download_options: Opcje pobierania
            save_failed: Czy zapisać niepowodzenia do pliku

        Returns:
            Słownik ze statystykami
        """
        # Wczytaj listę profili
        try:
            profiles = parse_profile_list_file(file_path)
        except (FileNotFoundError, ValueError) as e:
            print(f"❌ Błąd wczytywania pliku: {e}")
            logger.error(f"Błąd wczytywania pliku profili: {e}")
            return {'success': False, 'error': str(e)}

        self.stats['total'] = len(profiles)

        print_header(f"📦 POBIERANIE WSADOWE - {len(profiles)} PROFILI")
        logger.info(f"Rozpoczynam pobieranie wsadowe {len(profiles)} profili")

        # Pobierz każdy profil
        for i, username in enumerate(profiles, 1):
            print(f"\n{'='*60}")
            print(f"Profil {i}/{len(profiles)}: {username}")
            print(f"{'='*60}")

            try:
                # Pobierz profil
                result = self.downloader.download_profile(
                    username,
                    download_options=download_options
                )

                if result.get('success'):
                    self.stats['completed'] += 1
                    logger.info(f"✓ Ukończono {username}")
                else:
                    self.stats['failed'] += 1
                    error = result.get('error', 'Nieznany błąd')
                    self.failed_profiles.append((username, error))
                    logger.error(f"✗ Nieudane {username}: {error}")

            except KeyboardInterrupt:
                print(f"\n\n⚠️  Przerwano przez użytkownika")
                print(f"📊 Postęp: {i-1}/{len(profiles)} profili")
                logger.warning("Przerwano pobieranie wsadowe przez użytkownika")
                break

            except Exception as e:
                self.stats['failed'] += 1
                error_msg = str(e)
                self.failed_profiles.append((username, error_msg))
                print(f"❌ Błąd dla {username}: {e}")
                logger.error(f"Błąd pobierania {username}: {e}", exc_info=True)

            # Czekaj przed następnym profilem (oprócz ostatniego)
            if i < len(profiles):
                print(f"\n⏳ Czekam {self.delay_between}s przed następnym profilem...")

                for _ in tqdm(
                    range(self.delay_between),
                    desc="Czekam",
                    unit="s",
                    leave=False,
                    ncols=60
                ):
                    time.sleep(1)

        # Podsumowanie
        self._print_summary()

        # Zapisz niepowodzenia do pliku
        if save_failed and self.failed_profiles:
            self._save_failed_profiles()

        logger.info(
            f"Zakończono batch download: "
            f"{self.stats['completed']} OK, "
            f"{self.stats['failed']} błędów, "
            f"{self.stats['skipped']} pominiętych"
        )

        return {
            'success': True,
            'stats': self.stats,
            'failed': self.failed_profiles
        }

    def download_from_list(
        self,
        usernames: List[str],
        download_options: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Pobiera profile z listy

        Args:
            usernames: Lista nazw użytkowników
            download_options: Opcje pobierania

        Returns:
            Słownik ze statystykami
        """
        self.stats['total'] = len(usernames)

        print_header(f"📦 POBIERANIE WSADOWE - {len(usernames)} PROFILI")
        logger.info(f"Rozpoczynam pobieranie {len(usernames)} profili z listy")

        for i, username in enumerate(usernames, 1):
            print(f"\n{'='*60}")
            print(f"Profil {i}/{len(usernames)}: {username}")
            print(f"{'='*60}")

            try:
                result = self.downloader.download_profile(
                    username,
                    download_options=download_options
                )

                if result.get('success'):
                    self.stats['completed'] += 1
                else:
                    self.stats['failed'] += 1
                    error = result.get('error', 'Nieznany błąd')
                    self.failed_profiles.append((username, error))

            except KeyboardInterrupt:
                print(f"\n\n⚠️  Przerwano przez użytkownika")
                logger.warning("Przerwano batch download")
                break

            except Exception as e:
                self.stats['failed'] += 1
                self.failed_profiles.append((username, str(e)))
                logger.error(f"Błąd {username}: {e}", exc_info=True)

            # Czekaj przed następnym
            if i < len(usernames):
                for _ in tqdm(
                    range(self.delay_between),
                    desc="Czekam",
                    unit="s",
                    leave=False,
                    ncols=60
                ):
                    time.sleep(1)

        self._print_summary()

        return {
            'success': True,
            'stats': self.stats,
            'failed': self.failed_profiles
        }

    def _print_summary(self) -> None:
        """Wyświetla podsumowanie pobierania wsadowego"""
        print_separator("=")
        print("📊 PODSUMOWANIE POBIERANIA WSADOWEGO")
        print_separator("=")
        print(f"✅ Ukończone: {self.stats['completed']}/{self.stats['total']}")
        print(f"❌ Nieudane: {self.stats['failed']}")

        if self.failed_profiles:
            print(f"\n⚠️  Nieudane profile:")
            for username, error in self.failed_profiles:
                # Ogranicz długość błędu
                error_short = error[:60] + "..." if len(error) > 60 else error
                print(f"  - {username}: {error_short}")

        print_separator("=")

    def _save_failed_profiles(self, filename: str = "failed_profiles.txt") -> None:
        """
        Zapisuje listę nieudanych profili do pliku

        Args:
            filename: Nazwa pliku
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# Nieudane profile - Instagram Content Downloader\n")
                f.write(f"# Wygenerowano: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                for username, error in self.failed_profiles:
                    f.write(f"# Błąd: {error}\n")
                    f.write(f"{username}\n\n")

            print(f"\n💾 Lista nieudanych profili zapisana do: {filename}")
            logger.info(f"Zapisano nieudane profile do {filename}")

        except Exception as e:
            print(f"⚠️  Nie można zapisać listy nieudanych: {e}")
            logger.error(f"Błąd zapisu failed_profiles: {e}")


def create_example_profiles_file(filename: str = "config/profiles.example.txt") -> None:
    """
    Tworzy przykładowy plik z listą profili

    Args:
        filename: Ścieżka do pliku
    """
    example_content = """# Przykładowa lista profili do pobrania
# Instagram Content Downloader
#
# Format:
# - Jeden profil na linię
# - Linie zaczynające się od # to komentarze
# - Możesz użyć nazwy użytkownika lub pełnego URL
# - Puste linie są ignorowane

# Przykłady różnych formatów:
better.engineer
https://www.instagram.com/web.dev.peter/
@theaipeter
instagram.com/codewithpeter/

# Więcej przykładów:
# natgeo
# nasa
# spacex

# Usuń # aby odkomentować:
# twoja_ulubiona_nazwa
# inny_profil
"""

    try:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(example_content)
        print(f"✓ Utworzono przykładowy plik: {filename}")
        logger.info(f"Utworzono przykładowy plik profili: {filename}")
    except Exception as e:
        print(f"⚠️  Nie można utworzyć pliku: {e}")
        logger.error(f"Błąd tworzenia przykładowego pliku: {e}")
