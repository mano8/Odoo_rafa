# Linux CheatSheet

Les systèmes d'exploitation inspirés d'UNIX, comme Linux, gèrent tout comme un fichier, y compris les répertoires et les périphériques. Une bonne compréhension des commandes en ligne permet de gérer le système efficacement. L'aide pour la plupart des commandes est accessible via la commande `man`.

## Gestion de Fichiers et Répertoires de Base

Pour naviguer et manipuler les fichiers et répertoires :

* **`ls`** : Liste le contenu d'un répertoire.
  * Pour afficher le contenu détaillé (permissions, propriétaire, taille, date) :

        ```bash
        ls -l /chemin/vers/repertoire
        ```

  * Pour afficher les fichiers cachés (ceux qui commencent par un '.') :

        ```bash
        ls -a
        ```

  * Pour combiner les options (-al montre les fichiers cachés avec détails) :

        ```bash
        ls -al
        ```

* **`cd`** : Permet de se déplacer dans l'arborescence des répertoires.
  * Pour aller dans un répertoire spécifique :

        ```bash
        cd /var/log/
        ```

  * Pour revenir au répertoire personnel de l'utilisateur :

        ```bash
        cd
        ```

  * Pour remonter au répertoire parent :

        ```bash
        cd ..
        ```

* **`mv`** : Déplace ou renomme des fichiers et des répertoires.
  * Pour renommer un fichier :

        ```bash
        mv ancien_nom.txt nouveau_nom.txt
        ```

  * Pour déplacer un fichier vers un répertoire :

        ```bash
        mv fichier.txt /chemin/vers/repertoire/
        ```

  * Pour déplacer un fichier et le renommer dans le répertoire de destination :

        ```bash
        mv fichier.txt /chemin/vers/repertoire/nouveau_nom.txt
        ```

* **`cp`** : Copie des fichiers ou des répertoires.
  * Pour copier un fichier :

        ```bash
        cp fichier_source.txt fichier_destination.txt
        ```

  * Pour copier un répertoire et son contenu (récursif) :

        ```bash
        cp -r repertoire_source/ repertoire_destination/
        ```

* **`rm`** : Supprime des fichiers ou des répertoires. Cette commande est potentiellement dangereuse.
  * Pour supprimer un fichier :

        ```bash
        rm fichier_a_supprimer.txt
        ```

  * Pour supprimer un répertoire vide :

        ```bash
        rmdir repertoire_vide/
        ```

  * Pour supprimer un répertoire et son contenu (récursif) sans confirmation (force) :

        ```bash
        rm -rf repertoire_a_supprimer/
        ```

  * Il est recommandé d'utiliser le chemin absolu pour éviter les erreurs dangereuses :

        ```bash
        sudo rm -rf /path/to/file/filename
        ```

* **`mkdir`** : Crée un répertoire vide.
  * Pour créer un répertoire :

        ```bash
        mkdir nouveau_repertoire
        ```

  * Pour créer les répertoires parents si nécessaire :

        ```bash
        mkdir -p chemin/vers/nouveau/repertoire
        ```

### Affichage et Édition de Fichiers

Pour visualiser ou modifier le contenu de fichiers texte :

* **`cat`** : Affiche le contenu d'un fichier texte.
  * Pour afficher le contenu :

        ```bash
        cat /chemin/vers/fichier.txt
        ```

  * Peut aussi être utilisé pour créer un fichier en redirigeant l'entrée standard :

        ```bash
        cat > nouveau_fichier.txt
        # Saisir le texte ici
        # Appuyer sur Ctrl+D pour terminer
        ```

* **`head`** : Affiche les premières lignes d'un fichier.
  * Pour afficher les 10 premières lignes (par défaut) :

        ```bash
        head fichier.log
        ```

  * Pour afficher les 50 premières lignes :

        ```bash
        head -n 50 fichier.log
        ```

