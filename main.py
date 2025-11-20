#!/usr/bin/env python3
"""
Instagram Content Downloader - Główny plik programu
Narzędzie do pobierania zawartości z profili Instagram
"""

import sys
import argparse
from pathlib import Path

# Dodaj src do ścieżki importu
sys.path.insert(0, str(Path(__file__).parent))

from src.config import ConfigManager
from src.downloader import InstagramDownloader
from src.batch import BatchDownloader
from src.logger_setup import setup_logging_from_env
from src.utils import print_header, print_separator

__version__ = "3.0.0"


def interactive_mode(downloader: InstagramDownloader) -> None:
    """
    Tryb interaktywny z menu

    Args:
        downloader: Instancja InstagramDownloader
    """
    print_header("📸 Instagram Content Downloader - Tryb Interaktywny", "=")

    while True:
        print_separator("=")
        print("MENU GŁÓWNE".center(60))
        print_separator("=")
        print("1. Pobierz profil (bez logowania)")
        print("2. Zaloguj się przez przeglądarkę 🌐 (POLECANE)")
        print("3. Zaloguj się (login/hasło)")
        print("4. Pobierz profil (zalogowany)")
        print("5. Pobieranie wsadowe z pliku")
        print("6. Konfiguracja")
        print("7. Wyloguj się")
        print("0. Wyjście")
        print_separator("=")

        choice = input("\nWybierz opcję (0-7): ").strip()

        if choice == '1':
            # Pobierz bez logowania
            profile_url = input("\n📥 Podaj nazwę użytkownika lub URL: ").strip()
            if profile_url:
                downloader.download_profile(profile_url)

        elif choice == '2':
            # Logowanie przez przeglądarkę
            username = input("\n📧 Nazwa użytkownika (opcjonalne, Enter aby pominąć): ").strip()
            if downloader.auth.login_browser(username or None):
                print("\n✅ Zalogowano pomyślnie przez przeglądarkę!")
                # WAŻNE: Sesja jest już załadowana w obiekcie downloader.auth
                # Nie trzeba restartować programu!
            else:
                print("\n❌ Logowanie nieudane")

        elif choice == '3':
            # Logowanie login/hasło
            if downloader.auth.login():
                print("\n✅ Zalogowano pomyślnie!")
            else:
                print("\n❌ Logowanie nieudane")

        elif choice == '4':
            # Pobierz jako zalogowany
            if not downloader.auth.is_logged_in():
                print("\n⚠️  Najpierw się zaloguj (opcja 2 lub 3)")
                continue

            profile_url = input("\n📥 Podaj nazwę użytkownika lub URL: ").strip()
            if not profile_url:
                continue

            print("\n📦 Co chcesz pobrać?")
            print("1. Tylko posty")
            print("2. Posty + Stories")
            print("3. Posty + Highlights")
            print("4. Wszystko (Posty + Stories + Highlights + Tagged + IGTV)")
            print("5. Własny wybór")

            dl_choice = input("\nWybierz (1-5): ").strip()

            options = {}
            if dl_choice == '1':
                options = {'download_posts': True}
            elif dl_choice == '2':
                options = {'download_posts': True, 'download_stories': True}
            elif dl_choice == '3':
                options = {'download_posts': True, 'download_highlights': True}
            elif dl_choice == '4':
                options = {
                    'download_posts': True,
                    'download_stories': True,
                    'download_highlights': True,
                    'download_tagged': True,
                    'download_igtv': True
                }
            elif dl_choice == '5':
                print("\n")
                options = {
                    'download_posts': input("Pobierać posty? (t/n): ").lower() == 't',
                    'download_stories': input("Pobierać stories? (t/n): ").lower() == 't',
                    'download_highlights': input("Pobierać highlights? (t/n): ").lower() == 't',
                    'download_tagged': input("Pobierać tagged? (t/n): ").lower() == 't',
                    'download_igtv': input("Pobierać IGTV? (t/n): ").lower() == 't',
                }
            else:
                options = {'download_posts': True}

            downloader.download_profile(profile_url, download_options=options)

        elif choice == '5':
            # Pobieranie wsadowe
            file_path = input("\n📄 Podaj ścieżkę do pliku z listą profili: ").strip()
            if not file_path:
                continue

            delay = input("⏱️  Opóźnienie między profilami w sekundach (domyślnie 60): ").strip()
            delay_between = int(delay) if delay else 60

            batch = BatchDownloader(downloader, delay_between=delay_between)
            batch.download_from_file(file_path)

        elif choice == '6':
            # Konfiguracja
            _configure_settings(downloader)

        elif choice == '7':
            # Wyloguj
            downloader.auth.logout()

        elif choice == '0':
            # Wyjście
            print("\n👋 Do zobaczenia!")
            break

        else:
            print("\n❌ Nieprawidłowa opcja")


