**1. Gestion des utilisateurs et des groupes**

Les systèmes d'exploitation basés sur Unix/Linux, comme Debian et Ubuntu, sont multi-utilisateurs. La gestion des comptes utilisateur et de groupe est cruciale pour la sécurité.

* **`adduser`**
    Cette commande est un script Perl interactif utilisé pour ajouter des utilisateurs et des groupes sur les systèmes Debian et dérivés. Elle pose une série de questions pour configurer le nouveau compte. Par défaut, elle crée un répertoire personnel pour le nouvel utilisateur en copiant les fichiers depuis `/etc/skel/`.
  * `--system` : Utilisé pour créer des utilisateurs et groupes système qui sont alloués dynamiquement dans la plage 100-999.
  * `--disabled-login` : Crée un utilisateur qui ne peut pas se connecter directement tant qu'un mot de passe n'est pas attribué.
  * `--disabled-password` : Crée un utilisateur qui ne peut pas se connecter avec un mot de passe, mais peut utiliser l'authentification par clé SSH.
  * `--home <répertoire>` : Spécifie un répertoire personnel différent de celui par défaut.
  * `--no-create-home` : Ne crée pas de répertoire personnel.
  * `--ingroup <groupe>` : Ajoute le nouvel utilisateur au groupe spécifié.
  * `--uid <UID>` : Crée l'utilisateur avec un UID spécifique.

    Exemples d'utilisation :

    ```bash
    sudo adduser identifiant # Crée un utilisateur interactif
    sudo adduser --system nom_utilisateur # Crée un utilisateur système
    sudo adduser --disabled-password --no-create-home UtilisateurSSH # Crée un utilisateur pour l'accès SSH uniquement
    sudo adduser UtilisateurSSH fuse # Ajoute un utilisateur existant à un groupe existant
    ```

* **`useradd`**
    C'est un outil non-interactif pour créer des comptes utilisateur. Il est invoqué par `adduser`.

* **`deluser`**
    Utilisé pour supprimer un compte utilisateur.
  * `--remove-home` : Supprime le répertoire personnel de l'utilisateur en plus du compte. Attention, `rm -R` est une commande dangereuse.

    Exemples d'utilisation :

    ```bash
    sudo deluser nom_utilisateur # Supprime l'utilisateur, conserve le répertoire personnel
    sudo deluser --remove-home nom_utilisateur # Supprime l'utilisateur et son répertoire personnel
    sudo deluser UtilisateurSSH users # Supprime un utilisateur d'un groupe spécifique
    ```

* **`addgroup`**
    C'est le pendant de `adduser` pour la création de groupes. C'est un script interactif en mode console.
  * `--system` : Utilisé avec `adduser` pour créer un groupe système.

    Exemple d'utilisation :

    ```bash
    sudo addgroup nom_groupe # Crée un groupe de manière interactive
    ```

* **`groupadd`**
    Outil non-interactif pour créer des groupes.

* **`delgroup`**
    Utilisé pour supprimer un groupe.

    Exemple d'utilisation :

    ```bash
    sudo delgroup groupname # Supprime un groupe
    ```

* **`passwd`**
    Utilisé pour modifier le mot de passe d'un utilisateur. Par défaut, il gère la politique de mot de passe (longueur, complexité) via `/etc/pam.d/common-password`.
  * `-l` : Verrouille le mot de passe d'un utilisateur.
  * `-u` : Déverrouille le mot de passe d'un utilisateur.
  * `-e` : Force l'utilisateur à changer de mot de passe à la prochaine connexion.
  * `-S` : Affiche l'état d'un compte.

    Exemples d'utilisation :

    ```bash
    sudo passwd # Change le mot de passe de l'utilisateur courant (ou de root si exécuté par root)
    sudo passwd nom_utilisateur # Change le mot de passe d'un autre utilisateur (nécessite les droits d'administration)
    sudo passwd -l nom_utilisateur # Verrouille le compte
    sudo passwd -e jdoe # Force ldoe à changer de mot de passe à la prochaine connexion
    ```

* **`chage`**
    Permet de modifier les informations d'expiration du mot de passe et du compte.
  * `-l` : Affiche le statut actuel d'un compte utilisateur (dernière modification du mot de passe, expiration, etc.).
  * `-E <date>` : Définit la date d'expiration du compte.
  * `-m <jours>` : Définit le nombre minimum de jours entre les changements de mot de passe.
  * `-M <jours>` : Définit le nombre maximum de jours de validité du mot de passe.
  * `-I <jours>` : Définit la période d'inactivité autorisée après l'expiration du mot de passe.
  * `-W <jours>` : Définit la durée d'avertissement avant l'expiration du mot de passe.

    Exemples d'utilisation :

    ```bash
    sudo chage -l username # Affiche les informations d'expiration pour l'utilisateur
    sudo chage username # Démarre un mode interactif pour modifier les informations
    sudo chage -E 01/31/2015 -m 5 -M 90 -I 30 -W 14 username # Définit diverses politiques d'expiration
    ```

