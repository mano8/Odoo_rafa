# **Gestion des Paquets**

Sous Linux, en particulier dans les distributions basées sur Debian comme Ubuntu, la gestion des logiciels se fait principalement à l'aide de **paquets**. Un paquet est un ensemble de fichiers (programmes, bibliothèques, documentation, etc.) prêts à être installés sur le système. Les outils de gestion de paquets s'occupent d'installer, de mettre à jour, de configurer et de supprimer ces logiciels, en gérant automatiquement leurs dépendances.

Les sources fournies décrivent plusieurs outils pour la gestion des paquets, notamment `apt`, `apt-get`, `apt-cache` et `dpkg`. D'autres systèmes de gestion de paquets comme `yum` (pour CentOS) et `npm` (pour Node.js) ainsi que l'installation à partir des sources sont également mentionnés.

Voici un aperçu détaillé :

## **APT : L'outil de haut niveau**

**APT** (Advanced Package Tool) est un système de gestion de paquets de haut niveau utilisé dans Debian et ses dérivés comme Ubuntu. Il simplifie la gestion des logiciels en s'interfaçant avec des outils de plus bas niveau comme `dpkg` et en résolvant automatiquement les dépendances. La plupart des opérations quotidiennes de gestion de paquets sont effectuées avec les commandes `apt-get` ou la commande plus récente et souvent plus conviviale `apt`.

* **Mettre à jour la liste des paquets disponibles** : Il est essentiel de mettre à jour l'index des paquets disponibles à partir des sources configurées (serveurs de dépôts) avant d'installer ou de mettre à niveau des logiciels.
  * `sudo apt-get update`
  * `sudo apt update`
  * Cette commande met à jour la liste des paquets *disponibles*, pas les paquets installés sur votre système.

* **Installer des paquets** : Permet d'installer un ou plusieurs paquets ainsi que toutes les dépendances nécessaires.
  * `sudo apt-get install <paquet1> [<paquet2> ...]`
  * `sudo apt install <paquet1> [<paquet2> ...]`
  * L'option `-y` peut être utilisée pour répondre automatiquement "oui" à toutes les questions.
  * L'option `-f` (utilisée avec `install`) permet de réparer un système dont les dépendances sont défectueuses.

* **Supprimer des paquets** : Permet de désinstaller un ou plusieurs paquets.
  * `sudo apt-get remove <paquet1> [<paquet2> ...]`
  * `sudo apt remove <paquet1> [<paquet2> ...]`
  * L'option `--purge` utilisée avec `remove` supprime le paquet ainsi que tous ses fichiers de configuration, sauf ceux qui pourraient se trouver dans le répertoire personnel de l'utilisateur (`/home`).
  * `sudo apt --purge remove <paquet1>` ou `sudo apt purge <paquet1>`
  * L'option `-f` (utilisée avec `remove`) permet de réparer un système dont les dépendances sont défectueuses.

* **Mettre à niveau les paquets installés** : Permet de mettre à jour tous les paquets qui sont déjà installés sur le système avec leurs versions les plus récentes disponibles dans les dépôts.
  * `sudo apt-get upgrade`
  * `sudo apt upgrade`
  * `apt-get dist-upgrade` est similaire à `upgrade` mais permet en plus de passer à une version supérieure du noyau et de certains paquets sans changer de version d'Ubuntu. L'option `--reinstall` peut être utilisée avec `apt-get` pour réinstaller les paquets avec leur version la plus récente.

* **Nettoyer les paquets téléchargés** : Supprime les fichiers d'installation téléchargés (`.deb`) qui ne sont plus nécessaires du cache système (`/var/cache/apt/archives/`).
  * `sudo apt-get clean`
  * `sudo apt clean`
  * Cela efface les installateurs du système sans désinstaller de paquets.