def _configure_settings(downloader: InstagramDownloader) -> None:
    """
    Konfiguracja ustawień

    Args:
        downloader: Instancja InstagramDownloader
    """
    print_separator("=")
    print("KONFIGURACJA".center(60))
    print_separator("=")

    try:
        # Rate limiting
        sleep_time = input(f"Opóźnienie między requestami (sekundy, domyślnie 3): ").strip()
        if sleep_time:
            downloader.config.set('sleep_time', float(sleep_time))
            downloader.rate_limiter.base_delay = float(sleep_time)

        # Opcje mediów
        print("\nOpcje mediów:")
        download_videos = input("Pobierać wideo? (t/n, domyślnie t): ").lower()
        if download_videos:
            downloader.config.set('download_videos', download_videos == 't')

        download_comments = input("Pobierać komentarze? (t/n, domyślnie n): ").lower()
        if download_comments == 't':
            downloader.config.set('download_comments', True)

        download_geotags = input("Pobierać geotagi? (t/n, domyślnie n): ").lower()
        if download_geotags == 't':
            downloader.config.set('download_geotags', True)

        # Zapisz do pliku
        save_config = input("\n💾 Zapisać konfigurację do pliku? (t/n): ").lower()
        if save_config == 't':
            downloader.config.save_to_file()

        print("\n✅ Konfiguracja zaktualizowana")

    except Exception as e:
        print(f"\n⚠️  Błąd konfiguracji: {e}")


def main() -> None:
    """Główna funkcja programu"""
    # Konfiguruj logowanie
    setup_logging_from_env()

    # Header
    print_separator("=")
    print(f"📸 Instagram Content Downloader v{__version__}".center(60))
    print_separator("=")

    # Parsowanie argumentów
    parser = argparse.ArgumentParser(
        description="Narzędzie do pobierania zawartości z profili Instagram",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python main.py                              # Tryb interaktywny
  python main.py username                     # Szybkie pobieranie profilu
  python main.py https://instagram.com/user/  # Pobierz z URL
  python main.py -i                           # Tryb interaktywny
  python main.py -l                           # Tylko logowanie
  python main.py -b profiles.txt              # Pobieranie wsadowe
  python main.py --config                     # Pokaż konfigurację

Więcej informacji: https://github.com/user/ig_content_downloader
        """
    )

    parser.add_argument(
        'profile',
        nargs='?',
        help='Nazwa użytkownika lub URL profilu do pobrania'
    )

    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Uruchom w trybie interaktywnym'
    )

    parser.add_argument(
        '-l', '--login',
        action='store_true',
        help='Tylko zaloguj się i zapisz sesję'
    )

    parser.add_argument(
        '-b', '--batch',
        metavar='FILE',
        help='Pobieranie wsadowe z pliku'
    )

    parser.add_argument(
        '--browser-login',
        action='store_true',
        help='Zaloguj się przez przeglądarkę'
    )

    parser.add_argument(
        '--config',
        action='store_true',
        help='Pokaż aktualną konfigurację'
    )

    parser.add_argument(
        '--posts',
        action='store_true',
        help='Pobieraj posty (domyślnie włączone)'
    )

    parser.add_argument(
        '--stories',
        action='store_true',
        help='Pobieraj stories (wymaga logowania)'
    )

    parser.add_argument(
        '--highlights',
        action='store_true',
        help='Pobieraj highlights'
    )

    parser.add_argument(
        '--tagged',
        action='store_true',
        help='Pobieraj tagged posts'
    )

    parser.add_argument(
        '--igtv',
        action='store_true',
        help='Pobieraj IGTV'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Pobieraj wszystko (posty, stories, highlights, tagged, IGTV)'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'Instagram Content Downloader v{__version__}'
    )

    args = parser.parse_args()

    # Załaduj konfigurację
    config = ConfigManager()

    # Inicjalizuj downloader
    downloader = InstagramDownloader(config)

    # Obsługa różnych trybów
    if args.config:
        # Pokaż konfigurację
        print(config)
        return

    if args.interactive or (not args.profile and not args.login and not args.batch and not args.browser_login):
        # Tryb interaktywny
        interactive_mode(downloader)
        return

    if args.login or args.browser_login:
        # Tylko logowanie
        if args.browser_login:
            downloader.auth.login_browser()
        else:
            downloader.auth.login()
        return

    if args.batch:
        # Pobieranie wsadowe
        batch = BatchDownloader(downloader)
        batch.download_from_file(args.batch)
        return

    if args.profile:
        # Szybkie pobieranie
        # Spróbuj załadować sesję
        downloader.auth._load_session()

        # Przygotuj opcje pobierania
        download_options = {}

        if args.all:
            download_options = {
                'download_posts': True,
                'download_stories': True,
                'download_highlights': True,
                'download_tagged': True,
                'download_igtv': True
            }
        else:
            if args.posts or not (args.stories or args.highlights or args.tagged or args.igtv):
                download_options['download_posts'] = True
            if args.stories:
                download_options['download_stories'] = True
            if args.highlights:
                download_options['download_highlights'] = True
            if args.tagged:
                download_options['download_tagged'] = True
            if args.igtv:
                download_options['download_igtv'] = True

        # Pobierz profil
        downloader.download_profile(args.profile, download_options=download_options)
        return

    # Jeśli nic nie wybrano, pokaż pomoc
    parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Przerwano przez użytkownika")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Krytyczny błąd: {e}")
        import logging
        logging.error(f"Krytyczny błąd: {e}", exc_info=True)
        sys.exit(1)
