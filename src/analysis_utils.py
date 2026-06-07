import csv
import json
from pathlib import Path
from typing import Dict, Any, List

from src.ai_client import analyser_avis
from src.prompt_builder import formater_resultat


def analyser_avis_et_sauvegarder(
    avis: str,
    chemin_resultats: str = "data/resultats_analyses.csv"
) -> Dict[str, Any]:
    resultat = analyser_avis(avis)
    resultat["avis_original"] = avis

    fichier = Path(chemin_resultats)
    est_nouveau = not fichier.exists()

    with open(fichier, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if est_nouveau:
            writer.writerow([
                "avis", "sentiment", "confiance", "justification",
                "points_positifs", "points_negatifs", "categorie",
                "action_recommandee"
            ])
        writer.writerow([
            avis,
            resultat["sentiment"],
            resultat["confiance"],
            resultat["justification"],
            json.dumps(resultat["points_positifs"], ensure_ascii=False),
            json.dumps(resultat["points_negatifs"], ensure_ascii=False),
            resultat["categorie"],
            resultat["action_recommandee"],
        ])

    return resultat


def analyser_depuis_csv(
    chemin_csv: str,
    chemin_resultats: str = "data/resultats_analyses.csv"
) -> List[Dict[str, Any]]:
    resultats = []
    with open(chemin_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            avis = row.get("avis", row.get("review", ""))
            if avis:
                resultat = analyser_avis_et_sauvegarder(avis, chemin_resultats)
                resultats.append(resultat)
    return resultats


def afficher_resultats(resultats: List[Dict[str, Any]]):
    for resultat in resultats:
        print(formater_resultat(resultat.get("avis_original", ""), resultat))
        print()
