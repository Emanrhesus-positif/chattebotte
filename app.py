import streamlit as st
import pandas as pd
from pathlib import Path

from src.ai_client import analyser_avis
from src.analysis_utils import analyser_avis_et_sauvegarder, analyser_depuis_csv
from src.prompt_builder import construire_prompt
from src.learner import charger_registre, corriger_analyse
from src.ai_client import _extraire_mots

st.set_page_config(page_title="Chattest", layout="centered")
st.title("Chattest - sentiment analysis")
st.markdown("Analysez les avis clients avec une IA qui apprend de vos corrections.")

SENTIMENT_META = {
    "positif": {"color": "green"},
    "negatif": {"color": "red"},
    "mixte": {"color": "orange"},
    "neutre": {"color": "gray"},
}

tab_simple, tab_test, tab_learn, tab_prompt = st.tabs([
    "Analyse simple", "Test sur 8 avis", "Chatbot amélioratif", "Prompt d'analyse"
])

with tab_simple:
    avis_input = st.text_area(
        "Saisissez un avis client :",
        placeholder="Ex: Super produit, livraison rapide !",
        height=120,
    )
    if st.button("Analyser", type="primary") and avis_input:
        with st.spinner("Analyse en cours..."):
            resultat = analyser_avis_et_sauvegarder(avis_input)
        st.subheader("Résultat de l'analyse")
        col1, col2 = st.columns(2)
        with col1:
            s = resultat["sentiment"]
            meta = SENTIMENT_META[s]
            st.markdown(f"**Sentiment :** :{meta['color']}[{s.upper()}]")
            st.markdown(f"**Confiance :** {resultat['confiance']:.0%}")
            st.markdown(f"**Catégorie :** {resultat['categorie']}")
        with col2:
            st.markdown(f"**Action recommandée :** {resultat['action_recommandee']}")
            st.markdown(f"**Justification :** {resultat['justification']}")
        if resultat["points_positifs"]:
            st.markdown("**Points positifs :** " + ", ".join(resultat["points_positifs"]))
        if resultat["points_negatifs"]:
            st.markdown("**Points négatifs :** " + ", ".join(resultat["points_negatifs"]))
        st.json(resultat)

with tab_test:
    st.markdown("### Analyse des 8 avis de test")
    chemin_test = Path("data/avis_test.csv")
    if chemin_test.exists():
        df_test = pd.read_csv(chemin_test)
        st.dataframe(df_test, width="stretch")
        if st.button("Lancer l'analyse complète", type="primary"):
            with st.spinner("Analyse des 8 avis en cours..."):
                resultats = analyser_depuis_csv(str(chemin_test))
            st.success("Analyse terminée !")
            df_affichage = pd.DataFrame(resultats)
            if "avis_original" in df_affichage.columns:
                df_affichage.rename(columns={"avis_original": "avis"}, inplace=True)
            st.dataframe(df_affichage, width="stretch")
            chemin_res = Path("data/resultats_analyses.csv")
            if chemin_res.exists():
                with open(chemin_res, "rb") as f:
                    st.download_button(
                        "Télécharger les résultats (CSV)", f,
                        "resultats_analyses.csv", "text/csv",
                    )
    else:
        st.warning("Fichier data/avis_test.csv introuvable.")

with tab_learn:
    st.markdown("### Entraînement par correction")

    registre = charger_registre()
    c_count = registre["corrections_count"]
    next_train = 5 - (c_count % 5)
    if next_train == 5:
        next_train = 0
    st.markdown(
        f"Corrections enregistrées : **{c_count}** &nbsp;|&nbsp; "
        f"Prochain retraining dans : **{next_train}** correction(s) &nbsp;|&nbsp; "
        f"Mots dans le registre : **{len(registre['mots'])}**"
    )
    if c_count > 0 and c_count % 5 == 0:
        st.success(f"Retraining effectué ({registre['retrain_count']} au total)")

    col_comment, col_result = st.columns([2, 1])
    with col_comment:
        commentaire = st.text_area(
            "Saisissez un commentaire à corriger :",
            placeholder="Ex: wow, ce serait vraiment cool...si c'était pas éclaté",
            height=100, key="learn_input",
        )
        if st.button("Analyser le commentaire", key="learn_analyze"):
            if commentaire:
                st.session_state.learn_result = analyser_avis(commentaire)
                st.session_state.learn_mots = _extraire_mots(commentaire)
                st.session_state.learn_commentaire = commentaire

        if "learn_result" in st.session_state:
            res = st.session_state.learn_result
            s = res["sentiment"]
            meta = SENTIMENT_META[s]
            st.markdown(
                f"**Analyse actuelle :** :{meta['color']}[{s.upper()}] "
                f"(confiance {res['confiance']:.0%})"
            )
            st.markdown(f"Mots positifs : {', '.join(res['points_positifs']) or 'aucun'}")
            st.markdown(f"Mots négatifs : {', '.join(res['points_negatifs']) or 'aucun'}")

            st.markdown("---")
            st.markdown("**Corriger l'analyse :**")

            mots_dispo = st.session_state.get("learn_mots", [])
            mots_uniques = sorted(set(mots_dispo))

            mots_choisis = st.multiselect(
                "Mots significatifs (ceux qui déterminent le vrai sentiment) :",
                options=mots_uniques,
                default=mots_uniques,
                key="learn_words",
            )

            sentiment_reel = st.radio(
                "Sentiment réel :",
                ["positif", "negatif", "mixte", "neutre"],
                horizontal=True,
                key="learn_sentiment",
            )

            if st.button("Corriger et entraîner", type="primary", key="learn_correct"):
                if mots_choisis and st.session_state.get("learn_commentaire"):
                    info = corriger_analyse(
                        st.session_state.learn_commentaire,
                        mots_choisis,
                        sentiment_reel,
                    )
                    st.success(
                        f"Correction #{info['correction_n']} enregistrée. "
                        + (" Retraining effectué !" if info["retrain"] else "")
                    )
                    st.rerun()
                else:
                    st.warning("Sélectionne au moins un mot significatif.")

    with col_result:
        st.markdown("**Registre des mots appris**")
        registre = charger_registre()
        if registre["mots"]:
            rows = []
            for mot, c in sorted(registre["mots"].items()):
                total = c["positif"] + c["negatif"]
                if total == 0:
                    continue
                pct_pos = int(c["positif"] / total * 100)
                pct_neg = int(c["negatif"] / total * 100)
                manuel = "✓" if c.get("manuel") else ""
                rows.append({
                    "mot": mot,
                    "pos": c["positif"],
                    "neg": c["negatif"],
                    "penchant": f"{pct_pos}% / {pct_neg}%",
                    "manuel": manuel,
                })
            df_reg = pd.DataFrame(rows)
            st.dataframe(df_reg, width="stretch", height=500)
        else:
            st.info("Aucun mot appris.")

with tab_prompt:
    st.markdown("### Prompt utilisé pour l'analyse")
    avis_exemple = "Super produit, livraison rapide !"
    st.code(construire_prompt(avis_exemple), language="markdown")
    st.info(
        "Le prompt ci-dessus est conçu pour une IA externe (ex: GPT). "
        "L'analyse actuelle utilise un moteur lexical local avec apprentissage."
    )
