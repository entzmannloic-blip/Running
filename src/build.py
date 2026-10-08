# -*- coding: utf-8 -*-
"""Build unique : python src/build.py [--check]

1. copie src/ dans le dossier de travail (build/)
2. gen.py -> data.json, assemble.py -> site/index.html + site/data/*.json
3. node --check app.js, puis prepare site/ (src/app.js, sw.js, manifest, icones)
4. ecrit index.html et data/*.json a la racine du depot (ce que GitHub Pages publie)

Avec --stage, construit seulement site/ dans le dossier de travail (tests).
Avec --check, n'ecrit rien : echoue (code 1) si index.html ou data/*.json committes
different du resultat du build.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import ROOT, SRC, WORK, SITE  # noqa: E402

ENV = dict(os.environ, PYTHONUTF8="1")
STATIC = ["manifest.json", "icon-180.png", "icon-192.png", "icon-512.png", ".nojekyll"]


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
        if os.path.isfile(p):
            shutil.copy2(p, os.path.join(WORK, name))


def stage_site():
    """Complete site/ avec app.js et les fichiers statiques du depot."""
    os.makedirs(os.path.join(SITE, "src"), exist_ok=True)
    shutil.copyfile(os.path.join(WORK, "app.js"), os.path.join(SITE, "src", "app.js"))
    for name in STATIC:
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            shutil.copyfile(p, os.path.join(SITE, name))
    # sw.js : modele src/sw.js dont le nom de cache suit le numero de build
    meta = json.load(open(os.path.join(SITE, "data", "meta.json"), encoding="utf-8"))
    build = meta["CHANGELOG"][0]["build"]
    shell = ["./", "./index.html", "./manifest.json", "./icon-180.png", "./icon-192.png", "./icon-512.png",
             "./src/app.js"] + ["./data/" + n for n in sorted(os.listdir(os.path.join(SITE, "data")))]
    sw = open(os.path.join(WORK, "sw.js"), encoding="utf-8").read().replace("\r\n", "\n")
    sw = sw.replace("__BUILD__", str(build)).replace("__SHELL__", json.dumps(shell, indent=1))
    open(os.path.join(SITE, "sw.js"), "w", encoding="utf-8", newline="\n").write(sw)


def published_files():
    """Fichiers produits par le build et commites a la racine : index.html + data/*.json."""
    files = ["index.html", "sw.js"]
    d = os.path.join(SITE, "data")
    files += ["data/" + n for n in sorted(os.listdir(d))]
    return files


def build_date(check):
    """Date du build : en --check, celle enregistree dans data/meta.json (BUILT_ON) ; sinon aujourd'hui."""
    if check:
        p = os.path.join(ROOT, "data", "meta.json")
        if os.path.exists(p):
            d = json.load(open(p, encoding="utf-8")).get("BUILT_ON")
            if d:
                return d
    return os.environ.get("RUNNING_TODAY") or datetime.date.today().isoformat()


def main():
    check = "--check" in sys.argv[1:]
    ENV["RUNNING_TODAY"] = build_date(check)
    prepare()
    shutil.rmtree(SITE, ignore_errors=True)
    run([sys.executable, "gen.py"])
    run([sys.executable, "assemble.py"])
    run(["node", "--check", "app.js"])
    stage_site()
    files = published_files()
    if "--stage" in sys.argv[1:]:
        print("site/ construit dans", SITE, "(rien d'ecrit a la racine)")
        return
    if check:
        bad = []
        for rel in files:
            built = open(os.path.join(SITE, *rel.split("/")), "rb").read()
            target = os.path.join(ROOT, *rel.split("/"))
            committed = open(target, "rb").read().replace(b"\r\n", b"\n") if os.path.exists(target) else None
            if built != committed:
                bad.append(rel)
        root_data = os.path.join(ROOT, "data")
        stale = [f"data/{n}" for n in (os.listdir(root_data) if os.path.isdir(root_data) else [])
                 if f"data/{n}" not in files]
        if bad or stale:
            print("Fichiers differents du build :", ", ".join(bad + stale), "— relancer python src/build.py")
            sys.exit(1)
        print(f"Fichiers publies identiques au build ({len(files)})")
        return
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    for rel in files:
        shutil.copyfile(os.path.join(SITE, *rel.split("/")), os.path.join(ROOT, *rel.split("/")))
    print(f"{len(files)} fichiers ecrits : " + ", ".join(files))


if __name__ == "__main__":
    main()
