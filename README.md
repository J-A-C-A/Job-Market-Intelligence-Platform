# Job Market Intelligence Platform

Job Market Intelligence Platform to system do automatycznego zbierania, przetwarzania i analizowania ofert pracy z branży IT.

Aplikacja scrapuje oferty z portalu NoFluffJobs, przechowuje je w relacyjnej bazie danych PostgreSQL, udostępnia dane oraz statystyki rynku pracy poprzez REST API, a także automatycznie aktualizuje dane w tle dzięki wbudowanemu schedulerowi.

## ====OPIS PROJEKTU====

System składa się ze scrapera, warstwy przetwarzania i zapisu danych (repositories/services) oraz FastAPI, które udostępnia zebrane oferty i statystyki rynku pracy.

Aplikacja pobiera dane z NoFluffJobs, normalizuje je (widełki płacowe, poziom doświadczenia, tryb pracy, lokalizacja, typ umowy), zapisuje w PostgreSQL i śledzi zmiany ofert w czasie (historia zmian).

## ====FUNKCJONALNOŚCI====

- scraping ofert pracy z NoFluffJobs (pojedyncza oferta oraz pełne listy z ~50 kategorii/technologii)
- implementacja ograniczania częstotliwości zapytań (request throttling) i obsługi limitów API poprzez retry mechanism z exponential backoff dla odpowiedzi HTTP 429
- normalizacja danych ofertowych: widełki płacowe (UoP/B2B, różne waluty i okresy rozliczeniowe), poziom doświadczenia, tryb pracy (stacjonarny/hybrydowy/zdalny), lokalizacja, typ umowy
- zapis ofert do bazy danych PostgreSQL wraz z powiązanymi firmami i technologiami (relacje N:M)
- wykrywanie i zapis historii zmian oferty (np. zmiana widełek płacowych) w osobnej tabeli
- FastAPI do przeglądania, filtrowania, dodawania i usuwania ofert
- endpointy statystyczne: liczba ofert wg doświadczenia/technologii/lokalizacji/typu umowy/trybu pracy, średnie widełki płacowe w różnych przekrojach
- automatyczny, cykliczny scraping w tle dzięki schedulerowi 
- pełne pokrycie testami jednostkowymi dla scrapera, repozytoriów, serwisów i API

## ====STACK TECHNOLOGICZNY====

- **Python** – język główny
- **FastAPI** / **Uvicorn** – REST API i serwer aplikacji
- **Pydantic** – walidacja i schematy danych
- **PostgreSQL** – baza danych
- **SQLAlchemy 2.0** (`Mapped` / `mapped_column`) – ORM
- **Alembic** – migracje bazy danych
- **requests** / **BeautifulSoup4** – scraping stron NoFluffJobs
- **APScheduler** – automatyczny, cykliczny scraping
- **pytest** (+ `unittest.mock`, `monkeypatch`) – testy jednostkowe
- **Git / GitHub** – kontrola wersji

## ====STRUKTURA PROJEKTU====

**app/scrapers/nofluffjobs_scraper.py**
- pobieranie i parsowanie stron ofert oraz list kategorii
- normalizacja pól (widełki płacowe, doświadczenie, tryb pracy, lokalizacja, typ umowy)
- pipeline `run_scraper()` łączący scraping z throttlingiem i obsługą limitu żądań

**app/models/**
- modele SQLAlchemy: `companies`, `technologies`, `job_offers`, `offer_tech` (relacja N:M), `offer_history`

**app/repositories/**
- funkcje CRUD i zapytania do bazy dla firm, technologii, ofert pracy i historii zmian
- agregacje statystyczne (liczba ofert i średnie widełki płacowe w różnych przekrojach)

**app/services/**
- logika biznesowa: tworzenie/pobieranie firm i technologii, tworzenie ofert z danych ze scrapera, wykrywanie i zapis zmian ofert w czasie

**app/api/**
- endpointy REST: `GET/POST/DELETE /offers`, `GET /offers/{id}`, endpointy `/stats/...`

**app/scheduler.py**
- konfiguracja cyklicznego, automatycznego scrapingu w tle (APScheduler, trigger `cron`)

**app/main.py**
- inicjalizacja aplikacji FastAPI i podłączenie schedulera przez `lifespan`

**tests/**
- testy pytest dla scrapera, repozytoriów, serwisów i API

## ====URUCHOMIENIE PROJEKTU====

1. Skonfiguruj bazę danych PostgreSQL i zmienne środowiskowe połączenia.
2. Zastosuj migracje bazy danych (Alembic).
3. Uruchom serwer API:
   ```
   uvicorn app.main:app --reload
   ```
4. API będzie dostępne pod `http://127.0.0.1:8000`, dokumentacja Swagger pod `/docs`.

Scheduler uruchamia się automatycznie razem z serwerem i cyklicznie odświeża dane ofert w tle.
