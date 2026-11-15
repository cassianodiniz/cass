#!/bin/bash
# Builds ~/Applications/AbrirProjeto.app, which handles abrirprojeto:// links.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
APP="$HOME/Applications/AbrirProjeto.app"
TMP="$(mktemp -d)"
cat > "$TMP/main.applescript" <<'AS'
on open location theURL
	set scriptPath to POSIX path of (path to resource "abrir.py")
	try
		set out to do shell script "/usr/bin/python3 " & quoted form of scriptPath & " " & quoted form of theURL
	on error errMsg
		display notification errMsg with title "Abrir arquivo do projeto"
	end try
end open location
on run
	display notification "Este aplicativo só abre arquivos pelos links abrirprojeto://" with title "Abrir arquivo do projeto"
end run
AS
mkdir -p "$HOME/Applications"
if [ -e "$APP" ]; then mv "$APP" "$TMP/antigo.app"; fi
/usr/bin/osacompile -o "$APP" "$TMP/main.applescript"
cp "$HERE/abrir.py" "$APP/Contents/Resources/abrir.py"
PL="$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string com.cassiano.abrir-projeto" "$PL" 2>/dev/null || /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier com.cassiano.abrir-projeto" "$PL"
/usr/libexec/PlistBuddy -c "Add :LSUIElement bool true" "$PL" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes array" "$PL"
/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0 dict" "$PL"
/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0:CFBundleURLName string Abrir arquivo do projeto" "$PL"
/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes array" "$PL"
/usr/libexec/PlistBuddy -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes:0 string abrirprojeto" "$PL"
/usr/bin/codesign --force --deep -s - "$APP" >/dev/null 2>&1 || true
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP"
echo "instalado: $APP"
