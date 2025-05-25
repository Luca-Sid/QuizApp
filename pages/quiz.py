import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="QuizApp", page_icon='favicon.png')
st.title("Exam")

questions = st.session_state.questions
passingScorePercent = st.session_state.passingScore
passingScore = len(questions) * (passingScorePercent / 100)

# Store shuffled option states in session state only once
if 'shuffled_options' not in st.session_state:
    st.session_state.shuffled_options = {}

user_answers = []

# Phase 1: Initial selection UI
for i, row in questions.iterrows():
    question_key = f"q{i}"

    st.write(f"**{i + 1}: {row['Question']}**")

    # Build options dynamically including Option E if available and non-empty
    original_options = [row['Option A'], row['Option B'], row['Option C'], row['Option D']]

    # Only include Option E if column exists AND cell is not empty or NaN
    if 'Option E' in questions.columns and pd.notna(row['Option E']) and str(row['Option E']).strip():
        original_options.append(row['Option E'])

    # Extract correct answers
    correct_letters = [letter.strip().upper() for letter in row['Answer'].split(',')]
    correct_values = [original_options[ord(letter) - ord('A')] for letter in correct_letters]

    # Shuffle once and store in session_state
    if question_key not in st.session_state.shuffled_options:
        shuffled = original_options[:]
        random.shuffle(shuffled)
        st.session_state.shuffled_options[question_key] = shuffled
    else:
        shuffled = st.session_state.shuffled_options[question_key]

    # Label options A., B., C., ...
    labeled_options = [f"{chr(65 + j)}. {option}" for j, option in enumerate(shuffled)]
    option_label_to_value = dict(zip(labeled_options, shuffled))
    value_to_label = {v: k for k, v in option_label_to_value.items()}

    if len(correct_letters) == 1:
        selected_label = st.radio(
            f"Select your answer for Q{i + 1}",
            labeled_options,
            index=None,
            key=question_key
        )
        selected_value = option_label_to_value[selected_label] if selected_label else None
    else:
        st.markdown(f"**Select {len(correct_letters)} answer(s)**")
        selected_labels = st.multiselect(
            f"Select your answers for Q{i + 1}",
            labeled_options,
            default=[],
            key=question_key
        )
        selected_value = [option_label_to_value[label] for label in selected_labels]

    user_answers.append((
        selected_value,
        correct_values,
        row['Question'],
        shuffled,
        value_to_label
    ))

# Phase 2: Submission and feedback rendering
if st.button("Submit"):
    score = 0
    st.subheader("Results")

    for i, (user_answer, correct_values, question_text, options, value_to_label) in enumerate(user_answers):
        user_answer_list = user_answer if isinstance(user_answer, list) else [user_answer]

        is_correct = set(user_answer_list) == set(correct_values)
        if is_correct:
            score += 1

        bg_color = "#d4edda" if is_correct else "#f8d7da"
        text_color = "#155724" if is_correct else "#721c24"

        st.markdown(f"""
        <div style="background-color:{bg_color}; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
            <strong style="color:{text_color};">Q{i + 1}: {question_text}</strong><br><br>
        """, unsafe_allow_html=True)

        for j, opt in enumerate(options):
            label = f"{chr(65 + j)}. {opt}"
            checked = opt in user_answer_list
            st.checkbox(label, value=checked, disabled=True, key=f"result_q{i}_{j}")

        correct_display = ', '.join(f"{value_to_label[val]}" for val in correct_values)
        explanation_html = ""

        if "Explanation" in questions.columns:
            explanation = questions.iloc[i].get('Explanation', None)
            if explanation and isinstance(explanation, str):
                explanation_html = f"<br><em style='color:{text_color};'>Explanation: {explanation}</em>"

        st.markdown(f"""
            <br><span style="color:{text_color};"><strong>{'Correct!' if is_correct else 'Incorrect.'}</strong> Correct answer(s): {correct_display}</span>
            {explanation_html}
        </div>
        """, unsafe_allow_html=True)

    percentage = round(score / len(questions) * 100, 2)
    if score >= passingScore:
        st.balloons()
        st.success(f"You scored {score} out of {len(questions)}. ({percentage}%)")
    else:
        st.error(f"You scored {score} out of {len(questions)}. ({percentage}%)")
