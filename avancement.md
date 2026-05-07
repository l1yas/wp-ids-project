# Bilan du projet IDS WordPress — 07/05/2026

## 1. Mise à jour de `seed.sh`

### Changements effectués

Ajout de l’installation automatique du plugin WordPress **Simple History** via WP-CLI dans le container WordPress.

### Fonctionnalités ajoutées

* attente du container WordPress
* vérification du fonctionnement de WP-CLI
* installation automatique du plugin `simple-history`
* activation automatique du plugin
* comportement idempotent :

  * le script peut être relancé sans casser l’environnement
  * gestion des plugins déjà installés/activés

### Résultat

Le lab peut maintenant être entièrement préparé avec :

```bash id="cmd1"
docker compose up -d
./seed.sh
```

## 2. Ajustements de `bruteforce.py` (WIP)

## Nouvelle logique implémentée

Le module a été transformé en moteur de détection basé sur les événements d’authentification.

### Nouveaux comportements

Suivi des :

* failed logins par IP
* failed logins par username

### Structures utilisées

Utilisation de :

```python id="code1"
defaultdict(deque)
```

afin d’implémenter une sliding window efficace.

### Détections ajoutées

#### Bruteforce IP

Détection :

* d’un grand nombre d’échecs
* provenant de la même IP

#### Password spraying

Détection :

* d’un username ciblé plusieurs fois
* dans une fenêtre temporelle donnée

## 3. Liaison du parser avec `bruteforce.py` et amélioration de `detection.py` (WIP)

## Mise en relation des composants

Le parser WordPress produit désormais des événements structurés sous forme de dictionnaires Python.

Exemple :

```python id="code2"
{
    "type": "failed_login",
    "username": "test",
    "ip": None,
    "raw": "..."
}
```

Ces événements sont ensuite transmis à :

* `bruteforce.py`
* `detect_bruteforce()`



## Ajustements de `detection.py`

Le rôle de `detection.py` a commencé à évoluer vers :

* orchestrateur central
* pipeline de traitement
* gestionnaire d’alertes

### Sortie enrichie

Les alertes affichent désormais :

* type d’attaque
* username ciblé
* score
* données brutes associées

Le système commence donc à produire des logs beaucoup plus détaillés et exploitables.



# 4. Création du premier parser WordPress (WIP)

### Fichier créé

```text id="file1"
parsers/wp_simple_history.py
```



## Fonction du parser

Le parser :

* récupère les événements via WP-CLI
* lit les logs générés par Simple History
* extrait les failed logins
* transforme les données en événements structurés

### Technologies utilisées

* `subprocess`
* `regex`
* parsing ligne par ligne



## Fonctionnalités implémentées

### Extraction :

* username
* type d’événement
* logs bruts

### Génération d’events Python

Exemple :

```python id="code3"
{
    "type": "failed_login",
    "username": "admin",
    "ip": None,
    "raw": "..."
}
```

