# Linux CheatSheet

Absolument ! Je vais enrichir votre anti-sèche Linux en intégrant les informations pertinentes issues des sources que vous avez fournies et en m'appuyant sur mes connaissances pour la rendre plus complète et plus claire.

Voici une version améliorée de votre anti-sèche :

***

**Anti-Sèche des Commandes Essentielles Linux**

Ce document compile des commandes Linux courantes, particulièrement utiles sur les distributions basées sur Debian, comme Ubuntu.

**Concepts de Base**

* Dans Linux/Unix, presque tout est un fichier, y compris les répertoires et les périphériques.
* Le super-utilisateur **root** a la capacité d'accéder à n'importe quel fichier sur le système. Les développeurs d'Ubuntu désactivent le compte root par défaut, utilisant plutôt la commande **sudo** pour les tâches administratives.
* **sudo** ("superuser do") permet à un utilisateur autorisé d'exécuter des commandes avec les privilèges d'un autre utilisateur (souvent root), généralement en utilisant son propre mot de passe. L'utilisateur initial créé par l'installateur Ubuntu est par défaut membre du groupe `sudo`.

**Aide et Documentation**

* **man commande** : Affiche le manuel d'aide pour une `commande`. Appuyez sur `q` pour quitter le manuel.
* **commande --help** ou **commande -h** : Affiche une aide rapide pour la `commande`.
* **which commande** : Affiche le chemin complet de l'exécutable de la `commande`.
* **whereis commande** : Affiche les emplacements possibles de la `commande`, de la source et des pages de manuel.

**Navigation et Gestion de Fichiers/Répertoires**

* **ls** : Liste le contenu d'un répertoire.
  * **-l** : Affiche les détails (permissions, propriétaire, taille, date).
  * **-h** : Utilisé avec `-l`, affiche les tailles dans un format lisible (K, M, G).
  * **-a** : Affiche tous les fichiers, y compris les fichiers cachés (ceux commençant par un point `.`).
  * **-al** : Combine `-a` et `-l`.
  * **-lct** : Trie par date de modification décroissante.
  * **ls -1** : Liste un fichier par ligne (utile pour compter).
