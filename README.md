# Multi_agent_trading_analyst
Architecture initial des agents de trading.
# AI Trading Agents Suite

Système multi-agents autonome propulsé par **CrewAI** et **Gemini** pour l'analyse des marchés financiers en temps réel.

## Architecture
* **Analyste Technique Senior** : Récupère les prix réels via `yfinance` et identifie les zones clés.
* **Analyste Macroéconomique** : Analyse l'impact des actualités et du contexte économique.
* **Gestionnaire de Risques** : Synthétise les rapports pour fournir un plan de trading chiffré (Signal, Entrée, Stop Loss, Take Profit, Money Management).

## Stack Technique
* **Framework** : CrewAI, LiteLLM
* **Modèle** : Gemini 3.5 Flash-Lite
* **Données** : Yahoo Finance (`yfinance`)
* **Données** : duckduckgo-search
