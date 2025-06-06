# **Fiche d'aide : Gestion des Fichiers et Répertoires**

Cette catégorie regroupe les commandes essentielles pour naviguer dans l'arborescence du système de fichiers, créer, copier, déplacer, renommer, supprimer des fichiers et des dossiers (ou répertoires).

En Linux, tout est considéré comme un fichier, y compris les répertoires et les périphériques. Les commandes présentées ici permettent d'interagir avec ces éléments depuis la ligne de commande.

## **ls**

Action : **lister** le contenu d'un dossier (répertoire).

Options principales :

* **-l** : Permet un affichage détaillé listant les permissions d'accès, le nombre de liens physiques, le nom du propriétaire et du groupe, la taille en octets et l'horodatage.
* **-a** : Permet l'affichage des fichiers et répertoires cachés (ceux qui commencent par un point `.`).
* **-h** : Associé à `-l`, affiche la taille des fichiers avec un suffixe correspondant à l'unité (K, M, G) pour une meilleure lisibilité.
* **-lct** : Permet de trier les fichiers et répertoires par date de modification décroissante.
* **-1** : Liste un fichier par ligne. Utile avec `wc -l` pour compter les fichiers.

Exemples :

* Afficher le contenu détaillé du répertoire `Documents/` :

    ```bash
    ls -l Documents/
    ```

* Afficher tous les fichiers et répertoires (y compris cachés) du répertoire courant :

    ```bash
    ls -a
    ```

* Afficher les fichiers cachés avec les détails :

    ```bash
    ls -al
    ```

* Afficher le contenu du répertoire `/etc/` :

    ```bash
    ls /etc/
    ```

* Compter le nombre de fichiers dans le répertoire courant :

    ```bash
    ls -1 | wc -l
    ```

Notes :

* La commande `dir` est quasi identique à `ls` avec les mêmes options, mais l'affichage par défaut diffère (pas de couleur par défaut, caractères spéciaux échappés).

### **cd**

Action : se déplacer dans l'arborescence des répertoires.

Exemples :

* Se déplacer dans le répertoire `/var/log/` :

    ```bash
    cd /var/log/
    ```

* Revenir au répertoire personnel de l'utilisateur :

    ```bash
    cd
    # ou
    cd ~
    ```

* Remonter au répertoire parent :

    ```bash
    cd ..
    ```

* Remonter à la racine du système de fichiers :

    ```bash
    cd /
    ```

* Revenir au répertoire précédent :

    ```bash
    cd -
    ```

* Se placer dans un répertoire relatif :

    ```bash
    cd usr/bin
    ```

Notes :

* Les caractères spéciaux `~`, `.`, et `..` correspondent respectivement au répertoire personnel, au répertoire courant et au répertoire parent, et peuvent simplifier l'expression des chemins.

### **pwd**

Action : afficher le répertoire de travail courant (le chemin complet où vous vous trouvez).

Exemple :

* Afficher le répertoire courant :

    ```bash
    pwd
    ```

### **mv**

Action : **déplacer** ou **renommer** des fichiers et des répertoires. Le comportement (déplacer ou renommer) dépend si la destination est un répertoire existant ou un nouveau nom.

Options principales :

* **-f** : Force l'exécution, écrase les fichiers de destination sans confirmation.
* **-i** : Demande confirmation avant d'écraser.
* **-u** : N'écrase pas le fichier de destination si celui-ci est plus récent.

Exemples :

* Renommer un fichier `test.html` en `essai.html` dans le répertoire courant :

    ```bash
    mv test.html essai.html
    ```

* Déplacer un fichier `monFichier` dans le répertoire `unRep/` :

    ```bash
    mv monFichier unRep/
    ```

* Déplacer un fichier `monFichier` du répertoire `unRep/` vers le répertoire courant :

    ```bash
    mv unRep/monFichier .
    ```

* Renommer un répertoire `unRep` en `monRep` :

    ```bash
    mv unRep monRep
    ```

Notes :

