# **Configuration Réseau**

La gestion du réseau est essentielle sur un système Linux, qu'il s'agisse d'un serveur ou d'un poste de travail. Elle implique de configurer les interfaces réseau, l'adressage IP, la résolution de noms et la sécurité du trafic. Plusieurs outils en ligne de commande sont disponibles pour ces tâches, et les sources fournissent des informations détaillées sur beaucoup d'entre eux.

Voici un aperçu des concepts et commandes clés liés à la configuration réseau, basés sur les sources fournies :

## **Concepts Fondamentaux de la Configuration Réseau**

Le système Linux identifie les interfaces réseau à l'aide de noms logiques. Historiquement, les interfaces Ethernet étaient nommées `ethX` (où X est un chiffre, `eth0` étant la première). Dans les systèmes plus modernes, des noms d'interfaces réseau prévisibles peuvent être utilisés, tels que `eno1` ou `enp0s25`, bien que le style de nommage `eth#` puisse encore être rencontré dans certains cas.

La configuration réseau sur les distributions basées sur Debian/Ubuntu peut être gérée de différentes manières, soit via des fichiers de configuration textuels traditionnels comme `/etc/network/interfaces`, soit, dans les versions plus récentes d'Ubuntu Server, via Netplan, qui utilise des fichiers de configuration YAML (`/etc/netplan/`). Netplan est une abstraction de configuration de haut niveau qui rend la configuration réseau indépendante de la distribution.

### **Identification des Interfaces Réseau**

Avant de configurer le réseau, il est nécessaire d'identifier les interfaces disponibles.

* **`ifconfig`** : Une commande traditionnelle pour afficher les interfaces réseau. L'option `-a` permet de lister toutes les interfaces Ethernet disponibles. Par exemple, `ifconfig -a | grep eth` peut lister les interfaces `ethX`. Bien que toujours présente, `ifconfig` est considérée comme dépréciée au profit de la commande `ip`.
* **`ip a`** ou **`ip address show`** : La commande moderne pour afficher les informations d'adresse IP et les propriétés des interfaces. `ip a` affiche les informations pour toutes les adresses.
* **`lshw -class network`** : Cette commande permet d'identifier les interfaces réseau et fournit des détails matériels, le pilote et les fonctionnalités prises en charge.

Pour les interfaces sans fil (WiFi), la commande **`iwconfig`** est similaire à `ifconfig` mais spécifiquement pour gérer les interfaces sans fil. Elle permet de vérifier si la carte WiFi est détectée.

### **Configuration de l'Adressage IP**

L'attribution d'adresses IP peut être temporaire (perdue après un redémarrage) ou persistante (conservée après redémarrage).

* **Configuration temporaire** :
  * Avec **`ifconfig`** : Permet de configurer une adresse IP et un masque de sous-réseau. Par exemple, `sudo ifconfig eth0 10.0.0.100 netmask 255.255.255.0`. Pour vérifier la configuration, on peut utiliser `ifconfig eth0`.
  * Avec **`route`** : Utilisé pour configurer une passerelle par défaut. Par exemple, `sudo route add default gw 10.0.0.1 eth0`. La commande `route -n` permet de vérifier la configuration de la passerelle par défaut.
  * Avec **`ip`** : La commande moderne pour la configuration temporaire. Pour configurer une adresse IP, utilisez `sudo ip addr add 10.102.66.200/24 dev enp0s25`. Pour vérifier, utilisez `ip address show dev enp0s25`. Pour configurer une passerelle par défaut, utilisez `sudo ip route add default via 10.102.66.1`. La vérification se fait avec `ip route show default`.
  * Le fichier `/etc/resolv.conf` peut être modifié temporairement pour ajouter des adresses de serveurs DNS, bien que cela ne soit généralement pas recommandé en configuration persistante.
  * Pour supprimer toutes les configurations IP d'une interface temporairement, utilisez `ip addr flush <interface>`.

* **Configuration persistante (DHCP)** :
  * Avec `/etc/network/interfaces` (systèmes plus anciens) : Ajoutez la méthode `dhcp` pour l'interface appropriée dans le fichier `/etc/network/interfaces`. Exemple : `auto eth0` suivi de `iface eth0 inet dhcp`. L'interface peut être activée manuellement avec `sudo ifup eth0`, ce qui lance le processus DHCP via `dhclient`. Désactiver se fait avec `sudo ifdown eth0`.
  * Avec Netplan (systèmes modernes) : Créez ou modifiez un fichier de configuration YAML dans `/etc/netplan/`. Ajoutez `dhcp4: true` sous la définition de l'interface. Exemple : un fichier comme `/etc/netplan/99_config.yaml` peut contenir la configuration pour une interface comme `enp3s0`. Appliquez les changements avec `sudo netplan apply`.

