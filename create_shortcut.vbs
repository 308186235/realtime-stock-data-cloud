Set WshShell = WScript.CreateObject("WScript.Shell")
Set oShellLink = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") & "\AI-Stock-System.lnk")
oShellLink.TargetPath = "e:\交易8\start_tunnel.bat"
oShellLink.WorkingDirectory = "e:\交易8"
oShellLink.Description = "AI Stock Trading System - One Click Start"
oShellLink.IconLocation = "shell32.dll,137"
oShellLink.WindowStyle = 1
oShellLink.Save

WScript.Echo "Desktop shortcut created successfully!"
WScript.Echo "Shortcut name: AI-Stock-System"
WScript.Echo "Double click to start the system"
