import streamlit as st

user_answers = st.session_state.user_answers
questions = st.session_state.questions
passingScorePercent = st.session_state.passingScorePercent
passingScore = len(questions) * (passingScorePercent / 100)

score = 0

st.set_page_config(page_title="QuizApp", page_icon='favicon.png')
st.title("Results")

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

st.caption("Tip: to save your answers click on the 3 dots on the top right > Print > Save to PDF")