* **`tail`** : Affiche les dernières lignes d'un fichier.
  * Pour afficher les 10 dernières lignes (par défaut) :

        ```bash
        tail fichier.log
        ```

  * Pour afficher les 20 dernières lignes :

        ```bash
        tail -n 20 fichier.log
        ```

  * Pour afficher le contenu au fur et à mesure qu'il est ajouté (utile pour les fichiers de log) :

        ```bash
        tail -f fichier.log
        ```

* **`less`** : Permet de parcourir un fichier page par page avec navigation. Pour quitter, tapez `:q`.
  * Pour afficher un fichier :

        ```bash
        less grand_fichier.txt
        ```

* **`nano`** : Un éditeur de texte simple en console.
  * Pour ouvrir un fichier pour édition :

        ```bash
        nano fichier_a_modifier.txt
        ```

* **`vi` / `vim`** : Des éditeurs de texte plus puissants en console. Nécessitent d'apprendre leurs modes de fonctionnement (mode insertion, mode commande).
  * Pour ouvrir un fichier :

        ```bash
        vim fichier_a_modifier.txt
        ```

### Recherche de Fichiers et Contenu

Pour trouver des fichiers ou rechercher des chaînes de caractères dans des fichiers :

* **`find`** : Cherche des fichiers dans une hiérarchie de répertoires. La recherche est récursive par défaut.
  * Pour trouver un fichier par nom (insensible à la casse, `iname`) dans le répertoire courant (.) :

        ```bash
        find . -iname "monfichier.txt"
        ```

  * Pour trouver tous les fichiers `.log` dans un répertoire et ses sous-répertoires :

        ```bash
        find /var/log -name "*.log"
        ```

  * Pour trouver des fichiers modifiés récemment (moins de 1 jour) :

        ```bash
        find . -mtime -1
        ```

  * Pour trouver des fichiers et exécuter une commande dessus (`-exec`) :

        ```bash
        find /chemin/vers/dossier -name "*.old" -exec rm {} \;
        ```

* **`grep`** : Recherche une chaîne de caractères dans des fichiers ou l'entrée standard. Souvent utilisé pour filtrer la sortie d'autres commandes.
  * Pour chercher une chaîne dans un fichier :

        ```bash
        grep "chaine_recherchee" fichier.txt
        ```

  * Pour chercher une chaîne dans plusieurs fichiers (récursif, `r`) et afficher uniquement les noms de fichiers correspondants (`l`) :

        ```bash
        grep -rl "chaine_recherchee" /chemin/vers/dossier/
        ```

  * Pour chercher une chaîne (insensible à la casse, `i`) dans la sortie d'une autre commande :

        ```bash
        ps aux | grep -i "firefox"
        ```

* **`locate`** : Trouve rapidement des fichiers en utilisant une base de données indexée.
  * Pour trouver toutes les occurrences d'un nom de fichier :

        ```bash
        locate nom_du_fichier
        ```

### Permissions et Propriété des Fichiers

Chaque fichier et répertoire a des permissions qui contrôlent qui peut lire (`r`), écrire (`w`) et exécuter (`x`) le fichier. Ces permissions sont définies pour trois types d'utilisateurs : l'utilisateur propriétaire (`u`), le groupe propriétaire (`g`) et les autres (`o`). Les répertoires nécessitent la permission `x` pour y accéder (`cd`) et la permission `r` pour lister leur contenu (`ls`).

* **`chmod`** : Modifie les permissions d'accès à un fichier ou un répertoire. Peut utiliser des lettres (`u`, `g`, `o`, `a`, `r`, `w`, `x`, `+`, `-`, `=`) ou des nombres (octal, 4 pour r, 2 pour w, 1 pour x).
  * Pour ajouter la permission d'exécution au propriétaire :

        ```bash
        chmod u+x mon_script.sh
        ```

  * Pour supprimer la permission d'écriture pour le groupe et les autres :

        ```bash
        chmod go-w fichier.txt
        ```

  * Pour fixer les permissions (rw-r--r--) :

        ```bash
        chmod 644 fichier.txt
        ```

  * Pour modifier les permissions d'un répertoire et de son contenu (récursif, `-R`) :

        ```bash
        sudo chmod -R 755 /chemin/vers/repertoire/
        ```

