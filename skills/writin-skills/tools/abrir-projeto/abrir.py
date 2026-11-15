#!/usr/bin/python3
"""Opens, in the default app, a file named by an abrirprojeto:// link.

Link form: abrirprojeto://abrir/<Folder>/<path inside it>
<Folder> is a folder inside Projetos (or the Skills folder), so the same
link works on every machine. Only regular, non-executable files inside
the allowed roots are opened; everything else is refused.
"""
import os, sys, subprocess
from urllib.parse import urlparse, unquote

HOME = os.path.expanduser("~")
ROOTS = [os.path.join(HOME, "Projetos"), os.path.join(HOME, "Skills")]
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
    cands = [os.path.join(HOME, "Projetos", *parts)]
    if parts[0] == "Skills":
        cands.append(os.path.join(HOME, *parts))
    roots = [os.path.realpath(r) for r in ROOTS]
    for c in cands:
        real = os.path.realpath(c)
        if not os.path.isfile(real):
            continue
        if not any(real == r or real.startswith(r + os.sep) for r in roots):
            return None, "arquivo fora das pastas Projetos e Skills"
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
