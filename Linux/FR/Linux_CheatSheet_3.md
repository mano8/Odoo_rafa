# Linux CheatSheet

Absolument. Continuons notre feuille de référence basée sur les sources et notre conversation. Voici les prochaines catégories que vous avez demandées.

**9. Pare-feu (Firewall)**

Sous Linux, le sous-système du noyau responsable de la manipulation ou de la décision du sort du trafic réseau est **Netfilter**. L'outil en espace utilisateur `iptables` est l'interface permettant de gérer les règles de Netfilter. Sur Ubuntu, l'outil de configuration de pare-feu par défaut est **`ufw` (Uncomplicated Firewall)**. `ufw` est conçu pour simplifier la configuration d'`iptables` et est principalement utilisé pour les pare-feu basés sur l'hôte.

**Commandes Essentielles `ufw`**

* **Vérifier le statut du pare-feu**
  * `sudo ufw status` : Affiche le statut de `ufw` (actif ou inactif).
  * `sudo ufw status verbose` : Fournit des informations plus détaillées sur le statut, y compris la politique par défaut pour le trafic entrant, sortant et routé, ainsi que l'état de la journalisation.
  * `sudo ufw status numbered` : Liste les règles actuelles avec des numéros. Utile pour supprimer une règle spécifique par son ID.

* **Activer/Désactiver le pare-feu**
  * `sudo ufw enable` : Active le pare-feu. **Attention** : par défaut, l'activation de `ufw` bloque l'accès externe à tous les ports. Assurez-vous d'autoriser les services nécessaires (comme SSH) avant de l'activer pour éviter de vous déconnecter de votre serveur distant.
  * `sudo ufw disable` : Désactive complètement le service de pare-feu.

* **Gérer les Règles (Autoriser/Bloquer le Trafic)**
  * **Autoriser/Bloquer un port** : Vous pouvez spécifier le numéro de port ou le nom du service s'il est défini dans `/etc/services`.
    * `sudo ufw allow <port|service>` : Autorise le trafic entrant sur un port ou un service spécifié (ex: `sudo ufw allow 22` ou `sudo ufw allow ssh`).
    * `sudo ufw deny <port|service>` : Bloque le trafic entrant sur un port ou un service spécifié (ex: `sudo ufw deny 22` ou `sudo ufw deny ssh`).
  * **Spécifier le protocole** : Par défaut, les règles s'appliquent à la fois à TCP et UDP. Vous pouvez spécifier le protocole (`tcp` ou `udp`).
    * `sudo ufw allow <port>/tcp` : Autorise le trafic TCP sur un port spécifié.
    * `sudo ufw deny <port>/udp` : Bloque le trafic UDP sur un port spécifié.
  * **Spécifier une plage de ports** :
    * `sudo ufw allow <port1>:<port2>/<tcp|udp>` : Autorise le trafic sur une plage de ports (ex: `sudo ufw allow 6000:6007/tcp`) (Information ajoutée, non trouvée directement dans les sources).
  * **Autoriser/Bloquer plusieurs ports/services** :
    * `sudo ufw allow proto tcp from any to any port <port1>,<port2>` : Autorise le trafic TCP entrant sur plusieurs ports spécifiés (ex: `sudo ufw allow proto tcp from any to any port 80,443`).
  * **Spécifier l'interface** :
    * `sudo ufw allow in on <interface> to any port <port>` : Autorise le trafic entrant sur un port spécifique via une interface spécifiée (ex: `sudo ufw allow in on eth0 to any port 80`).
    * `sudo ufw deny out on <interface> to any port <port>` : Bloque le trafic sortant sur un port spécifique via une interface spécifiée (ex: `sudo ufw deny out on eth0 to any port 25`).
  * **Spécifier la source/destination (IP/Sous-réseau)** :
    * `sudo ufw allow from <ip_address|subnet>` : Autorise tout le trafic entrant provenant d'une adresse IP ou d'un sous-réseau spécifié.
    * `sudo ufw deny from <ip_address|subnet>` : Bloque tout le trafic entrant provenant d'une adresse IP ou d'un sous-réseau spécifié.
    * `sudo ufw allow from <ip_source|subnet> to <ip_destination|subnet> port <port>` : Autorise le trafic provenant d'une source spécifique vers une destination spécifique sur un port donné.
  * **Insérer une règle** : Les règles sont généralement ajoutées à la fin. Vous pouvez spécifier une position.
    * `sudo ufw insert <number> <rule>` : Insère une règle à la position numérotée spécifiée (ex: `sudo ufw insert 1 allow 80`).
  * **Supprimer une règle** :
    * `sudo ufw delete <rule>` : Supprime une règle en spécifiant sa définition (ex: `sudo ufw delete deny 22`).
    * `sudo ufw delete <number>` : Supprime une règle par son ID numéroté (obtenu avec `ufw status numbered`).

