#!/usr/bin/python3
"""Opens, in the default app, a file named by an abrirprojeto:// link.

Link form: abrirprojeto://abrir/<Folder>/<path inside it>
<Folder> is the name of an allowed folder, or of a folder inside one, so
the same link works on every machine. The allowed folders are listed one
per line in ~/.config/abrir-projeto/pastas.txt; without that file they are
~/Projetos and ~/Skills. Only regular, non-executable files inside them
are opened; everything else is refused.
"""
import os, sys, subprocess
from urllib.parse import urlparse, unquote

HOME = os.path.expanduser("~")
CONFIG = os.path.join(HOME, ".config", "abrir-projeto", "pastas.txt")
DEFAULT_ROOTS = [os.path.join(HOME, "Projetos"), os.path.join(HOME, "Skills")]


def allowed_roots():
    try:
        lines = open(CONFIG, encoding="utf-8").read().splitlines()
    except OSError:
        return DEFAULT_ROOTS
    roots = [os.path.expanduser(l.strip()) for l in lines if l.strip() and not l.strip().startswith("#")]
    return [r for r in roots if os.path.isabs(r)] or DEFAULT_ROOTS
BLOCKED = {".app", ".command", ".tool", ".sh", ".zsh", ".bash", ".scpt", ".scptd", ".applescript",
           ".workflow", ".action", ".pkg", ".mpkg", ".dmg", ".terminal", ".jar", ".py", ".rb", ".pl",
           ".js", ".mjs", ".exe", ".bat", ".cmd", ".ps1", ".webloc", ".inetloc", ".url", ".fileloc"}


def resolve(url):
    u = urlparse(url)
    if u.scheme != "abrirprojeto" or u.netloc != "abrir":
        return None, "link fora do formato abrirprojeto://abrir/..."
    parts = [p for p in unquote(u.path).split("/") if p]
    if not parts or any(p in (".", "..") for p in parts):
        return None, "caminho inválido"
    listed = allowed_roots()
    cands = [os.path.join(r, *parts[1:]) for r in listed if os.path.basename(r.rstrip(os.sep)) == parts[0]]
    cands += [os.path.join(r, *parts) for r in listed]
    roots = [os.path.realpath(r) for r in listed]
    for c in cands:
        real = os.path.realpath(c)
        if not os.path.isfile(real):
            continue
        if not any(real == r or real.startswith(r + os.sep) for r in roots):
            return None, "arquivo fora das pastas permitidas"
        if os.path.splitext(real)[1].lower() in BLOCKED or os.access(real, os.X_OK):
            return None, "tipo de arquivo que roda programa; não abro por link"
        return real, None
    return None, "arquivo não encontrado: " + "/".join(parts)


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else ""
    path, err = resolve(url)
    if err:
        print("RECUSADO: " + err)
        return 1
    if "--dry" in sys.argv:
        print("ABRIRIA: " + path)
        return 0
    subprocess.run(["/usr/bin/open", path], check=False)
    print("ABERTO: " + path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
