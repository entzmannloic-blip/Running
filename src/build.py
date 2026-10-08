# -*- coding: utf-8 -*-
"""Build unique : python src/build.py [--check]

Copie src/ dans le dossier de travail, lance gen.py puis assemble.py, valide
la syntaxe JS (node --check), puis ecrit index.html a la racine du depot.
Avec --check, n'ecrit rien : verifie que index.html committe est identique au
resultat du build (code retour 1 sinon).
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import ROOT, SRC, WORK, OUT_HTML  # noqa: E402

ENV = dict(os.environ, PYTHONUTF8="1")


def run(cmd):
    r = subprocess.run(cmd, cwd=WORK, env=ENV, capture_output=True, text=True, encoding="utf-8")
    out = (r.stdout or "") + (r.stderr or "")
    print(f"$ {' '.join(os.path.basename(c) if i == 0 else c for i, c in enumerate(cmd))}")
    if out.strip():
        print(out.rstrip())
    if r.returncode != 0:
        print(f"ECHEC (code {r.returncode})")
        sys.exit(1)


def prepare():
    """Copie les sources de src/ dans le dossier de travail."""
    os.makedirs(WORK, exist_ok=True)
    for name in os.listdir(SRC):
        p = os.path.join(SRC, name)
        if os.path.isfile(p) and name != "paths.py":
            shutil.copy2(p, os.path.join(WORK, name))


def main():
    check = "--check" in sys.argv[1:]
    prepare()
    run([sys.executable, "gen.py"])
    run([sys.executable, "assemble.py"])
    run(["node", "--check", "app.js"])
    built = open(OUT_HTML, "rb").read()
    target = os.path.join(ROOT, "index.html")
    if check:
        committed = open(target, "rb").read().replace(b"\r\n", b"\n")
        if built != committed:
            print("index.html NE correspond PAS au build : relancer python src/build.py")
            sys.exit(1)
        print("index.html identique au build")
        return
    open(target, "wb").write(built)
    print(f"index.html ecrit ({len(built)} octets)")


if __name__ == "__main__":
    main()