* Si la destination `file2` dans `mv file1 file2` est un répertoire existant, `file1` est déplacé *dans* ce répertoire.
* Si un chemin comporte un espace, il faut encadrer la totalité du chemin avec des guillemets ou des apostrophes.

### **cp**

Action : **copier** des fichiers ou des répertoires.

Options principales :

* **-r** : Copie récursivement, y compris les sous-répertoires et leur contenu. **Essentiel pour copier des répertoires.**
* **-a** : Mode archive. Copie en conservant les droits, dates, propriétaires, groupes, etc.. Utile pour la sauvegarde.
* **-i** : Demande une confirmation avant d'écraser un fichier existant.
* **-f** : Si le fichier de destination existe et ne peut être ouvert, le détruire et essayer à nouveau.
* **-u** : Ne copie que les fichiers plus récents ou qui n'existent pas dans la destination.
* **-v** : Permet de suivre les copies réalisées en temps réel (mode verbeux).

Exemples :

* Copier un fichier `fichier1.html` dans le répertoire `rep2/` :

    ```bash
    cp fichier1.html rep2/.
    ```

* Copier un répertoire `monRep/` et son contenu vers `ailleurs/` :

    ```bash
    cp -r monRep/ ailleurs/
    ```

* Copier plusieurs fichiers spécifiques d'un répertoire `monRep` vers `ailleurs/` :

    ```bash
    cp monRep/{*.cpp,*.h,MakeFile,Session.vim} ailleurs/
    ```

### **rm**

Action : **supprimer** des fichiers ou des répertoires.

Options principales :

* **-f** : Force l'exécution, ne demande pas de confirmation avant d'effacer.
* **-r** : Efface récursivement. Permet de supprimer un répertoire et tout ce qu'il contient. **Essentiel pour supprimer des répertoires non vides.**
* **-i** : Demande confirmation avant d'effacer.

Exemples :

* Supprimer un fichier `fichier.html` sans confirmation :

    ```bash
    rm -f fichier.html
    ```

* Supprimer un fichier `CeFichier` dans le répertoire courant :

    ```bash
    rm CeFichier
    ```

* Supprimer un répertoire `LeRep` et tout son contenu sans confirmation :

    ```bash
    rm -rf /tmp/LeRep
    ```

Notes :

* Cette commande est considérée comme très dangereuse, surtout avec les options `-r` et `-f` combinées.
* Soyez extrêmement prudent lorsque vous utilisez `rm -rf`, en particulier avec des chemins contenant des espaces ou la racine `/`.
* Pour supprimer un fichier dont vous n'avez pas la propriété, vous devez utiliser `sudo` :

    ```bash
    sudo rm -rf nom_fichier
    ```

* Il est fortement recommandé d'utiliser le chemin absolu du fichier ou répertoire à supprimer avec `sudo rm -rf` pour éviter les erreurs coûteuses.

### **mkdir**

Action : **créer** un ou plusieurs répertoires (dossiers).

Option principale :

* **-p** : Crée les répertoires parents s'ils n'existent pas.

Exemples :

* Créer un répertoire nommé `photos` :

    ```bash
    mkdir photos
    ```

* Créer une arborescence de répertoires, en s'assurant que les parents sont créés si nécessaire :

    ```bash
    mkdir -p photos/2005/noel
    ```

### **rmdir**

Action : **supprimer** un ou plusieurs répertoires, mais **seulement s'ils sont vides**.

Option principale :

* **-p** : Supprime les répertoires parents s'ils deviennent vides après la suppression du répertoire enfant.

Exemples :

* Supprimer un répertoire vide nommé `LeRep` :

    ```bash
    rmdir LeRep
    ```

* Supprimer une arborescence de répertoires vides, supprimant les parents s'ils deviennent vides :

    ```bash
    rmdir -p test/essai
    ```

### **touch**

Action : **créer** des fichiers vides s'ils n'existent pas, ou **mettre à jour l'horodatage** (date et heure de dernière modification/accès) d'un fichier existant.

Exemples :

* Créer un fichier vide nommé `file1` :

    ```bash
    touch file1
    ```

* Mettre à jour l'horodatage de `file1` :

    ```bash
    touch file1
    ```

