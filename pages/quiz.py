import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="QuizApp", page_icon='favicon.png')
st.title("Exam")

questions = st.session_state.questions
passingScorePercent = st.session_state.passingScorePercent
passingScore = len(questions) * (passingScorePercent / 100)
user_answers = []

for i, row in questions.iterrows():
    question_key = f"q{i}"  # key used in shuffled_options dict

    st.write(f"**{i + 1}: {row['Question']}**")

    # Dynamically gather available options (Option A, B, C, etc.)
    # Check if columns exists in the index and if it is empty for the current row.
    option_cols = [col for col in row.index if col.startswith('Option') and pd.notna(row[col]) and str(row[col]).strip()]
    # Values of all the options
    option_values = [row[col] for col in option_cols]

    # Extract correct answer values based on letters
    correct_letters = [letter.strip().upper() for letter in row['Answer'].split(',')]
    correct_values = [option_values[ord(letter) - ord('A')] for letter in correct_letters]

    # Shuffle options and store them in session state if not already there
    if question_key not in st.session_state.shuffled_options:
        shuffled = option_values[:]
        random.shuffle(shuffled)
        st.session_state.shuffled_options[question_key] = shuffled
    else:
        shuffled = st.session_state.shuffled_options[question_key]

    # Create labeled options like "A. [Option]"
    labeled_options = [f"{chr(65 + j)}. {option}" for j, option in enumerate(shuffled)]

    # Determine selected answer(s)
    if len(correct_values) == 1:
        selected_label = st.radio(
            f"Select your answer for Q{i + 1}",
            labeled_options,
            index=None,
            key=question_key
        )
        selected_value = None
        # If the radio button is used get the value of the answer (using the index of the labeled option)
        if selected_label:
            selected_value = shuffled[labeled_options.index(selected_label)]
    else:
        st.markdown(f"**Select {len(correct_values)} answer(s)**")
        selected_labels = st.multiselect(
            f"Select your answers for Q{i + 1}",
            labeled_options,
            default=[],
            key=question_key
        )
        selected_value = [
            shuffled[labeled_options.index(label)] for label in selected_labels
        ]

    # Store answers for results phase
    value_to_label = {v: f"{chr(65 + shuffled.index(v))}." for v in shuffled}
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

        # print(value_to_label)

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

        correct_display = ', '.join(value_to_label[val] for val in correct_values)
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