* **Utiliser les Profils d'Application** : Certaines applications installent des profils `ufw` simplifiant l'ouverture des ports nécessaires.
  * `sudo ufw app list` : Liste les profils d'application disponibles.
  * `sudo ufw allow <profil_application>` : Autorise le trafic selon le profil d'application (ex: `sudo ufw allow OpenSSH` ou `sudo ufw allow "Nginx Full"`). N'oubliez pas les guillemets pour les noms avec espaces.
  * `sudo ufw deny <profil_application>` : Bloque le trafic selon le profil. Pour désactiver, supprimez plutôt la règle correspondante.
  * `sudo ufw app info <profil_application>` : Affiche les détails du profil, y compris les ports et protocoles.

* **Journalisation (Logging)**
  * `sudo ufw logging on|off` : Active ou désactive la journalisation. Les logs sont généralement trouvés dans `/var/log/messages`, `/var/log/syslog`, `/var/log/kern.log`.

* **Essayer les changements sans les appliquer**
  * `sudo ufw --dry-run <commande_ufw>` : Exécute une commande `ufw` et affiche les règles résultantes sans les appliquer.

* **Masquage IP (NAT)**
  * Pour configurer le masquage IP avec `ufw`, vous devez modifier certains fichiers de configuration :
    * `/etc/default/ufw` : Changer `DEFAULT_FORWARD_POLICY="DROP"` à `DEFAULT_FORWARD_POLICY="ACCEPT"`.
    * `/etc/ufw/sysctl.conf` : Décommenter `net.ipv4.ip_forward=1` et éventuellement `net.ipv6.conf.default.forwarding=1`.
    * `/etc/ufw/before.rules` : Ajouter des règles à la table `nat` pour le masquage dans la chaîne `POSTROUTING`. Exemple pour le trafic sortant d'un sous-réseau privé via une interface externe :

            ```bash
            # Règles de la table nat
            *nat
            :POSTROUTING ACCEPT [0:0]
            # Transférer le trafic du sous-réseau privé via l'interface externe.
            -A POSTROUTING -s 192.168.0.0/24 -o eth0 -j MASQUERADE
            COMMIT
            ```

    * Appliquer les changements en désactivant et réactivant `ufw`.

* **Masquage IP avec `iptables` (Non-persistent par défaut)**
  * Activer le transfert IP dans `/etc/sysctl.conf` et appliquer avec `sudo sysctl -p`.
  * Ajouter la règle de masquage à la table `nat`:
    * `sudo iptables -t nat -A POSTROUTING -s 192.168.0.0/16 -o ppp0 -j MASQUERADE`. Remplacez le sous-réseau et l'interface.
  * Si la politique par défaut de la chaîne `FORWARD` est `DROP` ou `REJECT`, vous devez autoriser le trafic. (Ex: `sudo iptables -A FORWARD -s 192.168.0.0/16 -o ppp0 -j ACCEPT`).
  * **Persistance** : Les règles `iptables` définies directement sont temporaires. Pour les rendre persistantes, vous devez les enregistrer (par exemple avec `iptables-save` et `iptables-restore` ou le paquet `iptables-persistent`). La source mentionne l'ajout des commandes dans `/etc/rc.local`, mais ce fichier peut ne pas être utilisé par défaut dans les systèmes modernes basés sur `systemd` (Information ajoutée, non trouvée directement dans les sources). `ufw` gère automatiquement la persistance.

**Ressources `ufw` et `iptables`** : Page de manuel `ufw` (`man ufw`), page de manuel `iptables` (`man iptables`) (Information ajoutée, non trouvée directement dans les sources).

**10. Gestion des Paquets**

Ubuntu, étant basée sur Debian, utilise le système de gestion de paquets **APT (Advanced Package Tool)**. Les outils en ligne de commande les plus courants sont **`apt`**, **`apt-get`** et **`apt-cache`**.

