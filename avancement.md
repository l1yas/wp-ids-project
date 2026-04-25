# 25 avril



## 1. Mise en place de l’environnement Docker

Le projet a commencé avec la création d’un environnement WordPress basé sur Docker Compose, comprenant :

* un service MySQL (base de données)
* un service WordPress Apache
* un conteneur WP-CLI pour l’automatisation

Les premiers problèmes rencontrés concernaient :

* des conflits de conteneurs déjà existants (ports 8080 déjà utilisés)
* des erreurs de nommage de conteneurs Docker
* des incohérences entre images MySQL utilisées (mysql:5.7 vs mysql:8.0)



## 2. Problèmes liés à la base de données

Plusieurs erreurs ont bloqué l’initialisation :

* impossibilité de connexion entre WordPress et MySQL
* erreurs “Error establishing a database connection”
* délais d’attente insuffisants lors du démarrage de la base
* conteneur MySQL parfois non prêt au moment des requêtes WP-CLI

Des solutions partielles ont été mises en place :

* ajout de boucles d’attente (mysqladmin ping)
* redémarrages via docker compose down/up
* nettoyage des volumes Docker pour repartir d’un état propre



## 3. Problèmes WP-CLI

WP-CLI a présenté plusieurs blocages :

* commande `wp` introuvable dans certains contextes
* absence de WordPress installé dans `/var/www/html`
* erreurs lors de `core download` (manque de mémoire PHP)
* erreurs de permissions sur le volume `/var/www/html`
* impossibilité d’exécuter certaines commandes sans installation initiale WordPress

Conclusion fonctionnelle :
WP-CLI ne peut pas être utilisé tant que WordPress n’est pas initialisé correctement.



## 4. Initialisation WordPress (install.php)

Un blocage important a été identifié :

* WordPress nécessite une installation initiale via `wp-admin/install.php`
* sélection de langue obligatoire
* création manuelle de l’administrateur nécessaire

Cela a empêché une automatisation complète immédiate du setup.

Conclusion :
Une étape humaine minimale reste nécessaire pour finaliser l’installation initiale WordPress dans ce setup.



## 5. Seed de la base de données

Un script de seed a été introduit pour automatiser la création d’utilisateurs.

Problèmes rencontrés :

* tables WordPress inexistantes avant installation (`wp_users` absent)
* erreurs SQL lors de l’injection des utilisateurs
* nécessité d’attendre la création complète du schéma WordPress

Une fois la base correctement initialisée, le seed fonctionne correctement et permet :

* création d’utilisateurs supplémentaires
* insertion de données de test



## 6. Problèmes Git et gestion du repository

Un problème majeur a été identifié dans la gestion du dépôt Git :

* présence initiale d’un fichier `backup.sql` dans le repository
* mauvaise pratique (fichier de base de données versionné)
* nécessité de nettoyage de l’historique Git

Actions effectuées :

* tentative de suppression simple (rm + commit) insuffisante
* utilisation de `git filter-repo` pour réécriture complète de l’historique
* résolution des erreurs liées aux clones non propres
* correction des problèmes de remote GitHub supprimé par filter-repo
* utilisation de force push pour synchroniser GitHub

Résultat :
Repository nettoyé avec suppression complète du fichier `backup.sql` dans l’historique.



## 7. Stabilisation finale

Après plusieurs itérations :

* Docker fonctionne de manière stable après nettoyage des volumes
* WordPress démarre correctement
* la base de données est accessible
* le seed fonctionne une fois WordPress initialisé
* le repository GitHub est propre et synchronisé



## 8. Conclusion générale

Les difficultés principales ont été :

* synchronisation entre WordPress et MySQL au démarrage
* contrainte d’installation initiale WordPress empêchant l’automatisation complète
* gestion incorrecte initiale des données dans Git (backup.sql versionné)
* compréhension du cycle complet Docker + WordPress + WP-CLI

Le système est maintenant fonctionnel, reproductible via Docker, et le repository a été nettoyé pour correspondre à de bonnes pratiques (absence de dumps SQL, utilisation de scripts d’initialisation et seed).


