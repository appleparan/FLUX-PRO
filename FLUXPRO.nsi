;NSIS Script For FLUX PRO

;Background Colors
BGGradient 0000FF 000000 FFFFFF

;Title Of Your Application
Name "FLUX PRO"

;Do A CRC Check
CRCCheck On

;Output File Name
OutFile "FLUX PRO Setup.exe"

;The Default Installation Directory
InstallDir "$PROGRAMFILES\FLUX PRO"

;The text to prompt the user to enter a directory
DirText "Please select the folder below"


; - - - - Allow only one installer instance - - - - 
!ifdef onlyOneInstance
Function .onInit
 System::Call "kernel32::CreateMutexA(i 0, i 0, t '$(^Name)') i .r0 ?e"
 Pop $0
 StrCmp $0 0 launch
  Abort
 launch:
FunctionEnd
!endif
; - - - - Allow only one installer instance - - - - 


Section "Install"
  ;Install Files
  Call InstallVCRedist
  SetOutPath $INSTDIR
  SetCompress Auto
  SetOverwrite IfNewer
  File /r "D:\Project\FLUX PRO\dist6\distribution\dist\*"

  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FLUX PRO" "DisplayName" "FLUX PRO (remove only)"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FLUX PRO" "UninstallString" "$INSTDIR\Uninst.exe"
WriteUninstaller "Uninst.exe"
SectionEnd

Section "Shortcuts"
  ;Add Shortcuts
  CreateDirectory "$SMPROGRAMS\FLUX PRO"
  CreateShortCut "$SMPROGRAMS\FLUX PRO\FLUX PRO.lnk" "$INSTDIR\FLUX PRO.exe" "" "$INSTDIR\FLUX PRO.exe" 0
  CreateShortCut "$DESKTOP\FLUX PRO.lnk" "$INSTDIR\FLUX PRO.exe" "" "$INSTDIR\FLUX PRO.exe" 0
SectionEnd

UninstallText "This will uninstall FLUX PRO from your system"


Section Uninstall
  ;Delete Files
  Delete "$INSTDIR\*"

  ;Delete Start Menu Shortcuts
  Delete "$SMPROGRAMS\FLUX PRO\*.*"
  RmDir "$SMPROGRAMS\FLUX PRO"

  ;Delete Uninstaller And Unistall Registry Entries
  Delete "$INSTDIR\Uninst.exe"
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\FLUX PRO"
  DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\FLUX PRO"
  RMDir "$INSTDIR"
SectionEnd

Function InstallVCRedist
    Call CheckVCRedist
    Pop $R0
    StrCmp $R0 "No" 0 +3
    File "D:\Project\FLUX PRO\dist5\distribution\data\vcredist_x86.exe"
	ExecWait '"$INSTDIR\${DLLMSVC8}" /q:a /c:"VCREDI~1.EXE /q:a /c:""msiexec /i vcredist.msi /qb!"" "'  
FunctionEnd

Function CheckVCRedist
   Push $R0
   ClearErrors
   
   ; Install to the correct directory on 32 bit or 64 bit machines
   IfFileExists $WINDIR\SYSWOW64\*.* Is64bit Is32bit
   
   Is32bit:
   SetRegView 32
   StrCpy $INSTDIR "$PROGRAMFILES32\FLUX PRO"
   ReadRegDword $R0 HKLM "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{FF66E9F6-83E7-3A3E-AF14-8DE9A809A6A4}" "Version"
   GOTO End32Bitvs64BitCheck
   
   Is64bit:
   SetRegView 64
   StrCpy $INSTDIR "$PROGRAMFILES64\FLUX PRO"
   ReadRegDword $R0 HKLM "HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\{FF66E9F6-83E7-3A3E-AF14-8DE9A809A6A4}" "Version"
   
   End32Bitvs64BitCheck:

   ; if VS 2008 redist not installed, install it
   IfErrors 0 VSRedistInstalled
   StrCpy $R0 "No"

VSRedistInstalled:
   Exch $R0
FunctionEnd