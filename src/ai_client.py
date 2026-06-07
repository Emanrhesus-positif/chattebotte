import re
from typing import Dict, Any, List

from src.learner import mots_connus

MOTS_INTENSITE = {
    "très", "extrêmement", "vraiment", "totalement",
    "absolument", "complètement", "fortement", "particulièrement",
}
MOTS_CAT_LIVRAISON = {"livraison", "colis", "délai", "emballage"}
MOTS_CAT_SAV = {"service", "sav", "signalement", "remboursement"}
MOTS_CAT_PRODUIT = {"produit", "article", "qualité", "fabrication", "matériaux"}
MOTS_CAT_SERVICE = {"site", "commande", "prix", "frais"}


def _extraire_mots(avis: str) -> List[str]:
    return re.findall(r'\b\w+\b', avis.lower())


def _trouver_negations_locales(mots: List[str]) -> set:
    negated = set()
    for i, mot in enumerate(mots):
        if mot == "ne" and i + 2 < len(mots) and mots[i + 1] == "pas":
            negated.add(i + 1)
        elif mot == "pas" and i + 1 < len(mots):
            negated.add(i + 1)
        elif mot in ("ni", "jamais", "rien", "personne", "aucun"):
            for j in range(i + 1, min(i + 3, len(mots))):
                negated.add(j)
    return negated


def analyser_avis(avis: str) -> Dict[str, Any]:
    avis_lower = avis.lower()
    registre = mots_connus()
    mots_positifs = registre["positifs"]
    mots_negatifs = registre["negatifs"]
    mots_forts = registre["forts"]

    mots = _extraire_mots(avis)
    negated = _trouver_negations_locales(mots)

    nb_positifs = 0
    nb_negatifs = 0
    intensite = 1.0
    points_pos = set()
    points_neg = set()

    for i, mot in enumerate(mots):
        if mot in MOTS_INTENSITE:
            intensite = 1.5
        is_negated = i in negated and mot not in mots_forts
        if mot in mots_positifs and not is_negated:
            nb_positifs += 1
            points_pos.add(mot)
        elif mot in mots_negatifs and not is_negated:
            nb_negatifs += 1
            points_neg.add(mot)

    if nb_positifs > nb_negatifs:
        sentiment = "positif"
        confiance = min(0.5 + (nb_positifs * 0.12) * intensite, 0.98)
        action = "remercier"
    elif nb_negatifs > nb_positifs:
        sentiment = "negatif"
        confiance = min(0.5 + (nb_negatifs * 0.12) * intensite, 0.98)
        action = "offrir_compensation"
    elif nb_positifs > 0 and nb_negatifs > 0:
        sentiment = "mixte"
        confiance = min(0.4 + max(nb_positifs, nb_negatifs) * 0.1, 0.9)
        action = "repondre_inquietudes"
    else:
        sentiment = "neutre"
        confiance = 0.3
        action = "suivi"

    if any(m in avis_lower for m in MOTS_CAT_LIVRAISON):
        categorie = "livraison"
    elif any(m in avis_lower for m in MOTS_CAT_SAV):
        categorie = "SAV"
    elif any(m in avis_lower for m in MOTS_CAT_PRODUIT):
        categorie = "produit"
    elif any(m in avis_lower for m in MOTS_CAT_SERVICE):
        categorie = "service"
    else:
        categorie = "autre"

    if confiance > 0.8 and sentiment == "positif":
        action = "remercier"
    elif confiance > 0.8 and sentiment == "negatif":
        action = "offrir_compensation"
    elif sentiment == "mixte":
        action = "repondre_inquietudes"
    elif sentiment == "neutre" and nb_negatifs > 0:
        action = "contacter"
    elif sentiment == "neutre":
        action = "suivi"
    elif nb_negatifs > 0:
        action = "contacter"

    if nb_positifs > 0 or nb_negatifs > 0:
        justification = (
            f"Analyse basée sur {nb_positifs} terme(s) positif(s) "
            f"et {nb_negatifs} terme(s) négatif(s) "
            f"(intensité ×{intensite}). "
        )
        if sentiment == "positif":
            justification += "L'avis exprime une satisfaction générale."
        elif sentiment == "negatif":
            justification += "L'avis exprime une insatisfaction marquée."
        elif sentiment == "mixte":
            justification += "L'avis contient des éléments positifs et négatifs."
    else:
        justification = "Aucun mot clé de sentiment significatif détecté."

    return {
        "sentiment": sentiment,
        "confiance": round(confiance, 2),
        "justification": justification,
        "points_positifs": sorted(points_pos),
        "points_negatifs": sorted(points_neg),
        "categorie": categorie,
        "action_recommandee": action,
    }
