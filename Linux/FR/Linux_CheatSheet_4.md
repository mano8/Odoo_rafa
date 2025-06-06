Absolument. Voici un aide-mémoire détaillé, structuré par catégorie, en commençant par la catégorie 9 telle que définie dans la politique Debian, enrichi par les informations de toutes les sources fournies.

**Aide-Mémoire Détaillé Linux (Sources fournies)**

Cet aide-mémoire a été compilé à partir des documents et de la conversation fournis, couvrant des aspects fondamentaux du système d'exploitation et de la gestion réseau sous Linux, avec une attention particulière à Debian et Ubuntu.

**Catégorie 9 : Le Système d'Exploitation**

Cette section se base principalement sur la section 9 du Manuel de Politique Debian v4.7.2.0, complétée par des informations pratiques issues des autres sources.

**Concepts Généraux, Hiérarchie du Système de Fichiers et Permissions**

*   Dans Linux et Unix, **tout est considéré comme un fichier** : les répertoires, les fichiers ordinaires et les périphériques (appelés nœuds).
*   Les **droits d'accès** sur les fichiers et répertoires contrôlent qui peut les consulter, les modifier ou les exécuter.
*   Le super-utilisateur **"root"** dispose de la capacité d'accéder à n'importe quel fichier sur le système.
*   Chaque fichier est associé à des restrictions d'accès via des **permissions** et des restrictions utilisateur via une **association propriétaire/groupe**.
*   Les **permissions** sont de trois types :
    *   **lecture (read)** notée `r` ou `4`.
    *   **écriture (write)** notée `w` ou `2`.
    *   **exécution (execute)** notée `x` ou `1`.