* **`chown`** : Change le propriétaire (`user`) et/ou le groupe propriétaire (`group`) d'un fichier. Souvent nécessite `sudo`.
  * Pour changer l'utilisateur propriétaire :

        ```bash
        sudo chown nouvel_utilisateur fichier.txt
        ```

  * Pour changer le groupe propriétaire :

        ```bash
        sudo chown :nouveau_groupe fichier.txt
        # ou
        sudo chgrp nouveau_groupe fichier.txt
        ```

  * Pour changer l'utilisateur et le groupe propriétaires :

        ```bash
        sudo chown nouvel_utilisateur:nouveau_groupe fichier.txt
        ```

  * Pour changer la propriété d'un répertoire et de son contenu (récursif, `-R`) :

        ```bash
        sudo chown -R nouvel_utilisateur:nouveau_groupe /chemin/vers/repertoire/
        ```

### Gestion des Utilisateurs et Groupes

Linux est un système multi-utilisateurs. La gestion des utilisateurs et des groupes est cruciale pour la sécurité. L'utilisateur `root` a accès à tous les fichiers. Sous Ubuntu, le compte root est désactivé par défaut, et `sudo` est utilisé pour exécuter des commandes administratives avec des privilèges élevés.

* **`sudo`** : Permet à un utilisateur autorisé d'exécuter une commande avec les privilèges d'un autre utilisateur (souvent `root`). L'utilisateur doit faire partie du groupe `sudo` et utiliser son propre mot de passe.
  * Exécuter une commande en tant que root :

        ```bash
        sudo commande_administrative
        ```

  * Ouvrir un shell root interactif (déconseillé sauf nécessité) :

        ```bash
        sudo -i
        # ou
        sudo su
        ```

* **`adduser`** : Ajoute un utilisateur au système de manière interactive (recommandé pour les distributions basées sur Debian/Ubuntu). Crée également un répertoire personnel par défaut (`/home/username`) et copie les fichiers de squelette (`/etc/skel`).
  * Pour ajouter un nouvel utilisateur :

        ```bash
        sudo adduser nouvel_utilisateur
        # Le script posera des questions (mot de passe, nom complet, etc.)
        ```

* **`deluser`** : Supprime un utilisateur du système. Par défaut, le répertoire personnel n'est PAS supprimé.
  * Pour supprimer un utilisateur :

        ```bash
        sudo deluser ancien_utilisateur
        ```

  * Pour supprimer l'utilisateur ET son répertoire personnel :

        ```bash
        sudo deluser --remove-home ancien_utilisateur
        ```

* **`addgroup`** : Ajoute un groupe au système.
  * Pour ajouter un nouveau groupe :

        ```bash
        sudo addgroup nouveau_groupe
        ```

* **`delgroup`** : Supprime un groupe du système.
  * Pour supprimer un groupe :

        ```bash
        sudo delgroup ancien_groupe
        ```

* **`adduser <user> <group>`** : Ajoute un utilisateur existant à un groupe existant. L'utilisateur doit se déconnecter et se reconnecter pour que les changements prennent effet.
  * Pour ajouter un utilisateur à un groupe :

        ```bash
        sudo adduser nom_utilisateur nom_groupe
        ```

* **`usermod`** : Modifie les paramètres d'un compte utilisateur (pour des modifications non-interactives ou spécifiques).
  * Pour ajouter un utilisateur à des groupes supplémentaires sans le retirer des groupes existants (`-aG`) :

        ```bash
        sudo usermod -aG groupe1,groupe2 nom_utilisateur
        ```

  * Pour renommer un utilisateur et son répertoire personnel (`-l`, `-d`, `-m`) :

        ```bash
        sudo usermod --login nouveau_login --home /home/nouveau_login --move-home ancien_login
        ```

