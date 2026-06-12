# -*- coding: utf-8 -*-
"""
Strategia BFS (Breadth-First Search) — przeszukiwanie wszerz.

Strategia ŚLEPA (nieinformowana): nie używa heurystyki, rozwija wierzchołki
w kolejności odległości (liczby krawędzi) od startu. Frontier to kolejka FIFO.

Zgodna z kontraktem opisanym w strategie/__init__.py.
"""

from collections import deque

from graf import koszt_sciezki

# --- Metadane strategii (czytane przez rejestr i interfejs) ---
NAZWA = "BFS (wszerz)"
OPIS = "Strategia ślepa: przeszukiwanie wszerz, frontier = kolejka FIFO."
ETYKIETA_FRONTIERA = "Kolejka FIFO"


def przeszukaj(G, start, goal, tryb_cykli="multiple", limit_krokow=1000):
    """
    Generator realizujący przeszukiwanie BFS.

    Po KAŻDYM kroku (rozwinięciu jednego wierzchołka) zwraca słownik stanu,
    dzięki czemu interfejs może przewijać kroki pośrednie.

    tryb_cykli:
        "brak"     – brak eliminacji (może się zapętlić),
        "loop"     – loop detection (nie wracamy do węzła obecnego w ścieżce),
        "multiple" – multiple-path pruning (nie rozwijamy węzła rozwiniętego
                     już wcześniej).

    Frontier (kolejka FIFO) przechowuje całe ŚCIEŻKI, więc w każdym kroku
    znamy aktualną ścieżkę i jej koszt g.
    """
    frontier = deque()
    frontier.append([start])

    rozwiniete = []        # lista wierzchołków w kolejności rozwijania
    zamkniete = set()      # zbiór zamknięty (dla multiple-path pruning)
    krok = 0

    while frontier:
        # --- Warunek stopu: limit kroków ---
        if krok >= limit_krokow:
            yield {
                "krok": krok,
                "status": "limit",
                "current": None,
                "frontier": [list(p) for p in frontier],
                "rozwiniete": list(rozwiniete),
                "sciezka": None,
                "g": None,
                "nowe": [],
                "komunikat": f"Przekroczono limit kroków ({limit_krokow}).",
            }
            return

        # Pobieramy najstarszą ścieżkę z kolejki (FIFO — to czyni z tego BFS).
        sciezka = frontier.popleft()
        wezel = sciezka[-1]

        # multiple-path pruning: jeśli węzeł był już rozwinięty, pomijamy go
        # (nie liczymy tego jako kroku — to po prostu odrzucona, gorsza ścieżka).
        if tryb_cykli == "multiple" and wezel in zamkniete:
            continue

        zamkniete.add(wezel)
        krok += 1
        g = koszt_sciezki(G, sciezka)

        # --- Test celu (wykonywany przy zdejmowaniu z kolejki) ---
        if wezel == goal:
            yield {
                "krok": krok,
                "status": "found",
                "current": wezel,
                "frontier": [list(p) for p in frontier],
                "rozwiniete": list(rozwiniete),
                "sciezka": list(sciezka),
                "g": g,
                "nowe": [],
                "komunikat": f"Znaleziono cel '{goal}'! Koszt ścieżki g = {g}.",
            }
            return

        rozwiniete.append(wezel)

        # --- Rozwijanie sąsiadów (następników w grafie skierowanym) ---
        nowe_sciezki = []
        for sasiad in sorted(G.successors(wezel)):
            # loop detection: nie wracamy do węzła obecnego w tej ścieżce
            if tryb_cykli == "loop" and sasiad in sciezka:
                continue
            # multiple-path pruning: nie dodajemy węzłów już zamkniętych
            if tryb_cykli == "multiple" and sasiad in zamkniete:
                continue
            nowa = sciezka + [sasiad]
            frontier.append(nowa)
            nowe_sciezki.append(nowa)

        # Zwracamy stan po rozwinięciu tego wierzchołka.
        yield {
            "krok": krok,
            "status": "szukam",
            "current": wezel,
            "frontier": [list(p) for p in frontier],
            "rozwiniete": list(rozwiniete),
            "sciezka": list(sciezka),
            "g": g,
            "nowe": [list(p) for p in nowe_sciezki],
            "komunikat": f"Rozwijam wierzchołek '{wezel}' (g = {g}).",
        }

    # Kolejka pusta, a celu nie znaleziono.
    yield {
        "krok": krok,
        "status": "brak",
        "current": None,
        "frontier": [],
        "rozwiniete": list(rozwiniete),
        "sciezka": None,
        "g": None,
        "nowe": [],
        "komunikat": "Frontier pusty — nie znaleziono ścieżki do celu.",
    }