* **`apt`** : **(Utilitaire moderne recommandé pour les usages interactifs)** C'est un utilitaire de haut niveau qui combine les fonctionnalités courantes de `apt-get` et `apt-cache` de manière plus conviviale (Information ajoutée, non trouvée directement dans les sources).
  * `sudo apt update` : Met à jour la liste des paquets disponibles à partir des sources configurées. **À exécuter avant d'installer ou de mettre à jour des paquets.**
  * `sudo apt upgrade` : Installe les nouvelles versions de tous les paquets actuellement installés.
  * `sudo apt full-upgrade` : Effectue une mise à niveau complète du système, pouvant installer ou supprimer des paquets pour résoudre des dépendances complexes (Information ajoutée, non trouvée directement dans les sources, mais équivalent à `apt-get dist-upgrade`).
  * `sudo apt install <paquet(s)>` : Installe un ou plusieurs paquets spécifiés.
  * `sudo apt remove <paquet(s)>` : Supprime un ou plusieurs paquets spécifiés. Les fichiers de configuration peuvent être conservés.
  * `sudo apt purge <paquet(s)>` : Supprime un ou plusieurs paquets spécifiés, y compris leurs fichiers de configuration (à l'exception de ceux dans les répertoires personnels).
  * `sudo apt autoremove` : Supprime les paquets installés automatiquement pour satisfaire des dépendances et qui ne sont plus nécessaires (Information ajoutée, non trouvée directement dans les sources).
  * `apt search <terme>` : Recherche un paquet par nom ou description (Fonctionnalité combinée de `apt-cache search`).
  * `apt show <paquet>` : Affiche des informations détaillées sur un paquet, comme sa version, ses dépendances, sa description, etc. (Fonctionnalité combinée de `apt-cache show`).
  * `sudo apt clean` : Supprime les fichiers d'archives de paquets téléchargés (fichiers `.deb`) du répertoire cache local.

* **`apt-get`** : (Utilitaire traditionnel, souvent utilisé dans les scripts).
  * `sudo apt-get update`.
  * `sudo apt-get upgrade`.
  * `sudo apt-get dist-upgrade` : Équivalent à `apt full-upgrade`.
  * `sudo apt-get install <paquet(s)>`. Options utiles: `-y` (répond "oui" automatiquement), `--reinstall` (réinstalle un paquet), `-f` (tente de corriger les dépendances).
  * `sudo apt-get remove <paquet(s)>`. Options utiles: `--purge` (supprime aussi les fichiers de conf).
  * `sudo apt-get clean`.
  * `sudo apt-get autoclean` : Supprime uniquement les fichiers d'archives de paquets qui ne peuvent plus être téléchargés. (Information ajoutée, non trouvée directement dans les sources).
  * `sudo apt-get autoremove` (Équivalent à `apt autoremove`).

* **`apt-cache`** : (Utilitaire traditionnel pour interroger le cache local des paquets).
  * `apt-cache search <terme>` : Recherche dans les noms et descriptions. Option `-n` recherche uniquement dans les noms.
  * `apt-cache show <paquet>` : Affiche les informations d'un paquet.
  * `apt-cache depends <paquet>` : Affiche les dépendances d'un paquet.
  * `apt-cache rdepends <paquet>` : Affiche les paquets qui dépendent du paquet donné (dépendances inverses).
  * `apt-cache madison <paquet>` : Affiche la version et les informations de dépôt pour un paquet.

* **`dpkg`** : (Utilitaire de bas niveau pour gérer les paquets `.deb`) Principalement utilisé pour installer des fichiers `.deb` téléchargés localement.
  * `sudo dpkg -i <fichier.deb>` : Installe un paquet local. **Ne gère pas automatiquement les dépendances.**
  * `sudo dpkg -r <paquet>` : Supprime un paquet installé.
  * `sudo dpkg -P <paquet>` : Supprime un paquet installé et ses fichiers de configuration.
  * `dpkg -l` : Liste tous les paquets installés. Option `-l <modèle>` pour filtrer par nom.
  * `dpkg -s <paquet>` : Affiche des informations sur un paquet installé.
  * `dpkg -L <paquet>` : Liste les fichiers installés par un paquet.
  * `dpkg -S <fichier>` : Cherche quel paquet a installé un fichier donné.
  * **Note** : `apt` et `apt-get` sont des outils de plus haut niveau qui utilisent `dpkg` en arrière-plan et gèrent les dépendances.

* **Installation à partir des sources** : (Moins courant que l'installation de paquets binaires)
  * Les étapes générales impliquent l'utilisation d'outils de compilation :
        1. `./configure` : Configure le logiciel pour votre système.
        2. `make` : Compile le logiciel.
        3. `sudo make install` : Installe le logiciel.

**11. Services Système et Démarrage**

Sous Ubuntu moderne (depuis 15.04), le système d'initialisation et gestionnaire de services par défaut est **`systemd`**. `systemd` utilise des unités (`.service`, `.mount`, etc.) pour gérer les différents composants du système au démarrage et pendant l'exécution.

* **Commandes Essentielles `systemctl`** : Cet outil est l'interface principale pour contrôler `systemd`.
  * `systemctl status <service.service>` : Affiche l'état d'un service, s'il est actif, inactif, en échec, et affiche les dernières lignes de son journal.
  * `sudo systemctl start <service.service>` : Démarre un service.
  * `sudo systemctl stop <service.service>` : Arrête un service.
  * `sudo systemctl restart <service.service>` : Arrête puis redémarre un service (Information ajoutée, non trouvée directement dans les sources).
  * `sudo systemctl reload <service.service>` : Recharge la configuration d'un service sans l'arrêter si le service prend en charge cette fonctionnalité (Information ajoutée, non trouvée directement dans les sources). L'option `reload` existe aussi pour les anciens scripts init.d.
  * `sudo systemctl enable <service.service>` : Active un service pour qu'il démarre automatiquement au prochain démarrage du système.
  * `sudo systemctl disable <service.service>` : Désactive un service pour qu'il ne démarre pas automatiquement au prochain démarrage.
  * `systemctl is-enabled <service.service>` : Vérifie si un service est configuré pour démarrer automatiquement (Information ajoutée, non trouvée directement dans les sources).
  * `systemctl list-units --type=service` : Liste toutes les unités de service actives (Information ajoutée, non trouvée directement dans les sources).
  * `systemctl list-unit-files --type=service` : Liste tous les fichiers d'unité de service installés et leur état (activé/désactivé) (Information ajoutée, non trouvée directement dans les sources).

* **Anciens Scripts Init.d** : Pour des raisons de compatibilité, `systemd` peut encore utiliser les scripts de démarrage de style SysVinit situés dans `/etc/init.d`.
  * Les scripts Init.d devraient prendre en charge les actions `start`, `stop`, `restart`, `force-reload`.
  * **Note** : Il est recommandé d'utiliser `systemctl` pour interagir avec les services, même s'ils sont basés sur des scripts Init.d, car `systemd` les gère via une couche de compatibilité. L'exécution directe de `/etc/init.d/<service> <action>` est déconseillée.
  * **Scripts d'invocation pour les paquets** : Les scripts de maintenance de paquets doivent utiliser `invoke-rc.d` pour démarrer/arrêter les services au lieu de les appeler directement.
    * `invoke-rc.d <paquet> <action>`.

* **Gestion des liens de démarrage (`update-rc.d`)** : Utilisé par les scripts de maintenance de paquets pour gérer les liens symboliques dans `/etc/rcn.d` qui contrôlaient l'ordre de démarrage sous SysVinit. `systemd` utilise les informations de dépendance des unités, mais `update-rc.d` est toujours utilisé pour la compatibilité.
  * `update-rc.d <paquet> defaults` : Active le démarrage automatique (comportement par défaut).
  * `update-rc.d <paquet> defaults-disabled` : Désactive le démarrage automatique par défaut.
  * `update-rc.d <paquet> remove` : Supprime les liens de démarrage.
  * **Note** : Les mainteneurs de paquets devraient utiliser `update-rc.d` via des outils d'aide comme `dh_installinit`. L'utilisation directe est rare pour un utilisateur.

* **Journalisation des Services (`journalctl`)** : `systemd` centralise les logs.
  * `journalctl -u <service.service>` : Affiche les logs d'un service spécifique (Information ajoutée, déjà couverte dans une précédente section, mais pertinente ici).
  * `journalctl -f -u <service.service>` : Affiche les logs d'un service en temps réel (`follow`) (Information ajoutée, non trouvée directement dans les sources).

* **Réagir aux Changements Réseau (`networkd-dispatcher`)** : Pour les utilisateurs du renderer `networkd` (par opposition à `NetworkManager`), `networkd-dispatcher` permet d'exécuter des scripts en réaction aux changements d'état réseau. Netplan ne prend pas en charge les scripts "hooks" directement. Pour `NetworkManager`, utilisez les scripts NM Dispatcher. Ces hooks s'exécutent de manière asynchrone.

**12. Variables d'Environnement**

Les variables d'environnement sont des paires nom=valeur qui affectent le comportement des processus exécutés dans un shell.

* **Afficher les Variables d'Environnement** :
  * `printenv` : Affiche toutes les variables d'environnement définies pour la session courante.
  * `printenv <nom_variable>` : Affiche la valeur d'une variable spécifique.
  * `echo $<nom_variable>` : Une autre façon d'afficher la valeur d'une variable spécifique (ex: `echo $TERM`).
  * **Note** : Le signe dollar (`$`) est utilisé pour référer à la valeur d'une variable (ex: `ls $HOME/Desktop`).

* **Fichiers de Configuration des Variables d'Environnement** : Les variables peuvent être définies à différents niveaux, affectant soit un seul utilisateur, soit l'ensemble du système.
  * `/etc/environment` : **(Pour les variables système globales et simples)** Définit des variables d'environnement à l'échelle du système. Ce fichier est lu par `pam_env.so` lors de la connexion. Il doit contenir des paires `NOM=VALEUR` simples. **Pour l'éditer, utilisez `sudo -H nano /etc/environment` pour éviter les problèmes de permissions**. Les changements nécessitent une déconnexion/reconnexion.
  * `/etc/profile` : **(Pour les variables système globales dépendantes de la session)** Exécuté pour les shells de connexion par tous les utilisateurs. Souvent utilisé pour configurer `PATH` ou d'autres variables importantes pour l'environnement du shell.
  * `/etc/profile.d/*.sh` : **(Fragments de configuration système)** Scripts exécutés par `/etc/profile` pour ajouter des configurations spécifiques à différentes applications ou services.
  * `/etc/bash.bashrc` : **(Pour les variables système spécifiques à Bash, pour tous les shells interactifs non-connexion)** Exécuté pour les shells interactifs Bash (sauf les shells de connexion qui lisent `.bashrc` après `.profile`).
  * `~/.profile` : **(Variables utilisateur, session de connexion)** Exécuté pour les shells de connexion d'un utilisateur spécifique. C'est un bon endroit pour définir des variables qui doivent être disponibles pour l'ensemble de la session utilisateur (y compris l'environnement graphique).
  * `~/.bashrc` : **(Variables utilisateur, shells interactifs Bash)** Exécuté pour les shells interactifs Bash non-connexion d'un utilisateur spécifique. C'est l'endroit idéal pour définir des alias, des fonctions shell, ou des variables qui ne sont nécessaires que dans les sessions de terminal Bash.
  * **Ordre de Chargement** : Les fichiers système (`/etc/*`) sont généralement lus en premier, suivis des fichiers utilisateur (`~/.*`). Les shells de connexion chargent typiquement `/etc/profile` et `~/.profile`, tandis que les shells interactifs non-connexion chargent `/etc/bash.bashrc` et `~/.bashrc`.

* **Cas Spécifiques** :
  * Les démons et services système qui ne sont pas lancés via une session utilisateur peuvent avoir leurs propres méthodes de configuration des variables d'environnement (par exemple, via les fichiers d'unité `systemd` ou les fichiers dans `/etc/default`).
  * Les programmes qui dépendent de variables d'environnement pour leur configuration devraient idéalement avoir des valeurs par défaut intégrées. Si ce n'est pas possible (par ex, pour des logiciels non-libres), des scripts "wrappers" peuvent être utilisés pour définir les variables avant d'exécuter le programme original.

