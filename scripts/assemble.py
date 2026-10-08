import json
data=json.load(open('data.json',encoding='utf-8'))
css=open('css.txt',encoding='utf-8').read()
css+=open('css_extra.txt',encoding='utf-8').read()
DATA_JS="".join(f"const {k}={json.dumps(data[v],ensure_ascii=False)};\n" for k,v in [
 ("PHASES","PHASES"),("COUL","COUL"),("SEMAINES","SEMAINES"),("GEAR","GEAR"),("RACES","RACES"),
 ("PROFIL","PROFIL"),("RECORDS","RECORDS"),("VIGILANCE","VIGILANCE"),("S24R","S24R"),("HIST","HIST"),("POLAR","POLAR"),
 ("PROJ","PROJ"),
 ("ALLURES","ALLURES"),("ALLURES_COURSE","ALLURES_COURSE"),("MONTHLY","MONTHLY"),("SAISON2026","SAISON2026"),("SAISON_EFF","SAISON_EFF"),("ACWR_DATA","ACWR_DATA"),("RECORDS_PERF","RECORDS_PERF"),("JOURNAL","JOURNAL"),("REWINDS","REWINDS"),("ZONES_FC","ZONES_FC"),("SEANCES_BY_WEEK","SBW"),("MAJ","MAJ"),("HEATMAP","HEATMAP"),("DOSSIERS","DOSSIERS"),("PALMARES","PALMARES"),("CHANGELOG","CHANGELOG")])
JS=open('app.js',encoding='utf-8').read()
BODY=open('body.html',encoding='utf-8').read()
HTML=f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, must-revalidate"><meta http-equiv="Pragma" content="no-cache">
<title>Plan d'entraînement — {data['PROFIL']['prenom']} · Saison 2026</title>
<meta name="theme-color" content="#0f172a">
<link rel="manifest" href="manifest.json">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Plan">
<link rel="apple-touch-icon" href="icon-180.png">
<style>{css}</style></head>
<body>
{BODY}
<script>
{DATA_JS}
{JS}
</script></body></html>"""
open('plan-entrainement.html','w',encoding='utf-8',newline=chr(10)).write(HTML)
print("Écrit:",len(HTML),"caractères")