* **`usermod`**
    Utilisé pour modifier les paramètres d'un compte utilisateur existant. `adduser` utilise cet outil en arrière-plan.
  * `-aG <GROUPES>` : Ajoute l'utilisateur aux groupes supplémentaires spécifiés sans le supprimer de ses groupes d'origine.
  * `-g <GROUPE>` : Définit le groupe primaire de l'utilisateur.
  * `-d <répertoire> -m -l <nouveau_login> <ancien_login>` : Permet de renommer le répertoire personnel et le login d'un utilisateur.
  * `--expiredate 1` : Verrouille un compte en définissant une date d'expiration passée (le 1er janvier 1970).
  * `--expiredate ""` : Réactive un compte en supprimant la date d'expiration.

    Exemples d'utilisation :

    ```bash
    sudo usermod -aG toto machin # Ajoute l'utilisateur 'machin' au groupe 'toto'
    sudo usermod -g group1 user1 # Définit 'group1' comme groupe primaire pour 'user1'
    sudo usermod --expiredate 1 nom_utilisateur # Verrouille le compte
    sudo usermod --expiredate "" nom_utilisateur # Réactive le compte
    sudo usermod -d /home/new_login -m -l new_login old_login # Renomme l'utilisateur et son répertoire personnel
    ```

* **`groups`**
    Affiche les groupes auxquels appartient un utilisateur.

    Exemples d'utilisation :

    ```bash
    groups # Affiche les groupes de l'utilisateur courant
    groups MonUtilisateur # Affiche les groupes de l'utilisateur MonUtilisateur
    ```

* **`id`**
    Affiche les informations sur un utilisateur, y compris ses UID, GID et groupes d'appartenance.

    Exemple d'utilisation :

    ```bash
    id ubuntu-user # Affiche les informations pour l'utilisateur 'ubuntu-user'
    ```

**2. Démarrage des services système**

Debian et Ubuntu utilisent `systemd` comme système d'initialisation par défaut. Les services peuvent être gérés avec `systemctl`. Les systèmes plus anciens ou alternatifs peuvent utiliser des scripts `init.d` gérés par `update-rc.d` et invoqués par `invoke-rc.d`.

* **`systemctl`**
    Permet de contrôler et d'afficher l'état des services système.
  * `start <service.service>` : Lance le service.
  * `stop <service.service>` : Arrête le service.
  * `enable <service.service>` : Configure le service pour qu'il démarre automatiquement au boot.
  * `disable <service.service>` : Désactive le démarrage automatique du service au boot.
  * `status <service.service>` : Affiche l'état actuel du service.

    Exemples d'utilisation :

    ```bash
    sudo systemctl start NetworkManager.service # Lance le service NetworkManager
    sudo systemctl enable NetworkManager.service # Active le démarrage automatique de NetworkManager
    sudo systemctl status mysql.service # Affiche le statut du service MySQL
    ```

* **`update-rc.d`**
    Utilisé dans les scripts de maintenance de paquets pour gérer les liens symboliques SysVinit dans `/etc/rcn.d/`. Il ne faut pas modifier ces liens manuellement.
  * `package defaults` : Active le démarrage automatique du démon par défaut.
  * `package remove` : Supprime les liens de démarrage lors de la purge du paquet.
  * `package defaults-disabled` : Désactive le démarrage automatique par défaut, permettant à l'administrateur de l'activer manuellement.

    Exemples d'utilisation (dans les scripts postinst/prerm) :

    ```bash
    update-rc.d package defaults
    update-rc.d package remove # Dans le script prerm, pour une purge
    update-rc.d package defaults-disabled
    ```

* **`invoke-rc.d`**
    Utilisé par les scripts de maintenance pour invoquer les scripts init.d ou leur équivalent. Il respecte les runlevels et les contraintes locales.
  * `package action` : Invoque l'action spécifiée (start, stop, etc.) pour le paquet.

    Exemple d'utilisation (dans les scripts postinst/prerm) :

    ```bash
    invoke-rc.d package action
    ```

* **`start-stop-daemon`**
    Outil recommandé à utiliser *dans* les scripts init.d pour gérer les démons.
  * `--oknodo` : Permet au script de renvoyer succès même si le démon est déjà démarré lors d'une tentative de démarrage, ou déjà arrêté lors d'une tentative d'arrêt.

**3. Tâches planifiées (Cron jobs)**

Le service `cron` permet de planifier des tâches à exécuter régulièrement. Les tâches peuvent être placées dans des répertoires spécifiques (`/etc/cron.hourly`, `/etc/cron.daily`, etc.) ou définies dans des fichiers dans `/etc/cron.d/`.

* **`crontab`**
    Utilisé pour gérer les tâches cron des utilisateurs individuels. Le format du fichier `crontab` pour `/etc/cron.d/` et `/etc/crontab` inclut un champ supplémentaire pour l'utilisateur.
  * `crontab -e` : Édite le fichier crontab de l'utilisateur courant.
  * `crontab -l` : Affiche le fichier crontab de l'utilisateur courant.

    Exemple de ligne dans un fichier `/etc/cron.d/` ou `/etc/crontab` :

    ```crontab
    * * * * * user command_to_run # Exécute la commande chaque minute
    ```

