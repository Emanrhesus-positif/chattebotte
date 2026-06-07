import json
from pathlib import Path
from typing import Dict, Any, List

REGISTRE_PATH = Path("data/keywords.json")

MOTS_BASE_POSITIFS = [
    "excellent", "super", "parfaite", "parfait", "génial", "formidable",
    "satisfait", "content", "bon", "bien", "rapide", "rapidement", "qualité",
    "merveilleux", "top", "impeccable", "parfaitement", "facile",
    "pratique", "exceptionnel", "remarquable", "agréable",
    "confortable", "efficace", "performant", "fiable", "solide",
    "beau", "belle", "joli", "jolie", "sympa", "adoré", "correct",
    "soigné", "remboursement", "réactif", "conforme", "bonne",
    "cool", "nickel",
    "superbe", "magnifique", "splendide", "ravissant", "charmant",
    "délicieux", "succulent", "exquis", "fabuleux", "fantastique",
    "sensationnel", "extraordinaire", "incroyable", "inoubliable",
    "hors", "pair", "inégalé", "imbattable", "irréprochable",
    "épatant", "étonnant", "surprenant", "bluffant", "impressionnant",
    "extra", "gratuit", "offert", "remisé", "promo", "offre",
    "claire", "clair", "précis", "net", "limpide", "transparent",
    "simple", "intuitif", "ergonomique", "fonctionnel", "bien", "bon",
    "utile", "indispensable", "essentiel", "précieux", "incontournable",
    "complet", "intégral", "riche", "varié", "diversifié",
    "robuste", "résistant", "costaud", "solide", "indestructible",
    "puissant", "fort", "musclé", "véloce", "vif", "réactif",
    "moderne", "actuel", "tendance", "stylé", "élégant", "raffiné",
    "esthétique", "harmonieux", "équilibré", "proportionné",
    "lumineux", "coloré", "chatoyant", "brillant", "éclatant",
    "agréable", "plaisant", "sympathique", "accueillant", "chaleureux",
    "convivial", "professionnel", "compétent", " sérieux", "rigoureux",
    "ponctuel", "présent", "disponible", "à l'écoute", "attentionné",
    "aimable", "courtois", "poli", "respectueux", "gentil",
    "rapide", "express", "instantané", "fulgurant",
    "soigné", "propre", "net", "ordonné", "méticuleux",
    "emballage", "protégé", "sécurisé", "bien emballé",
    "suivi", "tracé", "informé", "notifié", "prévenu",
    "satisfaisant", "correct", "acceptable", "passable", "convenable",
    "réglo", "honnête", "correct", "transparent", "clair",
]

MOTS_BASE_NEGATIFS = [
    "mauvais", "mauvaise", "horrible", "terrible", "décevant", "déçu",
    "lent", "lente", "cher", "chère", "cassé", "cassée", "défectueux",
    "problème", "dommage", "insatisfait", "fragile", "compliqué",
    "difficile", "inutile", "médiocre", "abîmé", "abîmée", "trop",
    "pire", "nul", "nulle", "arnaque", "déplorable",
    "désastreux", "raté", "inacceptable", "honteux", "catastrophe",
    "excessif", "excessive", "excessifs", "reçu", "reçue", "reçus",
    "fonctionne", "signalement", "éclaté",
    "pourri", "pourrie", "naze", "moisi", "moisie",
    "minable", "lamentable", "infect", "infecte",
    "dégueulasse", "dégueu", "dégoûtant", "dégoutant",
    "merdique", "foireux", "bâclé", "ringard",
    "crado", "sale", "immonde", "souillé",
    "affreux", "hideux", "moche", "laid", "laide", "vilain",
    "frustré", "énervé", "irrité", "furieux", "fâché",
    "détestable", "exécrable", "insupportable", "intolérable",
    "inadmissible", "scandaleux", "pitoyable",
    "fade", "insipide", "banal", "quelconque",
    "barbant", "ennuyeux", "chiant", "rasoir", "lassant",
    "usé", "élimé", "miteux", "misérable",
    "triste", "déprimant", "dépressif", "morose", "lugubre",
    "stressant", "angoissant", "inquiétant",
    "choquant", "effrayant", "atroce", "abominable",
    "navrant", "désolant", "consternant", "vexant", "blessant",
    "injuste", "malhonnête", "trompeur", "mensonger",
    "erroné", "faux", "imprécis", "approximatif",
    "négligé", "idiot", "stupide", "bête", "débile",
    "dangereux", "risqué", "périlleux",
    "cabossé", "rayé", "taché", "sali", "fêlé", "percé",
    "toxique", "nuisible", "nocif", "malsain",
    "bizarre", "louche", "suspect", "douteux", "étrange",
    "confus", "embrouillé", "obscur",
    "surfait", "surévalué", "trop cher", "surcoté",
    "inconfortable", "mal conçu", "peu pratique",
    "encombrant", "bruyant", "sale", "poussiéreux",
    "compliqué", "prise de tête",
    "perte de temps", "temps perdu",
    "incomplet", "manquant", "manque",
    "déchiré", "décousu", "détaché", "déboîté",
    "explosé", "volé", "perdu",
    "endommagé", "détérioré", "dégradé", "corrompu",
    "foutu", "fichu", "esquinté",
]

