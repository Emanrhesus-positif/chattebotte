from typing import Dict, Any


def construire_prompt(avis: str) -> str:
    return f"""Tu es un expert en analyse de sentiment pour avis clients.

Analyse l'avis suivant et réponds UNIQUEMENT avec un objet JSON valide.

Avis client : "{avis}"

Format de réponse attendu (JSON uniquement) :
{{
  "sentiment": "positif" | "negatif" | "mixte" | "neutre",
  "confiance": 0.95,
  "justification": "explication concise",
  "points_positifs": ["point1", "point2"],
  "points_negatifs": ["point1", "point2"],
  "categorie": "produit" | "service" | "livraison" | "SAV" | "autre",
  "action_recommandee": "remercier" | "contacter" | "repondre_inquietudes" | "offrir_compensation" | "suivi"
}}

Ne réponds qu'avec le JSON, rien d'autre."""


def formater_resultat(avis: str, resultat: Dict[str, Any]) -> str:
    return (
        f"--- Analyse d'avis ---\n"
        f"Avis : \"{avis}\"\n"
        f"Sentiment : {resultat['sentiment']}\n"
        f"Confiance : {resultat['confiance']:.0%}\n"
        f"Justification : {resultat['justification']}\n"
        f"Points positifs : {', '.join(resultat['points_positifs']) if resultat['points_positifs'] else 'Aucun'}\n"
        f"Points négatifs : {', '.join(resultat['points_negatifs']) if resultat['points_negatifs'] else 'Aucun'}\n"
        f"Catégorie : {resultat['categorie']}\n"
        f"Action recommandée : {resultat['action_recommandee']}\n"
    )
