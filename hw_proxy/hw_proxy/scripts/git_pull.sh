
# Configuración
REPO_URL="https://github.com/mano8/Odoo_rafa.git"
BRANCH="server"
DIR="/opt/Odoo_rafa"

# Verificar si el directorio ya existe
if [ -d "$DIR" ]; then
    echo "El directorio '$DIR' ya existe. Intentando actualizar el repositorio..."
    cd "$DIR" || exit

    # Verificar si el directorio es un repositorio Git
    if [ -d ".git" ]; then
        # Intentar hacer pull
        if git pull origin "$BRANCH"; then
            echo "Repositorio actualizado correctamente."
        else
            echo "git pull falló. Forzando la actualización..."
            git fetch origin
            git reset --hard origin/"$BRANCH"
            git fetch --all
            echo "Repositorio forzado a sincronizar con origin/$BRANCH."
        fi
    else
        echo "El directorio '$DIR' no es un repositorio Git válido."
        exit 1
    fi
else
    echo "Clonando el repositorio..."
    git clone -b "$BRANCH" "$REPO_URL" "$DIR"
    cd "$DIR" || exit
    echo "Repositorio clonado correctamente."
fi
exit 0