**Variables Courantes (Information ajoutée, non trouvée directement dans les sources)** :

* `PATH` : Liste des répertoires où le shell cherche les commandes exécutables.
* `HOME` : Répertoire personnel de l'utilisateur actuel.
* `USER` : Nom d'utilisateur actuel.
* `SHELL` : Chemin du shell par défaut de l'utilisateur.
* `PWD` : Répertoire de travail actuel.

**13. Montage et Systèmes de Fichiers**

Sous Linux, les systèmes de fichiers (partitions de disque, clés USB, lecteurs réseau, etc.) doivent être **montés** pour être accessibles dans l'arborescence de fichiers. Le processus de montage attache le système de fichiers à un répertoire spécifié (point de montage).

* **Commandes Essentielles `mount` et `umount`** :
  * `mount` : **(Lister les systèmes de fichiers montés)** Exécuté sans arguments, `mount` affiche la liste de tous les systèmes de fichiers actuellement montés.
  * `sudo mount <périphérique> <point_de_montage>` : Monte le système de fichiers situé sur `<périphérique>` au répertoire `<point_de_montage>`. Le point de montage doit exister. (ex: `sudo mount /dev/sdb1 /mnt/usb`).
  * `sudo mount -a` : Monte tous les systèmes de fichiers listés dans le fichier `/etc/fstab` dont l'option `auto` est définie.
  * `sudo mount -t <type>` : Spécifie le type de système de fichiers (ex: `vfat`, `ntfs`, `ext4`, `iso9660`).
  * `sudo mount -o <options>` : Spécifie des options de montage (ex: `ro` pour lecture seule, `rw` pour lecture/écriture, `user` pour permettre aux utilisateurs non-root de monter/démonter). Exemple avec plusieurs options : `sudo mount -t vfat -o defaults,rw,user,umask=022,uid=1000 /dev/sda1 /mnt/Mondisk/`.
  * `sudo mount -o loop <fichier_image.iso> <point_de_montage>` : Monte un fichier image ISO comme un périphérique.
  * `umount <périphérique|point_de_montage>` : **(Démonter un système de fichiers)** Démonte le système de fichiers associé au périphérique ou au point de montage spécifié.
  * `sudo umount -a` : Démonte tous les systèmes de fichiers listés dans `/etc/mtab` (sauf `/proc`).
  * `sudo umount -f <périphérique|point_de_montage>` : Force le démontage (à utiliser avec prudence si le système de fichiers est occupé).

