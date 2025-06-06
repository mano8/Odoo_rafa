# **Fiche d'aide : Permissions et Propriété des Fichiers**

En Linux et Unix, **tout est considéré comme un fichier**, y compris les répertoires et les périphériques. Tous les fichiers d'un système possèdent des permissions qui régissent l'accès et les actions possibles par différents types d'utilisateurs. Ces permissions, souvent appelées "bits", sont associées à la propriété du fichier. Le super utilisateur "**root**" a la capacité d'accéder à n'importe quel fichier sur le système. Pour modifier des fichiers appartenant à `root`, l'utilisation de `sudo` est nécessaire.

## **Types de Restrictions d'Accès (Permissions)**

Il existe trois types principaux de restrictions d'accès (permissions) qui définissent ce que les utilisateurs peuvent faire avec un fichier ou un répertoire.

* **Lecture** (`r` ou `4`) :
  * Sur un **fichier** : Permet d'accéder au contenu du fichier (lire un texte, visionner un média).
  * Sur un **répertoire** : Permet de lister le contenu du répertoire (`ls`), mais pas d'y accéder (sauf si la permission d'exécution est également présente).
* **Écriture** (`w` ou `2`) :
  * Sur un **fichier** : Permet de modifier le contenu du fichier. Notez que le droit d'écriture sur un *répertoire* permet de supprimer des fichiers dans ce répertoire, même si l'utilisateur n'a pas les permissions d'écriture sur le fichier lui-même.
  * Sur un **répertoire** : Permet de modifier le contenu du répertoire, d'y créer ou supprimer des fichiers ou sous-répertoires (nécessite également la permission d'exécution).
* **Exécution** (`x` ou `1`) :
  * Sur un **fichier** : Permet de lancer les scripts et applications.
  * Sur un **répertoire** : Permet de "changer" dans le répertoire (`cd`) et d'utiliser les fichiers/sous-répertoires qu'il contient. **Les répertoires doivent impérativement avoir la permission 'exécution' pour fonctionner correctement**.

Ces permissions sont souvent représentées par une série de 9 caractères (`rwxrwxrwx`) ou en notation octale (trois nombres de 0 à 7). Un tiret (`-`) indique l'absence de la permission.

### **Types de Restrictions Utilisateurs (Propriété)**

Les permissions s'appliquent à trois catégories d'utilisateurs :

* **Propriétaire** (`u` pour *user*) : L'utilisateur qui possède le fichier, généralement son créateur.
* **Groupe** (`g` pour *group*) : Le groupe d'utilisateurs qui possède le fichier. Un utilisateur membre de ce groupe peut avoir certaines permissions particulières sur le fichier.
* **Autres** (`o` pour *others*) : Tous les autres utilisateurs qui ne sont ni le propriétaire ni membre du groupe propriétaire.

L'affichage détaillé d'une liste de fichiers (`ls -l`) montre ces permissions sous la forme `-rwxr-xr-x` où le premier caractère indique le type de fichier, suivi de 3 caractères pour le propriétaire, 3 pour le groupe, et 3 pour les autres. L'utilisateur propriétaire n'est pas affecté par les restrictions définies pour son groupe ou les autres.

### **Gestion des Permissions (`chmod`)**

La commande `chmod` est utilisée pour modifier les permissions d'accès à un fichier ou un répertoire. L'utilisation de `sudo` est souvent nécessaire pour modifier les permissions de fichiers dont l'utilisateur n'est pas propriétaire. Modifier les permissions de manière incorrecte sur des fichiers importants peut causer de sérieux problèmes système.

Il existe deux méthodes principales :