### **ln**

Action : Crée un **lien** vers un fichier ou un répertoire. Deux types de liens sont couramment utilisés : les liens physiques (hard links) et les liens symboliques (soft/symbolic links).

Options principales :

* **-s** : Crée un **lien symbolique** (similaire à un raccourci dans d'autres systèmes d'exploitation). Le lien symbolique pointe vers le nom du fichier source. Si le fichier source est supprimé, le lien symbolique ne fonctionnera plus.
* **-f** : Force l'écrasement du fichier de destination s'il existe.
* **-d** : Permet à l'utilisateur `root` (ou via `sudo`) de créer un lien physique sur un répertoire. (Attention, les liens physiques vers les répertoires sont généralement déconseillés).

Exemples :

* Créer un lien symbolique nommé `MonLien` pointant vers `Rep1/Rep2/Monfichier` :

    ```bash
    ln -s Rep1/Rep2/Monfichier MonLien
    # ou en utilisant un chemin source absolu
    ln -s /chemin/absolu/vers/source_file link
    ```

* Créer un lien physique nommé `AutreNom` pour `Monfichier` dans le répertoire `unRep/` :

    ```bash
    ln Monfichier unRep/AutreNom
    ```

Notes :

* Par défaut (sans l'option `-s`), `ln` crée un lien physique.
* Assurez-vous de vous trouver dans le répertoire où vous souhaitez créer le lien, ou spécifiez le chemin complet pour le lien.

### **file**

Action : Permet d'identifier le **type de fichier**. Il utilise des tests sur le contenu du fichier (les "magic tests") ainsi que son extension pour déterminer son type MIME, par exemple.

Exemple :

* Afficher le type de chaque fichier dans le répertoire `dossier/` :

    ```bash
    file dossier/*
    ```

### Création et Écriture de Fichiers (méthodes simples)

En plus des éditeurs de texte comme `nano` ou `vim`, il existe des moyens simples pour créer ou modifier le contenu d'un fichier directement depuis la ligne de commande.

* **cat > fichier** : Place l'entrée standard dans le fichier. Si le fichier existe, son contenu est écrasé. Pour terminer la saisie, pressez `Ctrl+D`.

    ```bash
    cat > nouveau_fichier.txt
    # Saisissez votre texte ici
    # ...
    # Appuyez sur Ctrl+D pour enregistrer et quitter
    ```

* **echo "texte" > fichier** : Crée un fichier avec le `texte` spécifié comme contenu, ou remplace le contenu d'un fichier existant.

    ```bash
    echo "Voici la première ligne." > mon_fichier.txt
    ```

* **echo "texte" >> fichier** : Ajoute le `texte` spécifié à la fin d'un fichier existant. Si le fichier n'existe pas, il est créé.

    ```bash
    echo "Ceci est une ligne supplémentaire." >> mon_fichier.txt
    ```

* **tee** : Lit l'entrée standard et l'écrit à la fois sur la sortie standard et dans un fichier. Utilisé avec `>` écrase le fichier, avec `>>` ajoute au fichier. Peut être utilisé avec `sudo` via un tube (`|`) pour écrire dans des fichiers systèmes. Le marqueur `EOF` peut être utilisé pour entrer plusieurs lignes de texte.

    ```bash
    # Écraser un fichier (avec sudo)
    echo "contenu important" | sudo tee /chemin/vers/fichier_systeme > /dev/null # > /dev/null pour ne pas afficher le contenu sur la sortie standard
    # Ajouter à un fichier (avec sudo et multi-lignes)
    sudo tee -a /chemin/vers/autre_fichier_systeme << EOF
    Ligne 1
    Ligne 2
    EOF
    # N'oubliez pas de taper 'EOF' manuellement à la fin.
    ```

### Ouvrir un répertoire dans le gestionnaire de fichiers graphique

* **xdg-open .** : Ouvre le répertoire courant dans le gestionnaire de fichiers graphique par défaut (par exemple, Nautilus sous GNOME). Utile pour passer rapidement de la ligne de commande à l'interface graphique.
