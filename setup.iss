[Setup]
AppName=Sistema PDV
AppVersion=1.0
DefaultDirName={pf}\SistemaPDV
DefaultGroupName=Sistema PDV
OutputDir=output
OutputBaseFilename=InstaladorPDV
Compression=lzma
SolidCompression=yes

[Files]
; Apenas o executável - logo e database já estão embutidos no .exe pelo PyInstaller
; O banco de dados (pdv_mercado.db) será criado automaticamente em %APPDATA%\SistemaPDV\ na primeira execução
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Sistema PDV"; Filename: "{app}\main.exe"
Name: "{commondesktop}\Sistema PDV"; Filename: "{app}\main.exe"

[Run]
Filename: "{app}\main.exe"; Description: "Abrir Sistema PDV"; Flags: nowait postinstall skipifsilent
