import json
import os

import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st
from graf import zbuduj_graf
from strategie import STRATEGIE


#  SEKCJA 1. Wizualizacja grafu 

def rysuj_graf(G, start, goal, stan=None):
    """
    Rysuje graf z wierzchołkami, krawędziami i wagami.
    Jeśli podano `stan` (krok algorytmu), koloruje:
      - aktualnie rozwijany wierzchołek,
      - wierzchołki już rozwinięte,
      - krawędzie aktualnej ścieżki.
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    # Układ wierzchołków — używamy współrzędnych x, y z danych.
    pos = {n: (G.nodes[n]["x"], G.nodes[n]["y"]) for n in G.nodes}

    # --- Kolorowanie wierzchołków ---
    rozwiniete = set(stan["rozwiniete"]) if stan else set()
    current = stan["current"] if stan else None
    sciezka = stan["sciezka"] if (stan and stan["sciezka"]) else []

    kolory = []
    for n in G.nodes:
        if n == start:
            kolory.append("#2ecc71")        # start — zielony
        elif n == goal:
            kolory.append("#e74c3c")        # cel — czerwony
        elif n == current:
            kolory.append("#f1c40f")        # aktualnie rozwijany — żółty
        elif n in rozwiniete:
            kolory.append("#aed6f1")        # już rozwinięty — jasnoniebieski
        else:
            kolory.append("#d5dbdb")        # nieodwiedzony — szary

    nx.draw_networkx_nodes(G, pos, node_color=kolory, node_size=750,
                           edgecolors="#34495e", ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=11, font_weight="bold", ax=ax)

    # --- Krawędzie ---
    nx.draw_networkx_edges(G, pos, edge_color="#95a5a6", arrows=True,
                           arrowsize=18, width=1.2, ax=ax,
                           connectionstyle="arc3,rad=0.05")

    # Podświetlenie krawędzi aktualnej ścieżki.
    if len(sciezka) > 1:
        kraw_sciezki = list(zip(sciezka, sciezka[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=kraw_sciezki, edge_color="#e67e22",
                               arrows=True, arrowsize=20, width=3.0, ax=ax,
                               connectionstyle="arc3,rad=0.05")

    # --- Wagi krawędzi ---
    etykiety = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=etykiety, font_size=8,
                                 label_pos=0.4, ax=ax)

    ax.set_title("Wizualizacja grafu (start=zielony, cel=czerwony)")
    ax.axis("off")
    plt.tight_layout()
    return fig


def porownaj_strategie(G, start, goal, tryb, limit):
    """
    Uruchamia WSZYSTKIE zarejestrowane strategie na tym samym grafie
    (te same start/goal/tryb/limit) i zwraca dla każdej zebrane metryki:
    liczbę kroków, liczbę rozwiniętych węzłów oraz koszt g znalezionej ścieżki.
    """
    podsumowanie = []
    for nazwa in sorted(STRATEGIE.keys()):
        strat = STRATEGIE[nazwa]
        try:
            kroki = list(strat.przeszukaj(G, start, goal, tryb, limit))
        except Exception as e:
            podsumowanie.append({"nazwa": nazwa, "blad": str(e)})
            continue

        if not kroki:
            podsumowanie.append({"nazwa": nazwa, "kroki": 0, "rozwiniete": 0,
                                 "koszt": None, "dlugosc_sciezki": None,
                                 "found": False})
            continue

        ostatni = kroki[-1]
        krok_celu = next((k for k in kroki if k["status"] == "found"), None)
        podsumowanie.append({
            "nazwa": nazwa,
            "kroki": ostatni["krok"],
            "rozwiniete": len(ostatni["rozwiniete"]),
            "koszt": krok_celu["g"] if krok_celu else None,
            "dlugosc_sciezki": len(krok_celu["sciezka"]) if krok_celu else None,
            "found": krok_celu is not None,
        })
    return podsumowanie


def rysuj_porownanie(podsumowanie):
    """
    Wykres słupkowy porównujący strategie:
      - po lewej efektywność (liczba kroków i rozwiniętych węzłów),
      - po prawej jakość (koszt g znalezionej ścieżki; 'brak' = nie znaleziono).
    """
    ok = [w for w in podsumowanie if "blad" not in w]

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 4))

    if not ok:
        for ax in (ax1, ax2, ax3):
            ax.text(0.5, 0.5, "Brak wyników do porównania.",
                    ha="center", va="center")
            ax.axis("off")
        plt.tight_layout()
        return fig

    nazwy = [w["nazwa"] for w in ok]
    kroki = [w["kroki"] for w in ok]
    rozw = [w["rozwiniete"] for w in ok]
    koszty = [w["koszt"] if w["koszt"] is not None else 0 for w in ok]
    dlugosci = [
    w["dlugosc_sciezki"] if w["dlugosc_sciezki"] is not None else 0 for w in ok]
    x = list(range(len(nazwy)))
    szer = 0.38

    ax1.bar([i - szer / 2 for i in x], kroki, szer,
            label="Liczba kroków", color="#2980b9")
    ax1.bar([i + szer / 2 for i in x], rozw, szer,
            label="Rozwinięte węzły", color="#27ae60")
    ax1.set_xticks(x)
    ax1.set_xticklabels(nazwy, rotation=20, ha="right", fontsize=8)
    ax1.set_title("Efektywność (koszt obliczeń)")
    ax1.legend(fontsize=8)
    ax1.grid(True, axis="y", linestyle="--", alpha=0.4)

    kolory = ["#e67e22" if w["found"] else "#c0392b" for w in ok]
    ax2.bar(x, koszty, color=kolory)
    ax2.set_xticks(x)
    ax2.set_xticklabels(nazwy, rotation=20, ha="right", fontsize=8)
    ax2.set_title("Jakość (koszt ścieżki g)")
    ax2.grid(True, axis="y", linestyle="--", alpha=0.4)
    for i, w in zip(x, ok):
        if not w["found"]:
            ax2.text(i, 0, "brak", ha="center", va="bottom",
                     fontsize=8, color="#c0392b")

    ax3.bar(x, dlugosci, color="#9b59b6")
    ax3.set_xticks(x)
    ax3.set_xticklabels(nazwy, rotation=20, ha="right", fontsize=8)
    ax3.set_title("Długość ścieżki")
    ax3.grid(True, axis="y", linestyle="--", alpha=0.4)
        
    plt.tight_layout()
    return fig


def rysuj_frontier_w_czasie(kroki, biezacy_krok=None):
    
    fig, ax = plt.subplots(figsize=(8, 3))

    numery = [k["krok"] for k in kroki]
    rozmiary = [len(k["frontier"]) for k in kroki]

    ax.plot(numery, rozmiary, marker="o", markersize=4,
            color="#8e44ad", linewidth=1.6)
    ax.fill_between(numery, rozmiary, color="#8e44ad", alpha=0.12)

    if biezacy_krok is not None:
        ax.axvline(biezacy_krok, color="#e67e22", linestyle="--",
                   linewidth=1.4, label=f"krok {biezacy_krok}")
        ax.legend(fontsize=8, loc="upper right")

    ax.set_xlabel("Krok algorytmu")
    ax.set_ylabel("Rozmiar frontiera")
    ax.set_title("Rozmiar frontiera w czasie (zużycie pamięci)")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.margins(x=0.01)
    plt.tight_layout()
    return fig


#  SEKCJA 2. Przykładowy graf — wczytywany z pliku JSON obok app.py

# Ścieżka do pliku z przykładowym grafem (w tym samym folderze co app.py).
PLIK_PRZYKLADU = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "przyklad_graf.json")


def wczytaj_przyklad():
    """Wczytuje przykładowy graf z pliku JSON i zwraca świeżą kopię słownika."""
    with open(PLIK_PRZYKLADU, encoding="utf-8") as f:
        return json.load(f)


#  SEKCJA 3. Interfejs Streamlit

st.set_page_config(page_title="Przeszukiwanie grafu", layout="wide")
st.title("Nauka strategii przeszukiwania grafu")
st.caption("Aplikacja dydaktyczna - modułowe strategie przeszukiwania")

# Inicjalizacja stanu sesji.
if "dane" not in st.session_state:
    try:
        st.session_state.dane = wczytaj_przyklad()
    except Exception as e:
        # Gdyby pliku z przykładem brakło — zaczynamy od pustego grafu.
        st.session_state.dane = {"directed": True, "start": None,
                                 "goal": None, "nodes": {}, "edges": []}
        st.warning(f"Nie udało się wczytać przykładu ({e}). "
                   f"Zacznij od pustego grafu lub wczytaj plik JSON.")
if "wyniki" not in st.session_state:
    st.session_state.wyniki = None

# Jeśli brak jakiejkolwiek strategii - nie ma co uruchamiać.
if not STRATEGIE:
    st.error("Nie znaleziono żadnej strategii w folderze strategie/.")
    st.stop()


#  PASEK BOCZNY - wczytanie / definiowanie grafu (wymaganie 1) i parametry (4)
with st.sidebar:
    st.header("1. Źródło grafu")

    # --- Wczytanie z pliku JSON ---
    plik = st.file_uploader("Wczytaj graf z pliku JSON", type=["json"])
    if plik is not None:
        try:
            st.session_state.dane = json.load(plik)
            st.success("Wczytano graf z pliku.")
        except Exception as e:
            st.error(f"Błąd wczytywania: {e}")

    if st.button("Załaduj przykładowy graf"):
        try:
            st.session_state.dane = wczytaj_przyklad()
            st.session_state.wyniki = None
        except Exception as e:
            st.error(f"Nie znaleziono pliku przyklad_graf.json: {e}")

    st.divider()

    # --- Definiowanie grafu z poziomu aplikacji ---
    st.header("2. Edycja grafu")
    dane = st.session_state.dane

    with st.expander("Dodaj wierzchołek"):
        nowy_w = st.text_input("Nazwa wierzchołka", key="nw_nazwa")
        nx_x = st.number_input("Współrzędna x", value=0.0, key="nw_x")
        nx_y = st.number_input("Współrzędna y", value=0.0, key="nw_y")
        if st.button("Dodaj wierzchołek"):
            if nowy_w:
                dane.setdefault("nodes", {})[nowy_w] = {"x": nx_x, "y": nx_y}
                st.session_state.wyniki = None
                st.success(f"Dodano wierzchołek '{nowy_w}'.")

    with st.expander("Dodaj krawędź"):
        lista_w = list(dane.get("nodes", {}).keys())
        if len(lista_w) >= 2:
            ce_u = st.selectbox("Z wierzchołka", lista_w, key="ce_u")
            ce_v = st.selectbox("Do wierzchołka", lista_w, key="ce_v")
            ce_w = st.text_input("Waga (puste = euklides)", key="ce_w")
            if st.button("Dodaj krawędź"):
                waga = float(ce_w) if ce_w.strip() else None
                dane.setdefault("edges", []).append([ce_u, ce_v, waga])
                st.session_state.wyniki = None
                st.success(f"Dodano krawędź {ce_u} → {ce_v}.")
        else:
            st.info("Dodaj najpierw co najmniej 2 wierzchołki.")
    
    with st.expander("Usuń wierzchołek"):
        lista_w = list(dane.get("nodes", {}).keys())
        if (lista_w):
            usun_w = st.selectbox("Nazwa wierzchołka", lista_w, key="usun_w")
            if st.button("Usuń wierzchołek"):
                ## Wierzchołek
                dane["nodes"].pop(usun_w, None)
                
                ## Krawędzie wierzchołka
                dane["edges"] = [
                    e for e in dane.get("edges", [])
                    if e[0] != usun_w and e[1] != usun_w
                ]

                st.session_state.wyniki = None
                st.success(f"Usunięto wierzchołek '{usun_w}'.")
        else:
            st.info("Brak wierzchołków do usunięcia.")
        
    with st.expander("Usuń krawędź"):
        lista_w = list(dane.get("nodes", {}).keys())
        if len(lista_w) >= 2:
            ue_u = st.selectbox("Z wierzchołka", lista_w, key="ue_u")
            ue_v = st.selectbox("Do wierzchołka", lista_w, key="ue_v")
            if st.button("Usuń krawędź"):
                dane["edges"] = [
                    e for e in dane.get("edges", [])
                    if not (e[0] == ue_u and e[1] == ue_v)
                ]
                st.session_state.wyniki = None
                st.success(f"Usunięto krawędź {ue_u} → {ue_v}.")
        else:
            st.info("Dodaj najpierw co najmniej 2 wierzchołki.")
                

    st.divider()

    # --- Wybór strategii i parametry algorytmu ---
    st.header("3. Strategia i parametry")

    # Wybór strategii z rejestru (automatycznie wykryte pliki strategie/*.py).
    nazwa_strat = st.selectbox("Strategia przeszukiwania",
                               sorted(STRATEGIE.keys()))
    strategia = STRATEGIE[nazwa_strat]
    if getattr(strategia, "OPIS", None):
        st.caption(strategia.OPIS)

    lista_w = list(dane.get("nodes", {}).keys())
    domyslny_start = dane.get("start", lista_w[0] if lista_w else None)
    domyslny_goal = dane.get("goal", lista_w[-1] if lista_w else None)

    idx_start = lista_w.index(domyslny_start) if domyslny_start in lista_w else 0
    idx_goal = lista_w.index(domyslny_goal) if domyslny_goal in lista_w else 0

    p_start = st.selectbox("Wierzchołek startowy", lista_w, index=idx_start)
    p_goal = st.selectbox("Wierzchołek końcowy", lista_w, index=idx_goal)

    p_tryb = st.selectbox(
        "Eliminacja cykli",
        options=["brak", "loop", "multiple"],
        format_func=lambda x: {
            "brak": "brak",
            "loop": "loop detection",
            "multiple": "multiple-path pruning",
        }[x],
        index=2,
    )

    p_limit = st.number_input("Limit kroków (warunek stopu)",
                              min_value=1, max_value=100000, value=1000)

    if st.button("Uruchom", type="primary"):
        dane["start"] = p_start
        dane["goal"] = p_goal
        try:
            G = zbuduj_graf(dane)
            # Uruchamiamy wybraną strategię (generator) i zbieramy kroki.
            kroki = list(strategia.przeszukaj(G, p_start, p_goal,
                                              p_tryb, int(p_limit)))
            st.session_state.wyniki = {
                "kroki": kroki,
                "strategia": nazwa_strat,
                "start": p_start,
                "goal": p_goal,
                "tryb": p_tryb,
                "limit": int(p_limit),
            }
        except Exception as e:
            st.error(f"Błąd uruchomienia: {e}")


#  GŁÓWNY OBSZAR
dane = st.session_state.dane

# Budujemy graf do wizualizacji.
try:
    G = zbuduj_graf(dane)
except Exception as e:
    st.error(f"Nie udało się zbudować grafu: {e}")
    st.stop()

start = dane.get("start")
goal = dane.get("goal")

kol1, kol2 = st.columns([3, 2])

# --- Wizualizacja kroków pośrednich (wymaganie 5) ---
wyniki = st.session_state.wyniki

# Etykieta frontiera zależna od wybranej strategii (np. kolejka vs stos).
if wyniki:
    _strat = STRATEGIE.get(wyniki["strategia"])
    etykieta_frontiera = getattr(_strat, "ETYKIETA_FRONTIERA", "Frontier")
else:
    etykieta_frontiera = "Frontier"

with kol1:
    st.subheader("Wizualizacja grafu")

    aktualny_stan = None
    if wyniki and wyniki["kroki"]:
        kroki = wyniki["kroki"]
        st.markdown("**Przewijanie kroków algorytmu:**")
        nr = st.slider("Krok", min_value=1, max_value=len(kroki),
                       value=len(kroki))
        aktualny_stan = kroki[nr - 1]

    fig = rysuj_graf(G, wyniki["start"] if wyniki else start,
                     wyniki["goal"] if wyniki else goal, aktualny_stan)
    st.pyplot(fig)

    # Wykres pomocniczy: jak rósł/malał frontier w trakcie przeszukiwania.
    if wyniki and wyniki["kroki"]:
        biezacy = aktualny_stan["krok"] if aktualny_stan else None
        st.pyplot(rysuj_frontier_w_czasie(wyniki["kroki"], biezacy))

with kol2:
    if wyniki and wyniki["kroki"] and aktualny_stan is not None:
        st.subheader(f"Stan w kroku {aktualny_stan['krok']}")
        st.info(aktualny_stan["komunikat"])

        # Aktualnie rozwijany wierzchołek.
        st.markdown(f"**Rozwijany wierzchołek:** "
                    f"`{aktualny_stan['current'] or '—'}`")

        # Aktualna ścieżka i koszt g.
        if aktualny_stan["sciezka"]:
            st.markdown(f"**Aktualna ścieżka:** "
                        f"`{' → '.join(aktualny_stan['sciezka'])}`")
            st.markdown(f"**Koszt g:** `{aktualny_stan['g']}`")

        # Frontier (nazwa zależna od strategii).
        st.markdown(f"**Frontier ({etykieta_frontiera}):**")
        if aktualny_stan["frontier"]:
            st.code("\n".join(" → ".join(p) for p in aktualny_stan["frontier"]))
        else:
            st.code("(pusty)")

        # Wierzchołki już rozwinięte.
        st.markdown("**Rozwinięte wierzchołki:**")
        st.code(", ".join(aktualny_stan["rozwiniete"]) or "(brak)")
    else:
        st.subheader("Informacje")
        st.write("Wybierz strategię i parametry w panelu bocznym, a następnie "
                 "kliknij **Uruchom**, aby zobaczyć kolejne kroki algorytmu.")
        st.write(f"- Dostępne strategie: **{', '.join(sorted(STRATEGIE))}**")
        st.write(f"- Liczba wierzchołków: **{G.number_of_nodes()}**")
        st.write(f"- Liczba krawędzi: **{G.number_of_edges()}**")
        st.write(f"- Start: **{start}**, Cel: **{goal}**")


# Prezentacja wyniku: jakość i efektywność 
if wyniki and wyniki["kroki"]:
    st.divider()
    st.subheader(f"Wynik końcowy — {wyniki['strategia']}")

    ostatni = wyniki["kroki"][-1]
    # Szukamy kroku, w którym znaleziono cel.
    krok_celu = next((k for k in wyniki["kroki"] if k["status"] == "found"), None)

    liczba_krokow = ostatni["krok"]
    liczba_rozwinietych = len(ostatni["rozwiniete"])

    c1, c2, c3 = st.columns(3)
    if krok_celu:
        c1.metric("JAKOŚĆ — koszt ścieżki g", krok_celu["g"])
        c2.metric("EFEKTYWNOŚĆ — liczba kroków", liczba_krokow)
        c3.metric("EFEKTYWNOŚĆ — rozwiniętych", liczba_rozwinietych)
        st.success(f"Znaleziona ścieżka: "
                   f"**{' → '.join(krok_celu['sciezka'])}** "
                   f"(koszt g = {krok_celu['g']})")
    else:
        c1.metric("JAKOŚĆ — koszt ścieżki g", "—")
        c2.metric("EFEKTYWNOŚĆ — liczba kroków", liczba_krokow)
        c3.metric("EFEKTYWNOŚĆ — rozwiniętych", liczba_rozwinietych)
        st.warning(f"Nie znaleziono ścieżki. {ostatni['komunikat']}")

    st.markdown("**Porównanie strategii**")
    st.caption("Wszystkie strategie uruchomione na tym samym grafie z tymi "
               "samymi parametrami (start, cel, eliminacja cykli, limit).")
    podsumowanie = porownaj_strategie(G, wyniki["start"], wyniki["goal"],
                                      wyniki["tryb"], wyniki["limit"])
    st.pyplot(rysuj_porownanie(podsumowanie))

    wiersze = []
    for w in podsumowanie:
        if "blad" in w:
            wiersze.append({"Strategia": w["nazwa"], "Kroki": "—",
                            "Rozwinięte": "—", "Koszt g": f"błąd: {w['blad']}",
                            "Znaleziono": "—"})
        else:
            wiersze.append({
                "Strategia": w["nazwa"],
                "Kroki": w["kroki"],
                "Rozwinięte": w["rozwiniete"],
                "Koszt g": w["koszt"] if w["koszt"] is not None else "—",
                "Długość ścieżki": w["dlugosc_sciezki"] if w["dlugosc_sciezki"] is not None else "—",
                "Znaleziono": "tak" if w["found"] else "nie",
                
            })
    st.table(wiersze)

# --- Zapis rozwiązania do pliku JSON---
    wynik_json = {
        "parametry": {
            "strategia": wyniki["strategia"],
            "start": wyniki["start"],
            "goal": wyniki["goal"],
            "eliminacja_cykli": wyniki["tryb"],
            "limit_krokow": wyniki["limit"],
        },
        "wynik": {
            "znaleziono": krok_celu is not None,
            "sciezka": krok_celu["sciezka"] if krok_celu else None,
            "koszt_g": krok_celu["g"] if krok_celu else None,
            "liczba_krokow": liczba_krokow,
            "liczba_rozwinietych": liczba_rozwinietych,
        },
    }
    st.download_button(
        "Zapisz rozwiązanie do JSON",
        data=json.dumps(wynik_json, ensure_ascii=False, indent=2),
        file_name="rozwiazanie.json",
        mime="application/json",
    )
