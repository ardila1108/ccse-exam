import streamlit as st
import json
import random
import os

# --- Configuration ---
st.set_page_config(page_title="Simulador Examen CCSE", page_icon="🇪🇸", layout="centered")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# --- Functions ---
@st.cache_data
def load_data():
    with open(os.path.join(DATA_DIR, "questions.json"), "r", encoding="utf-8") as f:
        questions = json.load(f)
    with open(os.path.join(DATA_DIR, "explanations.json"), "r", encoding="utf-8") as f:
        explanations = json.load(f)
    return questions, explanations

def init_session_state(questions):
    if 'selected_questions' not in st.session_state:
        # Balance distribution
        distribution = {1: 10, 2: 3, 3: 2, 4: 3, 5: 7}
        selected = []
        
        for task_id, count in distribution.items():
            task_qs = [q for q in questions.values() if q["task"] == task_id]
            # Handle cases where we might not have enough questions
            sample_size = min(count, len(task_qs))
            selected.extend(random.sample(task_qs, sample_size))
        
        # Shuffle the final list to mix tasks
        random.shuffle(selected)
        st.session_state.selected_questions = selected
    
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    if 'answers' not in st.session_state:
        st.session_state.answers = {}

def get_options_list(q):
    options = []
    option_keys = []
    if q.get("a"):
        options.append(f"A) {q['a']}")
        option_keys.append("a")
    if q.get("b"):
        options.append(f"B) {q['b']}")
        option_keys.append("b")
    if q.get("c"):
        options.append(f"C) {q['c']}")
        option_keys.append("c")
    return options, option_keys

def reset_exam():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- Main App ---
st.title("🇪🇸 Simulador Oficial Examen CCSE")
st.markdown("Ponte a prueba con este simulador que genera un examen con la misma estructura oficial (25 preguntas balanceadas por tareas).")

questions, explanations = load_data()
init_session_state(questions)

# Display questions
with st.form("exam_form"):
    for i, q in enumerate(st.session_state.selected_questions):
        st.markdown(f"**Pregunta {i+1}** (Tarea {q['task']}): {q['question']}")
        
        options, option_keys = get_options_list(q)
        
        # Determine index of previously selected answer if any
        prev_ans_key = st.session_state.answers.get(q['id'])
        index = 0
        if prev_ans_key in option_keys:
            index = option_keys.index(prev_ans_key)
            
        # Radio button for options
        choice = st.radio(
            "Selecciona una opción:", 
            options,
            index=index if prev_ans_key else None,
            key=f"q_{q['id']}",
            disabled=st.session_state.submitted
        )
        
        # Save choice to session state manually within form isn't strictly necessary for native components, 
        # but to keep track easily:
        if choice:
            # extract key
            ans_idx = options.index(choice)
            st.session_state.answers[q['id']] = option_keys[ans_idx]
            
        st.divider()
        
    submitted = st.form_submit_button("Finalizar Examen", disabled=st.session_state.submitted)
    if submitted:
        st.session_state.submitted = True
        st.rerun()

# --- Evaluation Section ---
if st.session_state.submitted:
    st.header("📊 Resultados del Examen")
    
    score = 0
    total = len(st.session_state.selected_questions)
    
    # Calculate score first
    for q in st.session_state.selected_questions:
        user_ans = st.session_state.answers.get(q['id'])
        if user_ans == q['answer']:
            score += 1
            
    # Display Score
    if score >= 15:
        st.success(f"### ¡Aprobado! Puntaje: {score} / {total}")
    else:
        st.error(f"### No Aprobado. Puntaje: {score} / {total}")
        
    st.markdown("Revisa tus respuestas a continuación:")
    
    # Review details
    for i, q in enumerate(st.session_state.selected_questions):
        user_ans = st.session_state.answers.get(q['id'])
        correct_ans = q['answer']
        is_correct = user_ans == correct_ans
        
        with st.expander(f"Pregunta {i+1} - {'✅ Correcta' if is_correct else '❌ Incorrecta'}"):
            st.markdown(f"**{q['question']}**")
            st.markdown(f"*Sección: Tarea {q['task']}*")
            
            # Show what user answered
            user_text = q.get(user_ans, "No respondida") if user_ans else "No respondida"
            correct_text = q.get(correct_ans, "")
            
            if is_correct:
                st.success(f"Tu respuesta: {user_ans.upper()}) {user_text}")
            else:
                st.error(f"Tu respuesta: {user_ans.upper() if user_ans else '-'}) {user_text}")
                st.info(f"Respuesta correcta: {correct_ans.upper()}) {correct_text}")
                
            # Explanation
            if q['id'] in explanations:
                st.markdown("**Explicación:**")
                st.markdown(explanations[q['id']])
                
    if st.button("🔄 Comenzar Nuevo Examen", on_click=reset_exam, type="primary"):
        pass