**4. Configuration réseau**

Les systèmes d'exploitation gèrent les interfaces réseau, les adresses IP, la résolution de noms, etc. Les commandes varient entre les distributions et les versions.

* **`iwconfig`**
    Utilisé sur Debian et les systèmes similaires pour découvrir et configurer les interfaces sans fil. Il est similaire à `ifconfig` mais pour le sans fil.

    Exemple d'utilisation :

    ```bash
    sudo iwconfig # Affiche les informations sur les interfaces sans fil
    ```

* **`iwlist`**
    Fournit des informations supplémentaires sur les périphériques sans fil, y compris la liste des réseaux disponibles.
  * `<interface> scan` : Analyse les réseaux disponibles via l'interface spécifiée.

    Exemples d'utilisation :

    ```bash
    sudo iwlist wlp3s0 scan # Analyse les réseaux via l'interface wlp3s0
    sudo iwlist wlp3s0 scan | grep ESSID # Affiche seulement les ESSID des réseaux trouvés
    ```

* **`ifconfig`**
    Une commande traditionnelle pour configurer et afficher les informations des interfaces réseau. Elle est considérée comme obsolète au profit de `ip`.
  * `-a` : Affiche toutes les interfaces, même celles désactivées.

    Exemples d'utilisation :

    ```bash
    ifconfig -a # Affiche toutes les interfaces réseau
    sudo ifconfig eth0 10.0.0.100 netmask 255.255.255.0 # Configure temporairement une adresse IP pour eth0
    ifconfig eth0 # Affiche la configuration de l'interface eth0
    ```

* **`ip`**
    La commande moderne et recommandée pour configurer et afficher les informations réseau (interfaces, adresses IP, routes, etc.).
  * `addr` : Gère les adresses IP.
    * `show [dev <interface>]` : Affiche les adresses IP.
    * `add <adresse>/<masque> dev <interface>` : Ajoute temporairement une adresse IP à une interface.
    * `flush <interface>` : Supprime temporairement toutes les configurations IP d'une interface.
  * `link` : Gère les interfaces réseau.
    * `show [dev <interface>]` : Affiche l'état des interfaces.
    * `set dev <interface> up` : Active une interface.
    * `set dev <interface> down` : Désactive une interface.
    * `set dev <interface> mtu <valeur>` : Définit le MTU d'une interface.
  * `route` : Gère la table de routage.
    * `list` : Affiche les entrées de la table de routage.
    * `add <destination> via <passerelle>` : Ajoute temporairement une route.
    * `add default via <passerelle> dev <interface>` : Ajoute temporairement une route par défaut.
    * `show default` : Affiche la route par défaut.
  * `-s` : Affiche des statistiques (souvent utilisé avec `link` ou `neigh`).
  * `neigh` : Gère la table ARP (voisins).
    * `show [dev <interface>]` : Affiche les voisins.

    Exemples d'utilisation :

    ```bash
    ip a # Affiche toutes les adresses IP et interfaces
    ip link show # Affiche l'état de toutes les interfaces
    sudo ip addr add 10.102.66.200/24 dev enp0s25 # Ajoute temporairement une adresse IP
    sudo ip route add default via 10.102.66.1 # Configure temporairement une passerelle par défaut
    ip route show # Affiche la table de routage
    ```

* **`route`**
    La commande traditionnelle pour gérer la table de routage. Elle est obsolète au profit de `ip route`.

    Exemples d'utilisation :

    ```bash
    sudo route add default gw 10.0.0.1 eth0 # Configure temporairement une passerelle par défaut
    route -n # Affiche la table de routage numérique
    ```

* **`nmcli`**
    NetworkManager Command Line Interface. C'est un outil puissant pour gérer les connexions et les périphériques réseau via NetworkManager.
  * `d` : Gère les périphériques (devices).
    * `d wifi` : Spécifie un périphérique sans fil.
    * `d wifi list` : Liste les réseaux Wi-Fi disponibles.
    * `d wifi hotspot ifname <interface> ssid <ssid> password <password>` : Crée un point d'accès Wi-Fi.
  * `c` : Gère les connexions (connections).
    * `c show` : Affiche les connexions configurées.
    * `c add type <type> con-name <nom> ifname <interface> ...` : Ajoute une nouvelle connexion.
    * `c modify <nom> <paramètre> <valeur>` : Modifie les paramètres d'une connexion.
    * `c up <nom>` : Active une connexion.
    * `c import type <type> file <fichier>` : Importe une configuration (ex: VPN).
    * `c edit` : Lance l'éditeur interactif de connexions.
  * `r` : Gère les radios (Wi-Fi, WWAN).
    * `r wifi on` : Active la radio Wi-Fi.
    * `r wifi off` : Désactive la radio Wi-Fi.
  * `general logging [level <level> [domain <domain>]]` : Modifie les niveaux de journalisation de NetworkManager.
    * Levels: `ERR`, `WARN`, `INFO`, `DEBUG`.

    Exemples d'utilisation :

    ```bash
    nmcli d # Affiche l'état des périphériques réseau
    nmcli c show # Affiche les connexions configurées
    nmcli d wifi list # Liste les réseaux Wi-Fi disponibles
    nmcli d wifi connect LinuxHint password morochita # Se connecte à un réseau Wi-Fi
    nmcli c add type wifi con-name my_hidden_network ifname wlan0 ssid hidden_ssid # Ajoute une connexion pour un réseau caché
    nmcli connection edit # Lance l'éditeur interactif nmcli
    ```

