[Setup]
AppName=WeatherProgramm
AppVersion=1.0.1
DefaultDirName={localappdata}\Programs\WeatherProgramm
DefaultGroupName=WeatherProgramm
PrivilegesRequired=lowest
OutputBaseFilename=WeatherProgramm-Setup
SetupIconFile=assets\logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\WeatherProgramm.exe"; DestDir: "{app}"; DestName: "WeatherProgramm.exe"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion

[Icons]
Name: "{group}\WeatherProgramm"; Filename: "{app}\WeatherProgramm.exe"
Name: "{userdesktop}\WeatherProgramm"; Filename: "{app}\WeatherProgramm.exe"

[Run]
Filename: "{app}\WeatherProgramm.exe"; Description: "Lancer WeatherProgramm"; Flags: nowait postinstall skipifsilent