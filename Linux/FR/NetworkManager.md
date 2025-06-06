# NetworkManager

NetworkManager est un service système standard sous Linux qui gère vos périphériques réseau et vos connexions pour maintenir la connectivité lorsque possible. Sur les systèmes Ubuntu récents, en particulier Ubuntu Core, NetworkManager prend le contrôle de la configuration réseau en se définissant comme le moteur de rendu réseau par défaut via un fichier de configuration Netplan.

L'outil principal en ligne de commande pour interagir avec NetworkManager est **`nmcli`**. Il permet de créer, éditer, supprimer, activer et désactiver des connexions, ainsi que d'afficher l'état des périphériques. Une interface utilisateur textuelle appelée **`nmtui`** est également disponible comme alternative.

**Persistance de la Configuration : L'Intégration avec Netplan sur Ubuntu Core**

Sur les versions d'Ubuntu Core à partir de `core20`, NetworkManager utilise un backend YAML basé sur `libnetplan`. Les configurations de connexion sont stockées dans des fichiers YAML sous `/etc/netplan/*.yaml`. Lorsque vous modifiez ou créez une connexion à l'aide d'outils NetworkManager comme `nmcli`, NetworkManager crée ou met à jour un fichier keyfile temporaire qui est immédiatement converti en YAML Netplan dans `/etc/netplan`, et `netplan generate` est automatiquement appelé. Le générateur Netplan traite ensuite ces fichiers YAML au démarrage pour créer les profils de connexion NetworkManager dans `/run/NetworkManager/system-connections`, assurant ainsi que **vos configurations sont persistantes après un redémarrage**.

Voici les commandes `nmcli` les plus utiles pour gérer vos connexions réseau de manière persistante sur les systèmes utilisant NetworkManager avec le backend Netplan :

* **Afficher l'état des périphériques réseau**
    Liste les interfaces réseau connues par NetworkManager et leur état actuel.

    ```bash
    nmcli device
    # ou forme courte
    nmcli d
    ```

    *Persistance : Non*. Cette commande affiche l'état en cours des périphériques, pas une configuration persistante.

* **Lister les réseaux Wi-Fi disponibles**
    Permet de scanner et d'afficher les points d'accès Wi-Fi détectés par l'interface Wi-Fi.

    ```bash
    nmcli device wifi list
    # ou forme courte
    nmcli d wifi list
    ```

    *Persistance : Non*. Cette commande liste les réseaux détectés et n'est pas une configuration persistante.

* **Activer ou désactiver la radio Wi-Fi**
    Contrôle l'état physique de l'interface Wi-Fi.

    ```bash
    nmcli radio wifi on
    # ou
    nmcli radio wifi off
    ```

    *Persistance : Non*. Contrôle l'état immédiat de la radio. L'activation automatique au démarrage dépend de la configuration persistante de l'interface gérée par NetworkManager/Netplan.

* **Se connecter à un réseau Wi-Fi (SSID diffusé)**
    Crée ou active une connexion à un réseau Wi-Fi spécifique en utilisant son SSID et son mot de passe.

    ```bash
    nmcli device wifi connect <SSID> password <mot_de_passe>
    # Exemple :
    nmcli d wifi connect MonReseauWifi password mon_super_mdp
    ```

    *Persistance : Oui*. Cette commande crée implicitement une définition de connexion NetworkManager persistante qui sera enregistrée dans les fichiers Netplan pour être réappliquée au démarrage.