* **Configuration persistante (Statique)** :
  * Avec `/etc/network/interfaces` (systèmes plus anciens) : Ajoutez la méthode `static` pour l'interface. Spécifiez `address`, `netmask` et `gateway`. Exemple : `auto eth0`, `iface eth0 inet static`, puis `address 10.0.0.100`, `netmask 255.255.255.0`, `gateway 10.0.0.1`. Activez avec `sudo ifup eth0` et désactivez avec `sudo ifdown eth0`.
  * Avec Netplan (systèmes modernes) : Créez ou modifiez un fichier Netplan YAML. Spécifiez `addresses`, `routes` et `nameservers`. Exemple : définissez `eth0` avec `addresses: - 10.10.10.2/24`, `routes: - to: default via: 10.10.10.1`, `nameservers: {search: [mydomain], addresses: [10.10.10.1]}`. Appliquez avec `sudo netplan apply`.
  * **Interfaces Loopback** : L'interface de boucle locale (`lo`) est identifiée par défaut avec l'adresse IP 127.0.0.1. Elle est généralement configurée automatiquement via `/etc/network/interfaces` avec les lignes `auto lo` et `iface lo inet loopback`. Elle peut être visualisée avec `ifconfig lo` ou `ip address show lo`.

* **Configuration de plusieurs adresses IP ou interfaces** : Il est possible de configurer plusieurs adresses IP sur une seule interface ou d'utiliser plusieurs interfaces physiques. Netplan permet de spécifier plusieurs adresses sous le champ `addresses` d'une interface. L'utilisation d'adresses secondaires sur une seule interface désactive le support DHCP pour cette interface.

### **Résolution de Noms**

La résolution de noms est le processus de mappage des noms d'hôtes aux adresses IP.

* **Configuration de client DNS** :
  * Traditionnellement géré par `/etc/resolv.conf`. Dans les systèmes modernes, ce fichier est souvent un lien symbolique vers un fichier géré par `resolvconf` ou `systemd-resolved`.
  * La configuration DNS persistante se fait en ajoutant les adresses des serveurs de noms (`dns-nameservers`) et éventuellement les listes de recherche de suffixes DNS (`dns-search`) dans le fichier `/etc/network/interfaces` ou dans le fichier Netplan YAML.
  * Lorsque plusieurs domaines de recherche sont spécifiés, le système interroge le DNS pour les Noms de Domaine Complètement Qualifiés (FQDN) en ajoutant les suffixes dans l'ordre indiqué.

* **Noms d'hôtes statiques** : Les mappages nom d'hôte-à-IP définis localement se trouvent dans le fichier `/etc/hosts`. Les entrées de `/etc/hosts` ont priorité sur le DNS par défaut. Le fichier peut contenir des alias pour les serveurs locaux.

* **Configuration du Service de Changement de Nom (NSS)** : L'ordre de résolution des noms d'hôtes (par exemple, vérifier d'abord `/etc/hosts` puis le DNS) est contrôlé par le fichier `/etc/nsswitch.conf`. La ligne `hosts:` définit cet ordre.

### **Configuration des Réseaux Sans Fil (WiFi)**

La connexion au WiFi depuis la ligne de commande sur Debian et les distributions basées sur Debian peut se faire de trois manières principales : en utilisant `nmcli`, `nmtui`, et `wpa_supplicant`. D'autres commandes comme `iwconfig`, `iwlist` et `dhclient` sont également utilisées.

* **Découvrir les réseaux** :
  * Utilisez `iwconfig` pour vérifier votre carte WiFi.
  * Utilisez **`iwlist <interface> scan`** pour scanner les réseaux disponibles et obtenir des informations comme l'ESSID (nom du réseau), la qualité du signal, le canal, etc.. Vous pouvez filtrer l'affichage pour ne montrer que les ESSID en utilisant `| grep ESSID`.
* **Se connecter** :
  * Avec **`nmcli`** : C'est une interface en ligne de commande pour NetworkManager. La syntaxe pour se connecter est `nmcli d wifi connect <essid> password <mot_de_passe>`.
  * Avec **`nmtui`** : C'est une interface interactive en mode texte (curses-based). Il suffit de lancer la commande `nmtui`, de choisir "Activate a connection", de sélectionner le point d'accès et de saisir le mot de passe.
  * Avec **`wpa_supplicant`** : Ce n'est pas installé par défaut. Il permet de gérer le processus d'authentification pour les réseaux sans fil. Vous devez éditer le fichier `/etc/wpa_supplicant.conf` pour ajouter l'ESSID et le mot de passe. La commande `wpa_passphrase <essid> <mot_de_passe> | sudo tee /etc/wpa_supplicant.conf` peut être utilisée pour générer et enregistrer la configuration. Ensuite, connectez-vous en exécutant `sudo wpa_supplicant -c /etc/wpa_supplicant.conf -i <interface>`. Après cela, utilisez **`dhclient <interface>`** pour obtenir une adresse IP dynamique.

### **Autres Configurations Réseau**

* **`ethtool`** : Permet d'afficher et de changer les paramètres d'une carte Ethernet tels que l'auto-négociation, la vitesse du port, le mode duplex, etc.. Les modifications faites avec `ethtool` sont temporaires, sauf si ajoutées à la configuration d'interface (ex: ligne `pre-up` dans `/etc/network/interfaces`).
* **Pont réseau (Bridging)** : Utile pour filtrer le trafic entre segments réseau ou permettre aux machines virtuelles d'accéder au réseau extérieur. Cela implique d'installer le paquet `bridge-utils` et de configurer le pont via `/etc/network/interfaces` ou Netplan. La commande `brctl` fournit des informations sur l'état du pont.

La configuration réseau est un vaste domaine, et les outils et méthodes disponibles peuvent varier légèrement en fonction de la distribution et de la version du système. Les sources fournies couvrent de manière assez exhaustive les commandes et fichiers de configuration courants sur les systèmes basés sur Debian/Ubuntu.
