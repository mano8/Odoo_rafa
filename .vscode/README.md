# Tips

## Remote dev

Fix: Fully restart the VS Code server

- Exit VS Code completely (on your host machine).
- SSH in again (if remote).
- Then stop the VS Code server:

```bash
pkill -u zepos node
```

or, more aggressively:

```bash
rm -rf ~/.vscode-server
```