* **`nmtui`**
    NetworkManager Text User Interface. Une interface interactive en mode texte pour gérer les connexions réseau via NetworkManager.

    Exemple d'utilisation :

    ```bash
    nmtui # Lance l'interface utilisateur texte
    ```

* **`wpa_supplicant`**
    Un outil pour la négociation de l'authentification WPA, souvent utilisé pour se connecter au Wi-Fi via la ligne de commande sur Debian. Il n'est pas installé par défaut sur Debian.
  * `-c <fichier_conf>` : Spécifie le fichier de configuration.
  * `-i <interface>` : Spécifie l'interface réseau.

    Exemples d'utilisation :

    ```bash
    sudo apt install wpasupplicant # Installe le paquet
    wpa_passphrase LinuxHint morochita | sudo tee /etc/wpa_supplicant.conf # Crée ou édite le fichier de configuration
    sudo wpa_supplicant -c /etc/wpa_supplicant.conf -i wlp3s0 # Lance wpa_supplicant
    ```

* **`dhclient`**
    Un client DHCP, utilisé pour obtenir une adresse IP dynamique à partir d'un serveur DHCP.

    Exemple d'utilisation :

    ```bash
    sudo dhclient wlp3s0 # Obtient une adresse IP pour l'interface wlp3s0
    ```

* **`netplan`**
    L'outil de configuration réseau par défaut sur les versions récentes d'Ubuntu, notamment Ubuntu 20.04. Il utilise des fichiers de configuration YAML. NetworkManager sur Ubuntu Core utilise un backend basé sur `libnetplan` et des fichiers YAML dans `/etc/netplan`.
  * `apply` : Applique la configuration réseau définie dans les fichiers YAML.
  * `generate` : Génère les fichiers de configuration des renderers (comme NetworkManager ou systemd-networkd) à partir des fichiers YAML.
  * `get` : Affiche la configuration réseau système.
  * `set <paramètre>=<valeur>` : Modifie les paramètres de configuration réseau.

    Exemples d'utilisation :

    ```bash
    ls /etc/netplan # Liste les fichiers de configuration Netplan
    sudo nano /etc/netplan/50-init-cloud.conf # Édite un fichier de configuration Netplan
    sudo netplan generate && sudo netplan apply # Génère et applique la configuration
    sudo netplan get # Affiche la configuration réseau système
    sudo netplan set ethernets.enp0s2.addresses=[10.0.2.15/24] # Modifie un paramètre
    ```

* **`brctl`**
    Utilitaire pour gérer les ponts réseau (bridges).

    Exemple d'utilisation :

    ```bash
    sudo apt install bridge-utils # Installe le paquet nécessaire
    sudo ifup br0 # Active une interface de pont configurée
    man brctl # Affiche le manuel de brctl pour plus d'informations
    ```

* **`lshw`**
    Liste le matériel du système.
  * `-class network` : Filtre l'affichage pour n'inclure que les périphériques réseau.

    Exemple d'utilisation :

    ```bash
    sudo lshw -class network # Affiche les informations détaillées sur les périphériques réseau
    ```

* **`ethtool`**
    Permet d'afficher et de modifier les paramètres des cartes Ethernet tels que la vitesse, le mode duplex, l'auto-négociation, etc..
  * `<interface>` : Affiche les paramètres de l'interface.
  * `-s <interface> speed <valeur> duplex <mode>` : Définit les paramètres de l'interface.

    Exemples d'utilisation :

    ```bash
    sudo apt install ethtool # Installe le paquet
    sudo ethtool eth0 # Affiche les paramètres de l'interface eth0
    sudo ethtool -s eth0 speed 1000 duplex full # Définit la vitesse et le mode duplex de eth0
    ```

