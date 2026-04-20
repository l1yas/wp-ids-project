# Draft Projet – IDS/IPS pour WordPress 



# 1. Objectif du projet

Mettre en place un environnement de test où :

- WordPress est volontairement exposé dans un lab local
- un attaquant simule des attaques web
- un système IDS/IPS Python analyse le trafic HTTP
- le système :
    - détecte les attaques
    - génère des alertes
    - bloque les IP si nécessaire



# 2. Architecture globale

```
[ Attaquant]
        ↓ HTTP requests
[ WordPress (cible locale) ]
        ↓ trafic HTTP
[ IDS/IPS Python Engine ]
        ↓
[ Logs + API + Actions (block/alert) ]
```



# 3. Composants du système

## A. Environnement WordPress (cible)

- WordPress local (Apache/Nginx + MySQL)
- endpoints exposés :
    - `/wp-login.php`
    - `/wp-admin`
    - pages publiques
- configuration volontairement testable (lab)



## B. Module de capture HTTP

- intercepte les requêtes vers WordPress
- récupère :
    - IP source
    - URL
    - méthode (GET/POST)
    - payload



## C. Moteur IDS (analyse)

- applique des règles de détection :
    - brute force login
    - scan de répertoires
    - injection SQL / XSS
    - flood HTTP



## D. Moteur IPS (réponse)

- actions possibles :
    - ALLOW
    - ALERT
    - BLOCK IP



## E. Logging

- enregistre chaque événement :
    - IP
    - type d’attaque
    - timestamp
    - score de menace



## F. API 

- expose les alertes pour un dashboard
- format JSON



## G. Dashboard 

- affichage des alertes IDS
- visualisation temps réel



# 4 . Types d’attaques testées dans le lab

## Brute force login

- `/wp-login.php`

## Scan de fichiers sensibles

- `/wp-admin`
- `/xmlrpc.php`
- `/wp-config.php`

## SQL Injection

```
?user=admin' OR 1=1--
```

## XSS

```
<script>alert(1)</script>
```

## HTTP Flood

- nombreuses requêtes rapides depuis une IP



# 5. Modes du système

## 🟢 IDS mode

- détecte seulement
- log + alert

## 🔴 IPS mode

- détecte + bloque IP en temps réel



# 6. Sorties du système

Chaque alerte contient (exemple) :

```json
{
  "ip": "192.168.1.5",
  "attack_type": "Brute Force",
  "url": "/wp-login.php",
  "severity": 5,
  "timestamp": "2026-04-20T10:00:00"
}
```



# 7. Évolutions possibles

- scoring avancé (risk engine)
- verification d’IP suspectes
- dashboard SOC complet