* **Options communes pour `apt-get` et `apt`** :
  * `-s` : Effectue une simulation des actions sans rien modifier sur le système.
  * `-y` : Répond automatiquement "oui" à toutes les questions.
  * `-u` : Affiche les paquets qui seront mis à jour.

### **apt-cache : Interroger le cache APT**

La commande `apt-cache` permet de gérer les paquets et de manipuler le cache utilisé par APT. Elle est utile pour rechercher des informations sur les paquets disponibles.

* **Rechercher des paquets** : Permet de rechercher une expression régulière (un mot ou une phrase) dans les noms et les descriptions de tous les paquets disponibles.
  * `apt-cache search <expression>`
  * L'option `-n` recherche uniquement dans les noms des paquets.
  * Exemple : `apt-cache search -n irc` recherche et affiche tous les paquets ayant "irc" dans leur nom.

* **Afficher les informations d'un paquet** : Affiche des informations détaillées sur un paquet spécifique, telles que sa description, ses dépendances, ses versions disponibles, etc..
  * `apt-cache show <paquet>`
  * Exemple : `apt-cache show xeyes` affiche les informations du paquet `xeyes`.

* **Vérifier les dépendances** :
  * `apt-cache depends <paquet>` : Affiche les paquets dont dépend le paquet spécifié.
  * `apt-cache rdepends <paquet>` : Affiche les paquets qui dépendent du paquet spécifié.
  * Exemple : `apt-cache depends ubuntu-desktop` affiche toutes les dépendances du paquet `ubuntu-desktop`.

* **Afficher le dépôt d'un paquet** : Indique quel dépôt (source de paquet) fournit le paquet spécifié.
  * `apt-cache madison <paquet>`
  * Exemple : `apt-cache madison brasero` indique le dépôt qui fournit le paquet `brasero`.

### **dpkg : L'outil de bas niveau**

`dpkg` est l'outil de gestion de paquets de base de Debian et Ubuntu. Il est utilisé par APT pour installer, configurer, mettre à niveau et supprimer des paquets, mais il ne gère pas automatiquement les dépendances.

* **Installer un fichier `.deb`** : Permet d'installer un paquet directement à partir d'un fichier `.deb` téléchargé. `dpkg` ne résoudra pas les dépendances manquantes ; il faudra peut-être utiliser `apt-get install -f` par la suite pour corriger les dépendances cassées.
  * `dpkg -i <fichier.deb>`

### **Installation à partir des sources**

Outre l'installation via des gestionnaires de paquets, il est également possible d'installer des logiciels à partir de leur code source. Cela implique généralement les étapes suivantes :

1. Exécuter `./configure` : Ce script vérifie l'environnement système et crée les Makefiles nécessaires à la compilation.
2. Exécuter `make` : Cette commande compile le code source pour créer les fichiers binaires.
3. Exécuter `make install` : Cette commande installe les fichiers compilés dans le système, généralement dans les répertoires standards comme `/usr/local/bin`, `/usr/local/lib`, etc..

Cette méthode est plus complexe et n'est généralement utilisée que si le logiciel n'est pas disponible dans les dépôts, si une version spécifique est requise, ou pour des raisons de développement.

### **Autres gestionnaires de paquets mentionnés**

Les sources mentionnent brièvement d'autres gestionnaires de paquets spécifiques à d'autres distributions ou types de logiciels :

* `yum` : Un gestionnaire de paquets couramment utilisé dans les distributions basées sur Red Hat/CentOS.
* `rpm` : L'outil de gestion de paquets de bas niveau pour les distributions basées sur Red Hat/CentOS, similaire à `dpkg`.
* `npm` : Le gestionnaire de paquets par défaut pour l'environnement d'exécution JavaScript Node.js.

La gestion des paquets est un aspect fondamental de l'administration d'un système Linux, permettant de maintenir les logiciels à jour et sécurisés.

Êtes-vous prêt(e) à passer à la catégorie suivante, qui pourrait être la **Configuration Réseau** ou la **Gestion des Utilisateurs et Groupes** ?
