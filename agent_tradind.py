# 0. On force la mise à jour des bibliothèques
!pip install --upgrade crewai litellm google-generativeai -q

import os
import nest_asyncio
from google.colab import userdata
from crewai import Agent, Task, Crew, LLM

# 1. On règle le conflit Colab
nest_asyncio.apply()

# 2. Récupération de la clé API
os.environ["GEMINI_API_KEY"] = userdata.get('GEMINI_API_KEY')

# 3. Le cerveau Gemini (Méthode native corrigée)
cerveau_gemini = LLM(
    model="gemini/gemini-3.5-flash-lite",
    api_key=os.environ["GEMINI_API_KEY"]
)

# --- LES AGENTS ---
analyste_technique = Agent(
    role='Analyste Technique Senior',
    goal='Analyser l\'action des prix, identifier les zones OTE (Optimal Trade Entry) et lire les indicateurs (RSI, moyennes mobiles) pour trouver le meilleur point d\'entrée.',
    backstory='Tu es un trader technique impitoyable. Tu ne prends des décisions que sur la base des mathématiques, des structures de marché et de la liquidité.',
    llm=cerveau_gemini,
    verbose=True,
    allow_delegation=False
)

analyste_fondamental = Agent(
    role='Économiste et Analyste Macro',
    goal='Évaluer l\'impact des événements économiques récents (NFP, taux de la Fed, géopolitique) sur la paire de devises ou la matière première étudiée.',
    backstory='Tu es un expert des banques centrales. Tu sais exactement comment une déclaration de la Réserve Fédérale ou une crise géopolitique va influencer les marchés.',
    llm=cerveau_gemini,
    verbose=True,
    allow_delegation=False
)

gestionnaire_risque = Agent(
    role='Gestionnaire de Risques et Lead Trader',
    goal='Synthétiser les analyses techniques et fondamentales, définir la taille de lot appropriée et émettre le signal de trading final.',
    backstory='Tu es le patron du desk de trading. Ton but absolu est de protéger le capital. Tu n\'autorises un trade que si le ratio risque/récompense est excellent.',
    llm=cerveau_gemini,
    verbose=True,
    allow_delegation=True
)

# --- DEMANDE INTERACTIVE ---
actif_a_analyser = input("📈 Quel actif veux-tu analyser aujourd'hui (ex: XAU/USD, EUR/USD) ? : ")
contexte_actuel = input("📰 Y a-t-il une news ou une configuration spécifique (ex: NFP à 14h30, RSI sur-vendu H1) ? : ")

# --- LES TÂCHES ---
task_technique = Task(
    description=f'Analyse l\'actif {actif_a_analyser}. Le contexte donné est : {contexte_actuel}. Identifie les zones de support/résistance clés et donne une probabilité de mouvement basée sur l\'analyse technique.',
    expected_output='Un rapport technique détaillé sur les niveaux de prix clés.',
    agent=analyste_technique
)

task_fondamentale = Task(
    description=f'Analyse le climat économique actuel autour de {actif_a_analyser}. Tiens compte du contexte : {contexte_actuel}. Détermine si les fondamentaux sont haussiers ou baissiers.',
    expected_output='Un résumé de la tendance macroéconomique.',
    agent=analyste_fondamental
)

task_decision = Task(
    description=f'Prends les rapports technique et fondamental pour {actif_a_analyser}. Rédige un plan de trading final incluant : 1) Le signal (Achat/Vente/Rien) 2) Le point d\'entrée idéal 3) Le Stop Loss 4) Le Take Profit 5) Un conseil sur le money management (lot size).',
    expected_output='Un plan de trading exécutable et sécurisé.',
    agent=gestionnaire_risque
)

# --- LE CREW ---
equipe_trading = Crew(
    agents=[analyste_technique, analyste_fondamental, gestionnaire_risque],
    tasks=[task_technique, task_fondamentale, task_decision],
    verbose=True
)

print(f"\n🚀 L'équipe analyse {actif_a_analyser}... (Patiente un instant)")
resultat_trading = await equipe_trading.kickoff_async()
print("\n\n========================================")
print(f"📊 PLAN DE TRADING FINAL POUR {actif_a_analyser} :")
print("========================================\n")
print(resultat_trading)