; Compile using Inno Setup 6:
; ISCC /DBuildRoot="C:\path\to\deployed-launcher" /DOutputRoot="C:\path\to\artifacts" tools\windows-installer.iss
#ifndef BuildRoot
  #error BuildRoot must point to the deployed launcher directory (including Qt and runtime DLLs).
#endif
#ifndef OutputRoot
  #define OutputRoot "..\dist\downloads"
#endif

[Setup]
AppId=io.github.Chekpoinss.SharpnessLauncher
AppName=Sharpness Launcher
AppVersion=12.0.0-preview.1
AppPublisher=Chekpoinss
AppPublisherURL=https://github.com/Chekpoinss/SharpnessLauncher
AppSupportURL=https://github.com/Chekpoinss/SharpnessLauncher/issues
DefaultDirName={localappdata}\Programs\SharpnessLauncher
DefaultGroupName=Sharpness Launcher
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#OutputRoot}
OutputBaseFilename=SharpnessLauncher-Windows-x64-Setup
SetupIconFile=..\program_info\sharpnesslauncher.ico
UninstallDisplayIcon={app}\sharpnesslauncher.exe
LicenseFile=..\LICENSE
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#BuildRoot}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Sharpness Launcher"; Filename: "{app}\sharpnesslauncher.exe"
Name: "{autodesktop}\Sharpness Launcher"; Filename: "{app}\sharpnesslauncher.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\sharpnesslauncher.exe"; Description: "{cm:LaunchProgram,Sharpness Launcher}"; Flags: nowait postinstall skipifsilent
