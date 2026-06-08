# Bilan technique — 08/06/2026

## Évolution du dashboard IDS (print → Rich live dashboard)

# 1. Première étape — Dashboard basique (print engine)

## Objectif initial

Créer une visualisation minimale des événements IDS directement dans le terminal.

## Approche

- utilisation de `print()`
- affichage brut des alertes
- pipeline simple basé sur `detection.py`

## Résultat

- affichage fonctionnel des attaques :
    - SQLi
    - LFI
    - XSS
    - bruteforce (partiel)
- validation du moteur IDS

## Limites

- aucune structure visuelle
- impossible d’analyser les tendances
- pas de lecture SOC-like
- aucune séparation des données

# 2. Deuxième étape — introduction de Rich (prototype dashboard)

## Objectif

Passer d’un flux brut à une **visualisation structurée**.

## Ajouts

- `rich.table`
- premières métriques :
    - attaques par type
    - IP les plus actives
    - utilisateurs

## Résultat

- premier tableau exploitable
- amélioration de la lisibilité
- début d’un SOC-like view

## Limites identifiées

- données mélangées
- pas de layout global
- pas de recent events clair
- logique encore monolithique

# 3. Troisième étape — Rich layout avancé (version actuelle)

## Objectif

Transformer le dashboard en **interface SOC temps réel**.

## Architecture introduite

### Layout principal :

- header (titre IDS)
- body (3 colonnes)
    - Attacks
    - Top IPs
    - Top Users
- footer (recent alerts)

## Pipeline de données

```
logs.json → load_stats() → Counter + deque → Rich Layout
```

## Fonctionnalités ajoutées

### 1. Agrégation statistique

- Counter sur :
    - attack types
    - IP
    - users

### 2. Timeline légère

- `deque(maxlen=10)` pour recent events

### 3. Live dashboard

- refresh via `Live()`
- affichage temps réel

## Problèmes rencontrés et corrigés

### 1. Erreur de type dans recent events

- cause : `str` au lieu de `dict`
- correction : validation `isinstance(event, dict)`

### 2. Bug slicing critique

- erreur :

```python
[-10]
```

- correction :

```python
[-10:]
```

### 3. Crash `.get()` sur string

- cause indirecte du slicing
- résolu par correction structurelle

### 4. Incohérence Live refresh

- correction de l’ordre :
    - sleep avant update

# 4. État actuel du dashboard

## Fonctionnel

- visualisation temps réel
- séparation claire des données
- statistiques exploitables
- recent events stable
- pipeline IDS complet connecté

## Architecture validée

```
detection.py
     ↓
logs.json
     ↓
dashboard.py (Rich Live)
     ↓
SOC view terminal
```

# 5. Prochaine étape logique (pas obligatoire mais naturelle)

Ton système est maintenant prêt pour :

- severity scoring (LOW / MEDIUM / HIGH)
- alert correlation (multi-event attack)
- export API (Flask)
- dashboard web HTML