* **`ufw`**
    Uncomplicated Firewall. L'outil de configuration de pare-feu par défaut sur Ubuntu. Il est basé sur `iptables`.
  * `enable` : Active le pare-feu.
  * `disable` : Désactive le pare-feu.
  * `status` : Vérifie l'état du pare-feu.
    * `verbose` : Affiche plus de détails sur l'état.
    * `numbered` : Affiche les règles numérotées.
  * `allow <port|service> [proto <protocole>] [from <adresse/réseau>] [to any port <port>]` : Ajoute une règle pour autoriser les connexions. Le port peut être spécifié par numéro ou par nom de service si défini dans `/etc/services`.
    * `in` : Applique la règle aux connexions entrantes.
    * `on <interface>` : Applique la règle à une interface spécifique.
    * `app <nom_profil>` : Utilise un profil d'application prédéfini.
  * `deny <port|service> [proto <protocole>] [from <adresse/réseau>] [to any port <port>]` : Ajoute une règle pour bloquer les connexions.
  * `delete <règle|numéro>` : Supprime une règle spécifiée ou identifiée par son numéro.
  * `app list` : Liste les profils d'application disponibles.
  * `app info <nom_profil>` : Affiche les détails d'un profil d'application.
  * `logging on|off` : Active ou désactive la journalisation du pare-feu.
  * `--dry-run` : Affiche les règles résultantes sans les appliquer.

    Exemples d'utilisation :

    ```bash
    sudo ufw enable # Active le pare-feu
    sudo ufw status verbose # Vérifie l'état et les règles
    sudo ufw allow 22 # Ouvre le port 22 (SSH)
    sudo ufw deny from 203.0.113.100 # Bloque toutes les connexions depuis une adresse IP
    sudo ufw status numbered # Affiche les règles numérotées pour suppression
    sudo ufw delete 1 # Supprime la règle numéro 1
    sudo ufw allow OpenSSH # Autorise les connexions SSH en utilisant le profil d'application
    sudo ufw allow from 192.168.0.0/24 proto tcp to any port 22 # Autorise les connexions SSH depuis un sous-réseau spécifique
    sudo ufw allow from 203.0.113.103 to any port 3306 # Autorise les connexions MySQL depuis une adresse IP
    ```

* **`iptables`**
    L'utilitaire bas niveau pour configurer Netfilter, le sous-système de filtrage de paquets du noyau Linux. `ufw` est une interface simplifiée pour `iptables`. Souvent utilisé pour des configurations avancées comme la translation d'adresses (NAT).
  * `-t <tableir>` : Spécifie la table (`filter`, `nat`, `mangle`, `raw`).
  * `-A <chaîne>` : Ajoute une règle à la fin d'une chaîne (`INPUT`, `OUTPUT`, `FORWARD`, `PREROUTING`, `POSTROUTING`).
  * `-s <adresse/réseau>` : Spécifie l'adresse source.
  * `-o <interface>` : Spécifie l'interface de sortie.
  * `-j <cible>` : Spécifie la cible de la règle (`ACCEPT`, `DROP`, `REJECT`, `MASQUERADE`, `LOG`, etc.).
  * `MASQUERADE` : Cible utilisée pour le NAT (masquage IP).
  * `LOG` : Cible pour journaliser les paquets.
  * `-m state --state <états>` : Fait correspondre l'état de la connexion (`NEW`, `ESTABLISHED`, `RELATED`, `INVALID`).
  * `-p <protocole>` : Spécifie le protocole (`tcp`, `udp`, `icmp`).
  * `--dport <port>` : Spécifie le port de destination.
  * `--log-prefix <préfixe>` : Ajoute un préfixe aux messages de log.

    Exemples d'utilisation :

    ```bash
    # Activer le masquage IP (NAT) pour un réseau local via ppp0
    sudo iptables -t nat -A POSTROUTING -s 192.168.0.0/16 -o ppp0 -j MASQUERADE
    # Autoriser le trafic établi et lié dans la chaîne FORWARD (si politique par défaut est DROP/REJECT)
    sudo iptables -A FORWARD -s 192.168.0.0/16 -o ppp0 -j ACCEPT
    sudo iptables -A FORWARD -d 192.168.0.0/16 -m state --state ESTABLISHED,RELATED -i ppp0 -j ACCEPT
    # Journaliser les nouvelles connexions HTTP entrantes
    sudo iptables -A INPUT -m state --state NEW -p tcp --dport 80 -j LOG --log-prefix "NEW_HTTP_CONN: "
    ```

* **`netstat`**
    Affiche les connexions réseau, les tables de routage, les statistiques d'interface, les connexions masquées et l'appartenance au multicast. Il est obsolète au profit de `ss` sur les systèmes récents.
  * `-a` : Affiche tous les sockets (écoute et non-écoute).
  * `-t` : Affiche les connexions TCP.
  * `-u` : Affiche les connexions UDP.
  * `-l` : Affiche les sockets en état d'écoute (LISTEN).
  * `-p` : Affiche le PID et le nom du programme associé au socket.
  * `-n` : Affiche les adresses numériques au lieu d'essayer de résoudre les noms (accélère l'affichage).
  * `-r` : Affiche la table de routage.

    Exemples d'utilisation :

    ```bash
    netstat -anp | grep :80 # Affiche les connexions sur le port 80 avec PID/Programme
    netstat -ltunp # Affiche tous les ports TCP/UDP en écoute avec PID/Programme (sans résolution de nom)
    ```