* **Configuration des Montages Permanents (`/etc/fstab`)** : Le fichier `/etc/fstab` contient les informations sur les systèmes de fichiers qui doivent être montés automatiquement au démarrage ou qui peuvent être montés facilement avec la commande `mount` simple (sans spécifier tous les arguments). Chaque ligne décrit un système de fichiers et ses options de montage.
  * Structure d'une ligne `/etc/fstab` (Information ajoutée, non trouvée directement dans les sources) :
        `<périphérique>` `<point_de_montage>` `<type_fs>` `<options>` `<dump>` `<pass>`
  * Le champ `<périphérique>` peut utiliser l'UUID (`UUID=<uuid>`) ou l'étiquette (`LABEL=<label>`) au lieu du nom de périphérique (`/dev/sda1`) pour une identification plus robuste (Information ajoutée, non trouvée directement dans les sources, mais implicite dans les sources).
  * Option `acl` dans `/etc/fstab` pour activer les listes de contrôle d'accès.

* **Droits d'Accès sur les Systèmes de Fichiers** :
  * **Systèmes de fichiers compatibles POSIX (ext4, etc.)** : Les permissions traditionnelles Linux (rwx pour propriétaire, groupe, autres) et la propriété (utilisateur, groupe) sont gérées nativement par le système de fichiers. Elles sont modifiables avec `chmod` et `chown`. Les permissions par défaut lors de la création de fichiers/répertoires sont déterminées par le masque utilisateur (`umask`).
  * **Systèmes de fichiers non-POSIX (FAT, NTFS)** : Ces systèmes ne gèrent pas les permissions Linux natives. Les permissions sont **émulées** par le pilote du système de fichiers au moment du montage. Elles sont déterminées par les options de montage spécifiées dans `/etc/fstab` ou la commande `mount`. Pour changer ces permissions émulées, il faut démonter puis remonter le système de fichiers avec de nouvelles options.

