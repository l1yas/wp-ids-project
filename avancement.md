# Résumé de l’avancement — 03/06/2026 — IDS WordPress

# Ajout d'un moteur d'authentification dédié

Création d'un pipeline séparé :

```python
auth_loop()
```

Objectif :

* surveiller les événements WordPress
* détecter les connexions échouées
* alimenter le moteur de brute force



## Source des événements

Utilisation de WP-CLI :

```bash
docker exec wordpress-wordpress-1 \
wp simple-history list --allow-root
```

Le plugin Simple History fournit :

```text
Failed to login with username "admin"
```



## Extraction des utilisateurs

Création d'un parser dédié :

```python
extract_username()
```

Regex utilisée :

```python
r'username "([^"]+)"'
```

Exemple :

```text
Failed to login with username "admin"
```

↓

```python
admin
```



# Gestion des doublons

Problème rencontré :

```text
wp simple-history list
```

renvoie l'historique complet à chaque exécution.

Conséquence :

* retraitement permanent des mêmes événements
* faux positifs possibles



## Solution

Ajout d'un cache mémoire :

```python
seen = set()
```

Chaque événement déjà traité est ignoré :

```python
if key in seen:
    continue
```



# Passage à une architecture multi-thread

Introduction du module :

```python
import threading
```



## Thread Web

Création :

```python
web_loop()
```

Responsabilités :

* lecture des logs Docker
* détection SQLi
* détection LFI
* détection XSS
* génération des alertes



## Thread Auth

Création :

```python
auth_loop()
```

Responsabilités :

* interrogation de WP-CLI
* extraction des utilisateurs
* comptage des échecs
* détection brute force



## Lancement parallèle

Mise en place :

```python
t1 = threading.Thread(target=web_loop, daemon=True)
t2 = threading.Thread(target=auth_loop, daemon=True)
```

Démarrage :

```python
t1.start()
t2.start()
```

Le système surveille désormais simultanément :

```text
Logs HTTP
+
Logs WordPress
```



# Débogage et corrections majeures

## Correction d'une boucle infinie coûteuse

Erreur d'indentation détectée :

```python
while True:
    process = subprocess.Popen(...)
```

sans traitement associé.

Conséquence :

```text
Création massive de processus Docker
CPU à 100 %
Système fortement ralenti
```

Correction :

* réintégration correcte du parsing dans la boucle
* ajout du délai :

```python
time.sleep(5)
```



## Correction des erreurs de logique

Correction de plusieurs problèmes :

* faute de frappe sur `threshold`
* mauvaise utilisation de `append()`
* erreurs d'indentation
* variables incohérentes
* logique de détection incomplète



# État actuel du projet

## Fonctionnel

### Détection Web

* SQL Injection
* Local File Inclusion
* Cross-Site Scripting
* surveillance en temps réel

### Détection Authentification

* extraction des échecs de connexion WordPress
* suivi des utilisateurs ciblés
* détection de brute force basée sur le temps

### Journalisation

* alertes console
* alertes fichier

```text
alerts.log
```

* événements JSON

```text
logs.json
```



# Architecture actuelle

```text
                +------------------+
                |  Docker Logs     |
                +---------+--------+
                          |
                          v
                   web_loop()
                          |
                    SQLi/LFI/XSS
                          |
                          v
                      Alertes

                +------------------+
                |  WP Simple History|
                +------+--+
                          |
                          v
                   auth_loop()
                          |
                    Bruteforce Engine
                          |
                          v
                      Alertes
```




