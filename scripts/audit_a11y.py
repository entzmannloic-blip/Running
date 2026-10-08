#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_a11y.py — audit d'accessibilite des 4 vues (390 px), sans dependance externe.

    python scripts/audit_a11y.py            # rapport + code retour 1 s'il y a des violations
    python scripts/audit_a11y.py --detail   # liste des elements en cause
    python scripts/audit_a11y.py --dark     # meme audit en mode sombre (reglage du telephone)

Regles (inspirees de WCAG 2.2 AA) :
  H1  un seul <h1> visible par vue                    H2  pas de saut de niveau de titre
  L1  un seul repere <main> ; <nav> etiquete
  N1  tout controle interactif a un nom accessible    N2  pas de div/span cliquable sans role ni tabindex
  T1  cibles tactiles >= 44 x 44 px (hors liens dans une phrase)
  F1  texte lisible >= 12 px (13 px pour le texte courant)
  C1  contraste du texte >= 4,5:1 (3:1 pour le grand texte)
  E1  statut porte par un emoji seul sans equivalent texte
  V1  zoom autorise (pas de maximum-scale/user-scalable=no)    Z1  <html lang>
Les arrière-plans en degrade ou en image sont ignores par C1 (non calculables).
"""
import json
import os
import sys

for _d in (os.path.dirname(os.path.abspath(__file__)),
           os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")):
    if os.path.exists(os.path.join(_d, "paths.py")):
        sys.path.insert(0, _d)
from paths import html_url  # noqa: E402

VIEWS = ["accueil", "plan", "cockpit", "palmares"]
MIN_FONT = 12  # px
BODY_FONT = 13  # px

JS = r"""
(view) => {
  const out = [];
  const root = document.getElementById('vue-' + view);
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && s.opacity !== '0'; };
  const sel = (e) => { let s = e.tagName.toLowerCase(); if (e.id) s += '#' + e.id;
    else if (e.className && typeof e.className === 'string') s += '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.'); return s; };
  const add = (rule, e, msg) => out.push({ rule, el: sel(e), msg, text: (e.innerText || e.getAttribute('aria-label') || '').trim().slice(0, 40) });

  // ---- titres et reperes
  const h = [...root.querySelectorAll('h1,h2,h3,h4,h5,h6,[role=heading]')].filter(vis);
  const h1 = h.filter(x => x.tagName === 'H1' || x.getAttribute('aria-level') === '1');
  if (h1.length !== 1) out.push({ rule: 'H1', el: '#vue-' + view, msg: h1.length + ' titre(s) de niveau 1 visible(s)', text: '' });
  let prev = 0;
  h.forEach(x => { const l = x.tagName.startsWith('H') ? +x.tagName[1] : +(x.getAttribute('aria-level') || 2);
    if (prev && l > prev + 1) add('H2', x, 'saut de niveau h' + prev + ' -> h' + l); prev = l; });
  const mains = [...document.querySelectorAll('main,[role=main]')].filter(vis);
  if (mains.length !== 1) out.push({ rule: 'L1', el: 'document', msg: mains.length + ' repere(s) main visible(s)', text: '' });
  document.querySelectorAll('nav').forEach(n => { if (!n.getAttribute('aria-label') && !n.getAttribute('aria-labelledby')) add('L1', n, 'nav sans nom'); });

  // ---- controles
  const interactive = [...root.querySelectorAll('a[href],button,input,select,textarea,[role=button],[role=tab],[tabindex]:not([tabindex="-1"])')].filter(vis);
  const nav = [...document.querySelectorAll('#botbar button')].filter(vis);
  const name = (e) => (e.getAttribute('aria-label') || e.getAttribute('aria-labelledby') && document.getElementById(e.getAttribute('aria-labelledby'))?.innerText ||
    e.innerText || e.value || e.getAttribute('title') || e.querySelector('img[alt]')?.alt || e.querySelector('svg title')?.textContent || '').trim();
  [...interactive, ...nav].forEach(e => {
    if (!name(e)) add('N1', e, 'controle sans nom accessible');
    const r = e.getBoundingClientRect();
    const inline = e.tagName === 'A' && getComputedStyle(e).display === 'inline';
    if (!inline && (r.width < 44 || r.height < 44)) add('T1', e, Math.round(r.width) + 'x' + Math.round(r.height) + ' px');
  });
  [...root.querySelectorAll('[onclick]')].filter(vis).forEach(e => {
    const t = e.tagName;
    if (!['BUTTON', 'A', 'INPUT', 'SELECT', 'SUMMARY'].includes(t) && !e.getAttribute('role') && e.getAttribute('tabindex') === null)
      add('N2', e, 'element cliquable non focalisable au clavier');
  });

  // ---- texte : taille, contraste, emoji
  const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(parseFloat);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const over = (f, b) => ({ r: f.r * f.a + b.r * (1 - f.a), g: f.g * f.a + b.g * (1 - f.a), b: f.b * f.a + b.b * (1 - f.a), a: 1 });
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const bgOf = (e) => { // fond effectif ; null si degrade / image
    let layers = []; for (let n = e; n && n.nodeType === 1; n = n.parentElement) { const s = getComputedStyle(n);
      if (s.backgroundImage && s.backgroundImage !== 'none') return null;
      const c = parse(s.backgroundColor); if (c && c.a > 0) { layers.push(c); if (c.a === 1) break; } }
    let base = parse(getComputedStyle(document.body).backgroundColor) || { r: 248, g: 250, b: 252, a: 1 };
    if (base.a < 1) base = over(base, { r: 255, g: 255, b: 255, a: 1 });
    for (let i = layers.length - 1; i >= 0; i--) base = over(layers[i], base); return base; };
  const emojiOnly = /^[\p{Extended_Pictographic}️‍\s]+$/u;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  for (let t = walker.nextNode(); t; t = walker.nextNode()) {
    const txt = t.textContent.trim(); const e = t.parentElement;
    if (!txt || !e || seen.has(e) || !vis(e) || e.closest('[aria-hidden=true],script,style')) continue; seen.add(e);
    const s = getComputedStyle(e); const px = parseFloat(s.fontSize);
    if (emojiOnly.test(txt)) { if (!e.getAttribute('aria-label') && !e.closest('[aria-label]') && !e.parentElement.innerText.replace(txt, '').trim()) add('E1', e, 'emoji seul : ' + txt); continue; }
    if (px < MIN_FONT) add('F1', e, px + ' px < ' + MIN_FONT);
    else if (px < BODY_FONT && txt.length > 40) add('F1', e, 'texte courant a ' + px + ' px < ' + BODY_FONT);
    const fg = parse(s.color), bg = bgOf(e); if (!fg || !bg) continue;
    const f = over(fg, bg); const L1 = lum(f), L2 = lum(bg);
    const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const large = px >= 24 || (px >= 18.66 && +s.fontWeight >= 700);
    if (ratio < (large ? 3 : 4.5)) add('C1', e, ratio.toFixed(2) + ':1 (' + s.color + ' sur ' + `rgb(${Math.round(bg.r)},${Math.round(bg.g)},${Math.round(bg.b)})` + ')');
  }
  return out;
}
"""

JS = JS.replace("MIN_FONT", str(MIN_FONT)).replace("BODY_FONT", str(BODY_FONT))


def main():
    from playwright.sync_api import sync_playwright
    detail = "--detail" in sys.argv[1:]
    rows = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, locale="fr-FR",
                            service_workers="block", reduced_motion="reduce",
                            color_scheme="dark" if "--dark" in sys.argv[1:] else "light")
        ctx.route("**/*open-meteo.com/**", lambda r: r.abort())
        p = ctx.new_page()
        p.clock.install(time="2026-10-08T10:00:00")
        p.goto(html_url(), wait_until="load", timeout=20000)
        p.wait_for_function("typeof showTab==='function'&&!document.getElementById('boot-load')", timeout=10000)
        p.wait_for_timeout(1200)
        p.evaluate("var o=document.getElementById('rwoverlay');if(o)o.style.display='none';")
        glob = p.evaluate("({lang:document.documentElement.lang,vp:document.querySelector('meta[name=viewport]').content})")
        if not glob["lang"]:
            rows.append(("-", {"rule": "Z1", "el": "html", "msg": "attribut lang absent", "text": ""}))
        import re
        if re.search(r"user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*[01](\.\d+)?\b", glob["vp"]):
            rows.append(("-", {"rule": "V1", "el": "meta viewport", "msg": glob["vp"], "text": ""}))
        for v in VIEWS:
            p.evaluate(f"showTab('{v}')")
            p.wait_for_timeout(500)
            for r in p.evaluate(JS, v):
                rows.append((v, r))
        b.close()

    by_rule = {}
    for v, r in rows:
        by_rule.setdefault(r["rule"], []).append((v, r))
    print("\nAUDIT ACCESSIBILITE — 4 vues, 390 px")
    for rule in sorted(by_rule):
        items = by_rule[rule]
        print(f"  ✗ {rule} : {len(items)} violation(s)  (ex. {items[0][1]['el']} — {items[0][1]['msg']})")
        if detail:
            for v, r in items[:60]:
                print(f"      [{v}] {r['el']}  {r['msg']}  « {r['text']} »")
    if not rows:
        print("  ✓ aucune violation")
    total = len(rows)
    print(f"\n  RESULTAT : {'OK' if not total else str(total) + ' violation(s) — a corriger'}")
    json.dump({"violations": [{"vue": v, **r} for v, r in rows]},
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "a11y.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1) if os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build")) else None
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
