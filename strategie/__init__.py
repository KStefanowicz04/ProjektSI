# -*- coding: utf-8 -*-
"""
Rejestr strategii przeszukiwania.

Każda strategia to OSOBNY plik .py w tym folderze (np. bfs.py, dfs.py, astar.py).
Ten moduł automatycznie wykrywa wszystkie strategie — wystarczy wrzucić nowy
plik, NIE trzeba ruszać app.py.

=============================================================================
 KONTRAKT — co musi zawierać plik strategii (przykład: patrz bfs.py)
=============================================================================

1) Stała  NAZWA  — tekst widoczny w interfejsie, np. "BFS (wszerz)".

2) (opcjonalnie) Stała  OPIS  — krótki opis pod tytułem.

3) (opcjonalnie) Stała  ETYKIETA_FRONTIERA  — jak nazwać frontier w UI,
   np. "Kolejka FIFO" dla BFS, "Stos LIFO" dla DFS. Domyślnie "Frontier".

4) Funkcja-GENERATOR:

       def przeszukaj(G, start, goal, tryb_cykli, limit_krokow):
           ...
           yield stan   # po KAŻDYM kroku

   Parametry:
     G            – graf NetworkX (z graf.zbuduj_graf)
     start, goal  – wierzchołek startowy i końcowy
     tryb_cykli   – "brak" | "loop" | "multiple"
     limit_krokow – maksymalna liczba kroków (warunek stopu)

   Każdy `yield` zwraca SŁOWNIK STANU o ustalonych kluczach (tak by
   wspólna wizualizacja w app.py działała dla każdej strategii):

     {
       "krok":       int,                # numer kroku (od 1)
       "status":     str,                # "szukam" | "found" | "brak" | "limit"
       "current":    str | None,         # aktualnie rozwijany wierzchołek
       "frontier":   list[list[str]],    # zawartość frontiera (lista ścieżek)
       "rozwiniete": list[str],          # wierzchołki już rozwinięte (kolejność)
       "sciezka":    list[str] | None,   # aktualna ścieżka
       "g":          float | None,       # koszt aktualnej ścieżki
       "nowe":       list[list[str]],    # ścieżki dodane do frontiera w tym kroku
       "komunikat":  str,                # opis kroku po polsku
     }
=============================================================================
"""

import importlib
import pkgutil

# Słownik: NAZWA strategii -> moduł (z funkcją przeszukaj).
STRATEGIE = {}

# Automatyczne wykrywanie: przeglądamy wszystkie moduły w tym pakiecie.
for _, _nazwa_modulu, _ in pkgutil.iter_modules(__path__):
    _modul = importlib.import_module(f"{__name__}.{_nazwa_modulu}")
    # Rejestrujemy tylko moduły spełniające kontrakt (NAZWA + przeszukaj).
    if hasattr(_modul, "NAZWA") and hasattr(_modul, "przeszukaj"):
        STRATEGIE[_modul.NAZWA] = _modul
