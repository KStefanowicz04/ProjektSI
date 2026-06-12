# -*- coding: utf-8 -*-
"""
Wspólny model grafu — używany przez aplikację oraz przez WSZYSTKIE strategie.

Tu trzymamy funkcje niezależne od konkretnej strategii przeszukiwania:
budowę grafu z danych JSON, odległość euklidesową i koszt ścieżki.
Dzięki temu każda strategia (BFS, a w przyszłości DFS, A* itd.) korzysta
z tego samego, jednego źródła prawdy.
"""

import math

import networkx as nx


def euklides(p1, p2):
    """Odległość euklidesowa między dwoma punktami (x, y)."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def zbuduj_graf(dane):
    """
    Tworzy skierowany graf NetworkX na podstawie słownika `dane`
    (w formacie JSON opisanym w treści zadania).

    - Jeśli krawędź nie ma podanej wagi, liczymy ją jako odległość
      euklidesową między współrzędnymi wierzchołków.
    - Heurystykę h(n) liczymy jako odległość euklidesową do celu,
      chyba że wierzchołek ma jawnie podane pole "h"
      (przyda się strategiom informowanym, np. A*).
    """
    G = nx.DiGraph()

    # 1) Dodajemy wierzchołki wraz ze współrzędnymi (x, y) i ewentualnym h.
    for nazwa, atrybuty in dane.get("nodes", {}).items():
        x = float(atrybuty.get("x", 0.0))
        y = float(atrybuty.get("y", 0.0))
        G.add_node(nazwa, x=x, y=y, h=atrybuty.get("h", None))

    goal = dane.get("goal")

    # 2) Dodajemy krawędzie. Brakującą wagę liczymy z odległości euklidesowej.
    for krawedz in dane.get("edges", []):
        u, v = krawedz[0], krawedz[1]
        waga = krawedz[2] if len(krawedz) > 2 and krawedz[2] is not None else None

        if waga is None:
            pu = (G.nodes[u]["x"], G.nodes[u]["y"])
            pv = (G.nodes[v]["x"], G.nodes[v]["y"])
            waga = euklides(pu, pv)

        G.add_edge(u, v, weight=round(float(waga), 3))

    # 3) Uzupełniamy heurystykę h(n) tam, gdzie nie została podana jawnie.
    if goal is not None and goal in G.nodes:
        pg = (G.nodes[goal]["x"], G.nodes[goal]["y"])
        for n in G.nodes:
            if G.nodes[n]["h"] is None:
                pn = (G.nodes[n]["x"], G.nodes[n]["y"])
                G.nodes[n]["h"] = round(euklides(pn, pg), 3)

    return G


def koszt_sciezki(G, sciezka):
    """Sumaryczny koszt g ścieżki (suma wag kolejnych krawędzi)."""
    koszt = 0.0
    for a, b in zip(sciezka, sciezka[1:]):
        koszt += G[a][b]["weight"]
    return round(koszt, 3)
