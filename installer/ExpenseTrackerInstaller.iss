#define EnableSigning 0

[Setup]
AppName=AI-Powered Expense Tracker
AppVersion=1.0.1
AppPublisher=Amol Solase
DefaultDirName={autopf}\Expense Tracker
DefaultGroupName=Expense Tracker
OutputDir={#SourcePath}output
OutputBaseFilename=ExpenseTrackerSetup
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=lowest
Compression=lzma
SolidCompression=yes
DisableDirPage=no
DisableProgramGroupPage=no
WizardStyle=modern

#if EnableSigning
; Enable signing (requires SignTool in PATH and a valid code-signing cert)
SignTool=signtool sign /fd SHA256 /a /tr http://timestamp.digicert.com /td SHA256 $f
SignedUninstaller=yes
#endif

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Main application executable built by PyInstaller (dist folder is one level up)
Source: "{#SourcePath}..\dist\ExpenseTrackerApp.exe"; DestDir: "{app}"; Flags: ignoreversion

; Optional: include initial data folder if you want to seed with a starter DB
; (Your app creates data/expenses.db automatically if missing, so this is not required.)
; Source: "{#SourcePath}..\dist\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu shortcut
Name: "{autoprograms}\\Expense Tracker"; Filename: "{app}\\ExpenseTrackerApp.exe"
; Optional Desktop shortcut (controlled by task)
Name: "{autodesktop}\\Expense Tracker"; Filename: "{app}\\ExpenseTrackerApp.exe"; Tasks: desktopicon

[Run]
; Offer to launch after installation completes
Filename: "{app}\\ExpenseTrackerApp.exe"; Description: "Launch Expense Tracker"; Flags: nowait postinstall skipifsilent


