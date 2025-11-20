#!/usr/bin/env python3
"""
Moduł główny pobierania - Instagram Content Downloader
Obsługuje pobieranie różnych typów zawartości z Instagram
"""

import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from tqdm import tqdm

import instaloader
import instaloader.exceptions as ig_exc

from src.config import ConfigManager
from src.auth import AuthManager
from src.utils import (
    validate_username,
    extract_username_from_url,
    ensure_directory,
    calculate_rate_limit_delay,
    print_header,
    print_separator
)

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Inteligentny rate limiter z adaptive backoff

    Automatycznie dostosowuje opóźnienia na podstawie błędów rate limiting
    """

    def __init__(self, base_delay: float = 3.0, min_delay: float = 2.0, max_delay: float = 30.0):
        """
        Inicjalizacja rate limitera

        Args:
            base_delay: Bazowe opóźnienie w sekundach
            min_delay: Minimalne opóźnienie
            max_delay: Maksymalne opóźnienie
        """
        self.base_delay = base_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.current_delay = base_delay
        self.error_count = 0
        self.success_count = 0

    def wait(self, description: str = "Czekam") -> None:
        """
        Czeka z wyświetlaniem paska postępu

        Args:
            description: Opis wyświetlany na pasku postępu
        """
        delay = max(self.min_delay, min(self.current_delay, self.max_delay))

        if delay <= 1:
            time.sleep(delay)
            return

        # Użyj tqdm dla progress bara
        for _ in tqdm(range(int(delay)), desc=description, unit="s", leave=False, ncols=80):
            time.sleep(1)

        # Poczekaj pozostałą część (jeśli delay nie jest całkowite)
        remainder = delay - int(delay)
        if remainder > 0:
            time.sleep(remainder)

    def on_success(self) -> None:
        """Wywołaj po udanym pobraniu - zmniejsza opóźnienie"""
        self.error_count = 0
        self.success_count += 1

        # Powoli zmniejszaj opóźnienie po sukcesach
        if self.success_count >= 10:
            self.current_delay = max(self.min_delay, self.current_delay * 0.9)
            self.success_count = 0
            logger.debug(f"Zmniejszono opóźnienie do {self.current_delay:.1f}s")

    def on_error(self, is_rate_limit: bool = False) -> None:
        """
        Wywołaj po błędzie - zwiększa opóźnienie

        Args:
            is_rate_limit: Czy błąd to rate limiting
        """
        self.success_count = 0
        self.error_count += 1

        if is_rate_limit:
            # Agresywne zwiększenie dla rate limit
            self.current_delay = min(self.max_delay, self.current_delay * 2.0)
            logger.warning(f"Rate limit hit! Zwiększono opóźnienie do {self.current_delay:.1f}s")
        else:
            # Łagodniejsze zwiększenie dla innych błędów
            self.current_delay = min(self.max_delay, self.current_delay * 1.2)
            logger.debug(f"Błąd - zwiększono opóźnienie do {self.current_delay:.1f}s")

    def reset(self) -> None:
        """Resetuje rate limiter do wartości początkowych"""
        self.current_delay = self.base_delay
        self.error_count = 0
        self.success_count = 0


class InstagramDownloader:
    """
    Główna klasa do pobierania zawartości z Instagram

    Obsługuje:
    - Pobieranie postów, stories, highlights, tagged, IGTV
    - Inteligentne rate limiting
    - Progress tracking
    - Error handling z retry logic
    - Wznowienie przerwanych pobierań
    """

    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Inicjalizacja downloadera

        Args:
            config: Menedżer konfiguracji (jeśli None, użyje domyślnego)
        """
        # Załaduj konfigurację
        self.config = config or ConfigManager()

        # Inicjalizuj Instaloader
        self.loader = instaloader.Instaloader(
            download_videos=self.config.get('download_videos', True),
            download_video_thumbnails=self.config.get('download_thumbnails', True),
            download_geotags=self.config.get('download_geotags', False),
            download_comments=self.config.get('download_comments', False),
            save_metadata=self.config.get('save_metadata', True),
            compress_json=self.config.get('compress_json', False),
            post_metadata_txt_pattern='',  # Wyłącz txt metadata (mamy JSON)
            max_connection_attempts=self.config.get('max_attempts', 3),
            request_timeout=self.config.get('request_timeout', 300.0)
        )

        # Inicjalizuj menedżera autoryzacji
        session_dir = self.config.get('session_dir', 'data/sessions')
        self.auth = AuthManager(
            loader=self.loader,
            session_dir=session_dir,
            encrypt_sessions=True
        )

        # Inicjalizuj rate limiter
        self.rate_limiter = RateLimiter(
            base_delay=self.config.get('sleep_time', 3.0),
            min_delay=self.config.get('min_sleep_time', 2.0),
            max_delay=self.config.get('max_sleep_time', 30.0)
        )

        # Katalog pobierania
        self.download_dir = Path(self.config.get('download_dir', 'data/downloads'))
        ensure_directory(self.download_dir)

        # AUTOMATYCZNIE załaduj sesję jeśli istnieje
        self.auth._load_session()

        logger.info("InstagramDownloader zainicjalizowany")

    def download_profile(
        self,
        profile_url: str,
        download_options: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Pobiera zawartość profilu Instagram

        Args:
            profile_url: URL profilu lub nazwa użytkownika
            download_options: Słownik z opcjami pobierania (co pobierać)

        Returns:
            Słownik ze statystykami pobierania
        """
        # Wyciągnij i zwaliduj nazwę użytkownika
        try:
            username = extract_username_from_url(profile_url)
            logger.info(f"Rozpoczynam pobieranie profilu: {username}")
        except ValueError as e:
            print(f"❌ Błąd: {e}")
            logger.error(f"Nieprawidłowa nazwa profilu: {profile_url}")
            return {'success': False, 'error': str(e)}

        # Przygotuj opcje pobierania
        options = download_options or {}

        # Statystyki
        stats = {
            'username': username,
            'success': False,
            'downloaded': {
                'posts': 0,
                'stories': 0,
                'highlights': 0,
                'tagged': 0,
                'igtv': 0
            },
            'errors': []
        }

        try:
            print(f"\n📥 Pobieram profil: {username}")
            logger.info(f"Pobieranie profilu {username}")

            # OSTRZEŻENIE: Instagram BARDZO często blokuje nieautoryzowane requesty
            if not self.auth.is_logged_in():
                print("\n⚠️  UWAGA: Nie jesteś zalogowany!")
                print("Instagram bardzo często blokuje pobieranie bez logowania (403 Forbidden).")
                print("Zalecane działania:")
                print("  1. Zaloguj się: python3 main.py --browser-login")
                print("  2. Lub: python3 main.py --login")
                print("  3. Następnie spróbuj ponownie pobrać profil")
                print("\nKontynuuję bez logowania (może się nie udać)...\n")
                logger.warning(f"Pobieranie {username} bez logowania - wysokie ryzyko blokady")

            # Pobierz obiekt profilu
            try:
                profile = instaloader.Profile.from_username(
                    self.loader.context,
                    username
                )
            except ig_exc.ProfileNotExistsException:
                error_msg = f"Profil '{username}' nie istnieje!"
                print(f"❌ Błąd: {error_msg}")
                logger.error(error_msg)
                stats['errors'].append(error_msg)
                return stats
            except ig_exc.ConnectionException as e:
                error_msg = f"Błąd połączenia: {e}"
                print(f"❌ {error_msg}")
                print("💡 Wskazówka: Sprawdź połączenie internetowe")
                logger.error(error_msg)
                stats['errors'].append(error_msg)
                return stats

            # Wyświetl informacje o profilu
            self._display_profile_info(profile)

            # Przygotuj katalog docelowy
            target_dir = self.download_dir / username
            ensure_directory(target_dir)

            # Pobieraj różne typy zawartości
            if options.get('download_posts', self.config.get('download_posts', True)):
                try:
                    count = self._download_posts(profile, username)
                    stats['downloaded']['posts'] = count
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Błąd pobierania postów: {e}", exc_info=True)
                    stats['errors'].append(f"Posty: {e}")

            if options.get('download_stories', self.config.get('download_stories', False)):
                try:
                    count = self._download_stories(profile, username)
                    stats['downloaded']['stories'] = count
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Błąd pobierania stories: {e}", exc_info=True)
                    stats['errors'].append(f"Stories: {e}")

            if options.get('download_highlights', self.config.get('download_highlights', False)):
                try:
                    count = self._download_highlights(profile, username)
                    stats['downloaded']['highlights'] = count
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Błąd pobierania highlights: {e}", exc_info=True)
                    stats['errors'].append(f"Highlights: {e}")

            if options.get('download_tagged', self.config.get('download_tagged', False)):
                try:
                    count = self._download_tagged(profile, username)
                    stats['downloaded']['tagged'] = count
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Błąd pobierania tagged: {e}", exc_info=True)
                    stats['errors'].append(f"Tagged: {e}")

            if options.get('download_igtv', self.config.get('download_igtv', False)):
                try:
                    count = self._download_igtv(profile, username)
                    stats['downloaded']['igtv'] = count
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Błąd pobierania IGTV: {e}", exc_info=True)
                    stats['errors'].append(f"IGTV: {e}")

            # Podsumowanie
            total_downloaded = sum(stats['downloaded'].values())
            stats['success'] = True

            print(f"\n✨ Zakończono!")
            print(f"📊 Pobrano łącznie: {total_downloaded} elementów")
            for content_type, count in stats['downloaded'].items():
                if count > 0:
                    print(f"  - {content_type}: {count}")

            if stats['errors']:
                print(f"\n⚠️  Wystąpiło {len(stats['errors'])} błędów")

            logger.info(f"Zakończono pobieranie {username}: {total_downloaded} elementów")

        except ig_exc.LoginRequiredException:
            error_msg = "Wymagane logowanie! Użyj opcji logowania."
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            stats['errors'].append(error_msg)

        except KeyboardInterrupt:
            print("\n⚠️  Przerwano przez użytkownika")
            print("💡 Możesz wznowić pobieranie później - Instaloader pomija już pobrane pliki")
            logger.warning("Przerwano pobieranie przez użytkownika")
            stats['interrupted'] = True

        except Exception as e:
            error_msg = f"Nieoczekiwany błąd: {e}"
            print(f"❌ {error_msg}")
            logger.error(error_msg, exc_info=True)
            stats['errors'].append(error_msg)

        return stats

    def _display_profile_info(self, profile) -> None:
        """
        Wyświetla informacje o profilu

        Args:
            profile: Obiekt instaloader.Profile
        """
        print_separator("=")
        print(f"👤 Użytkownik: {profile.full_name} (@{profile.username})")
        print(f"📊 Liczba postów: {profile.mediacount}")
        print(f"👥 Obserwujący: {profile.followers:,}")
        print(f"👥 Obserwowani: {profile.followees:,}")

        if profile.biography:
            bio = profile.biography[:100]
            if len(profile.biography) > 100:
                bio += "..."
            print(f"📝 Bio: {bio}")

        if profile.is_private:
            print("🔒 Profil prywatny")
        if profile.is_verified:
            print("✓ Profil zweryfikowany")

        print_separator("=")
        logger.info(f"Profil: {profile.username}, {profile.mediacount} postów, {profile.followers} obserwujących")

    def _download_posts(self, profile, username: str) -> int:
        """
        Pobiera wszystkie posty z profilu

        Args:
            profile: Obiekt instaloader.Profile
            username: Nazwa użytkownika

        Returns:
            Liczba pobranych postów
        """
        print(f"\n📸 Pobieram posty...")
        logger.info(f"Pobieranie postów dla {username}")

        count = 0
        error_count = 0
        max_errors = 5  # Maksymalna liczba kolejnych błędów

        try:
            posts = list(profile.get_posts())
            total = len(posts)

            with tqdm(total=total, desc="Posty", unit="post") as pbar:
                for post in posts:
                    try:
                        # Pobierz post
                        self.loader.download_post(post, target=str(self.download_dir / username))
                        count += 1
                        pbar.update(1)

                        # Oznacz sukces w rate limiterze
                        self.rate_limiter.on_success()

                        # Czekaj przed następnym postem
                        self.rate_limiter.wait("Rate limit")

                        # Reset licznika błędów
                        error_count = 0

                    except KeyboardInterrupt:
                        logger.warning("Przerwano pobieranie postów przez użytkownika")
                        raise

                    except ig_exc.QueryReturnedNotFoundException:
                        # Post został usunięty - pomiń
                        logger.debug(f"Post nie istnieje (usunięty?) - pominięto")
                        pbar.update(1)
                        continue

                    except (ig_exc.ConnectionException, ig_exc.TooManyRequestsException) as e:
                        # Rate limiting lub błąd połączenia
                        error_count += 1
                        self.rate_limiter.on_error(is_rate_limit=True)

                        error_msg = str(e)
                        logger.warning(f"Błąd połączenia/rate limit: {e}")

                        # Wykryj 403 Forbidden - Instagram blokuje
                        if "403" in error_msg or "Forbidden" in error_msg:
                            print(f"\n❌ Instagram zablokował requesty (403 Forbidden)!")
                            print("To oznacza że Instagram wykrył podejrzaną aktywność.")
                            print("\n💡 ROZWIĄZANIE:")
                            print("  1. MUSISZ się zalogować: python3 main.py --browser-login")
                            print("  2. Zwiększ opóźnienia w .env: SLEEP_TIME=5")
                            print("  3. Instagram bardzo agresywnie blokuje bez logowania!")
                            logger.error("403 Forbidden - Instagram zablokował. Wymagane logowanie.")
                            break

                        print(f"\n⚠️  Rate limit - czekam dłużej...")

                        # Czekaj dłużej
                        self.rate_limiter.wait("Backoff delay")

                        if error_count >= max_errors:
                            logger.error("Zbyt wiele błędów rate limiting - przerywam")
                            print(f"\n❌ Zbyt wiele błędów rate limiting - przerwano pobieranie postów")
                            print("💡 Spróbuj:")
                            print("  - Zalogować się: python3 main.py --login")
                            print("  - Zwiększyć opóźnienia w .env: SLEEP_TIME=5-10")
                            break

                    except Exception as e:
                        # Inny błąd
                        logger.error(f"Błąd pobierania postu: {e}")
                        print(f"\n⚠️  Błąd przy pobieraniu postu: {e}")
                        self.rate_limiter.on_error(is_rate_limit=False)
                        pbar.update(1)
                        continue

        except KeyboardInterrupt:
            raise

        except Exception as e:
            logger.error(f"Błąd iteracji postów: {e}", exc_info=True)
            print(f"\n❌ Błąd przy pobieraniu postów: {e}")

        logger.info(f"Pobrano {count} postów dla {username}")
        return count

    def _download_stories(self, profile, username: str) -> int:
        """
        Pobiera stories (wymaga logowania)

        Args:
            profile: Obiekt instaloader.Profile
            username: Nazwa użytkownika

        Returns:
            Liczba pobranych stories
        """
        if not self.auth.is_logged_in():
            print("⚠️  Stories wymagają zalogowania - pomijam")
            logger.info("Pominięto stories - brak logowania")
            return 0

        print(f"\n📱 Pobieram stories...")
        logger.info(f"Pobieranie stories dla {username}")

        count = 0

        try:
            target = str(self.download_dir / f"{username}_stories")

            for story in self.loader.get_stories(userids=[profile.userid]):
                items = list(story.get_items())

                for item in tqdm(items, desc="Stories", unit="story"):
                    try:
                        self.loader.download_storyitem(item, target=target)
                        count += 1
                        self.rate_limiter.on_success()
                        self.rate_limiter.wait("Rate limit")

                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        logger.error(f"Błąd pobierania story: {e}")
                        self.rate_limiter.on_error()
                        continue

        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania stories: {e}", exc_info=True)
            print(f"\n⚠️  Błąd przy pobieraniu stories: {e}")

        logger.info(f"Pobrano {count} stories dla {username}")
        return count

    def _download_highlights(self, profile, username: str) -> int:
        """
        Pobiera highlights

        Args:
            profile: Obiekt instaloader.Profile
            username: Nazwa użytkownika

        Returns:
            Liczba pobranych highlights
        """
        print(f"\n⭐ Pobieram highlights...")
        logger.info(f"Pobieranie highlights dla {username}")

        count = 0

        try:
            target = str(self.download_dir / f"{username}_highlights")

            highlights = list(self.loader.get_highlights(user=profile))

            for highlight in tqdm(highlights, desc="Highlights", unit="highlight"):
                try:
                    items = list(highlight.get_items())

                    for item in items:
                        try:
                            self.loader.download_storyitem(item, target=target)
                            count += 1
                            self.rate_limiter.on_success()
                            self.rate_limiter.wait("Rate limit")

                        except KeyboardInterrupt:
                            raise
                        except Exception as e:
                            logger.error(f"Błąd pobierania highlight item: {e}")
                            self.rate_limiter.on_error()
                            continue

                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Błąd pobierania highlight: {e}")
                    continue

        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania highlights: {e}", exc_info=True)
            print(f"\n⚠️  Błąd przy pobieraniu highlights: {e}")

        logger.info(f"Pobrano {count} highlights dla {username}")
        return count

    def _download_tagged(self, profile, username: str) -> int:
        """
        Pobiera posty w których użytkownik jest oznaczony

        Args:
            profile: Obiekt instaloader.Profile
            username: Nazwa użytkownika

        Returns:
            Liczba pobranych tagged posts
        """
        print(f"\n🏷️  Pobieram posty z tagiem...")
        logger.info(f"Pobieranie tagged posts dla {username}")

        count = 0

        try:
            target = str(self.download_dir / f"{username}_tagged")
            tagged_posts = list(profile.get_tagged_posts())

            with tqdm(total=len(tagged_posts), desc="Tagged posts", unit="post") as pbar:
                for post in tagged_posts:
                    try:
                        self.loader.download_post(post, target=target)
                        count += 1
                        pbar.update(1)
                        self.rate_limiter.on_success()
                        self.rate_limiter.wait("Rate limit")

                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        logger.error(f"Błąd pobierania tagged post: {e}")
                        self.rate_limiter.on_error()
                        pbar.update(1)
                        continue

        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania tagged posts: {e}", exc_info=True)
            print(f"\n⚠️  Błąd przy pobieraniu tagged posts: {e}")

        logger.info(f"Pobrano {count} tagged posts dla {username}")
        return count

    def _download_igtv(self, profile, username: str) -> int:
        """
        Pobiera filmy IGTV

        Args:
            profile: Obiekt instaloader.Profile
            username: Nazwa użytkownika

        Returns:
            Liczba pobranych IGTV
        """
        print(f"\n📺 Pobieram IGTV...")
        logger.info(f"Pobieranie IGTV dla {username}")

        count = 0

        try:
            target = str(self.download_dir / f"{username}_igtv")
            igtv_posts = list(profile.get_igtv_posts())

            with tqdm(total=len(igtv_posts), desc="IGTV", unit="video") as pbar:
                for post in igtv_posts:
                    try:
                        self.loader.download_post(post, target=target)
                        count += 1
                        pbar.update(1)
                        self.rate_limiter.on_success()
                        self.rate_limiter.wait("Rate limit")

                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        logger.error(f"Błąd pobierania IGTV: {e}")
                        self.rate_limiter.on_error()
                        pbar.update(1)
                        continue

        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Błąd pobierania IGTV: {e}", exc_info=True)
            print(f"\n⚠️  Błąd przy pobieraniu IGTV: {e}")

        logger.info(f"Pobrano {count} IGTV dla {username}")
        return count
