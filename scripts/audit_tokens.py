#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_tokens.py — couleurs hexadecimales « en dur » (hors jetons) : le nombre ne doit pas augmenter.

    python scripts/audit_tokens.py            # compare a scripts/tokens_baseline.json (code 1 si en hausse)
    python scripts/audit_tokens.py --update   # reecrit la base apres une reduction volontaire
    python scripts/audit_tokens.py --top      # detail des teintes les plus frequentes

Compte, dans src/css.txt + src/css_extra.txt (declarations hors definitions de variables --x et hors regles
du mode nuit) et dans les styles en ligne de src/app.js (color:, background:, border-color:), les couleurs #rrggbb.
Exceptions assumees (voir DESIGN.md) : blanc #fff sur texte/fonds d'accent, degrades, ombres, SVG des graphiques,
degrades par course (dossiers, dans les donnees).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "scripts", "tokens_baseline.json")
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")

# propriete -> {teinte : jeton}. Le texte et les fonds n'ont pas les memes correspondances :
# #1e293b est « l'encre » en texte, mais un fond sombre fixe (pastille active) en arriere-plan.
TEXT = {"#1e293b": "--texte", "#475569": "--texte-deux", "#64748b": "--texte-trois", "#94a3b8": "--gris",
        "#0d9488": "--primary", "#0f766e": "--primary-deux", "#16a34a": "--ok", "#15803d": "--ok-deux",
        "#f59e0b": "--warn", "#b45309": "--warn-deux", "#ef4444": "--danger", "#b91c1c": "--danger-deux"}
FILL = {"#f8fafc": "--gris-fond", "#e2e8f0": "--gris-clair", "#94a3b8": "--gris",
        "#0d9488": "--primary", "#0f766e": "--primary-deux", "#99f6e4": "--primary-clair", "#f0fdfa": "--primary-fond",
        "#16a34a": "--ok", "#15803d": "--ok-deux", "#bbf7d0": "--ok-clair", "#dcfce7": "--ok-fond",
        "#f59e0b": "--warn", "#b45309": "--warn-deux", "#fde68a": "--warn-clair", "#fef3c7": "--warn-fond",
        "#ef4444": "--danger", "#b91c1c": "--danger-deux", "#fecaca": "--danger-clair", "#fee2e2": "--danger-fond"}
MAPS = {"color": TEXT, "background": FILL, "background-color": FILL, "border-color": FILL,
        "border": FILL, "border-left": FILL, "border-right": FILL, "border-top": FILL, "border-bottom": FILL,
        "outline-color": FILL}


def _strip_comments(css):
    holes = []

    def keep(m):
        holes.append(m.group(0))
        return f"\x00{len(holes) - 1}\x00"
    return re.sub(r"/\*.*?\*/", keep, css, flags=re.S), holes


def _restore(css, holes):
    return re.sub(r"\x00(\d+)\x00", lambda m: holes[int(m.group(1))], css)


def transform_css(css, fn):
    """Reecrit chaque declaration par fn(contexte, declaration) ; le reste du texte est conserve."""
    css, holes = _strip_comments(css)
    out, stack, cur = [], [], []
    for ch in css:
        if ch == "{":
            stack.append("".join(cur).strip())
            out.append("".join(cur) + ch)
            cur = []
        elif ch in ";}":
            decl = "".join(cur)
            out.append(fn(list(stack), decl) if decl.strip() else decl)
            out.append(ch)
            cur = []
            if ch == "}" and stack:
                stack.pop()
        else:
            cur.append(ch)
    out.append("".join(cur))
    return _restore("".join(out), holes)


def skipped_context(ctx):
    return any("nuit" in c or "prefers-color-scheme" in c for c in ctx)


def css_declarations(css):
    seen = []
    transform_css(css, lambda ctx, d: (seen.append((ctx, d)), d)[1])
    return seen


def count_css():
    n, per = 0, {}
    for f in ("css.txt", "css_extra.txt"):
        css = open(os.path.join(ROOT, "src", f), encoding="utf-8").read()
        for ctx, d in css_declarations(css):
            m = re.match(r"\s*([\w-]+)\s*:(.*)$", d, re.S)
            if not m or m.group(1).startswith("--") or skipped_context(ctx):
                continue
            for h in HEX.findall(m.group(2)):
                n += 1
                per[h.lower()] = per.get(h.lower(), 0) + 1
    return n, per


JS_STYLE = re.compile(r"(?<![-\w])(color|background|background-color|border-color):\s*(#[0-9a-fA-F]{6})\b")


def count_js():
    s = open(os.path.join(ROOT, "src", "app.js"), encoding="utf-8").read()
    found = JS_STYLE.findall(s)
    per = {}
    for _, h in found:
        per[h.lower()] = per.get(h.lower(), 0) + 1
    return len(found), per


def counts():
    c, cp = count_css()
    j, jp = count_js()
    return {"css": c, "js": j}, cp, jp


def main():
    cur, cp, jp = counts()
    print(f"couleurs hex hors jetons : css {cur['css']} · js (styles en ligne) {cur['js']}")
    if "--top" in sys.argv[1:]:
        top = sorted({k: cp.get(k, 0) + jp.get(k, 0) for k in set(cp) | set(jp)}.items(), key=lambda x: -x[1])[:14]
        print("  plus frequentes :", ", ".join(f"{k}×{v}" for k, v in top))
    if "--update" in sys.argv[1:]:
        json.dump(cur, open(BASE, "w", encoding="utf-8"), indent=1)
        print("  base mise a jour :", cur)
        return
    base = json.load(open(BASE, encoding="utf-8")) if os.path.exists(BASE) else None
    if base is None:
        print("  ✗ scripts/tokens_baseline.json absent (lancer --update une fois)")
        sys.exit(1)
    bad = [k for k in cur if cur[k] > base.get(k, 0)]
    if bad:
        print("  ✗ en hausse :", ", ".join(f"{k} {base.get(k, 0)} -> {cur[k]}" for k in bad), "— utiliser un jeton (var(--…))")
        sys.exit(1)
    print("  ✓ pas de hausse (base :", base, ")")


if __name__ == "__main__":
    main()
