Set objShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName) & "\Check-Network-For-Server.ps1"
objShell.Run "powershell.exe -ExecutionPolicy Bypass -NoExit -File """ & scriptPath & """", 1, false