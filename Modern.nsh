;Change this file to customize zip2exe generated installers with a modern interface

!include "MUI.nsh"

#!insertmacro MUI_PAGE_DIRECTORY
#!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"


; example1.nsi
;
; This script is perhaps one of the simplest NSIs you can make. All of the
; optional settings are left to their default settings. The installer simply 
; prompts the user asking them where to install, and drops a copy of example1.nsi
; there. 

;--------------------------------

; The name of the installer
Name "st7bInstaller"

; The file to write
OutFile "st7bInstaller.exe"

; The default installation directory
InstallDir $PROGRAMFILES\phot0703rewr

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------

; Pages

Page directory
Page instfiles

;--------------------------------



; The stuff to install
Section "" ;No components page, name is not important

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
SectionEnd ; end the section

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\phot0703"
  CreateShortCut "$SMPROGRAMS\phot0703\st7b.lnk" "$INSTDIR\st7b.exe" "$INSTDIR\" "$INSTDIR\st7b.exe" 0
  CreateShortCut "$SMPROGRAMS\phot0703\config.lnk" "$INSTDIR\config.cfg" "" "$INSTDIR\config.cfg" 0

SectionEnd