* **Se connecter à un réseau caché (non diffusé)**
    Pour un réseau caché, vous devez explicitement créer la définition de connexion, puis l'activer.
    1. Créer la connexion :

        ```bash
        nmcli connection add type wifi con-name <nom_connexion> ifname <nom_interface_wifi> ssid <SSID_cache>
        # Exemple (remplacez 'wlan0' par le nom de votre interface Wi-Fi) :
        nmcli c add type wifi con-name ConnexionCachee ifname wlan0 ssid MonReseauCache
        ```

        *Persistance : Oui*.

    2. Configurer la sécurité (exemple pour WPA-PSK, nécessite 8-63 caractères ou 64 hexadécimaux) :

        ```bash
        nmcli connection modify <nom_connexion> wifi-sec.key-mgmt wpa-psk wifi-sec.psk <mot_de_passe>
        # Exemple :
        nmcli c modify ConnexionCachee wifi-sec.key-mgmt wpa-psk wifi-sec.psk mon_super_mdp_cache
        ```

        *Persistance : Oui*.

    3. Activer la connexion pour se connecter immédiatement :

        ```bash
        nmcli connection up <nom_connexion>
        # Exemple :
        nmcli c up ConnexionCachee
        ```

        *Persistance : Oui*. L'activation d'une connexion définie est persistante dans le sens où NetworkManager essaiera de se connecter à ce profil au démarrage s'il est disponible et configuré pour l'auto-connexion (comportement par défaut lors de la création via `nmcli`).

* **Créer un point d'accès Wi-Fi (Hotspot)**
    Transforme une interface Wi-Fi en point d'accès, configurant généralement un serveur DHCP pour les clients connectés.

    ```bash
    nmcli device wifi hotspot ifname <nom_interface_wifi> ssid <SSID_hotspot> password <mot_de_passe>
    # Exemple (remplacez 'wlan0' par le nom de votre interface Wi-Fi ; le mot de passe doit avoir 8-63 caractères ou 64 hexadécimaux) :
    nmcli d wifi hotspot ifname wlan0 ssid MonHotspot password mdp_hotspot123
    ```

    *Persistance : Oui*. Crée une connexion persistante de type `hotspot`. Par défaut, elle utilise la méthode `shared` pour IPv4.

* **Configurer une connexion partagée (type passerelle)**
    Crée une connexion qui configure l'interface pour partager une connexion existante, agissant comme un serveur DHCP pour les clients qui s'y connectent.

    ```bash
    nmcli connection add con-name <nom> type ethernet ifname <interface> ipv4.method shared ipv6.method ignore
    # Exemple (partager la connexion via l'interface eth0) :
    nmcli c add con-name MaConnexionPartagee type ethernet ifname eth0 ipv4.method shared ipv6.method ignore
    ```

    *Persistance : Oui*. Crée une connexion persistante de type `shared`.

* **Lister les connexions définies**
    Affiche les profils de connexion persistants configurés sur le système.

    ```bash
    nmcli connection show
    # ou forme courte
    nmcli c
    ```

    *Note :* Liste les configurations persistantes.

* **Afficher les détails d'une connexion**
    Permet de voir tous les paramètres configurés pour une connexion spécifique.

    ```bash
    nmcli connection show <nom_connexion>
    # Exemple :
    nmcli c show "Wired connection 1"
    ```

    *Note :* Affiche la configuration persistante.

* **Modifier une connexion existante**
    Permet de changer les paramètres d'une connexion existante. NetworkManager met à jour la configuration persistante correspondante.

    ```bash
    nmcli connection modify <nom_connexion> <paramètre1> <valeur1> <paramètre2> <valeur2> ...
    # Exemple (modifier la métrique IPv4 pour une connexion - voir section sur le routage) :
    nmcli c modify "Wired connection 1" ipv4.route-metric 100
    ```

    *Persistance : Oui*. Modifie la configuration persistante de la connexion.

* **Gérer les routes pour une connexion**
    Modifie les paramètres de routage associés à une connexion spécifique.
  * Ajouter une route statique (syntaxe pour IPv4 : `destination [passerelle]`) :

        ```bash
        nmcli connection modify <nom_connexion> +ipv4.routes "<destination> [<gateway>]"
        # Exemple :
        nmcli c modify "Wired connection 1" +ipv4.routes "192.168.2.0/24 192.168.1.254"
        ```

        *Persistance : Oui*.

  * Définir la passerelle par défaut (syntaxe pour IPv4) :

        ```bash
        nmcli connection modify <nom_connexion> ipv4.gateway <gateway>
        # Exemple :
        nmcli c modify "Wired connection 1" ipv4.gateway 192.168.1.1
        ```

        *Persistance : Oui*.

  * Définir la métrique (priorité) d'une route pour une connexion (plus la métrique est basse, plus la route est préférée) :

        ```bash
        nmcli connection modify <nom_connexion> ipv4.route-metric <metric>
        # Exemple :
        nmcli c modify "Wired connection 1" ipv4.route-metric 100
        ```

        *Persistance : Oui*.
  * *Il existe des options équivalentes pour IPv6 (`+ipv6.routes`, `ipv6.gateway`, `ipv6.route-metric`).*

