# Profilácia Pytition projektu

## Prehľad

Tento adresár obsahuje nástroje na **časovú profiláciu** Pytition projektu.

## Inštalácia závislostí

```bash
pdm add snakeviz line-profiler --dev
```

## Spustenie profilácie

### Základné použitie

```bash
# Profilovať HTML sanitizáciu (default)
pdm run python profiling/run_profiler.py sanitize

# Profilovať databázové operácie
pdm run python profiling/run_profiler.py models

# Profilovať vytváranie podpisov
pdm run python profiling/run_profiler.py signatures

# Profilovať databázové query
pdm run python profiling/run_profiler.py queries

# Spustiť všetky scenáre
pdm run python profiling/run_profiler.py all
```

### Vizualizácia výsledkov

Po spustení profilácie sa vytvorí `.prof` súbor v `profiling/results/`. Vizualizuj ho pomocou:

```bash
pdm run snakeviz profiling/results/sanitize.prof
```

Otvorí sa prehliadač s interaktívnou vizualizáciou.

## Scenáre

| Scenár | Popis | Čo meria |
|--------|-------|----------|
| `sanitize` | HTML sanitizácia | Výkon `sanitize_html()` funkcie z helpers.py |
| `models` | CRUD operácie | Vytváranie, čítanie, aktualizácia modelov |
| `signatures` | Podpisy | Vytváranie a počítanie podpisov petícií |
| `queries` | DB queries | Komplexné databázové dotazy s filtráciou |

## Interpretácia výsledkov

### Kľúčové metriky

- **ncalls** - počet volaní funkcie
- **tottime** - celkový čas strávený v funkcii (bez subfunkcií)
- **cumtime** - kumulatívny čas (vrátane subfunkcií)
- **percall** - čas na jedno volanie

### Identifikácia bottleneckov

1. Hľadaj funkcie s vysokým **cumtime** - celkovo zaberajú najviac času
2. Hľadaj funkcie s vysokým **tottime** - samotná funkcia je pomalá
3. Hľadaj funkcie s vysokým **ncalls** - volajú sa príliš často

## Príklad optimalizácie

### Pred optimalizáciou

```
   ncalls  tottime  cumtime  filename:lineno(function)
     1000    2.500    2.500  helpers.py:18(sanitize_html)
```

### Identifikovaný problém

Funkcia `sanitize_html` sa volá 1000x a zaberá 2.5s.

### Riešenie

Pridať caching pre opakované HTML:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def sanitize_html_cached(html):
    return sanitize_html(html)
```

### Po optimalizácii

```
   ncalls  tottime  cumtime  filename:lineno(function)
     1000    0.100    0.100  helpers.py:18(sanitize_html_cached)
```

## Dokumentácia výsledkov

Pri odovzdávaní úlohy zaznamenaj:

1. **Vybraný scenár** a prečo
2. **Identifikovaný bottleneck** (funkcia, riadky kódu)
3. **Meranie PRED** optimalizáciou (čas, ncalls)
4. **Popis optimalizácie** čo si zmenil
5. **Meranie PO** optimalizácii (čas, ncalls)
6. **Percentuálne zlepšenie**
