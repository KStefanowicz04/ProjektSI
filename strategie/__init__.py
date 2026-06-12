# -*- coding: utf-8 -*-
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
