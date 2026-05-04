## Bilan du projet IDS WordPress — 04/05/2026

### 1. État actuel du système

Le projet IDS repose sur une architecture simple mais fonctionnelle permettant l’analyse en temps réel des logs WordPress exécutés dans un environnement Docker. Le système détecte actuellement des attaques basées sur des signatures et commence à intégrer des comportements anormaux.

### 2. Évolution de detection.py
Objectif de l'évolution :

Structurer les alertes de sécurité en sortie exploitable pour analyse et extension future.

Changements effectués :
- Ajout d’un output JSON structuré (NDJSON) pour chaque événement détecté
- Conservation du logging console pour debug humain
Enrichissement des événements avec des champs exploitables :
- IP source
- type d’attaque
- timestamp (si extrait)
- log brut
- Résultat

Le système produit désormais deux flux :

Logs texte (lecture humaine)
Logs JSON (analyse machine / futur SIEM)


### 3. Ajout de bruteforce.py
Objectif

Introduire une détection comportementale basée sur le temps, en complément des signatures statiques.

Logique implémentée
- Suivi des requêtes par IP dans une fenêtre temporelle
Détection basée sur :
- fréquence de requêtes
- seuil défini sur une période courte
Limites actuelles
- Détection trop permissive sans données de statut HTTP ou login success/failure
- Impossible de distinguer avec certitude échec ou succès d’authentification
- Déclenchements parfois précoces selon le trafic de fond du container

### 4. Prochains objectifs

Enrichir l’environnement WordPress afin d’améliorer la précision du module bruteforce.
Mise à jour de seed.sh
- Ajouter des plugins WordPress permettant :
    - la journalisation des événements d’authentification
    - la visibilité des failed logins
    - l’enrichissement des logs exploitables par l’IDS
Avec les plugins :
- détection de failed login réelle
- identification des usernames ciblés
- réduction des faux positifs
