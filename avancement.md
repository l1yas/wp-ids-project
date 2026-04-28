## 28/04 - Bilan technique de `detection.py` (IDS WordPress Docker)

### 1. Rôle général du script

Le script `detection.py` est un système de détection d’intrusions (IDS) basique conçu pour analyser en temps réel les logs HTTP générés par un conteneur WordPress exécuté sous Docker. Son objectif est d’identifier des comportements potentiellement malveillants à partir de patterns connus d’attaques web.



### 2. Source des données

Le script s’appuie sur un flux en temps réel des logs du conteneur Docker WordPress :

* Source : `docker logs -f wordpress-wordpress-1`
* Type de données : logs Apache HTTP (format access log)
* Contenu typique :

  * Adresse IP source
  * Timestamp
  * Requête HTTP (méthode, URL, paramètres)
  * Code de réponse
  * User-Agent

Le flux est consommé ligne par ligne via un subprocess Python.



### 3. Fonctionnement du pipeline

#### a. Lecture des logs

Le script ouvre un processus Docker et lit les logs en streaming continu. Chaque ligne représente une requête HTTP traitée par WordPress/Apache.

#### b. Extraction implicite

Aucune structuration avancée n’est appliquée. La ligne brute est directement utilisée pour l’analyse.

#### c. Moteur de détection

Le cœur du système repose sur un dictionnaire de signatures regex :

* SQL Injection :

  * détection de caractères d’échappement (`'`, `--`, `#`)
  * patterns de type `union select`
  * conditions classiques `or 1=1`
  * fonctions suspectes comme `sleep()`

* Local File Inclusion :

  * traversal de répertoires (`../`)
  * accès à fichiers sensibles (`/etc/passwd`, `wp-config.php`)

* Cross-Site Scripting :

  * balises `<script>`
  * schémas `javascript:`
  * événements HTML (`onerror=`)

Chaque ligne est testée contre ces expressions régulières.



### 4. Logique de décision

* Si une correspondance regex est trouvée :

  * un type d’attaque est assigné (SQLi, LFI, XSS)
  * une alerte est générée immédiatement

* Si aucune correspondance :

  * la ligne est ignorée

Le système fonctionne donc en classification binaire simple : match ou non-match.



### 5. Système d’alerting

Lorsqu’une détection est effectuée :

* Un message est affiché en console
* L’événement est écrit dans un fichier `alerts.log`

Le format inclut :

* type d’attaque détecté
* ligne brute du log



### 6. Limites actuelles

#### a. Absence de parsing structuré

Le script analyse la ligne brute sans extraction formelle des champs (IP, URL, méthode, etc.), ce qui limite la précision.

#### b. Détection uniquement par signature

Le moteur repose exclusivement sur des regex statiques, sans analyse comportementale.

#### c. Aucun système de corrélation

Il n’y a pas de notion :

* de fréquence par IP
* de répétition d’attaque
* de séquence d’événements

#### d. Faux positifs possibles

Certaines regex (ex : `'` ou `--`) peuvent déclencher sur du trafic normal.

#### e. Absence de scoring

Toutes les alertes ont le même niveau de gravité.



### 7. Forces du prototype

* Fonctionne en temps réel
* Simple à comprendre et à étendre
* Facilement modifiable (ajout de patterns)
* Compatible environnement Docker
* Bonne base pédagogique pour IDS signature-based



### 8. Positionnement du projet

Ce script correspond à un IDS de niveau débutant à intermédiaire basé sur signatures. Il se rapproche conceptuellement de :

* un mini moteur Suricata simplifié
* un logger de sécurité applicatif
* une base de SOC prototype



### 9. Évolutivité naturelle

Le design permet plusieurs améliorations structurantes :

* parsing avancé des logs Apache
* système de scoring par sévérité
* détection comportementale (rate-based detection)
* corrélation multi-requêtes par IP
* export JSON pour SIEM externe
* interface de visualisation (dashboard)



### 10. Conclusion

Le script `detection.py` constitue un prototype fonctionnel d’IDS basé sur l’analyse de logs WordPress en environnement Docker. Il démontre la capacité à :

* consommer un flux de logs en temps réel
* appliquer des règles de détection par signatures
* générer des alertes simples

Cependant, il reste limité à une logique statique et non contextuelle, ce qui en fait une base pédagogique solide mais non adaptée à un environnement de production ou à une détection avancée de menaces.
