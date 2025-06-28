import streamlit as st
import random
import pandas as pd

@st.dialog("Are you sure?")
def confirmation():
    st.markdown(f"The following questions have been marked for review:")
    st.markdown(''.join([f"- {i+1} \n" for i in flagged_questions]))
    st.markdown("**Close this dialog to review your answers**")
    if st.button("I'm sure, I want to submit my answers."):
        submit()

def submit():
    st.session_state.user_answers = user_answers
    st.switch_page('pages/results.py')

st.set_page_config(page_title="QuizApp", page_icon='favicon.png')
st.title("Exam")

questions = st.session_state.questions
user_answers = []
flagged_questions = []

for i, row in questions.iterrows():
    question_key = f"q{i}"  # key used in shuffled_options dict
    st.html(f"<span style='font-weight:600'>{i + 1}: {row['Question']}</span>")

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

    if st.checkbox("Flag question for later review", key=f"flag_{question_key}", label_visibility='visible'):
        flagged_questions.append(i)

    st.html("<br>")

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
    if flagged_questions:
        confirmation()
    else:
        submit()
