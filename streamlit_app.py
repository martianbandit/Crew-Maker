import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

# Configuration Streamlit
st.set_page_config(page_title="CrewAI Manager", layout="wide")
st.title("CrewAI Manager : Gérer vos agents et tâches")

# Définition d'un outil personnalisé
@tool("Recherche Web")
def web_search(query: str) -> str:
    """Effectue une recherche web pour obtenir des informations pertinentes."""
    return f"Résultat fictif de la recherche pour: {query}"

# Initialisation des états
if "agents" not in st.session_state:
    st.session_state["agents"] = []

if "tasks" not in st.session_state:
    st.session_state["tasks"] = []

if "crew" not in st.session_state:
    st.session_state["crew"] = None

# Fonction pour afficher les agents créés
def display_agents():
    if st.session_state["agents"]:
        for i, agent in enumerate(st.session_state["agents"]):
            st.sidebar.write(f"**Agent {i+1}:** {agent.role}")
            if st.sidebar.button(f"Supprimer {agent.role}", key=f"del_agent_{i}"):
                st.session_state["agents"].pop(i)
                st.rerun()
    else:
        st.sidebar.write("Aucun agent créé.")

# Interface pour créer un agent
st.sidebar.header("Créer un Agent")
agent_name = st.sidebar.text_input("Nom de l'Agent", "Agent de Recherche")
agent_role = st.sidebar.text_input("Rôle", "Chercheur d'information")
agent_goal = st.sidebar.text_area("Objectif", "Fournir des informations pertinentes basées sur des recherches.")
memory = st.sidebar.checkbox("Activer la mémoire", True)
verbose = st.sidebar.checkbox("Mode verbeux", True)
llm_choice = st.sidebar.selectbox("Modèle LLM", ["gpt-3.5-turbo", "gpt-4"])

if st.sidebar.button("Ajouter Agent"):
    agent = Agent(
        role=agent_role,
        goal=agent_goal,
        backstory=f"Agent spécialisé dans la recherche d'informations sur {agent_goal}.",
        tools=[web_search],
        memory=memory,
        verbose=verbose,
        llm=llm_choice
    )
    st.session_state["agents"].append(agent)
    st.success(f"Agent {agent_name} ajouté avec succès !")
    st.rerun()

display_agents()

# Interface pour créer une tâche
st.sidebar.header("Créer une Tâche")
task_desc = st.sidebar.text_area("Description de la tâche", "Rechercher les dernières tendances en IA.")
expected_output = st.sidebar.text_area("Sortie attendue", "Liste des 5 principales tendances IA.")
selected_agent_idx = st.sidebar.selectbox("Attribuer à un agent", options=range(len(st.session_state["agents"])), format_func=lambda x: st.session_state["agents"][x].role if st.session_state["agents"] else "Aucun")

if st.sidebar.button("Ajouter Tâche"):
    if st.session_state["agents"]:
        task = Task(
            description=task_desc,
            expected_output=expected_output,
            agent=st.session_state["agents"][selected_agent_idx],
            async_execution=True
        )
        st.session_state["tasks"].append(task)
        st.success("Tâche ajoutée avec succès !")
        st.rerun()
    else:
        st.error("Veuillez créer un agent avant d'ajouter une tâche.")

# Affichage des tâches
if st.session_state["tasks"]:
    st.header("Tâches créées")
    for i, task in enumerate(st.session_state["tasks"]):
        st.write(f"**Tâche {i+1}:** {task.description}")
        if st.button(f"Exécuter la tâche {i+1}", key=f"run_task_{i}"):
            result = task.execute()
            st.subheader("Résultat de la tâche")
            st.write(result)
else:
    st.write("Aucune tâche ajoutée.")

# Interface pour créer un Crew
st.sidebar.header("Créer un Crew")
crew_name = st.sidebar.text_input("Nom du Crew", "Team Recherche")
process_type = st.sidebar.selectbox("Type de processus", ["séquentiel", "parallèle"])

if st.sidebar.button("Créer Crew"):
    if st.session_state["agents"] and st.session_state["tasks"]:
        process = Process.sequential if process_type == "séquentiel" else Process.parallel
        crew = Crew(agents=st.session_state["agents"], tasks=st.session_state["tasks"], process=process)
        st.session_state["crew"] = crew
        st.success(f"Crew '{crew_name}' créé avec succès !")
    else:
        st.error("Veuillez ajouter au moins un agent et une tâche.")

# Exécution du Crew
if st.session_state["crew"]:
    st.header("Exécuter le Crew")
    if st.button("Démarrer Crew"):
        results = st.session_state["crew"].kickoff()
        st.subheader("Résultat du Crew")
        st.write(results)

# Informations supplémentaires
st.sidebar.header("Informations")
st.sidebar.write("Cette application vous permet de gérer des agents CrewAI et d'exécuter des tâches.")