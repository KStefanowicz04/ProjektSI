# -*- coding: utf-8 -*-
"""
Strategia A* (A-star).

Strategia INFORMOWANA: wykorzystuje funkcję heurystyczną h(n).
Strukturą frontier jest kolejka priorytetowa.
"""

import heapq

from graf import koszt_sciezki

#  Metadane strategii 
NAZWA = "A*"
OPIS = "Strategia informowana: A* z heurystyką opartą na etykietach wierzchołków."
ETYKIETA_FRONTIERA = "Kolejka priorytetowa"


def heurystyka(wezel, goal):
       return abs(ord(goal) - ord(wezel))


def przeszukaj(G, start, goal, tryb_cykli="multiple", limit_krokow=1000):
    """
    Generator realizujący algorytm A*.
    """

    frontier = []
    heapq.heappush(frontier, (0, [start]))

    rozwiniete = []
    zamkniete = set()
    koszt = {start: 0}

    krok = 0

    while frontier:

        if krok >= limit_krokow:
            yield {
                "krok": krok,
                "status": "limit",
                "current": None,
                "frontier": [p for _, p in frontier],
                "rozwiniete": list(rozwiniete),
                "sciezka": None,
                "g": None,
                "nowe": [],
                "komunikat": f"Przekroczono limit kroków ({limit_krokow}).",
            }
            return

        priorytet, sciezka = heapq.heappop(frontier)
        wezel = sciezka[-1]

        if tryb_cykli == "multiple" and wezel in zamkniete:
            continue

        zamkniete.add(wezel)
        krok += 1

        g = koszt_sciezki(G, sciezka)

        # sprawdzenie celu
        if wezel == goal:
            yield {
                "krok": krok,
                "status": "found",
                "current": wezel,
                "frontier": [p for _, p in frontier],
                "rozwiniete": list(rozwiniete),
                "sciezka": list(sciezka),
                "g": g,
                "nowe": [],
                "komunikat": f"Znaleziono cel '{goal}'! Koszt ścieżki g = {g}.",
            }
            return

        rozwiniete.append(wezel)

        nowe_sciezki = []

        for sasiad in sorted(G.successors(wezel)):

            if tryb_cykli == "loop" and sasiad in sciezka:
                continue

            if tryb_cykli == "multiple" and sasiad in zamkniete:
                continue

            nowa_sciezka = sciezka + [sasiad]

            nowy_koszt = koszt_sciezki(G, nowa_sciezka)

            if sasiad not in koszt or nowy_koszt < koszt[sasiad]:

                koszt[sasiad] = nowy_koszt

                f = nowy_koszt + heurystyka(sasiad, goal)

                heapq.heappush(frontier, (f, nowa_sciezka))

                nowe_sciezki.append(nowa_sciezka)

        yield {
            "krok": krok,
            "status": "szukam",
            "current": wezel,
            "frontier": [p for _, p in frontier],
            "rozwiniete": list(rozwiniete),
            "sciezka": list(sciezka),
            "g": g,
            "nowe": [list(p) for p in nowe_sciezki],
            "komunikat": f"Rozwijam wierzchołek '{wezel}' (g = {g}).",
        }

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