* **`passwd`** : Modifie le mot de passe d'un utilisateur. Nécessite `sudo` pour changer le mot de passe d'un autre utilisateur.
  * Pour changer votre propre mot de passe :

        ```bash
        passwd
        ```

  * Pour changer le mot de passe d'un autre utilisateur (en tant qu'administrateur) :

        ```bash
        sudo passwd nom_utilisateur
        ```

* **`groups`** : Affiche les groupes auxquels appartient un utilisateur.
  * Pour afficher vos propres groupes :

        ```bash
        groups
        ```

  * Pour afficher les groupes d'un autre utilisateur :

        ```bash
        groups nom_utilisateur
        ```

* **`id`** : Affiche l'identifiant numérique (UID) et l'identifiant de groupe (GID) d'un utilisateur, ainsi que ses groupes.
  * Pour afficher les informations de votre compte :

        ```bash
        id
        ```

  * Pour afficher les informations d'un autre utilisateur :

        ```bash
        id nom_utilisateur
        ```

### Informations Système

Pour obtenir des informations sur le système, le matériel, l'OS, etc. :

* **`uname`** : Affiche des informations sur le système et le noyau.
  * Pour afficher toutes les informations (`-a`) :

        ```bash
        uname -a
        ```

  * Pour afficher la version du noyau (`-r`) :

        ```bash
        uname -r
        ```

* **`hostnamectl`** : Alternative pour obtenir des informations sur le système, y compris la distribution, la version du noyau et l'architecture.
  * Pour afficher les informations :

        ```bash
        hostnamectl
        ```

* **`lsb_release`** : Affiche des informations sur la distribution Linux Standard Base (LSB), y compris l'ID de la distribution et la version. Nécessite généralement le paquet `lsb-release`.
  * Pour afficher toutes les informations (`-a`) :

        ```bash
        lsb_release -a
        ```

* **`/etc/*-release`** : Fichiers contenant des informations sur la distribution. Leur contenu peut varier légèrement.
  * Pour afficher le contenu de `/etc/os-release` :

        ```bash
        cat /etc/os-release
        ```

* **`free`** : Affiche la mémoire disponible et utilisée (RAM et swap).
  * Pour afficher la mémoire en gigaoctets (`-g`) :

        ```bash
        free -g
        ```

  * Pour afficher la mémoire en unités lisibles par l'humain (`-h`) avec les totaux (`-t`) :

        ```bash
        free -th
        ```

* **`df`** : Affiche l'espace disque utilisé par les systèmes de fichiers.
  * Pour afficher l'espace disque en unités lisibles par l'humain (`-h`) :

        ```bash
        df -h
        ```

  * Pour afficher le type de système de fichiers (`-T`) en plus des informations lisibles par l'humain :

        ```bash
        df -Th
        ```

* **`du`** : Affiche l'espace disque utilisé par des fichiers ou répertoires.
  * Pour afficher la taille d'un répertoire en unités lisibles par l'humain (`-h`) :

        ```bash
        du -h /chemin/vers/repertoire
        ```

  * Pour afficher le total de l'espace utilisé par un répertoire (`-s`) en unités lisibles par l'humain :

        ```bash
        du -sh /chemin/vers/repertoire
        ```

* **`lspci`** : Liste les périphériques PCI.
  * Pour lister les périphériques :

        ```bash
        lspci
        ```

* **`lsusb`** : Liste les périphériques USB.
  * Pour lister les périphériques :

        ```bash
        lsusb
        ```

* **`lshw`** : Liste le matériel. Peut être utilisé pour identifier les interfaces réseau. Nécessite `sudo`.
  * Pour lister le matériel réseau :

        ```bash
        sudo lshw -class network
        ```

* **`uptime`** : Indique depuis combien de temps le système fonctionne.
  * Pour afficher l'uptime :

        ```bash
        uptime
        ```

