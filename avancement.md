# 20 avril 2026.

## 1. Brouillon du projet

Le projet a commencé par la définition d’un lab WordPress orienté sécurité, avec l’idée de construire un environnement de test local reproductible. L’objectif était de préparer une base utile pour la suite du projet IDS/IPS en Python, avec un WordPress fonctionnel, attaquable et observable. Le brouillon du projet a servi à poser l’architecture générale, les objectifs et la logique de travail avant la mise en place technique.

## 2. Mise en place de la repo

Une repo GitHub a été préparée pour centraliser le projet. L’idée était de séparer proprement le code du lab, les futurs scripts IDS/IPS, les attaques de test et la documentation. Une première structure a été pensée autour du projet WordPress et de l’analyse sécurité. La repo a ensuite été utilisée comme support principal pour versionner l’avancement, conserver les fichiers importants et rendre le travail partageable.

## 3. Problèmes avec Docker

L’installation et l’utilisation de Docker ont rencontré plusieurs problèmes successifs sur Kali Linux. Il y a d’abord eu des erreurs APT liées à un miroir cassé avec des paquets introuvables. Ensuite, l’installation de Docker a été incomplète au départ, avec absence du daemon, service `docker.service` manquant, puis problème de permissions sur le socket Docker. Le système a été corrigé étape par étape : mise à jour des dépôts, réinstallation de Docker, activation du service, puis ajout de l’utilisateur au groupe `docker`. À la fin, Docker a été validé avec `docker ps` et `docker run hello-world`.

## 4. Mise en place de WordPress

Le lab WordPress a ensuite été lancé avec Docker Compose. Le conteneur WordPress et le conteneur MySQL ont été démarrés sur `localhost:8080`. Une fois l’interface accessible, WordPress a été configuré manuellement. Un compte admin volontairement faible a été créé avec `admin:admin`, et un compte utilisateur simple avec `user:user123`, afin de préparer plus tard des tests de sécurité et de brute force dans un environnement contrôlé. Le site a été personnalisé, notamment avec l’ajout d’une image de chat sur une page de blog, ce qui a servi de test de modification de contenu. Des tests ont ensuite été réalisés avec Burp Suite, qui ont montré des différences intéressantes entre les réponses HTTP en cas de mauvais identifiants et en cas de connexion réussie. Enfin, le plugin WP Activity Log a été installé pour ajouter de la visibilité sur les actions et les connexions.

## 5. Relier GitHub à mon terminal Linux

Le terminal Linux a été relié à GitHub via une clé SSH. Une clé a été générée, ajoutée au compte GitHub, puis testée avec `ssh -T git@github.com`. La connexion a été confirmée avec succès, ce qui a permis de pousser le projet sans passer par un mot de passe à chaque fois. Ensuite, le dépôt local a été initialisé avec Git, le remote GitHub a été ajouté, puis la branche principale a été synchronisée avec le dépôt distant malgré la présence d’un README déjà existant sur GitHub. Après résolution du conflit d’historiques, le projet local a pu être poussé correctement vers la repo.

## 6. La backup SQL

Pour conserver l’état réel du WordPress, une sauvegarde SQL a été extraite depuis le conteneur MySQL. Cette base contient les données du site, les utilisateurs, les pages et les contenus créés pendant la configuration. Le fichier `backup.sql` a été vérifié et on y a retrouvé notamment l’entrée du compte admin et son hash de mot de passe. Cette sauvegarde permet de reconstruire l’état exact du WordPress plus tard, au lieu de repartir sur une installation vide. Elle a été pensée comme une base de restauration pour garder le progrès du lab au-delà de la machine locale.

## Bilan de la journée

La journée a servi à mettre en place la base complète du projet : infrastructure Docker réparée, WordPress fonctionnel, repo GitHub reliée, premier contenu créé, tests de comportement avec Burp Suite, et sauvegarde SQL du site. Le lab est maintenant prêt pour la suite du projet, à savoir la structuration du dépôt, puis le début du développement IDS/IPS en Python.
