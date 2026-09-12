# 0. Ajout de yfinance à la liste des installations
!pip install --upgrade crewai litellm google-generativeai yfinance -q

import os
import nest_asyncio
import yfinance as yf
from google.colab import userdata
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

# 1. Configuration de base
nest_asyncio.apply()
os.environ["GEMINI_API_KEY"] = userdata.get('GEMINI_API_KEY')

cerveau_gemini = LLM(
    model="gemini/gemini-3.5-flash-lite",
    api_key=os.environ["GEMINI_API_KEY"]
)

# ==========================================
# 2. NOUVEL OUTIL : CONNEXION AU MARCHÉ
# ==========================================
@tool("Outil de donnees de marche en direct")
def obtenir_donnees_marche(ticker: str) -> str:
    """
    Indispensable pour obtenir le vrai prix actuel et l'historique récent (5 derniers jours) d'un actif boursier.
    ATTENTION : Utilise les symboles Yahoo Finance (ex: 'XAUUSD=X' pour l'Or, 'EURUSD=X' pour l'Euro, 'BTC-USD' pour le Bitcoin).
    """
    print(f"\n📡 [L'Analyste Technique interroge le marché] -> Ticker : {ticker}")
    try:
        actif = yf.Ticker(ticker)
        # On récupère les bougies des 5 derniers jours
        historique = actif.history(period="5d")
        if historique.empty:
            return f"Aucune donnée trouvée pour le ticker {ticker}. Vérifie le symbole."
            
        prix_actuel = historique['Close'].iloc[-1]
        
        # On formate les données pour que l'IA puisse les lire facilement
        resume = f"Données réelles pour {ticker}:\n"
        resume += f"▶ PRIX ACTUEL : {prix_actuel:.2f}\n\n"
        resume += "▶ HISTORIQUE DES 5 DERNIERS JOURS (Bougies Journalières) :\n"
        resume += historique[['Open', 'High', 'Low', 'Close']].to_string()
        
        return resume
    except Exception as e:
        return f"Erreur lors de la connexion au marché : {str(e)}"

# ==========================================
# 3. LES AGENTS
# ==========================================
analyste_technique = Agent(
    role='Analyste Technique Senior',
    goal='Analyser l\'action des prix RÉELS, identifier les zones OTE et lire les structures de marché pour trouver le meilleur point d\'entrée.',
    backstory='Tu es un trader technique impitoyable. Tu utilises TOUJOURS ton outil de marché pour récupérer les vrais prix avant de parler. Tu ne devines jamais un prix.',
    llm=cerveau_gemini,
    tools=[obtenir_donnees_marche], # <--- On donne le terminal de trading à l'analyste !
    verbose=True,
    allow_delegation=False
)

analyste_fondamental = Agent(
    role='Économiste et Analyste Macro',
    goal='Évaluer l\'impact des événements économiques récents sur l\'actif étudié.',
    backstory='Tu es un expert des banques centrales. Tu sais exactement comment une déclaration économique influence les marchés.',
    llm=cerveau_gemini,
    verbose=True,
    allow_delegation=False
)

gestionnaire_risque = Agent(
    role='Gestionnaire de Risques et Lead Trader',
    goal='Synthétiser les analyses, définir la taille de lot appropriée et émettre le signal de trading final.',
    backstory='Tu es le patron du desk de trading. Ton but absolu est de protéger le capital. Tu exiges des chiffres précis.',
    llm=cerveau_gemini,
    verbose=True,
    allow_delegation=True
)

# ==========================================
# 4. INTERFACE UTILISATEUR
# ==========================================
print("💡 ASTUCE SYMBOL : Pour l'Or, tape XAUUSD=X | Pour l'Euro, tape EURUSD=X | Pour le Bitcoin, tape BTC-USD")
actif_a_analyser = input("📈 Quel actif veux-tu analyser aujourd'hui ? : ")
contexte_actuel = input("📰 Y a-t-il une news ou un contexte spécifique ? : ")

# ==========================================
# 5. LES TÂCHES
# ==========================================
task_technique = Task(
    description=f'1. UTILISE obligatoirement ton outil de marché pour obtenir les prix de {actif_a_analyser}.\n2. En te basant sur ces VRAIS chiffres, identifie les supports/résistances.\n3. Tiens compte du contexte : {contexte_actuel}.',
    expected_output='Un rapport technique listant le prix actuel réel et les zones d\'intervention mathématiques.',
    agent=analyste_technique
)

task_fondamentale = Task(
    description=f'Analyse le climat économique actuel autour de {actif_a_analyser}. Tiens compte du contexte : {contexte_actuel}. Détermine la tendance macro.',
    expected_output='Un résumé de la tendance macroéconomique.',
    agent=analyste_fondamental
)

task_decision = Task(
    description=f'Prends les rapports pour {actif_a_analyser}. Rédige un plan de trading final incluant : 1) Signal 2) Point d\'entrée précis basé sur les vrais prix 3) Stop Loss 4) Take Profit 5) Money management.',
    expected_output='Un plan de trading exécutable et chiffré.',
    agent=gestionnaire_risque
)

equipe_trading = Crew(
    agents=[analyste_technique, analyste_fondamental, gestionnaire_risque],
    tasks=[task_technique, task_fondamentale, task_decision],
    verbose=True
)

print(f"\n🚀 L'équipe se connecte aux serveurs boursiers pour analyser {actif_a_analyser}...")
resultat_trading = await equipe_trading.kickoff_async()

print("\n\n========================================")
print(f"📊 PLAN DE TRADING FINAL POUR {actif_a_analyser} :")
print("========================================\n")
print(resultat_trading)