* **`ss`**
    Commande moderne pour afficher les statistiques des sockets. Elle remplace `netstat`.
  * `-a` : Affiche tous les sockets.
  * `-l` : Affiche les sockets en écoute.
  * `-t` : Affiche les sockets TCP.
  * `-u` : Affiche les sockets UDP.
  * `-p` : Affiche le processus utilisant le socket.
  * `-n` : Ne pas résoudre les noms de service.
  * `-e` : Affiche des informations détaillées.

    Exemples d'utilisation :

    ```bash
    ss -anp | grep :8443 # Affiche les sockets sur le port 8443 avec PID/Programme (numérique, tous)
    ss -lnpt 'sport = :3000' # Affiche les sockets TCP en écoute sur le port 3000 avec PID (numérique)
    ```

* **`ping`**
    Envoie des paquets ICMP à un hôte pour vérifier la connectivité réseau.

    Exemple d'utilisation :

    ```bash
    ping google.com # Vérifie la connectivité vers google.com
    ```

* **`whois`**
    Récupère les informations d'enregistrement d'un domaine.

    Exemple d'utilisation :

    ```bash
    whois example.com
    ```

* **`dig`**
    Utilitaire pour interroger les serveurs DNS afin d'obtenir des informations sur les noms de domaine.
  * `-x <hôte>` : Effectue une recherche inversée (adresse IP vers nom d'hôte).

    Exemples d'utilisation :

    ```bash
    dig example.com # Obtient les informations DNS pour example.com
    dig -x 8.8.8.8 # Effectue une recherche inversée pour l'adresse IP 8.8.8.8
    ```

* **`wget`**
    Outil en ligne de commande pour télécharger des fichiers depuis le web.
  * `-c` : Continue un téléchargement interrompu.

    Exemples d'utilisation :

    ```bash
    wget http://example.com/file.tar.gz # Télécharge un fichier
    wget -c http://example.com/largefile.iso # Continue un téléchargement
    ```

* **`curl`**
    Outil pour transférer des données avec diverses protocoles (HTTP, FTP, etc.). Souvent utilisé pour les requêtes web.
  * `-X <méthode>` : Spécifie la méthode de requête HTTP (GET, POST, PUT, DELETE, etc.).
  * `-L` : Suit les redirections.
  * `-d <données>` : Envoie des données pour une requête POST.
  * `-k` : Autorise les connexions serveur non sécurisées (HTTPS sans validation de certificat).

    Exemples d'utilisation :

    ```bash
    curl http://example.com # Effectue une requête GET simple
    curl -X POST -d "param1=value1&param2=value2" http://example.com/api # Effectue une requête POST
    ```

* **`hostnamectl`**
    Permet de contrôler le nom d'hôte système. Il affiche également des informations sur l'OS et le noyau.

    Exemple d'utilisation :

    ```bash
    hostnamectl # Affiche le nom d'hôte et des informations système
    ```

**5. Gestion des fichiers et répertoires**

Les commandes de base pour manipuler les fichiers et répertoires sont fondamentales pour l'utilisation du système d'exploitation.

* **`mkdir`**
    Crée des répertoires (dossiers).
  * `-p` : Crée les répertoires parents si nécessaire.

    Exemples d'utilisation :

    ```bash
    mkdir photos # Crée un répertoire nommé photos
    mkdir -p photos/2005/noel # Crée une structure de répertoires imbriqués
    ```

* **`rmdir`**
    Supprime un répertoire *vide*.
  * `-p` : Supprime les répertoires parents s'ils deviennent vides.

    Exemples d'utilisation :

    ```bash
    rmdir LeRep # Supprime le répertoire LeRep (s'il est vide)
    rmdir -p test/essai # Supprime essai, puis test s'il devient vide
    ```

* **`chown`**
    Change le propriétaire et/ou le groupe propriétaire d'un fichier ou répertoire.
  * `-R` : Applique le changement récursivement aux fichiers et sous-répertoires.

    Exemples d'utilisation :

    ```bash
    sudo chown tux foobar # Change le propriétaire du fichier foobar à l'utilisateur tux
    sudo chown :penguins foobar # Change le groupe propriétaire du fichier foobar au groupe penguins
    sudo chown tux:penguins foobar # Change le propriétaire et le groupe du fichier foobar
    sudo chown -R root:root /home/username/ # Change récursivement le propriétaire et le groupe d'un répertoire
    sudo chown -R lui:nous monRep # Change propriétaire et groupe récursivement pour monRep
    ```

* **`chmod`**
    Change les permissions d'accès à un fichier ou répertoire. Les permissions peuvent être définies avec des lettres (u, g, o, a ; r, w, x, s, t ; +, -, =) ou des nombres octaux (4=lecture, 2=écriture, 1=exécution).
  * `-R` : Applique le changement récursivement.
  * `+t` : Ajoute le sticky bit à un répertoire (empêche les utilisateurs de supprimer/renommer les fichiers dont ils ne sont pas propriétaires dans ce répertoire).
  * `-t` : Retire le sticky bit.
  * `g+s` : Positionne le bit Setgid sur un répertoire (les fichiers créés dans ce répertoire appartiendront par défaut au groupe propriétaire du répertoire).
  * `g-s` : Retire le bit Setgid d'un répertoire.

    Exemples d'utilisation :

    ```bash
    chmod u+x file1 # Ajoute la permission d'exécution pour le propriétaire
    chmod go-wx monRep # Supprime les permissions d'écriture et exécution pour le groupe et les autres
    chmod u=rw,go=r MonFichier # Définit les permissions (propriétaire: rw, groupe/autres: r)
    chmod 644 MonFichier # Identique à l'exemple précédent, avec notation octale
    sudo chmod 0750 /home/username # Supprime la permission de lecture/exécution mondiale pour un répertoire personnel
    sudo chmod 777 -R /path/to/someDirectory # Ajoute toutes les permissions récursivement (potentiellement dangereux)
    chmod +t folder # Ajoute le sticky bit à un répertoire
    ```

* **`test`**
    Évalue des expressions conditionnelles. Souvent utilisé dans les scripts shell, y compris les scripts init.d.
  * `-f <fichier>` : Vrai si <fichier> existe et est un fichier ordinaire.

    Exemple d'utilisation (extrait de script init.d) :

    ```bash
    test -f program-executed-later-in-script || exit 0 # Quitte si le fichier exécutable n'existe pas
    ```

* **`find`**
    Recherche des fichiers et répertoires en suivant une hiérarchie. Peut exécuter des commandes sur les éléments trouvés. La recherche est récursive par défaut.
  * `.` : Représente le répertoire courant (point de départ de la recherche).
  * `-name <modèle>` : Recherche par nom (respecte la casse).
  * `-iname <modèle>` : Recherche par nom (ignore la casse).
  * `-type <type>` : Recherche par type (f: fichier, d: répertoire, l: lien symbolique, etc.).
  * `-mtime <n>` : Recherche par date de dernière modification (n jours).
  * `-user <utilisateur>` : Recherche par propriétaire.
  * `-group <groupe>` : Recherche par groupe propriétaire.
  * `-size <+/-n>` : Recherche par taille (plus/moins de n).
  * `-exec <commande> {} \;` : Exécute la commande spécifiée sur chaque fichier trouvé (`{}` est remplacé par le nom du fichier).
  * `-print0` : Affiche le chemin complet de chaque fichier trouvé, suivi d'un caractère nul (utile pour le combiner avec `xargs -0`).

    Exemples d'utilisation :

    ```bash
    find . -type f -name "*.conf" # Cherche tous les fichiers .conf dans le répertoire courant et ses sous-répertoires
    sudo find /path/to/someDirectory -type f -print0 | xargs -0 sudo chmod 644 # Change les permissions de tous les fichiers sous un répertoire
    sudo find /path/to/someDirectory -type d -print0 | xargs -0 sudo chmod 755 # Change les permissions de tous les répertoires sous un répertoire
    find /home/$USER -type f -name "*.mp3" # Trouve tous les fichiers mp3 dans le répertoire personnel
    find . \( -type f -exec sudo chmod 664 "{}" \; \) , \( -type d -exec sudo chmod 775 "{}" \; \) # Modifie les permissions des fichiers et répertoires différemment
    ```

* **`grep`**
    Recherche une chaîne de caractères ou un modèle (expression régulière) dans des fichiers ou une entrée standard.
  * `-i` : Ignore la casse.
  * `-r` : Recherche récursivement dans les répertoires.
  * `-n` : Affiche les numéros de ligne des correspondances.
  * `-l` : Affiche seulement les noms des fichiers contenant des correspondances.
  * `-v` : Inverse la correspondance (affiche les lignes *qui ne* correspondent *pas*).
  * `-E` : Utilise des expressions régulières étendues (équivalent à `egrep`).
  * `-F` : Utilise des chaînes fixes (équivalent à `fgrep`).
  * `--include <modèle_fichier>` : Recherche uniquement dans les fichiers correspondant au modèle.
  * `-A <nombre>` : Affiche <nombre> lignes après la correspondance.
  * `-B <nombre>` : Affiche <nombre> lignes avant la correspondance.

    Exemples d'utilisation :

    ```bash
    sudo iwlist wlp3s0 scan | grep ESSID # Filtre la sortie pour afficher seulement les ESSID
    grep -r 'pattern' . # Recherche récursivement 'pattern' dans le répertoire courant
    grep -n montexte monfichier # Recherche 'montexte' dans 'monfichier' et affiche les numéros de ligne
    command | grep pattern # Recherche 'pattern' dans la sortie d'une commande
    grep 'pattern1\|pattern2' filename # Recherche 'pattern1' OU 'pattern2' dans un fichier
    ```

* **`file`**
    Détermine le type d'un fichier en utilisant des tests sur son contenu.

    Exemple d'utilisation :

    ```bash
    file dossier/* # Identifie le type de tous les fichiers dans un dossier
    ```

* **`touch`**
    Met à jour l'horodatage des fichiers ou crée de nouveaux fichiers vides.

    Exemple d'utilisation :

    ```bash
    touch file1 file2 # Crée des fichiers vides
    touch /run/reboot-required # Signale qu'un redémarrage est nécessaire
    ```

* **`rm`**
    Supprime des fichiers ou des répertoires. **C'est une commande très dangereuse !** Utilisez-la avec une extrême prudence.
  * `-f` : Force la suppression sans confirmation.
  * `-r` : Supprime récursivement des répertoires et leur contenu.

    Exemples d'utilisation :

    ```bash
    rm file.html # Supprime un fichier
    rm -f file.html # Supprime un fichier sans confirmation
    rm -r dir # Supprime un répertoire et son contenu
    sudo rm -rf /path/to/file/filename # Supprime un fichier avec les droits d'administration, en forçant et récursivement (dangereux, utilisez le chemin absolu)
    rm -rf /tmp/LeRep # Supprime le répertoire /tmp/LeRep et tout son contenu sans confirmation
    ```

* **`cat`**
    Affiche le contenu de fichiers texte. Peut également être utilisé pour concaténer des fichiers ou créer un fichier à partir de l'entrée standard.
  * `-n` : Affiche le contenu avec les numéros de ligne.

    Exemples d'utilisation :

    ```bash
    cat /etc/os-release # Affiche le contenu du fichier /etc/os-release
    cat -n monFichier # Affiche monFichier avec numéros de ligne
    cat > newfile.txt # Crée un nouveau fichier et y écrit l'entrée standard (Terminer avec Ctrl+D)
    ```

* **`head`**
    Affiche les premières lignes d'un fichier.
  * `-n <nombre>` : Spécifie le nombre de lignes à afficher.

    Exemple d'utilisation :

    ```bash
    head /etc/fichier # Affiche les 10 premières lignes
    head -n 100 /etc/fichier # Affiche les 100 premières lignes
    ```

* **`tail`**
    Affiche les dernières lignes d'un fichier.
  * `-n <nombre>` : Spécifie le nombre de lignes à afficher.
  * `-f` : Surveille le fichier et affiche les nouvelles lignes au fur et à mesure qu'elles sont ajoutées (utile pour les fichiers journaux).

    Exemples d'utilisation :

    ```bash
    tail /etc/fichier # Affiche les 10 dernières lignes
    tail -n 100 /etc/fichier # Affiche les 100 dernières lignes
    tail -f /var/log/syslog # Affiche les nouvelles lignes du fichier journal
    ```

* **`more`**
    Affiche le contenu d'un fichier page par page. Permet une navigation simple.

    Exemple d'utilisation :

    ```bash
    more file # Affiche le contenu de file page par page
    ```

* **`less`**
    Similaire à `more`, affiche un fichier page par page mais avec plus de fonctionnalités (navigation arrière, recherche, etc.). Quitter avec `:q`.

    Exemple d'utilisation :

    ```bash
    less /var/log/syslog # Affiche le fichier journal en mode interactif
    ```

* **`echo`**
    Affiche une chaîne de caractères ou la valeur de variables. Souvent utilisé pour écrire du texte dans des fichiers.

    Exemples d'utilisation :

    ```bash
    echo $TERM # Affiche la valeur de la variable TERM
    echo "Contenu du fichier" > fichier.txt # Écrit (et remplace) le contenu dans fichier.txt
    echo "Contenu supplémentaire" >> fichier.txt # Ajoute du contenu à la fin de fichier.txt
    ```

* **`tee`**
    Lit l'entrée standard et écrit à la fois sur la sortie standard et dans un ou plusieurs fichiers. Utile pour écrire dans des fichiers nécessitant des droits d'administration en conjonction avec `sudo`.
  * `-a` : Ajoute le contenu à la fin du fichier au lieu de l'écraser.

    Exemple d'utilisation :

    ```bash
    wpa_passphrase LinuxHint morochita | sudo tee /etc/wpa_supplicant.conf # Écrit la sortie de wpa_passphrase dans un fichier système avec droits d'administration
    echo "Ligne à écrire" | tee -a fichier.txt # Ajoute une ligne à fichier.txt
    ```

* **`ls`**
    Liste le contenu d'un répertoire.
  * `-l` : Affiche une liste détaillée (permissions, propriétaire, taille, date).
  * `-a` : Affiche tous les fichiers, y compris les fichiers cachés (ceux qui commencent par un point).
  * `-h` : Associé à `-l`, affiche les tailles de fichiers dans un format lisible par l'homme (K, M, G).
  * `-al` : Combinaison de `-a` et `-l`.
  * `-d` : Utilisé avec des motifs pour afficher des informations sur le répertoire lui-même plutôt que son contenu.

    Exemples d'utilisation :

    ```bash
    ls -l Documents/ # Liste le contenu détaillé du répertoire Documents/
    ls -al # Liste tous les fichiers (y compris cachés) avec détails dans le répertoire courant
    ls -ld /home/username # Affiche les détails du répertoire /home/username lui-même
    ```