* **Listes de Contrôle d'Accès (ACL)** : Permettent une gestion des permissions plus fine que les permissions traditionnelles (propriétaire, groupe, autres). Nécessitent l'installation du paquet `acl` et l'option `acl` activée dans `/etc/fstab`.
  * `setfacl` : Définir les ACLs.
  * `getfacl` : Afficher les ACLs.

* **Informations sur les Périphériques Bloc** :
  * `sudo fdisk -l` : Liste les partitions sur vos disques.
  * `lsblk` : Liste les périphériques bloc dans une arborescence (Information ajoutée, non trouvée directement dans les sources).

**14. Compression et Archivage**

L'archivage combine plusieurs fichiers et/ou répertoires en un seul fichier (une archive). La compression réduit la taille de ce fichier archive. Sous Linux, l'outil le plus couramment utilisé pour l'archivage est **`tar`**, souvent combiné avec des outils de compression comme `gzip` ou `bzip2`.

* **Commande `tar`** : **(Archivage et/ou compression)**
  * `tar -c -f <fichier_archive.tar> <fichiers_ou_répertoires>` : **Crée** une archive (`-c`) à partir de fichiers/répertoires (`<fichiers_ou_répertoires>`), nommée `<fichier_archive.tar>` (`-f`). (ex: `tar -cf archive.tar /home/user/docs`).
  * `tar -x -f <fichier_archive.tar>` : **Extrait** (`-x`) les fichiers d'une archive nommée `<fichier_archive.tar>` (`-f`) vers le répertoire courant.
  * `tar -v` : Option pour un mode **verbeux** (`-v`), affichant les fichiers traités. (Souvent utilisé : `tar -cvf ...`, `tar -xvf ...`)
  * `tar -z` : Option pour utiliser la compression/décompression **gzip** (`-z`). Crée des fichiers `.tar.gz` ou `.tgz`.
  * `tar -j` : Option pour utiliser la compression/décompression **bzip2** (`-j`). Crée des fichiers `.tar.bz2` ou `.tbz`.
  * `tar -J` : Option pour utiliser la compression/décompression **xz** (`-J`) (Information ajoutée, non trouvée directement dans les sources, mais courant). Crée des fichiers `.tar.xz`.
  * **Combinaison pour Archiver et Compresser** :
    * `tar -czvf <fichier.tar.gz> <fichiers/répertoires>` : Crée une archive compressée en gzip, mode verbeux. (ex: `tar -czvf archive.tar.gz /home/user/data`)
    * `tar -cjvf <fichier.tar.bz2> <fichiers/répertoires>` : Crée une archive compressée en bzip2, mode verbeux.
    * `tar -cJvf <fichier.tar.xz> <fichiers/répertoires>` : Crée une archive compressée en xz, mode verbeux. (Information ajoutée)
  * **Combinaison pour Décompresser et Extraire** :
    * `tar -xzvf <fichier.tar.gz>` : Décompresse (gzip) et extrait une archive, mode verbeux. (ex: `tar -xzvf archive.tar.gz`)
    * `tar -xjvf <fichier.tar.bz2>` : Décompresse (bzip2) et extrait une archive, mode verbeux.
    * `tar -xJvf <fichier.tar.xz>` : Décompresse (xz) et extrait une archive, mode verbeux. (Information ajoutée)
  * **Extraire vers un répertoire spécifique** :
    * `tar -xzvf <fichier.tar.gz> -C <répertoire_destination>` : Extrait l'archive vers le répertoire spécifié (`-C`). (ex: `tar -xzvf archive.tar.gz -C /tmp/extraits`)
  * **Exclure des fichiers/répertoires** :
    * `tar -czvf archive.tar.gz /path/to/dir --exclude=<chemin/motif>` : Exclut un chemin ou un motif spécifié lors de la création de l'archive. Option `--exclude` peut être répétée plusieurs fois. Les motifs (comme `*.mp4`) sont pris en charge.

* **Commandes `gzip` et `bzip2` (Compression seule)** : Ces commandes sont utilisées pour compresser ou décompresser des fichiers individuels, pas des archives de plusieurs fichiers.
  * `gzip <fichier>` : Compresse un fichier en utilisant gzip, le remplace par `<fichier>.gz`.
  * `gzip -d <fichier.gz>` : Décompresse un fichier `.gz`, le remplace par le fichier original.
  * `bzip2 <fichier>` : Compresse un fichier en utilisant bzip2, le remplace par `<fichier>.bz2`. (Information ajoutée, similaire à gzip et `tar -j`)
  * `bzip2 -d <fichier.bz2>` : Décompresse un fichier `.bz2`. (Information ajoutée)

* **Commande `zip` et `unzip`** : **(Archivage et compression combinés au format `.zip`)** Un format différent de `tar`. (Information ajoutée, mentionnée dans mais sans détails)
  * `zip <fichier_archive.zip> <fichiers/répertoires>` : Crée ou met à jour une archive `.zip`.
  * `unzip <fichier_archive.zip>` : Extrait les fichiers d'une archive `.zip`.

---
