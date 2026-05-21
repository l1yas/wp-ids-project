# Résumé de l’avancement  21/05/2026 — IDS WordPress

## Mise en place et debugging du parser WordPress

Travail effectué sur :

```text id="f1"
parsers/wp_simple_history.py
```



# Objectif du parser

Le parser a été conçu pour :

* récupérer les logs WordPress via WP-CLI
* parser les événements du plugin Simple History
* détecter les tentatives de connexion échouées
* transformer les logs en événements Python structurés



# Intégration Docker + WP-CLI

## Problème rencontré

Le parser utilisait initialement :

```python id="c1"
["wp", "simple-history", "list", "--allow-root"]
```

Ce qui provoquait :

```text id="c2"
FileNotFoundError: No such file or directory: 'wp'
```



## Cause identifiée

WP-CLI était disponible uniquement dans le container Docker WordPress et non sur l’hôte Kali.



## Correction appliquée

Migration vers :

```python id="c3"
["docker", "exec", "wordpress-wordpress-1",
 "wp", "simple-history", "list", "--allow-root"]
```

# Parsing des événements

## Première approche

Utilisation d’un filtrage simple :

```python id="c6"
if "Failed to login" in line:
```



## Regex initiale incorrecte

Regex problématique :

```python id="c7"
r'user name "([^"]+)"'
```

Puis :

```python id="c8"
r'username "(^"]+)"'
```



## Correction finale

Regex fonctionnelle :

```python id="c9"
r'username "([^"]+)"'
```



# Structuration du parsing

Ajout d’une fonction dédiée :

```python id="c10"
parse_line()
```



## Fonction du parser structuré

Découpage des colonnes WP-CLI via :

```python id="c11"
line.split("\t")
```

Extraction des champs :

* ID
* date
* initiator
* description
* level
* raw log



# Génération d’événements structurés

Le parser produit désormais :

```python id="c12"
{
    "type": "failed_login",
    "username": "admin",
    "date": "2026-05-21 17:11:06",
    "level": "warning",
    "raw": "..."
}
```



# Mise en place du mode debug

Ajout d’un mode debug affichant :

* les logs bruts WP-CLI
* les événements générés

via :

```python id="c13"
debug()
```

et commence à dépasser le simple script de parsing de logs.