SEED_COUNT = 3


def _creer_registre_initial() -> dict:
    mots = {}
    for w in MOTS_BASE_POSITIFS:
        mots[w] = {"positif": SEED_COUNT, "negatif": 0}
    for w in MOTS_BASE_NEGATIFS:
        mots[w] = {"positif": 0, "negatif": SEED_COUNT}
    return {
        "version": 1,
        "corrections_count": 0,
        "retrain_count": 0,
        "mots": mots,
        "historique": [],
    }


def charger_registre() -> dict:
    if not REGISTRE_PATH.exists():
        data = _creer_registre_initial()
        with open(REGISTRE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return data
    with open(REGISTRE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def sauvegarder_registre(data: dict):
    with open(REGISTRE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def mots_connus() -> dict:
    registre = charger_registre()
    pos = set()
    neg = set()
    forts = set()
    for mot, comptes in registre["mots"].items():
        if comptes.get("manuel"):
            forts.add(mot)
        if comptes["positif"] > comptes["negatif"]:
            pos.add(mot)
        elif comptes["negatif"] > comptes["positif"]:
            neg.add(mot)
    return {"positifs": pos, "negatifs": neg, "forts": forts}


def corriger_analyse(
    commentaire: str,
    mots_significatifs: List[str],
    sentiment_reel: str,
) -> Dict[str, Any]:
    registre = charger_registre()
    registre["corrections_count"] += 1
    compteur = registre["corrections_count"]

    for mot in mots_significatifs:
        mot = mot.lower().strip()
        if mot not in registre["mots"]:
            registre["mots"][mot] = {"positif": 0, "negatif": 0}
        if sentiment_reel == "positif":
            registre["mots"][mot]["positif"] += 1
        elif sentiment_reel == "negatif":
            registre["mots"][mot]["negatif"] += 1
        registre["mots"][mot]["manuel"] = True

    retrain = compteur % 5 == 0
    if retrain:
        registre["retrain_count"] += 1
        for mot in list(registre["mots"].keys()):
            c = registre["mots"][mot]
            c["positif"] = min(c["positif"], 20)
            c["negatif"] = min(c["negatif"], 20)
            if c["positif"] == 0 and c["negatif"] == 0:
                del registre["mots"][mot]

    registre["historique"].append({
        "commentaire": commentaire,
        "mots": mots_significatifs,
        "sentiment": sentiment_reel,
        "correction_n": compteur,
    })
    if len(registre["historique"]) > 50:
        registre["historique"] = registre["historique"][-50:]

    sauvegarder_registre(registre)
    return {
        "correction_n": compteur,
        "retrain": retrain,
        "prochain_retrain": 5 - (compteur % 5),
        "mots_appris": len(mots_significatifs),
        "total_mots": len(registre["mots"]),
    }
