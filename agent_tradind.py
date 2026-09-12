# 0. Installation des dépendances nécessaires
!pip install --upgrade crewai litellm google-generativeai yfinance python-dotenv -q

import os
import nest_asyncio
import yfinance as yf
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

# 1. Gestion universelle de l'environnement (Colab vs Local/Cloud)
nest_asyncio.apply()

try:
    from google.colab import userdata
    os.environ["GEMINI_API_KEY"] = userdata.get('GEMINI_API_KEY')
    print("Environnement détecté : Google Colab")
except ImportError:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environnement détecté : Local/Cloud (via .env)")

# 2. Initialisation du modèle Gemini
cerveau_gemini = LLM(
    model="gemini/gemini-3.5-flash-lite",
    api_key=os.environ["GEMINI_API_KEY"]
)

# 3. Outil de marché en direct (yfinance)
@tool("Outil de donnees de marche en direct")
def obtenir_donnees_marche(ticker: str) -> str:
    """
    Indispensable pour obtenir le vrai prix actuel et l'historique récent d'un actif boursier.
    Exemples de symboles : 'XAUUSD=X' pour l'Or, 'EURUSD=X' pour l'Euro, 'BTC-USD' pour le Bitcoin.
    """
    print(f"\n📡 [L'Analyste Technique interroge le marché] -> Ticker : {ticker}")
    try:
        actif = yf.Ticker(ticker)
        historique = actif.history(period="5d")
        if historique.empty:
            return f"Aucune donnée trouvée pour le ticker {ticker}. Vérifie le symbole."
            
        prix_actuel = historique['Close'].iloc[-1]
        
        resume = f"Données réelles pour {ticker}:\n"
        resume += f"▶ PRIX ACTUEL : {prix_actuel:.2f}\n\n"
        resume += "▶ HISTORIQUE DES 5 DERNIERS JOURS :\n"
        resume += historique[['Open', 'High', 'Low', 'Close']].to_string()
        
        return resume
    except Exception as e:
        return f"Erreur lors de la connexion au marché : {str(e)}"

# 4. Définition des Agents
analyste_technique = Agent(
    role='Analyste Technique Senior',
    goal='Analyser l\'action des prix RÉELS, identifier les zones OTE et lire les structures de marché.',
    backstory='Trader technique impitoyable. Utilise TOUJOURS son outil de marché pour récupérer les vrais prix avant de parler.',
    llm=cerveau_gemini,
    tools=[obtenir_donnees_marche],
    verbose=True,
    allow_delegation=False
)

analyste_fondamental = Agent(
    role='Économiste et Analyste Macro',
    goal='Évaluer l\'impact des événements économiques récents sur l\'actif étudié.',
    backstory='Expert des banques centrales. Analyse l\'influence des annonces macroéconomiques sur les cours.',
    llm=cerveau_gemini,
    verbose=True,
    allow_delegation=False
)

gestionnaire_risque = Agent(
    role='Gestionnaire de Risques et Lead Trader',
    goal='Synthétiser les analyses, définir la taille de lot optimale et émettre le plan de trading final.',
    backstory='Patron du desk de trading. Protège le capital et exige des chiffres précis.',
    llm=cerveau_gemini,
    verbose=True,
    allow_delegation=True
)

# 5. Interface utilisateur interactive
print("\n💡 ASTUCE SYMBOL : Pour l'Or, tape XAUUSD=X | Pour l'Euro, tape EURUSD=X | Pour le Bitcoin, tape BTC-USD")
actif_a_analyser = input("📈 Quel actif veux-tu analyser aujourd'hui ? : ")
contexte_actuel = input("📰 Y a-t-il une news ou un contexte spécifique ? : ")

# 6. Définition des Tâches
task_technique = Task(
    description=f'1. UTILISE obligatoirement ton outil de marché pour obtenir les prix de {actif_a_analyser}.\n2. En te basant sur ces VRAIS chiffres, identifie les supports/résistances.\n3. Tiens compte du contexte : {contexte_actuel}.',
    expected_output='Un rapport technique listant le prix actuel réel et les zones d\'intervention mathématiques.',
    agent=analyste_technique
)

task_fondamentale = Task(
    description=f'Analyse le climat économique actuel autour de {actif_a_analyser}. Contexte : {contexte_actuel}. Détermine la tendance macro.',
    expected_output='Un résumé de la tendance macroéconomique.',
    agent=analyste_fondamental
)

task_decision = Task(
    description=f'Prends les rapports pour {actif_a_analyser}. Rédige un plan de trading final incluant : 1) Signal 2) Point d\'entrée précis basé sur les vrais prix 3) Stop Loss 4) Take Profit 5) Money management.',
    expected_output='Un plan de trading exécutable et chiffré.',
    agent=gestionnaire_risque
)

# 7. Assemblage et Lancement de l'équipe (Asynchrone)
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