# 1. Suppression des avertissements système (DeprecationWarning)
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

# 0. Installation des dépendances
!pip install --upgrade crewai litellm google-generativeai yfinance python-dotenv duckduckgo-search -q

import os
import nest_asyncio
import yfinance as yf
from duckduckgo_search import DDGS
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool



# 2. Gestion universelle de l'environnement (Local/Colab/Cloud)
nest_asyncio.apply()

try:

    os.environ["GEMINI_API_KEY"] = userdata.get('GEMINI_API_KEY')

    print("Environnement détecté : Google Colab")
except ImportError:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environnement détecté : Serveur Cloud / Local (via .env)")

# 3. Initialisation du modèle
cerveau_gemini = LLM(
    model="gemini/gemini-3.5-flash-lite",
    api_key=os.environ["GEMINI_API_KEY"]
)

# ==========================================
# 4. OUTILS DES AGENTS
# ==========================================
@tool("Outil de donnees de marche en direct")
def obtenir_donnees_marche(ticker: str) -> str:
    """Indispensable pour obtenir le vrai prix actuel et l'historique."""
    print(f"\n📡 [Analyste Technique] -> Extraction des prix pour : {ticker}")
    try:
        actif = yf.Ticker(ticker)
        historique = actif.history(period="5d")
        if historique.empty: return "Aucune donnée trouvée."
        prix_actuel = historique['Close'].iloc[-1]
        resume = f"PRIX ACTUEL : {prix_actuel:.2f}\n" + historique[['Open', 'High', 'Low', 'Close']].to_string()
        return resume
    except Exception as e: return f"Erreur de flux : {str(e)}"

@tool("Outil de recherche web actualites")
def rechercher_actualites_macro(requete: str) -> str:
    """Indispensable pour rechercher les actualités macroéconomiques et financières mondiales."""
    print(f"\n📰 [Analyste Macro] -> Recherche web autonome : '{requete}'")
    try:
        resultats = ""
        with DDGS() as ddgs:
            for r in ddgs.text(requete + " actualités économie finance", max_results=5):
                resultats += f"- Titre : {r['title']}\n- Résumé : {r['body']}\n\n"
        if not resultats: return "Aucune actualité récente trouvée."
        return resultats
    except Exception as e: return f"Erreur réseau : {str(e)}"

# ==========================================
# 5. LES AGENTS
# ==========================================
analyste_technique = Agent(
    role='Analyste Technique Senior',
    goal='Analyser l\'action des prix RÉELS, identifier la liquidité et les zones OTE.',
    backstory='Trader technique algorithmique. Tu te bases uniquement sur les chiffres exacts fournis par ton outil.',
    llm=cerveau_gemini,
    tools=[obtenir_donnees_marche],
    verbose=True,
    allow_delegation=False
)

analyste_fondamental = Agent(
    role='Économiste et Analyste Macroéconomique',
    goal='Scanner internet de façon autonome pour évaluer le climat géopolitique et économique.',
    backstory='Expert des marchés globaux. Tu lis l\'actualité avec ton outil de recherche pour anticiper les mouvements institutionnels.',
    llm=cerveau_gemini,
    tools=[rechercher_actualites_macro],
    verbose=True,
    allow_delegation=False
)

gestionnaire_risque = Agent(
    role='Chief Risk Officer (CRO) & Quantitative Trader',
    goal='Calculer au centime près le risque mathématique de la position et fournir une stratégie de gestion de position exhaustive.',
    backstory='Responsable de la gestion des risques dans un hedge fund. Tu appliques la gestion du risque strictement. Tu refuses de faire des conclusions vagues.',
    llm=cerveau_gemini,
    verbose=True,
    allow_delegation=False
)

# ==========================================
# 6. CONFIGURATION DE COMPTE & BOT
# ==========================================
ACTIF_CIBLE = "XAUUSD=X"
CAPITAL_TOTAL_USD = 10000.0  # Capital du portefeuille en $
POURCENTAGE_RISQUE_MAX = 1.0  # Risque maximal toléré par trade en %

# ==========================================
# 7. LES TÂCHES
# ==========================================
task_technique = Task(
    description=f'1. Utilise ton outil de marché pour récupérer les prix de {ACTIF_CIBLE}.\n2. Établis les zones de support, résistance et le point d\'entrée idéal (OTE).',
    expected_output='Rapport technique détaillé avec des prix exacts.',
    agent=analyste_technique
)

task_fondamentale = Task(
    description=f'1. Recherche l\'actualité économique et géopolitique récente pour {ACTIF_CIBLE}.\n2. Évalue l\'impact macroéconomique sur la tendance.',
    expected_output='Rapport géopolitique et macroéconomique temps réel.',
    agent=analyste_fondamental
)

task_decision = Task(
    description=f'''
    Analyse les rapports pour {ACTIF_CIBLE}.

    PARAMÈTRES DE GESTION DU RISQUE DU COMPTE :
    - Capital disponible : {CAPITAL_TOTAL_USD} $
    - Risque maximal autorisé : {POURCENTAGE_RISQUE_MAX} %

    CONSIGNES DE CALCUL ET DE RÉDACTION STRICTES :
    1. CALCUL DU RISQUE EN USD : Risque Max ($) = Capital * (Risque% / 100).
    2. DISTANCE DE STOP LOSS : Calcule la différence en points entre le prix d'entrée et le Stop Loss.
    3. TAILLE DU LOT EXACTE : Calcule la taille de lot à ouvrir selon la formule du marché pour cet actif.
    4. RATIO RISQUE / RENDEMENT (R:R) : Affiche la valeur exacte du ratio (ex: 1:2.5).
    5. CONCLUSION ÉTENDUE : Rédige une section "Conduite du Trade" complète décrivant la gestion post-entrée (Break-Even, fermetures partielles, invalides géopolitiques).
    ''',
    expected_output='Plan de trading institutionnel avec calculs de risque mathématiques et section de conduite détaillée.',
    agent=gestionnaire_risque
)

# ==========================================
# 8. EXÉCUTION DU SYSTÈME
# ==========================================
equipe_trading = Crew(
    agents=[analyste_technique, analyste_fondamental, gestionnaire_risque],
    tasks=[task_technique, task_fondamentale, task_decision],
    verbose=True
)

print(f"\n🚀 Calcul des risques et analyse globale pour : {ACTIF_CIBLE}...")
resultat_trading = await equipe_trading.kickoff_async()

print("\n\n========================================")
print(f"📊 PLAN DE TRADING & CALCUL DE RISQUE ({ACTIF_CIBLE}) :")
print("========================================\n")
print(resultat_trading)