### Gestion des Processus

Pour afficher, gérer et arrêter les processus en cours :

* **`top`** : Affiche les processus en cours, l'utilisation du CPU, de la mémoire, etc.. `htop` est une alternative plus complète et colorée. Pour quitter, tapez `q`.
  * Pour afficher la liste des processus :

        ```bash
        top
        ```

* **`ps`** : Affiche un instantané des processus en cours.
  * Pour afficher tous les processus du système (`aux`) :

        ```bash
        ps aux
        ```

* **`kill`** : Envoie un signal à un processus spécifié par son ID (PID). Le signal `TERM` (15) demande au processus de s'arrêter proprement, `KILL` (9) l'arrête de force.
  * Pour arrêter un processus proprement (ID 1234) :

        ```bash
        kill 1234
        ```

  * Pour arrêter un processus de force (ID 5678) :

        ```bash
        kill -9 5678
        # ou
        kill -KILL 5678
        ```

* **`killall`** : Envoie un signal à tous les processus portant un nom spécifique.
  * Pour arrêter tous les processus `firefox` :

        ```bash
        killall firefox
        ```

* **`pkill`** : Envoie un signal à des processus basés sur leur nom ou d'autres critères.
  * Pour arrêter tous les processus d'un utilisateur :

        ```bash
        sudo pkill -u nom_utilisateur
        ```

