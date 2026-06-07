# Bilan d’avancement — 07/06/2026

## IDS WordPress : refactor parsing et intégration detection engine



## 1. Stabilisation du parser WordPress

### Objectif

Externaliser complètement le parsing des logs WordPress depuis `detection.py` vers un module dédié basé sur WP-CLI.

### Travail réalisé (`parsers/wp_simple_history.py`)

* Récupération des logs via :

  * `docker exec wordpress-wordpress-1 wp simple-history list`
* Parsing des lignes tabulées avec `split("\t")`
* Filtrage des événements de type `Failed to login`
* Extraction du username via regex :

  ```python
  r'username "([^"]+)"'
  ```

### Résultat

Les logs WordPress sont désormais normalisés en événements structurés :

```python
{
    "type": "failed_login",
    "username": "admin",
    "date": "2026-06-04 01:28:04",
    "level": "warning",
    "raw": "..."
}
```



## 2. Intégration propre dans detection.py

### Objectif

Supprimer toute logique WP-CLI et parsing WordPress dans le moteur IDS principal.

### Nettoyage effectué

* Suppression du parsing manuel des logs WordPress
* Suppression de :

  * `extract_username`
  * `is_failed_login`
* Remplacement du flux auth par consommation directe du parser :

  * `get_failed_logins_events()`



## 3. Nouveau pipeline authentication

### Avant

```
detection.py → WP-CLI → regex → bruteforce detection
```

### Après

```
detection.py → parser WordPress → events structurés → bruteforce detection
```



## 4. Correction de schéma de données

### Problème rencontré

Erreur runtime :

```
KeyError: 'timestamp'
```

### Cause

Incohérence entre les champs :

* `date` dans le parser initial
* `timestamp` dans le moteur IDS

### Correction appliquée

Fallback robuste :

```python
event.get("timestamp", event.get("date"))
```



## 5. Stabilisation du moteur threading

### Objectif

Éviter les crashs et les boucles de polling inefficaces.

### Correctifs appliqués

* Threads définis en `daemon=True`
* Ajout de `time.sleep(5)` dans la boucle auth
* Introduction d’un `seen set()` pour éviter les doublons
* Suppression du polling WP-CLI dans `detection.py`



## 6. État global du système

| Module                       | État                      |
| ---------------------------- | ------------------------- |
| Parser WordPress             | Stable                    |
| Détection web (SQLi/LFI/XSS) | Stable                    |
| Pipeline authentication      | Stable                    |
| Threading                    | Fonctionnel mais sensible |
| Schéma d’événements          | Partiellement unifié      |



## Conclusion

Cette étape marque la transition d’un script IDS monolithique vers une architecture modulaire basée sur des événements.

Le parsing WordPress est désormais isolé et réutilisable, et `detection.py` se concentre uniquement sur la logique de détection et de corrélation.

La prochaine étape logique est l’unification complète du schéma d’événements et l’introduction d’une corrélation multi-sources (IP, utilisateur, temporalité).