* **cd répertoire** : Change de répertoire pour le `répertoire` spécifié.
  * **cd** (sans argument) : Retourne au répertoire personnel de l'utilisateur (`~`).
  * **cd -** : Retourne au répertoire précédent.
  * **cd ..** : Remonte d'un niveau dans l'arborescence.
  * **cd /** : Va à la racine du système de fichiers.
* **pwd** : Affiche le chemin complet du répertoire de travail actuel.
* **mkdir répertoire** : Crée un nouveau répertoire.
  * **-p** : Crée les répertoires parents si nécessaire.
* **rmdir répertoire** : Supprime un répertoire **vide**.
  * **-p** : Supprime les répertoires parents s'ils deviennent vides.
* **mv source destination** : Déplace ou renomme des fichiers/répertoires.
  * **-f** : Force l'écrasement sans confirmation.
  * **-i** : Demande confirmation avant d'écraser.
  * **-u** : Ne déplace/renomme que si le fichier source est plus récent que la destination.
* **cp source destination** : Copie des fichiers/répertoires.
  * **-r** ou **-R** : Copie un répertoire et son contenu de manière récursive.
  * **-a** : Mode archive, préserve les permissions, les dates, les propriétaires, etc..
  * **-i** : Demande confirmation avant d'écraser.
  * **-u** : Ne copie que les fichiers plus récents ou qui n'existent pas.
* **rm fichier** : Supprime des fichiers. **Attention : cette commande est très dangereuse, surtout avec `-r` et `-f` !**.
  * **-f** : Force la suppression sans confirmation.
  * **-r** : Supprime de manière récursive (dossiers et leur contenu).
  * **rm -rf répertoire** : Supprime de manière forcée et récursive un répertoire et son contenu. **À utiliser avec la plus grande prudence !**.
* **touch fichier** : Crée un fichier vide ou met à jour l'horodatage d'un fichier existant.
* **ln -s cible lien** : Crée un **lien symbolique** (raccourci) vers une `cible`.
  * **ln cible lien** : Crée un lien physique (moins courant).

**Affichage et Édition de Fichiers**

* **cat fichier** : Affiche le contenu complet d'un fichier texte.
  * **-n** : Affiche le contenu avec les numéros de ligne.
* **more fichier** : Affiche le contenu d'un fichier page par page (utilisez Espace pour avancer, `q` pour quitter).
* **less fichier** : Affiche le contenu d'un fichier avec plus d'options de navigation (flèches, PgUp/PgDn, recherche, `q` pour quitter).
* **head fichier** : Affiche les premières lignes d'un fichier (par défaut 10).
  * **-n N** : Affiche les `N` premières lignes.
* **tail fichier** : Affiche les dernières lignes d'un fichier (par défaut 10).
  * **-n N** : Affiche les `N` dernières lignes.
  * **-f** : Affiche le contenu au fur et à mesure qu'il est ajouté au fichier (utile pour les logs).
* **nano fichier** : Ouvre un fichier dans l'éditeur de texte nano (souvent plus simple pour les débutants).
* **vi / vim fichier** : Ouvre un fichier dans l'éditeur de texte vi/vim (puissant mais avec une courbe d'apprentissage).

**Recherche**

* **grep "modèle" fichier(s)** : Recherche les lignes correspondant au "modèle" dans les fichiers spécifiés.
  * **-i** : Recherche insensible à la casse.
  * **-r** : Recherche récursivement dans les sous-répertoires. (Il existe aussi la commande `rgrep`).
  * **-n** : Affiche le numéro de ligne pour chaque correspondance.
  * **-c** : Affiche le nombre de lignes correspondantes dans chaque fichier.
  * **-v** : Inverse la recherche, affiche les lignes *ne* correspondant *pas* au modèle.
  * **-A N** : Affiche les `N` lignes *après* la correspondance.
  * **-B N** : Affiche les `N` lignes *avant* la correspondance.
  * **-C N** : Affiche les `N` lignes *autour* de la correspondance (`-A N -B N`).
  * **grep "modèle1\|modèle2" fichier** ou **grep -E "modèle1|modèle2" fichier** : Recherche les lignes contenant l'un ou l'autre modèle (opérateur OR).
  * **commande | grep "modèle"** : Filtre la sortie d'une `commande` pour n'afficher que les lignes contenant le "modèle".
* **find chemin options actions** : Recherche des fichiers et répertoires dans une arborescence.
  * **chemin** : Répertoire de départ (ex: `.` pour le répertoire courant, `/` pour la racine).
  * **-name "nom"** : Recherche par nom de fichier (supporte les jokers comme `*`, `?`).
  * **-iname "nom"** : Recherche par nom insensible à la casse.
  * **-type type** : Recherche par type (`f`=fichier, `d`=répertoire, `l`=lien symbolique, etc.).
  * **-user utilisateur** : Recherche les fichiers appartenant à un utilisateur.
  * **-group groupe** : Recherche les fichiers appartenant à un groupe.
  * **-size +NC** : Recherche les fichiers de taille supérieure à `N` unités (`c` pour octets, `k` pour Kio, `M` pour Mio, `G` pour Gio). Ex: `+500000k`.
  * **-mtime -N** : Recherche les fichiers modifiés il y a moins de `N` jours.
  * **-exec commande {} \;** : Exécute une `commande` pour chaque fichier trouvé (`{}` est remplacé par le chemin du fichier).
  * **-ok commande {} \;** : Comme `-exec` mais demande confirmation avant chaque exécution.
* **locate fichier** : Recherche rapidement des fichiers dans une base de données indexée (peut nécessiter une mise à jour préalable avec `sudo updatedb`).

**Permissions et Propriété**

* Les permissions sont gérées pour trois catégories d'utilisateurs : le propriétaire (u), le groupe propriétaire (g), et les autres (o). Les permissions définissent si un utilisateur peut lire (r), écrire (w) ou exécuter (x) un fichier.
* **chmod mode fichier(s)** : Change les permissions.
  * Le `mode` peut être symbolique (ex: `u+x`, `g-w`, `o=r`).
  * Le `mode` peut être octal (trois chiffres, chaque chiffre est la somme des valeurs : r=4, w=2, x=1). Ex: `755` (rwxr-xr-x), `644` (rw-r--r--).
  * **-R** : Applique les changements récursivement aux sous-répertoires et fichiers. **Attention aux changements récursifs inappropriés !**.
* **chown nouvel_propriétaire fichier(s)** : Change le propriétaire d'un fichier. Nécessite généralement `sudo`.
  * **chown nouvel_propriétaire:nouveau_groupe fichier(s)** : Change le propriétaire et le groupe en une seule commande.
  * **-R** : Change de manière récursive.
* **chgrp nouveau_groupe fichier(s)** : Change le groupe propriétaire d'un fichier. Nécessite généralement `sudo`.
  * **-R** : Change de manière récursive.
* **umask [mode]** : Affiche ou définit le masque utilisateur, qui détermine les permissions par défaut des nouveaux fichiers/répertoires. Le umask par défaut est souvent `022`. Le masque est soustrait des permissions maximales (666 pour les fichiers, 777 pour les répertoires) pour obtenir les permissions par défaut.

**Gestion des Utilisateurs et Groupes**

* **adduser nom_utilisateur** : Ajoute un nouvel utilisateur au système de manière interactive (crée l'utilisateur, le groupe principal, le répertoire personnel, demande le mot de passe et les informations). C'est un script Perl spécifique à Debian/Ubuntu.
  * **--disabled-password** : Crée un utilisateur sans mot de passe, utile pour l'authentification par clé SSH uniquement.
  * **--no-create-home** : Ne crée pas de répertoire personnel.
  * **nom_utilisateur nom_groupe** : Ajoute un utilisateur existant à un groupe existant.
* **useradd nom_utilisateur** : Commande non-interactive pour créer un utilisateur (souvent utilisée dans les scripts).
* **deluser nom_utilisateur** : Supprime un utilisateur du système. Le répertoire personnel n'est pas supprimé par défaut.
  * **--remove-home** : Supprime l'utilisateur et son répertoire personnel. **Attention : rm -R est utilisé en arrière-plan, soyez prudent !**.
  * **nom_utilisateur nom_groupe** : Supprime un utilisateur d'un groupe.
* **addgroup nom_groupe** : Ajoute un nouveau groupe au système de manière interactive.
* **groupadd nom_groupe** : Commande non-interactive pour créer un groupe.
* **groupdel nom_groupe** : Supprime un groupe.
* **usermod options nom_utilisateur** : Modifie les paramètres d'un compte utilisateur.
  * **-G GROUPE1[,...]** : Ajoute l'utilisateur aux groupes spécifiés (remplace les groupes secondaires existants).
  * **-aG GROUPE1[,...]** : **Ajoute** l'utilisateur aux groupes spécifiés sans le supprimer de ses groupes d'origine.
  * **-l nouveau_login ancien_login** : Change le nom d'utilisateur (le compte doit être inactif).
  * **-d /nouveau/chemin -m** : Change le répertoire personnel et déplace son contenu.
  * **--expiredate YYYY-MM-DD** : Définit une date d'expiration pour le compte. Utilisez `1` pour verrouiller, `""` pour déverrouiller.
* **groupmod --new-name nouveau_nom ancien_nom** : Modifie le nom d'un groupe.
* **passwd [nom_utilisateur]** : Change le mot de passe de l'utilisateur courant ou de l'utilisateur spécifié (si exécuté par root ou via sudo).
  * **-l nom_utilisateur** : Verrouille le mot de passe d'un utilisateur (désactive la connexion par mot de passe, mais pas forcément par clé SSH).
  * **-u nom_utilisateur** : Déverrouille le mot de passe d'un utilisateur.
  * **-e nom_utilisateur** : Force l'utilisateur à changer de mot de passe à la prochaine connexion.
  * **-S nom_utilisateur** : Affiche le statut du mot de passe (verrouillé, sans mot de passe, utilisable, dates d'expiration, etc.).
* **chage -l nom_utilisateur** : Affiche les informations d'expiration du mot de passe.
* **groups [nom_utilisateur]** : Affiche les groupes auxquels appartient l'utilisateur courant ou l'utilisateur spécifié.
* **compgen -u** : Liste tous les utilisateurs.
* **compgen -g** : Liste tous les groupes.
* **cut -d: -f1 /etc/passwd** : Liste les noms d'utilisateur depuis `/etc/passwd`.
* **cut -d: -f1 /etc/group** : Liste les noms de groupe depuis `/etc/group`.
* Les informations sur les utilisateurs et groupes sont stockées dans `/etc/passwd`, `/etc/shadow` (mots de passe hachés), `/etc/group`, et `/etc/gshadow`.

**Informations Système**

* **uname -a** : Affiche toutes les informations sur le noyau Linux et le système (nom du noyau, nom d'hôte, version du noyau, type de machine, système d'exploitation).
  * **-r** : Affiche la version du noyau.
* **lsb_release -a** : Affiche les informations spécifiques à la distribution (ID, description, version, nom de code).
* **hostnamectl** : Affiche le nom d'hôte statique, l'ID machine, le système d'exploitation, la version du noyau et l'architecture.
* **getconf LONG_BIT** : Affiche l'architecture (32 ou 64 bits).
* **uname -i** : Affiche l'architecture du processeur.
* **cat /etc/*-release** : Affiche le contenu des fichiers de version du système.
* **cat /proc/cpuinfo** : Affiche les informations détaillées sur le CPU.
  * **grep -c ^processor /proc/cpuinfo** : Compte le nombre de cœurs CPU.
* **cat /proc/meminfo** : Affiche les informations détaillées sur la mémoire.
* **free -h** : Affiche l'utilisation de la mémoire et du swap dans un format lisible.
* **df -h** : Affiche l'espace disque utilisé par les systèmes de fichiers dans un format lisible.
* **du -h -s [répertoire]** : Affiche la taille totale d'un répertoire dans un format lisible.
  * **--max-depth=N** : Limite la profondeur de l'affichage.
* **lshw -class network** : Affiche des informations détaillées sur les interfaces réseau.
* **lspci** : Liste les périphériques PCI.
* **lsusb** : Liste les périphériques USB.
* **ethtool interface** : Affiche ou modifie les paramètres d'une interface Ethernet (vitesse, duplex, etc.).
* **uptime** : Affiche l'heure actuelle, la durée d'exécution du système, le nombre d'utilisateurs connectés et la charge moyenne.

**Gestion des Processus**

* **ps aux** : Affiche tous les processus en cours sur le système (style BSD).
  * **-u utilisateur** : Affiche les processus appartenant à un utilisateur.
  * **-ef** : Affiche tous les processus en cours (style SysV).
  * **-p PID -o args** : Affiche la ligne de commande complète d'un processus par son PID.
* **top** : Affiche une vue dynamique des processus les plus gourmands en ressources (CPU, mémoire). Utilisez `M` pour trier par mémoire, `P` pour trier par CPU, `k` pour tuer un processus par PID, `q` pour quitter.
* **htop** : Alternative interactive et plus complète à top (souvent non installée par défaut).
* **kill PID** : Envoie un signal (par défaut `TERM`, 15) à un processus spécifié par son ID.
  * **-9** ou **-KILL** : Envoie le signal `KILL` (9) pour terminer brutalement un processus qui ne répond pas.
* **killall nom_processus** : Envoie un signal (par défaut `TERM`) à **tous** les processus portant le nom spécifié.
* **pkill nom_processus** : Tue un processus par son nom (souvent plus simple que `killall`).
* **bg** : Liste les tâches arrêtées ou en arrière-plan ; reprend une tâche arrêtée en arrière-plan.
* **fg [job ID]** : Met une tâche en arrière-plan au premier plan.
* **systemctl status service.service** : Affiche l'état d'un service systemd.
  * **start service.service** : Démarre un service systemd.
  * **stop service.service** : Arrête un service systemd.
  * **enable service.service** : Active un service pour qu'il démarre au boot.
  * **disable service.service** : Désactive un service pour qu'il ne démarre pas au boot.

**Gestion des Paquets (Debian/Ubuntu)**

* **apt update** : Met à jour la liste des paquets disponibles depuis les sources configurées. **À exécuter avant `apt upgrade` ou `apt install` !**.
* **apt upgrade** : Installe les nouvelles versions de tous les paquets actuellement installés.
* **apt full-upgrade** : Met à niveau le système entier vers la dernière version des paquets, y compris les changements de dépendances majeurs et la suppression de paquets obsolètes. Similaire à `apt-get dist-upgrade`.
* **apt install paquet(s)** : Installe un ou plusieurs paquets.
* **apt remove paquet(s)** : Supprime un ou plusieurs paquets.
* **apt purge paquet(s)** : Supprime un ou plusieurs paquets ainsi que leurs fichiers de configuration.
* **apt autoremove** : Supprime les paquets installés automatiquement pour satisfaire des dépendances mais qui ne sont plus nécessaires.
* **apt search modèle** : Recherche des paquets dont le nom ou la description contient le modèle.
* **apt show paquet** : Affiche les informations détaillées sur un paquet (version, dépendances, description, etc.).
* **apt clean** : Supprime les fichiers d'archive des paquets téléchargés du cache local.

**Réseau**

* **ip a** ou **ip addr** : Affiche les adresses IP et les informations des interfaces réseau. `ip link show` affiche l'état des interfaces.
* **ifconfig [interface]** : Affiche les informations d'une interface réseau spécifique ou de toutes. (Peut être obsolète au profit d'`ip` sur les systèmes récents).
* **ip route show** : Affiche la table de routage du noyau.
  * **add default via passerelle dev interface** : Ajoute une route par défaut temporaire.
  * **del default via passerelle dev interface** : Supprime une route par défaut temporaire.
* **route -n** : Affiche la table de routage numérique. (Peut être obsolète au profit d'`ip route`).
* **ss [options]** : Utilitaire pour afficher les statistiques de socket (remplace `netstat` sur les systèmes récents).
  * **-t** : Sockets TCP.
  * **-u** : Sockets UDP.
  * **-l** : Sockets en écoute (listening).
  * **-n** : N'affiche pas les noms de service/hôte (utilise les numéros).
  * **-p** : Affiche le PID et le nom du programme utilisant le socket.
* **netstat [options]** : Affiche les connexions réseau, tables de routage, etc.. (Obsolète, utiliser `ss`).
* **ping hôte** : Envoie des paquets ICMP à un hôte pour tester la connectivité.
* **curl URL** : Outil pour transférer des données avec différentes syntaxes réseau (HTTP, FTP, etc.).
* **wget URL** : Télécharge des fichiers depuis le web.
* **nmcli** : Utilitaire en ligne de commande pour NetworkManager.
  * **nmcli d** : Affiche le statut des périphériques réseau.
  * **nmcli c** : Affiche les connexions réseau configurées.
  * **nmcli r wifi on/off** : Active/désactive le radio Wi-Fi.
  * **nmcli d wifi list** : Liste les réseaux Wi-Fi disponibles.
  * **nmcli d wifi connect ESSID password motdepasse** : Connecte à un réseau Wi-Fi.
  * **nmcli c add type wifi con-name nom ifname interface ssid ESSID** : Crée une connexion Wi-Fi.
  * **nmcli c modify nom wifi-sec.key-mgmt wpa-psk wifi-sec.psk motdepasse** : Modifie une connexion (ex: ajoute le mot de passe).
  * **nmcli c up nom** : Active une connexion.
  * **nmcli connection edit** : Lance un éditeur interactif pour les connexions NetworkManager.
  * **nmcli general logging** : Affiche/modifie le niveau de journalisation de NetworkManager.
  * **nmcli monitor** : Surveille l'activité de NetworkManager.
* **nmtui** : Interface utilisateur textuelle pour NetworkManager. Permet de gérer les connexions réseau de manière interactive.
* **wpa_supplicant** : Supplicant pour l'authentification WPA (méthode alternative pour le Wi-Fi).
  * **wpa_passphrase ESSID motdepasse** : Génère la configuration WPA pour un réseau.
  * **wpa_supplicant -c fichier.conf -i interface** : Lance wpa_supplicant avec un fichier de configuration.
* **dhclient interface** : Client DHCP pour obtenir une adresse IP dynamique.
* **Netplan** : Outil de configuration réseau par défaut sur les versions récentes d'Ubuntu Server, utilisant des fichiers YAML dans `/etc/netplan/`.
  * **netplan generate** : Génère les configurations du moteur réseau (systemd-networkd ou NetworkManager) à partir des fichiers YAML.
  * **netplan apply** : Applique la configuration réseau.
  * **netplan set chemin=valeur** : Modifie la configuration Netplan (pour les versions récentes).
* `/etc/network/interfaces` : Fichier de configuration réseau traditionnel sur les systèmes plus anciens (comme Ubuntu 16.04 Server).
* `/etc/resolv.conf` : Fichier configurant les serveurs DNS. Souvent un lien symbolique vers un fichier géré par `resolvconf` ou `systemd-resolved`.
* `/etc/hosts` : Fichier de mappages statiques noms d'hôte vers adresses IP. Les entrées ont priorité sur le DNS par défaut.
* `/etc/nsswitch.conf` : Configure l'ordre de recherche pour la résolution de noms (fichiers, DNS, etc.).

**pare-feu**

* **ufw** (Uncomplicated Firewall) : Outil par défaut sur Ubuntu pour gérer le pare-feu. Interface simplifiée pour `iptables`.
  * **ufw status** : Affiche l'état du pare-feu (actif/inactif) et les règles.
  * **ufw enable** : Active le pare-feu. Bloque toutes les connexions entrantes par défaut.
  * **ufw disable** : Désactive le pare-feu.
  * **ufw default allow/deny [incoming/outgoing]** : Définit la politique par défaut.
  * **ufw allow port[/protocole]** : Autorise les connexions entrantes sur le `port` spécifié et optionnellement le `protocole` (tcp/udp). Ex: `ufw allow 22/tcp`, `ufw allow 80`, `ufw allow http`.
  * **ufw deny port[/protocole]** : Bloque les connexions entrantes sur le `port`. Ex: `ufw deny 25` (bloque le SMTP entrant).
  * **ufw allow from adresse_ip [to any port port]** : Autorise les connexions depuis une `adresse_ip` (peut être un masque de sous-réseau comme `192.168.1.0/24`). Peut être combiné avec `to any port` pour spécifier un port de destination.
  * **ufw deny from adresse_ip** : Bloque toutes les connexions depuis une `adresse_ip`.
  * **ufw allow in on interface from adresse_ip to any port port** : Autorise les connexions **entrantes** sur une `interface` spécifique. `ufw deny in on interface from adresse_ip`.
  * **ufw allow out port[/protocole]** : Autorise les connexions **sortantes**. `ufw deny out 25` (bloque le SMTP sortant).
  * **ufw app list** : Liste les profils d'application disponibles (ex: OpenSSH, Nginx Full). Ces profils définissent les ports nécessaires à une application.
  * **ufw allow "Nom du profil"** : Autorise les connexions selon un profil d'application.
  * **ufw delete règle** : Supprime une règle (peut être spécifiée par son numéro avec `ufw status numbered`).
  * **ufw logging on/off** : Active/désactive la journalisation du pare-feu. Les logs UFW se trouvent dans `/var/log/syslog` ou `/var/log/kern.log`.
  * **ufw --dry-run commande** : Affiche les règles qui seraient appliquées par une commande sans les exécuter.
* **iptables [chaîne] [critères] [action]** : Outil de bas niveau pour configurer le pare-feu Netfilter.
  * **-t table** : Spécifie la table (`filter` par défaut, `nat` pour la translation d'adresses).
  * **-A chaîne** : Ajoute une règle à la fin d'une chaîne (`INPUT`, `OUTPUT`, `FORWARD`, `PREROUTING`, `POSTROUTING`).
  * **-j action** : Spécifie l'action (`ACCEPT`, `DROP`, `REJECT`, `LOG`, `MASQUERADE`).
  * **-s adresse_ip** : Spécifie l'adresse source.
  * **-d adresse_ip** : Spécifie l'adresse de destination.
  * **-p protocole** : Spécifie le protocole (`tcp`, `udp`).
  * **--dport port** : Spécifie le port de destination.
  * **--sport port** : Spécifie le port source.
  * **-o interface** : Spécifie l'interface de sortie.
  * **-i interface** : Spécifie l'interface d'entrée.
  * Exemple de NAT/Masquerading avec iptables : `iptables -t nat -A POSTROUTING -s 192.168.0.0/16 -o interface_internet -j MASQUERADE`.

**Compression et Archivage**

* **tar options archive fichier(s) ou répertoire(s)** : Crée ou extrait des archives `.tar`.
  * **-c** : Crée une archive.
  * **-x** : Extrait une archive.
  * **-f fichier_archive.tar** : Spécifie le nom du fichier archive.
  * **-v** : Mode verbeux (affiche les fichiers traités).
  * **-z** : Compresse/décompresse avec **gzip** (`.tar.gz` ou `.tgz`).
  * **-j** : Compresse/décompresse avec **bzip2** (`.tar.bz2`, `.tar.bz`, ou `.tbz`).
  * **-C répertoire** : Extrait l'archive dans un `répertoire` différent.
  * **--exclude=modèle** : Exclut les fichiers/répertoires correspondant au `modèle` lors de la création.
* **gzip fichier** : Compresse un fichier avec gzip (crée `fichier.gz`).
* **gzip -d fichier.gz** : Décompresse un fichier gzip. (Équivalent à `gunzip fichier.gz`).
* **bzip2 fichier** : Compresse un fichier avec bzip2 (crée `fichier.bz2`).
* **bzip2 -d fichier.bz2** : Décompresse un fichier bzip2. (Équivalent à `bunzip2 fichier.bz2`).

**Gestion du Disque et des Systèmes de Fichiers**

* **df -h** : Affiche l'espace disque libre sur les systèmes de fichiers.
* **du -h -s [répertoire]** : Affiche la taille totale d'un répertoire ou des fichiers spécifiés.
* **mount** : Affiche les systèmes de fichiers montés.
  * **mount périphérique point_de_montage** : Monte un système de fichiers. Options importantes avec `-o` (ex: `defaults`, `rw`, `ro`, `user`, `acl`, `loop`).
* **umount point_de_montage** ou **umount périphérique** : Démonte un système de fichiers.
  * **-f** : Force le démontage (dangereux).

**Journalisation (Logs)**

* **journalctl** : Affiche les logs du journal systemd.
  * **-u service.service** : Affiche les logs d'un service spécifique.
  * **--since "YYYY-MM-DD HH:MM:SS"** : Affiche les logs depuis une date/heure.
  * **-f** : Suit les nouvelles entrées du journal.
* Les logs système généraux se trouvent dans des fichiers comme `/var/log/syslog`, `/var/log/messages`, `/var/log/kern.log`.
* Les logs d'audit se trouvent dans `/var/log/audit/audit.log`.

**Environnement**

* **printenv [variable]** : Affiche la valeur de toutes les variables d'environnement ou d'une variable spécifique.
* **echo $VARIABLE** : Affiche la valeur d'une variable d'environnement.
* Les variables d'environnement système peuvent être définies dans `/etc/environment` ou des fichiers dans `/etc/profile.d/`. Des scripts wrapper peuvent être utilisés pour les programmes non modifiables.

**Raccourcis Clavier (Terminal)**

* **Ctrl+Alt+T** : Ouvre un nouveau terminal.
* **Ctrl+C** : Interrompt le processus en cours (`SIGINT`, arrêt "poli").
* **Ctrl+Z** : Suspend le processus en cours (`SIGTSTP`, peut être repris avec `fg` ou `bg`).
* **Ctrl+D** : Signale la fin de l'entrée (équivalent à `exit` si le terminal est vide).
* **Ctrl+L** : Efface l'écran (équivalent à `clear`).
* **Ctrl+W** : Efface le mot avant le curseur.
* **Ctrl+U** : Efface toute la ligne avant le curseur.
* **Ctrl+R** : Recherche dans l'historique des commandes.
* **!!** : Répète la dernière commande.
* **Historique des commandes** : Utilisez les flèches Haut/Bas pour naviguer dans les commandes précédentes.

***

N'hésitez pas si vous souhaitez approfondir un domaine particulier ou ajouter d'autres commandes !