* **`bg`** : Reprend un processus arrêté en arrière-plan.
  * Pour placer un job en arrière-plan (après l'avoir suspendu avec Ctrl+Z) :

        ```bash
        bg
        ```

* **`fg`** : Ramène le dernier processus mis en arrière-plan au premier plan.
  * Pour ramener le dernier job en arrière-plan au premier plan :

        ```bash
        fg
        ```

### Gestion des Paquets

Pour installer, supprimer et gérer les logiciels (paquets) :

* **`apt` / `apt-get`** : Outil de gestion des paquets pour les distributions basées sur Debian (comme Ubuntu). `apt-get` est un outil plus ancien mais toujours largement utilisé.
  * Pour mettre à jour la liste des paquets disponibles (`update`) :

        ```bash
        sudo apt update
        # ou
        sudo apt-get update
        ```

  * Pour mettre à niveau tous les paquets installés (`upgrade`) :

        ```bash
        sudo apt upgrade
        # ou
        sudo apt-get upgrade
        ```

  * Pour installer un paquet (`install`) :

        ```bash
        sudo apt install nom_paquet
        # ou
        sudo apt-get install nom_paquet
        ```

  * Pour supprimer un paquet (`remove`) :

        ```bash
        sudo apt remove nom_paquet
        # ou
        sudo apt-get remove nom_paquet
        ```

  * Pour supprimer un paquet et ses fichiers de configuration (`purge`) :

        ```bash
        sudo apt purge nom_paquet
        # ou
        sudo apt-get --purge remove nom_paquet
        ```

* **`apt-cache`** : Outil pour consulter le cache des paquets APT.
  * Pour rechercher un paquet par nom ou description (`search`) :

        ```bash
        apt-cache search mot_cle
        ```

  * Pour afficher les informations détaillées d'un paquet (`show`) :

        ```bash
        apt-cache show nom_paquet
        ```

### Archivage et Compression

Pour créer ou extraire des archives (souvent compressées) :

* **`tar`** : Utilisé pour créer et extraire des fichiers archive `.tar`, souvent combiné avec la compression gzip ou bzip2 pour créer des `.tar.gz` ou `.tar.bz2`.
  * Pour créer une archive `.tar.gz` (`c`reate, g`z`ip, `v`erbose, `f`ilename) :

        ```bash
        tar -czvf archive.tar.gz /chemin/vers/repertoire_ou_fichier
        ```

  * Pour extraire une archive `.tar.gz` (`x`tract, `z`, `v`, `f`) dans le répertoire courant :

        ```bash
        tar -xzvf archive.tar.gz
        ```

  * Pour extraire une archive `.tar.gz` dans un répertoire spécifique (`-C`) :

        ```bash
        tar -xzvf archive.tar.gz -C /chemin/vers/repertoire_destination/
        ```

  * Pour utiliser la compression bzip2 (`-j` au lieu de `-z`) :

        ```bash
        tar -cjvf archive.tar.bz2 /chemin/vers/source
        tar -xjvf archive.tar.bz2
        ```

### Gestion des Services

Les services système sont gérés par un système d'initialisation (`init system`), souvent `systemd` sous Ubuntu. Les paquets fournissant des services incluent des unités `systemd`.

* **`systemctl`** : Utilisé pour contrôler et interroger l'état des services système sous `systemd`.
  * Pour démarrer un service :

        ```bash
        sudo systemctl start nom_du_service.service
        ```

  * Pour arrêter un service :

        ```bash
        sudo systemctl stop nom_du_service.service
        ```

  * Pour afficher l'état d'un service :

        ```bash
        systemctl status nom_du_service.service
        ```

  * Pour activer un service afin qu'il démarre au boot :

        ```bash
        sudo systemctl enable nom_du_service.service
        ```

  * Pour désactiver un service :

        ```bash
        sudo systemctl disable nom_du_service.service
        ```

### Configuration Réseau

La configuration réseau peut être gérée de diverses manières selon la distribution et les outils utilisés. Sur les systèmes modernes comme Ubuntu 18.04+ Serveur, Netplan est l'outil par défaut. Sur d'autres systèmes ou pour des configurations temporaires, des outils comme `ip`, `ifconfig`, `route`, etc. sont utilisés. La résolution de noms utilise `/etc/hosts` et les serveurs DNS configurés dans `/etc/resolv.conf`.

* **`ip`** : Utilisé pour afficher et configurer les adresses IP, les interfaces réseau et la table de routage. Remplace les anciens outils comme `ifconfig` et `route`.
  * Pour afficher les adresses IP de toutes les interfaces :

        ```bash
        ip addr show
        # ou plus court
        ip a
        ```

  * Pour configurer temporairement une adresse IP :

        ```bash
        sudo ip addr add 192.168.1.100/24 dev eth0
        ```

  * Pour activer (`up`) ou désactiver (`down`) une interface :

        ```bash
        sudo ip link set dev eth0 up
        sudo ip link set dev eth0 down
        ```

  * Pour afficher la table de routage :

        ```bash
        ip route show
        ```

  * Pour configurer temporairement une passerelle par défaut :

        ```bash
        sudo ip route add default via 192.168.1.1 dev eth0
        ```

* **`netplan`** : Utilisé sous Ubuntu Serveur pour configurer le réseau via des fichiers YAML dans `/etc/netplan/`.
  * Pour générer les configurations à partir des fichiers YAML et les appliquer :

        ```bash
        sudo netplan generate && sudo netplan apply
        ```

* **`ufw` (Uncomplicated Firewall)** : Outil par défaut sous Ubuntu pour gérer le pare-feu Netfilter/iptables.
  * Pour vérifier l'état du pare-feu :

        ```bash
        sudo ufw status
        ```

  * Pour activer le pare-feu :

        ```bash
        sudo ufw enable
        ```

  * Pour désactiver le pare-feu :

        ```bash
        sudo ufw disable
        ```

  * Pour autoriser le trafic entrant sur un port (ex: 22 pour SSH) :

        ```bash
        sudo ufw allow 22
        # ou en utilisant le nom du service s'il est connu
        sudo ufw allow ssh
        ```

  * Pour refuser le trafic entrant sur un port :

        ```bash
        sudo ufw deny 22
        ```

  * Pour autoriser le trafic entrant d'une adresse IP spécifique :

        ```bash
        sudo ufw allow from 203.0.113.101
        ```

  * Pour refuser le trafic entrant d'un sous-réseau :

        ```bash
        sudo ufw deny from 203.0.113.0/24
        ```

  * Pour autoriser le trafic entrant sur un port spécifique depuis une IP spécifique (ex: SSH port 22) :

        ```bash
        sudo ufw allow from 203.0.113.103 to any port 22 proto tcp
        ```

  * Pour lister les profils d'application disponibles (ex: pour Apache, Nginx, OpenSSH) :

        ```bash
        sudo ufw app list
        ```

  * Pour autoriser un profil d'application (ex: pour Nginx Full - HTTP et HTTPS) :

        ```bash
        sudo ufw allow "Nginx Full"
        ```

  * Pour supprimer une règle UFW (par la règle elle-même ou par son numéro, listé par `sudo ufw status numbered`) :

        ```bash
        sudo ufw delete deny 22
        # ou
        sudo ufw delete 1
        ```

  * Pour activer la journalisation (logging) UFW :

        ```bash
        sudo ufw logging on
        ```

### Commandes Diverses Utiles

* **`man <commande>`** : Affiche le manuel (documentation) pour une commande. Pour quitter, tapez `q`.
  * Pour lire le manuel de `ls` :

        ```bash
        man ls
        ```

* **`echo`** : Affiche une ligne de texte. Peut être utilisé pour écrire dans un fichier, écraser (`>`) ou ajouter (`>>`).
  * Pour afficher du texte :

        ```bash
        echo "Bonjour le monde"
        ```

  * Pour écrire du texte dans un fichier (écrase le contenu existant) :

        ```bash
        echo "Ceci est la première ligne." > mon_fichier.txt
        ```

  * Pour ajouter du texte à la fin d'un fichier :

        ```bash
        echo "Ceci est une ligne supplémentaire." >> mon_fichier.txt
        ```

* **`tee`** : Lit l'entrée standard et écrit simultanément sur la sortie standard et dans un ou plusieurs fichiers.
  * Pour écrire du texte dans un fichier et l'afficher simultanément :

        ```bash
        echo "Mon texte" | tee mon_fichier.txt
        ```

* **`ln -s <source> <lien>`** : Crée un lien symbolique (raccourci).
  * Pour créer un lien symbolique :

        ```bash
        ln -s /chemin/vers/fichier_original /chemin/vers/le_lien
        ```

* **`crontab`** : Gère les tâches planifiées (cron jobs) pour un utilisateur. Les tâches système globales sont souvent placées dans des fichiers sous `/etc/cron.d/` ou dans les répertoires `cron.hourly`, `cron.daily`, etc..
  * Pour éditer votre crontab :

        ```bash
        crontab -e
        ```

* **`/run` et `/var/run`** : Répertoire pour les fichiers temporaires créés au démarrage ou par les services. Généralement effacé au boot. `/var/run` est un lien symbolique vers `/run`. Les services doivent créer les sous-répertoires nécessaires dynamiquement.

* **`/etc/default/`** : Répertoire contenant des fichiers de configuration pour les variables utilisées par les scripts d'initialisation (`init.d`). Ces fichiers doivent être sourced par les scripts.

* **Redémarrage nécessaire** : Un fichier de signalisation `/run/reboot-required` est touché lorsque le système nécessite un redémarrage (souvent après une mise à jour de paquet). Les paquets concernés peuvent être listés dans `/run/reboot-required.pkgs`.

Cette liste couvre un large éventail de commandes et concepts essentiels pour l'utilisation et l'administration d'un système Linux basé sur les sources fournies. **L'utilisation de `sudo` est requise pour la plupart des commandes administratives** qui modifient les fichiers système, les utilisateurs, les groupes, les permissions ou la configuration réseau. **Soyez toujours prudent lors de l'utilisation de commandes comme `rm -rf` ou lors de la modification de permissions/propriété avec `chmod`/`chown` sur des fichiers système importants**. En cas de doute, consultez le manuel (`man`) ou utilisez l'option `-s` (simulation) avec `apt-get`.
