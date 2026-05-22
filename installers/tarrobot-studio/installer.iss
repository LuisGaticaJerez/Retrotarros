; ─────────────────────────────────────────────────────────────────────
; TarroBot Studio - Inno Setup installer
; Construye TarroBot-Studio-Setup-v1.2.exe
;
; Requiere Inno Setup 6+ instalado:
;   https://jrsoftware.org/isinfo.php  (gratis, ~5 MB)
;
; Compilar manual:
;   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
;
; O via build-package.ps1 que detecta ISCC automatico.
; ─────────────────────────────────────────────────────────────────────

#define MyAppName "TarroBot Studio"
#define MyAppVersion "1.2.1"
#define MyAppPublisher "Retrotarros - Luis Gatica Jerez"
#define MyAppURL "https://github.com/LuisGaticaJerez/Retrotarros"
#define MyAppExeName "TarroBot.bat"
#define MyAppMutex "TarroBotStudioMutex_1.2"

[Setup]
AppId={{A91F3D6B-7E2C-4E8F-9D2A-7C8F1B3D4E5F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\TarroBot Studio
DefaultGroupName=TarroBot Studio
DisableProgramGroupPage=yes
DisableDirPage=no
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
OutputDir=dist
OutputBaseFilename=TarroBot-Studio-Setup-v{#MyAppVersion}
Compression=lzma2/ultra
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=110
SetupIconFile=
UninstallDisplayIcon={app}\TarroBot.bat
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
AppMutex={#MyAppMutex}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: checkedonce
Name: "runinstall"; Description: "Ejecutar install.bat al terminar (instala Python, dependencias, ffmpeg, FluidSynth)"; GroupDescription: "Postinstalacion:"; Flags: checkedonce

[Files]
; ───────── Scripts Python ─────────
Source: "..\..\scripts\tarrobot.py";              DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\..\scripts\tarrobot-live.py";         DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\..\scripts\tarrobot-tray.py";         DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\..\scripts\obs_controller.py";        DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\..\scripts\sync-tarrobot-to-drive.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion

; ───────── Templates HTML ─────────
Source: "..\..\studio\_template-tarrobot-live.html";    DestDir: "{app}\studio"; Flags: ignoreversion
Source: "..\..\studio\_template-tarrobot-control.html"; DestDir: "{app}\studio"; Flags: ignoreversion

; ───────── Config editables ─────────
Source: "..\..\studio\obs-aliases.json";       DestDir: "{app}\studio"; Flags: ignoreversion onlyifdoesntexist
Source: "..\..\studio\tarrobot-recetas.json";  DestDir: "{app}\studio"; Flags: ignoreversion onlyifdoesntexist

; ───────── Base de datos ─────────
Source: "..\..\data\tarrobot-database.json";   DestDir: "{app}\data"; Flags: ignoreversion onlyifdoesntexist

; ───────── Pautas + MP3s + Melodias (opcional via componente Full) ─────────
Source: "..\..\studio\pautas\*.tarrobot.json";     DestDir: "{app}\studio\pautas";       Flags: ignoreversion skipifsourcedoesntexist; Components: full
Source: "..\..\studio\pautas\audio\*";             DestDir: "{app}\studio\pautas\audio"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist; Components: full
Source: "..\..\studio\melodias\*.mid";             DestDir: "{app}\studio\melodias";     Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist; Components: full
Source: "..\..\studio\melodias\*.midi";            DestDir: "{app}\studio\melodias";     Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist; Components: full
Source: "..\..\studio\melodias\soundfont.sf2";     DestDir: "{app}\studio\melodias";     Flags: ignoreversion skipifsourcedoesntexist; Components: full

; ───────── FluidSynth bundle (si esta local) ─────────
Source: "bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion skipifsourcedoesntexist

; ───────── Launchers + installer interno ─────────
Source: "install.bat";          DestDir: "{app}"; Flags: ignoreversion
Source: "TarroBot.bat";         DestDir: "{app}"; Flags: ignoreversion
Source: "TarroBot-debug.bat";   DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt";     DestDir: "{app}"; Flags: ignoreversion
Source: "README-ESTUDIO.txt";   DestDir: "{app}"; Flags: ignoreversion isreadme

[Dirs]
; Asegurar que estos dirs existen para que TarroBot escriba sin permission denied
Name: "{app}\studio\exports"; Flags: uninsneveruninstall
Name: "{app}\studio\shorts";  Flags: uninsneveruninstall
Name: "{app}\studio\out";     Flags: uninsneveruninstall

[Components]
Name: "core"; Description: "TarroBot Studio (scripts, templates, DB) - REQUERIDO"; Types: full slim custom; Flags: fixed
Name: "full"; Description: "Pautas + MP3s + melodias + soundfont (incluye contenido del canal)"; Types: full

[Types]
Name: "full"; Description: "Instalacion completa (autocontenida, ~35 MB)"
Name: "slim"; Description: "Instalacion minima (3 MB - leera contenido desde Drive sincronizado)"
Name: "custom"; Description: "Personalizada"; Flags: iscustom

[Icons]
Name: "{group}\TarroBot Studio"; Filename: "{app}\TarroBot.bat"; WorkingDir: "{app}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 13
Name: "{group}\TarroBot Debug (con logs)"; Filename: "{app}\TarroBot-debug.bat"; WorkingDir: "{app}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 23
Name: "{group}\Carpeta del programa"; Filename: "{app}"
Name: "{group}\Manual TarroBot (README)"; Filename: "{app}\README-ESTUDIO.txt"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\TarroBot Studio"; Filename: "{app}\TarroBot.bat"; WorkingDir: "{app}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 13; Tasks: desktopicon

[Run]
; Ejecutar install.bat al terminar (descarga deps, configura API key, etc)
Filename: "{app}\install.bat"; Description: "Ejecutar configuracion inicial (Python, deps, ffmpeg, FluidSynth, API key)"; Flags: postinstall shellexec waituntilterminated; Tasks: runinstall

[UninstallRun]
; No corremos nada especial al desinstalar (Python y deps son del usuario, los dejamos)

[UninstallDelete]
; Limpiar caches/outputs generados
Type: filesandordirs; Name: "{app}\.venv"
Type: filesandordirs; Name: "{app}\studio\out"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\scripts\__pycache__"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  // Hook para pasos custom si se necesita en el futuro
end;
