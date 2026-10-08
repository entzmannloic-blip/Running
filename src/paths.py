# -*- coding: utf-8 -*-
"""Chemins du pipeline : valables sous Windows, Linux et en CI.

WORK  = dossier de travail du build (copie de src/ + fichiers generes).
        Defaut : <depot>/build (ignore par Git). Surchargeable par RUNNING_WORK.
"""
import os
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
WORK = os.environ.get("RUNNING_WORK") or os.path.join(ROOT, "build")
OUT_HTML = os.path.join(WORK, "plan-entrainement.html")
DATA_JSON = os.path.join(WORK, "data.json")


def html_url():
    return Path(OUT_HTML).as_uri()