* **Avec des lettres** : Utilise des codes pour les utilisateurs (`u`, `g`, `o`, `a` pour tous) et les permissions (`r`, `w`, `x`), combinés avec `+` (ajouter), `-` (enlever), ou `=` (définir).
  * Exemple : `chmod u+x fichier1` (ajoute la permission d'exécution pour le propriétaire).
  * Exemple : `chmod g-r file3` (enlève la permission de lecture pour le groupe).
  * Exemple : `chmod u=rw,go=r MonFichier` (définit rw pour le propriétaire et r pour le groupe/autres).
* **Avec des nombres (Octal)** : Représente les permissions de lecture (4), écriture (2) et exécution (1) par des nombres. On additionne ces valeurs pour chaque catégorie (propriétaire, groupe, autres) pour obtenir un nombre à trois chiffres.
  * Exemple : `chmod 755 répertoire` (propriétaire=rwx (4+2+1=7), groupe=r-x (4+1=5), autres=r-x (4+1=5)).
  * Exemple : `chmod 644 fichier` (propriétaire=rw- (4+2=6), groupe=r-- (4), autres=r--).
  * Exemple : `chmod 667 filename` (propriétaire=6, groupe=6, autres=7).

### **Modification Récursive des Permissions**

Pour modifier les permissions de plusieurs fichiers et répertoires sous un chemin donné :

* **`chmod -R`** : Applique les permissions de manière récursive à tous les fichiers et sous-répertoires. Par exemple, `sudo chmod 777 -R /chemin/du/dossier`.
* **`find` et `chmod`** : Permet une application plus sélective en combinant la commande `find` (pour localiser les fichiers/répertoires) avec `chmod`. Il est courant d'utiliser `find` pour cibler séparément les fichiers (permissions 644) et les répertoires (permissions 755).
  * Exemple (fichiers seulement) : `sudo find /path/to/someDirectory -type f -print0 | xargs -0 sudo chmod 644`.
  * Exemple (répertoires seulement) : `sudo find /path/to/someDirectory -type d -print0 | xargs -0 sudo chmod 755`.

**ATTENTION :** Les commandes récursives, surtout combinées avec `sudo`, sont extrêmement dangereuses. Une faute de frappe peut entraîner la suppression ou la modification des permissions de fichiers système critiques. Soyez très prudent !

### **Changement de Propriétaire et de Groupe**

* **`chown`** : Permet de changer le propriétaire d'un fichier ou répertoire. Il peut également changer le groupe propriétaire.
  * Exemple (changer propriétaire) : `sudo chown utilisateur_cible fichier`.
  * Exemple (changer propriétaire et groupe) : `sudo chown utilisateur_cible:groupe_cible fichier`.
  * Exemple (changer groupe seulement) : `sudo chown :groupe_cible fichier`.
  * L'option `-R` permet l'action récursivement.
* **`chgrp`** : Permet spécifiquement de changer le groupe propriétaire d'un fichier ou répertoire. C'est équivalent à utiliser `chown :groupe_cible fichier`.
  * Exemple : `sudo chgrp groupe_cible fichier`.
  * L'option `-R` permet l'action récursivement.
  * L'option `-h` change le groupe propriétaire d'un lien symbolique lui-même.

Par défaut, l'utilisation de `sudo` est requise pour changer le propriétaire ou le groupe d'un fichier.

### **Permissions par Défaut (`umask`)**

Lorsqu'un nouveau fichier ou répertoire est créé, il obtient automatiquement des permissions par défaut. Ce comportement est déterminé par un paramètre appelé le **masque utilisateur** (`umask`).

* La valeur par défaut de l'`umask` est souvent `022` dans Ubuntu.
* Cela se traduit par des permissions par défaut de `644` (`rw-r--r--`) pour les **fichiers** et `755` (`rwxr-xr-x`) pour les **répertoires**.
* L'`umask` peut être modifié pour la session courante (`umask 007`), pour un utilisateur particulier (`~/.bashrc` ou `~/.profile`), ou globalement (`/etc/profile` ou `/etc/pam.d/common-session` - déconseillé globalement).

Les systèmes de fichiers compatibles POSIX (comme ext4) gèrent les permissions directement sur le système de fichiers. Pour les systèmes de fichiers incompatibles POSIX (comme FAT/NTFS), les permissions sont émulées au moment du montage et définies par les options de montage (`mount -o`).

### **Le Sticky Bit**

Le sticky bit est une permission spéciale qui s'applique principalement aux répertoires, typiquement ceux accessibles en écriture par "autres" (comme `/tmp`).

* Lorsqu'il est activé sur un répertoire, le sticky bit **empêche les utilisateurs de supprimer ou de renommer les fichiers qu'ils ne possèdent pas personnellement** dans ce répertoire.
* Il est défini ou retiré à l'aide de `chmod` avec l'indicateur `t`:
  * Ajouter : `chmod +t <répertoire>`.
  * Retirer : `chmod -t <répertoire>`.
* Dans l'affichage détaillé de `ls -l`, la présence du sticky bit est indiquée par un `t` ou `T` à la place du bit d'exécution pour les "autres".

### **Autres Concepts Liés**

* **ACL (Access Control List)** : Une méthode pour obtenir une granularité de permissions plus fine que les permissions Unix standard. Cela nécessite l'installation du package `acl` et l'activation de l'option `acl` dans `/etc/fstab`. Les commandes `setfacl` et `getfacl` sont utilisées pour gérer les ACLs.
* **Gestion des utilisateurs et groupes** : Les commandes comme `adduser`, `addgroup`, `useradd`, `groupadd`, `userdel`, `deluser`, `usermod`, `passwd`, `groups` sont utilisées pour gérer les utilisateurs et les groupes. Elles sont fondamentales car elles définissent les utilisateurs et groupes auxquels les permissions sont attribuées. Ces commandes modifient des fichiers système critiques comme `/etc/passwd`, `/etc/shadow`, et `/etc/group`.

---

J'espère que cette fiche détaillée vous sera utile pour comprendre et gérer les permissions et la propriété des fichiers sous Linux.

Êtes-vous prêt(e) à passer à la catégorie suivante : **Gestion des Paquets** ?
