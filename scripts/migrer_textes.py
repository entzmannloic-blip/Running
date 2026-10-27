#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrer_textes.py — migration ponctuelle (chantier P2, octobre 2026) : sortir de src/gen.py
les revues de seance, les revues de semaine et les Rewinds, vers src/textes/.

    python src/build.py                 # d'abord : build/data.json = etat de reference
    python scripts/migrer_textes.py     # ecrit src/textes/ et reecrit src/gen.py
    python src/build.py && git diff --exit-code -- data index.html sw.js   # preuve : sortie identique

Principe :
- les textes sont extraits de la SORTIE du build (build/data.json), donc dans leur etat final ;
- dans gen.py, la valeur "revue" des blocs realise devient le marqueur _REVUE_FICHIER (la cle garde
  sa place : l'ordre des cles du JSON produit ne change pas) ; le marqueur est remplace par le
  fichier au moment de l'ecriture ;
- la boucle des revues de semaine devient _charge_revues_semaines(SEMAINES), au meme endroit ;
- la liste REWINDS devient _charge_rewinds() ;
- les constantes *REVUE* devenues inutiles sont supprimees.
"""
import ast
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from paths import DATA_JSON, SRC  # noqa: E402

GEN = os.path.join(SRC, "gen.py")
TXT = os.path.join(SRC, "textes")

HELPERS = b'''
# --- Textes (revues de seance, revues de semaine, Rewinds) : fichiers de src/textes/ (voir docs/ENRICHISSEMENT.md)
import os as _os
_TEXTES = "textes"
_REVUE_FICHIER = "\\x00revue:fichier"  # marqueur : la revue de cette seance est dans textes/seances/


def _lit_texte(*parts):
    with open(_os.path.join(_TEXTES, *parts), encoding="utf-8", newline="") as _f:
        return _f.read()


def _charge_revues_semaines(semaines):
    """textes/semaines/S43.html -> SEMAINES[...]["revue"]."""
    _par_num = {_s["num"]: _s for _s in semaines}
    for _nom in sorted(_os.listdir(_os.path.join(_TEXTES, "semaines"))):
        if _nom.endswith(".html"):
            _num = int(_nom[1:-5])
            if _num not in _par_num:
                raise SystemExit(f"textes/semaines/{_nom} : semaine inconnue")
            _par_num[_num]["revue"] = _lit_texte("semaines", _nom)


def _charge_revues_seances(sbw):
    """textes/seances/S44-2.html -> realise["revue"] de la seance 2 de la semaine 44."""
    _vus = set()
    for _nom in sorted(_os.listdir(_os.path.join(_TEXTES, "seances"))):
        if not _nom.endswith(".html"):
            continue
        _w, _i = _nom[1:-5].split("-", 1)
        _arr = sbw.get(int(_w), sbw.get(_w))
        _cible = [_x for _x in (_arr or []) if str(_x["id"]) == _i and _x.get("realise")]
        if len(_cible) != 1:
            raise SystemExit(f"textes/seances/{_nom} : seance introuvable ou sans bloc realise")
        _cible[0]["realise"]["revue"] = _lit_texte("seances", _nom)
        _vus.add((str(_w), _i))
    for _w, _arr in sbw.items():
        for _x in _arr:
            _r = _x.get("realise") or {}
            if _r.get("revue") == _REVUE_FICHIER and (str(_w), str(_x["id"])) not in _vus:
                raise SystemExit(f"S{_w}-{_x['id']} : revue attendue dans textes/seances/ mais fichier absent")


def _charge_rewinds():
    """textes/rewinds/S43.json -> REWINDS, tries par numero de semaine (rwAuto ouvre le dernier)."""
    _noms = [_n for _n in _os.listdir(_os.path.join(_TEXTES, "rewinds")) if _n.endswith(".json")]
    _noms.sort(key=lambda _n: int(_n[1:-5]))
    return [json.loads(_lit_texte("rewinds", _n)) for _n in _noms]
# --- fin des textes

'''


def ecrire(chemin, contenu):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)


def extraire():
    with open(DATA_JSON, encoding="utf-8") as f:
        d = json.load(f)
    n = {"seances": 0, "semaines": 0, "rewinds": 0}
    for w, arr in d["SBW"].items():
        for s in arr:
            r = s.get("realise") or {}
            if "revue" in r:
                ecrire(os.path.join(TXT, "seances", f"S{w}-{s['id']}.html"), r["revue"])
                n["seances"] += 1
    for s in d["SEMAINES"]:
        if "revue" in s:
            ecrire(os.path.join(TXT, "semaines", f"S{s['num']}.html"), s["revue"])
            n["semaines"] += 1
    for rw in d["REWINDS"]:
        ecrire(os.path.join(TXT, "rewinds", f"{rw['id']}.json"), json.dumps(rw, ensure_ascii=False, indent=1) + "\n")
        n["rewinds"] += 1
    return n


class Src:
    """Source en octets : ast donne des colonnes en octets UTF-8."""

    def __init__(self, b):
        self.b = b
        self.starts = [0]
        for i, c in enumerate(b):
            if c == 0x0A:
                self.starts.append(i + 1)

    def off(self, line, col):
        return self.starts[line - 1] + col

    def span(self, node):
        return self.off(node.lineno, node.col_offset), self.off(node.end_lineno, node.end_col_offset)

    def lines(self, node):
        """Plage des lignes entieres d'une instruction seule sur ses lignes, sinon None."""
        a, z = self.span(node)
        la = self.starts[node.lineno - 1]
        lz = self.starts[node.end_lineno] if node.end_lineno < len(self.starts) else len(self.b)
        if self.b[la:a].strip() or self.b[z:lz].strip():
            return None
        return la, lz


def appliquer(b, edits):
    for a, z, rep in sorted(edits, key=lambda e: e[0], reverse=True):
        b = b[:a] + rep + b[z:]
    return b


def _cle(k):
    return k.value if isinstance(k, ast.Constant) else None


def transformer(b):
    s = Src(b)
    tree = ast.parse(b)
    edits = []
    n_seances = 0
    for node in ast.walk(tree):
        # A. revue des blocs realise -> marqueur
        if isinstance(node, ast.Dict):
            cles = [_cle(k) for k in node.keys]
            if "statut" in cles and "revue" in cles:
                v = node.values[cles.index("revue")]
                a, z = s.span(v)
                edits.append((a, z, b"_REVUE_FICHIER"))
                n_seances += 1
        # B. boucle des revues de semaine
        if (isinstance(node, ast.For) and isinstance(node.iter, ast.Name) and node.iter.id == "SEMAINES"
                and all(isinstance(x, ast.If) and not x.orelse and len(x.body) == 1
                        and isinstance(x.body[0], ast.Assign)
                        and ast.unparse(x.body[0].targets[0]).endswith("['revue']")
                        and isinstance(x.body[0].value, ast.Name)
                        for x in node.body)):
            la, lz = s.lines(node)
            edits.append((la, lz, b"_charge_revues_semaines(SEMAINES)\n"))
        # C. REWINDS
        if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "REWINDS" and isinstance(node.value, ast.List)):
            a, z = s.span(node.value)
            edits.append((a, z, b"_charge_rewinds()"))
        # D. chargement des revues de seance juste avant l'ecriture de data.json
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and ast.unparse(node.value.func) == "_j.dump":
            la = s.starts[node.lineno - 1]
            edits.append((la, la, b"_charge_revues_seances(SEANCES_BY_WEEK)\n"))
    b = appliquer(b, edits)
    print(f"  marqueurs de revue de seance : {n_seances}")

    # E. constantes *REVUE* devenues inutiles
    total = 0
    while True:
        s = Src(b)
        tree = ast.parse(b)
        lus = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        edits = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                    and "REVUE" in node.targets[0].id and node.targets[0].id not in lus):
                plage = s.lines(node)
                if plage:
                    edits.append((plage[0], plage[1], b""))
        if not edits:
            break
        total += len(edits)
        b = appliquer(b, edits)
    print(f"  constantes de revue supprimees : {total}")

    # F. fonctions de chargement apres « import json, re »
    i = b.index(b"import json, re\n") + len(b"import json, re\n")
    return b[:i] + HELPERS + b[i:]


def main():
    if not os.path.exists(DATA_JSON):
        sys.exit("Lancer d'abord : python src/build.py")
    if os.path.isdir(TXT):
        sys.exit("src/textes/ existe deja : migration deja faite")
    print("Extraction :", extraire())
    with open(GEN, "rb") as f:
        avant = f.read()
    apres = transformer(avant)
    compile(apres, "gen.py", "exec")
    with open(GEN, "wb") as f:
        f.write(apres)
    print(f"gen.py : {len(avant):,} -> {len(apres):,} octets".replace(",", " "))


if __name__ == "__main__":
    main()