*   Les **restrictions utilisateur** s'appliquent au **propriétaire (owner)** (noté `u`), au **groupe (group)** (noté `g`), et aux **autres (other)** (noté `o` ou `a` pour tous).
*   Pour les **répertoires**, les permissions ont des actions spécifiques :
    *   **lecture** (`r` ou 4) permet de lister le contenu (commande `ls`).
    *   **écriture** (`w` ou 2) permet de créer ou supprimer des fichiers dans le répertoire (même si l'utilisateur n'a pas les droits d'écriture sur le fichier lui-même, s'il a les droits d'écriture sur le répertoire).
    *   **exécution** (`x` ou 1) permet de naviguer dans le répertoire (commande `cd`).
*   Les dossiers (répertoires) **doivent impérativement avoir la permission 'exécution'** (`x` ou 1) pour fonctionner correctement en tant que répertoires.
*   Les droits sont affichés sous la forme de 9 caractères (ex: `-rw-r--r--`), groupés par trois pour le propriétaire, le groupe et les autres. Le caractère `-` signifie que la permission est absente. Ils peuvent aussi être représentés en notation octale (de 000 à 777).
*   Le **sticky bit** (`t`) peut être appliqué aux répertoires pour empêcher les utilisateurs de supprimer ou renommer des fichiers qu'ils ne possèdent pas personnellement dans ce répertoire, même s'ils ont les droits d'écriture sur le répertoire. Il est indiqué par `t` ou `T` dans le champ d'exécution des "autres" dans la sortie de `ls -l`. On l'ajoute/supprime avec `chmod +t <répertoire>` / `chmod -t <répertoire>`.
*   Le **Setgid bit** (`g+s`) sur un répertoire permet aux fichiers et sous-répertoires créés à l'intérieur d'hériter du groupe propriétaire du répertoire, au lieu du groupe principal de l'utilisateur créateur.
*   La **hiérarchie du système de fichiers (FHS)**, version 3.0, définit l'emplacement des fichiers et répertoires sur Debian, avec certaines exceptions.
    *   Les fichiers indépendants de l'architecture doivent de préférence être dans `/usr/share`, mais une sous-arborescence de `/usr/lib` peut contenir un mélange de fichiers dépendants et indépendants.
    *   Les fichiers de configuration spécifiques à l'utilisateur sont généralement stockés dans le répertoire personnel de l'utilisateur, souvent des "fichiers dot" (commençant par '.') ou des "répertoires dot".
    *   Seuls l'éditeur de liens dynamiques et libc sont autorisés à installer des fichiers dans `/lib64`.
    *   Les fichiers objet, les binaires internes et les bibliothèques peuvent être installés dans `/lib{,32}` ou `/usr/lib{,32}`, ainsi que dans `/lib/triplet` et `/usr/lib/triplet` pour la prise en charge multiarch.
    *   Les paquets pour architectures 64 bits ne doivent pas installer de fichiers dans `/usr/lib64`.
    *   Les fichiers d'en-tête C et C++ sont accessibles via `/usr/include/` ou `/usr/include/triplet`.
    *   `/var/run` doit être un lien symbolique vers `/run`, et `/var/lock` vers `/run/lock`.
    *   Le répertoire `/var/www` est également autorisé.
    *   Les paquets ne doivent pas placer de fichiers dans `/usr/local`, mais peuvent créer des sous-répertoires vides en dessous via des scripts de maintenance (`postinst`, `prerm`), qui doivent être retirés si vides lors de la suppression du paquet. Ils ne doivent pas créer de sous-répertoires *dans* `/usr/local` lui-même, sauf ceux listés par FHS. Les permissions de `/usr/local` et ses sous-répertoires créés par paquets doivent respecter des règles spécifiques.
    *   Les paquets ne doivent pas dépendre de la présence/absence de fichiers dans `/usr/local` pour leur fonctionnement normal.
    *   Le répertoire de messagerie système est `/var/mail` ; l'utilisation de `/var/spool/mail` est obsolète.
    *   Le répertoire `/run` est effacé au démarrage ; les paquets ne doivent pas inclure de fichiers sous `/run` ou les anciens chemins `/var/run` et `/var/lock`. Les sous-répertoires nécessaires sous `/run` doivent être créés dynamiquement par les scripts init.

**Commandes Essentielles du Système de Fichiers**

*   **Obtenir de l'aide :**
    *   `man <commande>` : Affiche la page du manuel pour une commande spécifique. Tapez `q` pour quitter.
*   **Navigation dans l'arborescence :**
    *   `pwd` : Affiche le répertoire de travail courant.
    *   `cd <répertoire>` : Change de répertoire.
    *   `cd` : Revient au répertoire personnel de l'utilisateur.
    *   `cd -` : Revient au répertoire précédent.
    *   `cd ..` : Remonte au répertoire parent.
    *   `cd /` : Remonte à la racine du système de fichiers.
    *   Raccourcis utiles : `~` (répertoire personnel), `.` (répertoire courant), `..` (répertoire parent).
    *   Les chemins absolus commencent par `/`, les chemins relatifs ne commencent pas par `/`.
    *   Pour les chemins contenant des espaces, utilisez des guillemets ou des apostrophes.
*   **Gestion des fichiers et répertoires :**
    *   `ls` : Liste le contenu d'un répertoire.
        *   `-l` : Affichage détaillé.
        *   `-a` : Affiche tous les fichiers, y compris cachés.
        *   `-h` : Affiche la taille dans un format lisible (avec `-l`).
        *   `-al` : Combine `-a` et `-l`. `ll` est souvent un alias pour `ls -al`.
        *   `-1` : Liste un fichier par ligne.
    *   `mkdir <dossier>` : Crée un dossier vide.
        *   `-p` : Crée les dossiers parents si nécessaire.
    *   `rmdir <dossier>` : Supprime un dossier vide.
        *   `-p` : Supprime les dossiers parents s'ils deviennent vides.
    *   `touch <fichier>` : Crée un fichier vide ou met à jour son horodatage.
    *   `mv <source> <destination>` : Déplace ou renomme des fichiers et répertoires.
        *   `-f` : Force l'exécution (écrase sans confirmation).
        *   `-i` : Demande confirmation avant d'écraser.
    *   `cp <source> <destination>` : Copie des fichiers ou répertoires.
        *   `-r` ou `-R` : Copie récursivement (répertoires et leur contenu).
        *   `-a` : Mode archive (préserve les droits, dates, etc.).
        *   `-u` : Copie uniquement les fichiers plus récents ou inexistants.
    *   `rm <fichier>` : Supprime des fichiers. **Soyez extrêmement prudent avec cette commande**.
        *   `-f` : Ne demande pas de confirmation.
        *   `-r` : Supprime récursivement (dossiers et leur contenu).
        *   `-rf` : Suppression forcée et récursive. L'utilisation d'un chemin absolu est recommandée pour plus de sécurité.
*   **Affichage du contenu de fichiers :**
    *   `cat <fichier>` : Affiche le contenu d'un fichier texte.
        *   `-n` : Numérote les lignes.
    *   `head <fichier>` : Affiche les premières lignes (par défaut 10). `-n <nombre>` spécifie le nombre de lignes.
    *   `tail <fichier>` : Affiche les dernières lignes (par défaut 10). `-n <nombre>` spécifie le nombre de lignes. `-f` affiche le contenu en temps réel à mesure que le fichier grandit.
    *   `more <fichier>` : Affiche un fichier page par page. Tapez `q` pour quitter.
    *   `less <fichier>` : Affiche un fichier avec navigation et recherche. Tapez `:` puis `q` pour quitter.
*   **Recherche de fichiers et de contenu :**
    *   `grep <modèle> <fichier(s)>` : Cherche des lignes correspondant à un modèle dans des fichiers. Peut filtrer la sortie d'autres commandes via un pipe `|`.
        *   `-n` : Affiche les lignes trouvées avec leur numéro.
        *   `-i` : Recherche insensible à la casse.
        *   `-r` : Recherche récursive dans les sous-répertoires.
        *   `-l` : N'affiche que les noms des fichiers contenant des correspondances.
        *   `-E` : Utilise les expressions rationnelles étendues (comme `egrep`).
        *   `-v` : Inverse la correspondance (affiche les lignes NE correspondant PAS au modèle).
        *   `-B <nombre>` : Affiche le nombre de lignes *avant* la correspondance.
        *   `-A <nombre>` : Affiche le nombre de lignes *après* la correspondance.
        *   `--exclude=<modèle_fichier>` : Exclut les fichiers correspondant au modèle de la recherche.
        *   `--include=<modèle_fichier>` : Inclut seulement les fichiers correspondant au modèle.
        *   Recherche OR : `grep 'pattern1\|pattern2' filename` ou `grep -E 'pattern1|pattern2' filename`.
    *   `locate <fichier>` : Recherche rapide de fichiers en utilisant une base de données pré-indexée.
    *   `find <chemin> <critères> <action>` : Recherche récursive de fichiers ou répertoires selon divers critères (`-name`, `-iname`, `-type`, `-atime`, `-mtime`, `-user`, `-group`) et peut exécuter des actions (`-exec`, `-ok`, `-ls`) sur les résultats. Les opérateurs `-a` (ET), `-o` (OU), `!` (NOT) peuvent être utilisés.
*   **Modification des permissions (chmod) :**
    *   `chmod <mode> <fichier(s)>` : Modifie les permissions d'accès.
        *   Mode symbolique : combine les utilisateurs (`u`, `g`, `o`, `a`), les actions (`+` ajouter, `-` supprimer, `=` définir), et les permissions (`r`, `w`, `x`, `s` pour setuid/setgid). Ex: `chmod u+x file1`, `chmod go-wx monRep`.
        *   Mode numérique (octal) : trois chiffres (propriétaire, groupe, autres), chaque chiffre est la somme des valeurs des permissions (`r=4`, `w=2`, `x=1`). Ex: `chmod 644 MonFichier`, `chmod 777 file4`.
        *   `-R` : Applique les modifications récursivement aux sous-répertoires et leur contenu. **Attention : l'utilisation de `-R` avec `rm` ou `chown` peut être très dangereuse**.
        *   `sudo chmod ...` : Nécessaire pour changer les permissions de fichiers dont on n'est pas propriétaire.
*   **Modification du propriétaire et du groupe (chown, chgrp) :**
    *   `chown <nouveau_propriétaire> <fichier(s)>` : Change le propriétaire d'un fichier.
    *   `chown <nouveau_propriétaire>:<nouveau_groupe> <fichier(s)>` : Change le propriétaire ET le groupe d'un fichier.
    *   `chgrp <nouveau_groupe> <fichier(s)>` : Change le groupe propriétaire d'un fichier.
    *   `-R` : Applique les modifications récursivement.
    *   `sudo chown ...` ou `sudo chgrp ...` : Nécessaire pour changer le propriétaire/groupe de fichiers dont on n'est pas le propriétaire actuel (généralement root).

**Gestion des Utilisateurs et Groupes**

*   Les systèmes comme Ubuntu sont conçus pour être multi-utilisateurs.
*   Seul un **administrateur système** ou un utilisateur disposant des droits `sudo` peut créer ou supprimer des utilisateurs et des groupes.
*   Le compte **"root"** est désactivé par défaut dans les installations Ubuntu pour des raisons de sécurité. L'outil `sudo` est utilisé pour exécuter des tâches administratives avec des privilèges élevés.
*   `sudo` permet à un utilisateur autorisé (membre du groupe `sudo` par défaut) d'exécuter une commande en tant qu'un autre utilisateur (par défaut root) en utilisant son propre mot de passe.
*   Pour activer le compte `root`, il faut lui attribuer un mot de passe avec `sudo passwd`. Pour désactiver son mot de passe, utilisez `sudo passwd -l root`.
*   **Classes d'UID (identifiant utilisateur) et GID (identifiant groupe) dans Debian Policy :**
    *   **0-99** : IDs alloués globalement par le projet Debian, identiques sur tous les systèmes Debian. Pour les paquets nécessitant un ID statique.
    *   **100-999** : Utilisateurs et groupes système alloués dynamiquement. Utilisés par les paquets qui créent des utilisateurs ou groupes via `adduser --system`. Les nouveaux noms d'utilisateur créés par les mainteneurs devraient commencer par un underscore `_` pour éviter les conflits locaux.
    *   **1000-59999** : Comptes utilisateur alloués dynamiquement par `adduser` par défaut.
    *   **60000-64999** : IDs alloués globalement par Debian, mais créés seulement à la demande sur les systèmes utilisateur (pour paquets spécifiques ou nécessitant de nombreux IDs statiques).
    *   **65000-65533** : Réservés.
    *   **65534** : Utilisateur `nobody` et groupe `nogroup`.
    *   **65535** : Ne doit **pas** être utilisé (valeur sentinelle d'erreur 16 bits).
    *   **Autres valeurs spécifiques** (4294967294, 4294967295) ne doivent pas non plus être utilisées pour diverses raisons.
*   Les paquets autres que `base-passwd` ne doivent pas modifier directement les fichiers systèmes comme `/etc/passwd`, `/etc/shadow`, `/etc/group`, `/etc/gshadow`.
*   Le répertoire personnel canonique pour les utilisateurs sans répertoire personnel est `/nonexistent`.
*   **Commandes de gestion des utilisateurs et groupes :**
    *   Lister les utilisateurs : `compgen -u` ou `cut -d: -f1 /etc/passwd`.
    *   Lister les groupes : `compgen -g` ou `cut -d: -f1 /etc/group`.
    *   `adduser <identifiant>` : Crée un compte utilisateur de manière interactive, crée un groupe du même nom par défaut, et copie les fichiers du répertoire squelette `/etc/skel` dans le nouveau répertoire personnel. Pose une série de questions sur les informations de l'utilisateur.
        *   `--disabled-login` : Crée un utilisateur qui ne peut pas se connecter tant qu'un mot de passe n'est pas défini.
        *   `--disabled-password` : Crée un utilisateur sans mot de passe direct, mais qui peut se connecter via authentification par clé SSH.
        *   `--system` : Crée un utilisateur système.
        *   `--home <répertoire>` : Définit le répertoire personnel.
        *   `--no-create-home` : Ne crée pas de répertoire personnel.
        *   `--ingroup <groupe>` : Ajoute l'utilisateur au groupe spécifié.
        *   `--uid <uid>` : Spécifie l'UID de l'utilisateur.
    *   `deluser <identifiant>` : Supprime un compte utilisateur et son groupe principal par défaut. Ne supprime pas le répertoire personnel sauf si l'option `--remove-home` est utilisée.
    *   `addgroup <nom_groupe>` : Crée un groupe. Peut être interactif.
    *   `delgroup <nom_groupe>` : Supprime un groupe.
    *   `adduser <identifiant> <nom_groupe>` : Ajoute un utilisateur existant à un groupe.
    *   `usermod <options> <identifiant>` : Modifie les paramètres d'un compte utilisateur.
        *   `-G <groupe1>[,<groupe2>...]` : Définit les groupes supplémentaires (utiliser avec `-a` pour ajouter sans supprimer les groupes existants).
        *   `-aG <groupe1>[,<groupe2>...]` : Ajoute l'utilisateur aux groupes spécifiés sans le retirer des autres groupes.
        *   `-g <groupe_primaire>` : Définit le groupe primaire de l'utilisateur.
        *   `-l <nouveau_login>` : Change l'identifiant (login) de l'utilisateur.
        *   `-d <nouveau_répertoire_home>` : Change le répertoire personnel. Utilisez `-m` avec `-d` pour déplacer le contenu de l'ancien répertoire personnel vers le nouveau.
        *   `--expiredate <date>` : Définit une date d'expiration pour le compte. Utiliser `--expiredate 1` pour verrouiller temporairement un compte, et `--expiredate ""` pour le réactiver.
    *   `groupmod --new-name <nouveau_nom> <nom_actuel>` : Modifie le nom d'un groupe.
    *   `passwd <identifiant>` : Modifie le mot de passe d'un utilisateur. Si aucun identifiant n'est spécifié, modifie le mot de passe de l'utilisateur courant.
        *   `-l <identifiant>` : Verrouille le mot de passe d'un utilisateur.
        *   `-u <identifiant>` : Déverrouille le mot de passe d'un utilisateur.
        *   `-e <identifiant>` : Force l'utilisateur à changer de mot de passe à sa prochaine connexion.
        *   `-S <identifiant>` : Affiche l'état du compte et du mot de passe.
    *   `groups <identifiant>` : Affiche les groupes auxquels appartient un utilisateur (ou l'utilisateur courant si aucun spécifié).
    *   `id <identifiant>` : Affiche les informations UID, GID et groupes pour un utilisateur (ou l'utilisateur courant).
*   **Sécurité des Profils Utilisateur :**
    *   Le répertoire personnel par défaut est créé à partir de `/etc/skel`.
    *   Les permissions par défaut des répertoires personnels peuvent permettre aux "autres" de lire/exécuter. Il est recommandé de les restreindre (ex: `0750`) en utilisant `sudo chmod 0750 /home/<utilisateur>` ou en modifiant `DIR_MODE` dans `/etc/adduser.conf` pour les nouveaux utilisateurs.
*   **Politique de Mot de Passe :**
    *   Une politique de mot de passe forte (longueur minimum, expiration) est cruciale pour la sécurité.
    *   La longueur minimum et les vérifications d'entropie sont configurées dans `/etc/pam.d/common-password`. La valeur par défaut est 6 caractères minimum.
    *   L'état du compte et du mot de passe (date du dernier changement, expiration, etc.) peut être affiché avec `sudo chage -l <utilisateur>`.
    *   La commande `chage <utilisateur>` permet de définir interactivement ou via options (`-E` expiration, `-m` minimum age, `-M` maximum age, `-I` inactivité, `-W` avertissement) ces valeurs.
*   **Autres Considérations de Sécurité (Utilisateurs) :**
    *   Désactiver ou verrouiller le mot de passe d'un utilisateur **ne l'empêche pas** de se connecter via SSH si l'authentification par clé publique est configurée (clés dans `/home/<utilisateur>/.ssh/authorized_keys`). Pour bloquer cet accès, supprimer ou renommer le répertoire `.ssh/`.
    *   Vérifiez les sessions actives de l'utilisateur désactivé (`who | grep <utilisateur>`) et tuez les processus si nécessaire (`sudo pkill -f <terminal>`).
    *   Vous pouvez restreindre l'accès SSH à des groupes spécifiques en modifiant le fichier `/etc/ssh/sshd_config` et en ajoutant la directive `AllowGroups <groupe(s)>`. Redémarrez le service SSH (`sudo systemctl restart ssh.service`) après modification.

**Gestion des Services Système**

*   Le système d'initialisation et gestionnaire de services par défaut dans Debian et Ubuntu récents est **systemd**.
*   Les paquets qui fournissent des services système doivent inclure des **unités de service systemd** (fichiers `.service`). Le nom de l'unité correspond généralement au nom du paquet.
*   Les paquets peuvent également inclure des **scripts init** dans `/etc/init.d` pour les systèmes init alternatifs. Si un script init porte le même nom qu'une unité systemd, systemd l'ignorera au profit de l'unité.
*   Les scripts init dans `/etc/init.d` doivent supporter des arguments standard tels que `start`, `stop`, `restart`, `try-restart`, `reload`, `force-reload`, `status`.
*   `start`, `stop`, `restart`, `force-reload` sont requis. `status` est recommandé.
*   Les scripts doivent gérer correctement les cas où le service est déjà démarré ou arrêté (ne pas démarrer plusieurs instances, ne pas échouer) et ne pas tuer des processus utilisateur portant un nom similaire. L'utilisation de `start-stop-daemon --oknodo` est recommandée.
*   Évitez d'utiliser `set -e` dans les scripts init.
*   Les scripts dans `/etc/init.d` doivent être considérés comme des **fichiers de configuration** et gérés comme tels lors des mises à jour de paquets. Ils persistent si le paquet est désinstallé sans l'option `--purge`. Un test en début de script est recommandé pour sortir proprement si le programme n'est pas installé.
*   Les valeurs configurables par l'administrateur devraient être stockées dans un fichier séparé dans `/etc/default/` (nommé comme le script init) et sourcé par le script, plutôt que directement dans le script principal. Ce fichier doit être au format `sh` POSIX et géré comme fichier de configuration.
*   Le script init doit définir des valeurs par défaut pour ses variables si le fichier `/etc/default/` n'existe pas ou ne définit pas ces variables.
*   Les fichiers et répertoires temporaires sous `/run` doivent être créés dynamiquement par les scripts init car ils ne sont pas persistants au redémarrage.
*   Les scripts de maintenance des paquets doivent utiliser les outils `update-rc.d` et `invoke-rc.d` pour interagir avec le gestionnaire de services. Ne pas manipuler directement les liens `/etc/rcn.d` ou appeler directement les scripts dans `/etc/init.d`.
    *   `update-rc.d` est utilisé pour gérer les liens de démarrage/arrêt dans les runlevels (`/etc/rcn.d`).
        *   Pour activer l'autodémarrage par défaut : `update-rc.d package defaults` dans `postinst`. Dans `postrm`, `if [ "$1" = purge ]; then update-rc.d package remove fi`.
        *   Pour désactiver l'autodémarrage par défaut : `update-rc.d package defaults-disabled` dans `postinst` (nécessite `init-system-helpers >= 1.50`). L'administrateur peut activer avec `update-rc.d package enable`.
    *   `invoke-rc.d` est utilisé pour exécuter les actions des services (`start`, `stop`, etc.) en respectant les contraintes locales. Syntaxe courante dans les scripts de maintenance : `invoke-rc.d package action`. Le service doit être enregistré avec `update-rc.d` avant d'être appelé par `invoke-rc.d`.
*   Il est recommandé d'utiliser les outils `debhelper` (`dh_installinit`, `dh_installsystemd`) qui gèrent automatiquement les appels à `update-rc.d` et `invoke-rc.d`.
*   **Commandes systemd :**
    *   `systemctl start <service>` : Lance un service.
    *   `systemctl stop <service>` : Arrête un service.
    *   `systemctl enable <service>` : Active le démarrage automatique d'un service au boot.
    *   `systemctl disable <service>` : Désactive le démarrage automatique d'un service.
    *   `systemctl status <service>` : Affiche l'état d'un service.

**Variables d'Environnement**

*   Les programmes installés dans les répertoires listés dans le PATH (`/bin`, `/usr/bin`, `/sbin`, `/usr/sbin`, etc.) ne doivent pas dépendre de réglages de variables d'environnement personnalisées pour leurs valeurs par défaut.
*   Si un programme dépend de variables d'environnement, il doit soit avoir une configuration par défaut raisonnable en leur absence, soit être exécuté via un **script wrapper** qui définit ces variables si elles ne le sont pas déjà.
*   Les variables d'environnement système peuvent être définies dans des fichiers tels que ceux dans `/etc/profile.d/` ou `/etc/environment`.
*   Le fichier `/etc/environment` est lu à la connexion de l'utilisateur via `pam_env.so`. Les changements nécessitent une déconnexion/reconnexion pour être pris en compte par toutes les sessions.
*   Pour éditer `/etc/environment` en tant que root, il est recommandé d'utiliser `sudo -H nano /etc/environment`.
*   **Commandes liées aux variables d'environnement :**
    *   `printenv` : Affiche toutes les variables d'environnement définies.
    *   `printenv <variable>` : Affiche la valeur d'une variable spécifique.
    *   `echo $<variable>` : Affiche la valeur d'une variable spécifique.
    *   Le signe `$` est utilisé pour obtenir la valeur d'une variable. Ex: `ls $HOME/Desktop`.

**Gestion des Cron Jobs**

*   Les paquets ne doivent pas modifier directement les fichiers `/etc/crontab` ou ceux dans `/var/spool/cron/crontabs`.
*   Les tâches planifiées via cron par les paquets doivent être placées dans des scripts exécutables dans les répertoires suivants, en fonction de la fréquence :
    *   `/etc/cron.hourly` : Exécuté chaque heure.
    *   `/etc/cron.daily` : Exécuté chaque jour.
    *   `/etc/cron.weekly` : Exécuté chaque semaine.
    *   `/etc/cron.monthly` : Exécuté chaque mois.
*   Ces scripts doivent être traités comme des fichiers de configuration.
*   Pour des fréquences ou heures spécifiques non couvertes par les répertoires ci-dessus, un paquet peut installer un fichier dans `/etc/cron.d`. Ce fichier utilise la même syntaxe que `/etc/crontab` et est traité automatiquement par `cron`. Les entrées dans `/etc/cron.d` ne sont pas gérées par `anacron`.
*   Les fichiers dans `/etc/cron.d` et `/etc/crontab` ont sept champs : Minute, Hour, Day of the month, Month of the year, Day of the week, Username, Command.
*   Les scripts ou entrées crontab doivent vérifier si les programmes nécessaires sont installés avant de tenter de les exécuter.
*   Les noms de fichiers pour les jobs cron doivent normalement correspondre au nom du paquet. Les noms ne doivent pas inclure les caractères `.` ou `+` (utiliser `_` à la place).

**Menus**

*   Les applications destinées aux environnements de bureau peuvent s'enregistrer dans le menu en utilisant les **fichiers desktop entry** (standard FreeDesktop).
*   Ces fichiers sont installés dans `/usr/share/applications` et les menus sont mis à jour par des `dpkg triggers`.
*   Les entrées de menu doivent utiliser des icônes (PNG ou SVG, minimum 22x22, préférablement jusqu'à 64x64) avec fond transparent, idéalement installées dans les répertoires `hicolor`.
*   Si une application n'est pas destinée à être lancée seule depuis le menu, son fichier desktop entry doit inclure `NoDisplay=true`.
*   Si un paquet installe un fichier desktop entry FreeDesktop, il ne doit pas installer en plus une entrée dans le système de menu spécifique à Debian (legacy).

**Gestionnaires Multimédia**

*   Les **types de média** (MIME types, ex: `image/png`, `text/html`) sont utilisés pour identifier le format des fichiers et flux de données.
*   L'enregistrement des gestionnaires de types de média permet aux applications (clients mail, navigateurs) d'ouvrir ou de manipuler ces types.
*   Il existe deux systèmes principaux : **mailcap** (ancien) et **FreeDesktop** (pour les environnements de bureau). Dans Debian, les entrées FreeDesktop sont automatiquement traduites en entrées mailcap.
*   **Enregistrement via desktop entries :** Les paquets peuvent lister les types de média gérés dans la clé `MimeType` du fichier desktop entry de l'application. Pour les schémas URI (liens), utiliser les types `x-scheme-handler/*`.
*   **Enregistrement via mailcap :** Les paquets n'utilisant pas de desktop entries peuvent installer un fichier au format `mailcap(5)` dans le répertoire `/usr/lib/mime/packages/`. Le nom du fichier doit être le nom du paquet binaire.
*   Le paquet `mailcap` fournit l'outil `update-mime` qui intègre ces enregistrements dans `/etc/mailcap` via des `dpkg triggers`. L'appel manuel du trigger peut être nécessaire depuis les scripts de maintenance.
*   Les paquets utilisant les desktop entries ne doivent pas installer d'entrées mailcap séparément.
*   **Fournir des types de média aux fichiers :** Le type de média d'un fichier peut être découvert par son extension ou son modèle "magic" (`magic(5)`). Ces associations sont stockées dans des bases de données.
*   Les nouvelles associations peuvent être enregistrées auprès de l'IANA ou déclarées au système **Shared MIME Info** en installant un fichier XML dans `/usr/share/mime/packages`.

**Configuration Clavier**

*   Certaines touches doivent avoir des interprétations standardisées sur tous les programmes : `<--` pour supprimer le caractère à gauche, `Delete` pour supprimer le caractère à droite, `Control+H` comme préfixe d'aide Emacs.
*   Cette interprétation doit être cohérente quel que soit le terminal utilisé (console virtuelle, émulateur X, session distante).
*   `<--` génère `KB_BackSpace` en X, `Delete` génère `KB_Delete` en X. Les translations X (`xrdb`) mappent `KB_BackSpace` à ASCII DEL et `KB_Delete` à `ESC [ 3 ~`.
*   La console Linux est configurée pour mapper `<--` à DEL et `Delete` à `ESC [ 3 ~`.
*   Les applications X sont configurées pour que `<--` supprime à gauche et `Delete` à droite.
*   Les terminaux devraient avoir `stty erase ^?`. L'entrée `terminfo` pour `xterm` doit avoir `ESC [ 3 ~` pour `kdch1`.
*   Emacs mappe `KB_BackSpace` ou le caractère `stty erase` à `delete-backward-char`, et `KB_Delete` ou `kdch1` à `delete-forward-char`.

**Enregistrement des Documents (doc-base)**

*   Le paquet `doc-base` gère la documentation en ligne.
*   Les paquets fournissant de la documentation peuvent l'enregistrer auprès de `doc-base` en installant un fichier de contrôle dans `/usr/share/doc-base/`.

**Signalement qu'un Redémarrage est Nécessaire**

*   Les programmes peuvent signaler qu'un redémarrage est requis en créant (touchant) le fichier `/run/reboot-required`.
*   Il est courant d'ajouter le nom du ou des paquets nécessitant le redémarrage au fichier `/run/reboot-required.pkgs`. Les paquets ne doivent pas ajouter leur nom s'il est déjà présent.
*   Ce mécanisme est généralement déclenché par le script de maintenance `postinst` du paquet à la fin d'une installation ou mise à jour réussie.
*   Il n'y a aucune garantie sur le moment ou la réalisation effective du redémarrage demandé.

**Catégorie : Réseau**

Cette section couvre les aspects réseau importants du système, avec des détails de configuration et des commandes pratiques issus de diverses sources.

**Interfaces Réseau**

*   Les interfaces Ethernet sont identifiées par le système. Les noms peuvent être **prévisibles** (ex: `eno1`, `enp0s25`) ou suivre l'ancien style **kernel** (ex: `eth0`).
*   **Commandes d'identification des interfaces :**
    *   `ifconfig -a` : Liste toutes les interfaces réseau disponibles.
    *   `ip a` (ou `ip addr show`) : Affiche les adresses IP et l'état de toutes les interfaces. `ip addr show dev <interface>` pour une interface spécifique.
    *   `ip link show` : Affiche l'état des interfaces. `ip link show dev <interface>` pour une interface spécifique.
    *   `lshw -class network` : Fournit des détails sur les interfaces réseau (nom logique, adresse MAC, pilote, capacités). Nécessite `sudo`.
*   **Configuration des noms logiques (pour les interfaces prévisibles) :**
    *   Sur les versions récentes d'Ubuntu Server, Netplan gère les noms logiques via le fichier de configuration Netplan (`/etc/netplan/*.yaml`). Utiliser les clés `match` et `set-name`.
    *   Sur Ubuntu 16.04, la configuration se faisait via `/etc/udev/rules.d/70-persistent-net.rules` en modifiant la valeur `NAME=ethX` basée sur l'adresse MAC, nécessitant un redémarrage.
*   **Paramètres d'interface (ethtool) :**
    *   `ethtool` : Programme pour afficher et modifier les paramètres de la carte Ethernet (vitesse, duplex, auto-négociation, Wake-on-LAN). Installer avec `sudo apt install ethtool`.
    *   Afficher les paramètres : `sudo ethtool <interface>`.
    *   Modifier les paramètres (temporaire) : `sudo ethtool -s <interface> speed <vitesse> duplex <mode>`.
*   **Adresse MAC :** Peut être trouvée avec `sudo ip addr` ou `ifconfig`. C'est un identifiant unique.

**Adressage IP**

*   **Adressage temporaire :** Utilisé pour des configurations non persistantes (perdues au redémarrage).
    *   Assigner une IP : `sudo ifconfig <interface> <adresse_ip> netmask <masque>` (ancienne méthode) ou `sudo ip addr add <adresse_ip>/<CIDR> dev <interface>`.
    *   Définir la passerelle par défaut : `sudo route add default gw <adresse_passerelle> <interface>` (ancienne méthode) ou `sudo ip route add default via <adresse_passerelle>`.
    *   Mettre une interface `up` ou `down` : `ip link set dev <interface> up` ou `ip link set dev <interface> down`.
    *   Supprimer toute configuration IP temporaire d'une interface : `ip addr flush <interface>`.
*   **Adressage dynamique (client DHCP) :** Obtient automatiquement l'adresse IP, le masque, la passerelle et les serveurs DNS du réseau.
    *   Avec Netplan (Ubuntu Server récent) : Ajouter `dhcp4: true` sous l'interface dans `/etc/netplan/*.yaml`. Appliquer avec `sudo netplan apply`.
    *   Avec `/etc/network/interfaces` (Ubuntu 16.04) : Ajouter `iface <interface> inet dhcp` dans le fichier. Activer/désactiver manuellement avec `sudo ifup <interface>` / `sudo ifdown <interface>`.
*   **Adressage statique :** Nécessite de définir manuellement l'adresse IP, le masque, la passerelle et les serveurs DNS.
    *   Avec Netplan (Ubuntu Server récent) : Ajouter l'interface et le bloc `addresses` avec l'IP/CIDR dans `/etc/netplan/*.yaml`. Définir la passerelle dans le bloc `routes` et les serveurs DNS dans `nameservers`. Appliquer avec `sudo netplan apply`. Pour Ubuntu 18.04 LTS, utiliser `gateway4:` au lieu du bloc `routes:` pour la passerelle par défaut.
    *   Avec `/etc/network/interfaces` (Ubuntu 16.04) : Ajouter l'interface avec `inet static`, `address`, `netmask`, `gateway`.
*   **Interface loopback (lo) :** Identifiée par `lo`, adresse IP par défaut `127.0.0.1`. Utilisée pour la communication inter-processus sur la machine locale. Visualisable avec `ifconfig lo` ou `ip address show lo`.
*   **Adresses IP secondaires :** Plusieurs adresses IP peuvent être assignées à une seule interface. Utiles pour la séparation de services, la connectivité additionnelle, l'isolation. Avec Netplan, ajouter les adresses à la liste `addresses` sous l'interface.

**Résolution de Noms**

*   Le système mappe les noms d'hôtes aux adresses IP.
*   **Configuration du client DNS :**
    *   Le fichier de configuration est `/etc/resolv.conf`. Il s'agit généralement d'un lien symbolique géré par un service (comme `systemd-resolved` sur Ubuntu Server récent ou `resolvconf` sur Ubuntu 16.04).
    *   Modifier `/etc/resolv.conf` directement n'est pas recommandé car les changements peuvent être écrasés.
    *   Avec Netplan (Ubuntu Server récent) : Configurer les serveurs DNS dans le bloc `nameservers` sous l'interface dans le fichier `/etc/netplan/*.yaml`. L'option `search` définit les domaines de recherche.
    *   Avec `/etc/network/interfaces` (Ubuntu 16.04) : Configurer les serveurs DNS et les domaines de recherche avec `dns-nameservers` et `dns-search` sous l'interface.
*   **Noms d'hôtes statiques :** Définis localement dans le fichier `/etc/hosts`. Ces entrées ont par défaut priorité sur le DNS. Utile pour un nombre limité de ressources ou sans accès externe.
*   **Name Service Switch (NSS) :** L'ordre de résolution des noms est contrôlé par `/etc/nsswitch.conf`. La ligne `hosts:` définit l'ordre (ex: `files dns mdns4_minimal mdns4`). `files` fait référence à `/etc/hosts`, `dns` au DNS unicast, `mdns4_minimal`/`mdns4` au Multicast DNS.

**NetworkManager**

*   Service système qui gère les périphériques réseau et les connexions, cherchant à maintenir la connectivité. Gère Ethernet, Wi-Fi, mobile broadband, PPPoE, et offre une intégration VPN.
*   Sur Ubuntu Desktop, NetworkManager est généralement installé par défaut.
*   Sur Ubuntu Core, NetworkManager peut prendre le contrôle de la gestion réseau par défaut (qui est normalement gérée par `systemd-networkd` et Netplan) en se définissant comme renderer dans Netplan. Ce comportement est contrôlé par l'option `defaultrenderer` du snap.
*   Supporte les connexions Wi-Fi, WAN, Ethernet, la création de points d'accès Wi-Fi, les connexions partagées et les connexions VPN.
*   Le support VPN est modulaire, nécessitant l'installation de plugins (ex: `network-manager-openvpn`, `network-manager-wireguard`). Pour l'intégration graphique, les paquets correspondants `*-gnome` sont nécessaires. NetworkManager supporte OpenVPN et WireGuard.
*   **Configuration et gestion des connexions :** Les configurations de connexion sont stockées en fichiers ( `.ini` dans les anciennes versions, `.yaml` avec Netplan dans les récentes). Sur Ubuntu (23.10+), NetworkManager utilise Netplan pour les configurations, stockées dans `/etc/netplan/`.
*   **Outils de contrôle :**
    *   `nmcli` : Outil en ligne de commande pour interagir avec NetworkManager.
        *   `nmcli d` : Affiche l'état des périphériques.
        *   `nmcli c show` : Liste les connexions configurées.
        *   `nmcli r wifi on/off` : Active/désactive la radio Wi-Fi.
        *   `nmcli d wifi list` : Liste les réseaux Wi-Fi disponibles.
        *   `nmcli d wifi connect <essid> password <mot_de_passe>` : Connecte à un réseau Wi-Fi et crée la connexion implicitement. Le mot de passe doit avoir entre 8-63 caractères ou 64 hexadécimaux.
        *   `nmcli c add type wifi con-name <nom> ifname <interface> ssid <ssid>` : Crée une nouvelle connexion Wi-Fi (utile pour les réseaux cachés). `nmcli c modify <nom> wifi-sec.psk <mot_de_passe>` pour ajouter le mot de passe.
        *   `nmcli c up <nom>` : Active une connexion configurée.
        *   `nmcli d wifi hotspot ifname <interface_wifi> ssid <ssid> password <mot_de_passe>` : Crée un point d'accès Wi-Fi.
        *   `nmcli c add con-name <nom> type ethernet ifname <interface> ipv4.method shared` : Crée une connexion partagée.
        *   `nmcli connection edit [type <type>]` : Ouvre l'éditeur interactif de `nmcli` pour créer/modifier une connexion.
        *   `nmcli general logging [level <niveau> [domain <domaine>]]` : Modifie les niveaux de log (ERR, WARN, INFO, DEBUG) pour NetworkManager.
        *   `nmcli monitor` : Surveille l'activité de NetworkManager.
    *   `nmtui` : Interface textuelle interactive (curses) pour contrôler NetworkManager. Permet de naviguer, éditer et activer des connexions.
*   **Configuration VPN avec NetworkManager :**
    *   Nécessite les plugins VPN installés.
    *   Importer un fichier de configuration (ex: `.ovpn`, `.wg.conf`) : `sudo nmcli c import type openvpn file <chemin/fichier.ovpn>` ou `nmcli c import type WireGuard file <chemin/fichier.conf>`. Les fichiers source doivent être dans un répertoire accessible par le snap network-manager sur Ubuntu Core (ex: `/var/snap/network-manager/common/creds`).
    *   Créer/modifier manuellement via `nmcli c add` ou `nmcli c modify` en spécifiant les paramètres VPN (`vpn.data` pour OpenVPN).

**Connexion WiFi (Exemples de Commandes)**

*   **Découvrir les réseaux :**
    *   `iwconfig` : Affiche l'état des interfaces sans fil.
    *   `iwlist <interface> scan` : Scanne et liste les points d'accès disponibles avec des détails (ESSID, signal, etc.). Ex: `sudo iwlist wlp3s0 scan`.
    *   `sudo iwlist <interface> scan | grep ESSID` : Affiche uniquement les ESSID (noms de réseau).
*   **Connexion via nmcli :**
    *   `nmcli d wifi connect <essid> password <mot_de_passe>`.
*   **Connexion via nmtui :**
    *   Exécuter `nmtui`. Sélectionner "Activate a connection", choisir le réseau, entrer le mot de passe.
*   **Connexion via wpa_supplicant :**
    *   Installer : `sudo apt install wpasupplicant`.
    *   Créer ou modifier le fichier de configuration `/etc/wpa_supplicant.conf`.
    *   Générer l'entrée : `wpa_passphrase <essid> <mot_de_passe> | sudo tee /etc/wpa_supplicant.conf`.
    *   Connecter le supplicant à l'interface : `sudo wpa_supplicant -c /etc/wpa_supplicant.conf -i <interface_wifi>`.
    *   Obtenir une adresse IP (DHCP) : `sudo dhclient <interface_wifi>`.

**Pare-feu**

*   Le pare-feu Linux est basé sur le sous-système **Netfilter** du noyau. `iptables` est l'outil traditionnel pour le configurer.
*   **ufw (uncomplicated firewall)** est l'outil par défaut sur Ubuntu, fournissant une interface simplifiée pour `iptables`.
*   **Commandes de base ufw :**
    *   `sudo ufw enable` : Active le pare-feu. Par défaut, bloque tout le trafic entrant sauf explicitement autorisé.
    *   `sudo ufw disable` : Désactive le pare-feu.
    *   `sudo ufw status` : Affiche l'état du pare-feu. `sudo ufw status verbose` pour plus de détails. `sudo ufw status numbered` pour afficher les règles avec des numéros.
    *   `sudo ufw allow <port>` : Autorise le trafic entrant sur un port (ex: `sudo ufw allow 22` pour SSH). Peut utiliser le nom du service (ex: `sudo ufw allow ssh`).
    *   `sudo ufw deny <port>` : Bloque le trafic entrant sur un port.
    *   `sudo ufw delete <règle>` : Supprime une règle. `sudo ufw delete <numéro_règle>` supprime par numéro.
    *   `sudo ufw allow from <adresse_ip>` : Autorise tout trafic entrant depuis une IP. `sudo ufw deny from <adresse_ip>` bloque tout trafic entrant depuis une IP.
    *   Spécifier un sous-réseau : Utiliser la notation CIDR (ex: `192.168.0.0/24`).
    *   `sudo ufw allow in on <interface> from <adresse_ip>` : Autorise le trafic entrant depuis une IP sur une interface spécifique.
    *   `sudo ufw deny out <port>` : Bloque le trafic SORTANT sur un port (ex: `sudo ufw deny out 25` pour SMTP sortant).
    *   Règles plus complexes : `sudo ufw allow proto <protocole> from <source> to <destination> port <port(s)>` (ex: `sudo ufw allow proto tcp from any to any port 80,443`).
    *   `--dry-run` : Affiche les règles résultantes sans les appliquer.
*   **Profils d'application ufw :** Les applications peuvent définir des profils préconfigurés dans `/etc/ufw/applications.d`.
    *   `sudo ufw app list` : Liste les profils disponibles (ex: `OpenSSH`, `Nginx Full`, `Apache Full`).
    *   `sudo ufw allow <NomProfil>` : Active un profil. Utiliser des guillemets si le nom contient des espaces.
    *   `sudo ufw deny <NomProfil>` ou `sudo ufw delete allow <NomProfil>` : Désactive un profil.
    *   `sudo ufw app info <NomProfil>` : Affiche les détails d'un profil (ports, protocoles).
    *   Restreindre un profil à une source : `sudo ufw allow from <source> to any app <NomProfil>`.
*   **Masquerade IP :** Permet aux machines d'un réseau interne (IPs privées) d'accéder à l'extérieur via la machine faisant office de passerelle, en utilisant l'adresse IP de cette passerelle.
    *   Avec ufw : Nécessite d'activer le forwarding IP (`DEFAULT_FORWARD_POLICY="ACCEPT"` dans `/etc/default/ufw` et `net.ipv4.ip_forward=1` dans `/etc/ufw/sysctl.conf`). Ajouter des règles NAT dans `/etc/ufw/before.rules` (ex: `-A POSTROUTING -s 192.168.0.0/24 -o eth0 -j MASQUERADE` sous la section `*nat`). Appliquer les changements avec `sudo ufw disable && sudo ufw enable`.
    *   Avec iptables : Activer le forwarding IP (`net.ipv4.ip_forward=1` dans `/etc/sysctl.conf`, appliqué avec `sudo sysctl -p`). Ajouter une règle NAT POSTROUTING (ex: `sudo iptables -t nat -A POSTROUTING -s 192.168.0.0/16 -o ppp0 -j MASQUERADE`). Des règles `FORWARD` peuvent être nécessaires si la politique par défaut est restrictive. Pour rendre persistant, ajouter les commandes dans `/etc/rc.local`.
*   **Logs du pare-feu :** Utiles pour le debugging et la surveillance.
    *   Activer les logs dans ufw : `sudo ufw logging on`. Désactiver : `sudo ufw logging off`.
    *   Activer les logs dans iptables : Ajouter la cible `LOG` aux règles. Les logs apparaissent dans `dmesg`, `/var/log/messages`, `/var/log/syslog`, `/var/log/kern.log`.

**Tables de Routage**

*   La table de routage est gérée par le noyau et indique comment le trafic doit être dirigé vers différentes destinations réseau.
*   Plusieurs outils peuvent modifier la table de routage, y compris `ip`, `route`, le client DHCP et NetworkManager.
*   La métrique (`metric`) indique le coût pour atteindre une destination ; une métrique plus faible indique une route préférée. NetworkManager attribue des métriques par défaut (Ethernet < Wi-Fi < WWAN).
*   **Visualiser les tables de routage :**
    *   `route -n` (ancienne méthode).
    *   `ip route show` ou simplement `ip route`.
*   **Modifier les tables de routage :**
    *   Via `ip route add <destination> via <gateway> dev <interface>` ou `ip route delete <destination> via <gateway>`.
    *   Via `nmcli` pour les connexions gérées par NetworkManager, en utilisant les options `ipv4.gateway`, `ipv4.routes`, `ipv4.route-metric` (et ipv6 équivalents). Ex: `nmcli connection modify <nom> +ipv4.routes <destination> ipv4.gateway <gateway>`. `nmcli connection modify <nom> ipv4.route-metric <metric>`. Ces changements s'appliquent lorsque la connexion est active.

J'espère que cet aide-mémoire détaillé vous sera utile !