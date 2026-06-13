# Pipeline de build du plan d'entrainement

Reprise dans une nouvelle conversation :
1. Recuperer src/* dans /tmp
2. python3 gen.py        -> /tmp/data.json
3. python3 assemble.py   -> /mnt/user-data/outputs/plan-entrainement.html
4. Valider : node --check sur le script extrait, puis node test.js
5. Pousser index.html via API GitHub Contents (PUT base64, branch main, recuperer le sha d'abord)

Fichiers .fit des seances : dossier fit/ (genere via fit-tool, pip --break-system-packages).
Marqueur de version visible dans la legende du calendrier : 'build N' (incrementer a chaque push).

Etat au handoff : build 5. Sprint 1 LIVRE (vue du jour + bouton .fit, countdown 2 courses sur une ligne, horodatage, PWA add-to-home, calendrier mensuel vert/orange/gris cliquable).
Jours des seances : ordre des seances (seance 1 = lundi...), sortie longue = dimanche.
Prochain : Sprint 2 = heatmap annuelle facon GitHub + badges/jalons + metaphores distance + records tombes.