* **Supprimer une connexion**
    Supprime un profil de connexion défini.

    ```bash
    nmcli connection delete <nom_connexion>
    # Exemple :
    nmcli c delete ConnexionCachee
    ```

    *Persistance : Oui*. Supprime la configuration persistante de la connexion.

* **Importer une configuration VPN**
    Permet d'importer un fichier de configuration VPN (.ovpn pour OpenVPN, .conf pour WireGuard) pour créer une connexion NM. Notez que les fichiers utilisés (configuration, certificats, clés) doivent être dans des répertoires accessibles par le snap network-manager, généralement sous `/var/snap/network-manager/common/` ou `/var/snap/nm-vpn-client/common/`.

    ```bash
    sudo nmcli connection import type openvpn file <chemin_fichier_ovpn>
    # Exemple (fichier .ovpn dans un répertoire accessible par le snap) :
    sudo nmcli c import type openvpn file /var/snap/network-manager/common/myopenvpn.ovpn
    # Pour WireGuard :
    # nmcli c import type WireGuard file <chemin_fichier_wg_conf> # Exemple (fichier .conf dans un répertoire accessible par le snap nm-vpn-client) :
    # nmcli c import type WireGuard file /var/snap/nm-vpn-client/common/wg.conf
    ```

    *Persistance : Oui*. Crée une nouvelle connexion persistante.

* **Utiliser l'éditeur interactif `nmcli`**
    Fournit une console interactive pour gérer et modifier les connexions.

    ```bash
    nmcli connection edit
    # ou pour un type spécifique
    nmcli connection edit type <type>
    # Exemple pour le Wi-Fi :
    nmcli c edit type wifi
    ```

    *Persistance : Oui*. Les modifications effectuées dans l'éditeur interactif sont persistantes, car elles utilisent le même mécanisme que les commandes `add`/`modify`/`delete`.

* **Surveiller l'activité de NetworkManager**
    Permet d'observer les changements d'état des connexions et des périphériques.

    ```bash
    nmcli monitor
    ```

    *Persistance : Non*. Outil de diagnostic pour afficher l'activité en temps réel.

* **Ajuster les niveaux de journalisation de NetworkManager**
    Permet de modifier les niveaux de verbosité de NetworkManager globalement ou par domaine (ex: WIFI, IP4).

    ```bash
    nmcli general logging [level <niveau> [domain <domaine>]]
    # Niveaux possibles : ERR, WARN, INFO, DEBUG
    # Exemples (journalisation détaillée pour les messages liés au Wi-Fi) :
    nmcli general logging level DEBUG domain WIFI
    # Afficher les niveaux actuels :
    nmcli general logging
    ```

    *Persistance : Non spécifié comme persistant par les sources*. Les sources indiquent que cela peut être modifié "à la volée", ce qui suggère que ces réglages ne sont pas persistants par défaut et pourraient nécessiter une configuration système supplémentaire non décrite dans les sources fournies.

En résumé, **`nmcli`** est l'outil de ligne de commande polyvalent pour gérer les configurations réseau via NetworkManager. Sur les systèmes Ubuntu récents utilisant NetworkManager et Netplan, la plupart des commandes `nmcli` pour la gestion des *connexions* (`add`, `modify`, `delete`, `wifi connect`, `hotspot`, `import`) sont automatiquement enregistrées dans les fichiers `/etc/netplan/*.yaml` et sont donc **persistantes après un redémarrage**. Les commandes affichant l'état (`device`, `connection show`, `wifi list`, `monitor`) ou contrôlant l'état physique immédiat (`radio`) ne sont pas des configurations persistantes en elles-mêmes.