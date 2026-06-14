[Setup]
AppName=WeatherProgramm
AppVersion=1.0.0
DefaultDirName={autopf}\WeatherProgramm
DefaultGroupName=WeatherProgramm
OutputBaseFilename=WeatherProgramm-Setup
SetupIconFile=assets\logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "dist\WeatherProgramm.exe"; DestDir: "{app}"; DestName: "WeatherProgramm.exe"; Flags: ignoreversion
Source: ".env.example"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\WeatherProgramm"; Filename: "{app}\WeatherProgramm.exe"
Name: "{commondesktop}\WeatherProgramm"; Filename: "{app}\WeatherProgramm.exe"

[Run]
Filename: "{app}\WeatherProgramm.exe"; Description: "Lancer WeatherProgramm"; Flags: nowait postinstall skipifsilent