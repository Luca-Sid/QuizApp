import streamlit as st
import pandas as pd

st.set_page_config(page_title="QuizApp",
                   page_icon='favicon.png')

st.title("QuizApp!")
st.caption("Version 1.1")
st.write("This app accepts question banks in a spreadsheet format. Download the sample file to fill out!")
with open('Example-spreadsheet.xlsx', 'rb') as file:
    data=file.read()
    st.download_button("Download",data,"Example-spreadsheet.xlsx")

st.subheader("Upload your question bank")
quizFile = st.file_uploader("Question bank file", type=['.xls','.xlsx'])
if quizFile:
    df = pd.read_excel(quizFile)

    if not st.toggle("Use all Questions", value = True):
        total_rows = len(df)
        st.write(f"Total rows (excluding header): {total_rows}")

        startRow = st.number_input(
            "Start row (1 = first question)", step=1, value=1,
            min_value=1, max_value=total_rows
        )
        endRow = st.number_input(
            "End row (inclusive)", step=1, value=total_rows,
            min_value=startRow, max_value=total_rows
        )

        # Adjust for 1-based indexing from user input
        df = df.iloc[startRow - 1:endRow]

    shuffle = st.toggle("Shuffle Questions", value=True, help="Decide if you want to randomize the order of questions.\n"                                                          "The order of the options (A, B, C, ...) will always be randomized.")
    if shuffle:
        questionNum = st.slider("How many questions for this run?", step=1,
                                      value=min(30,len(df)),min_value=1, max_value=len(df))
        st.session_state.questions = df.sample(questionNum).reset_index(drop=True)
    else:
        st.session_state.questions = df
        print(df.head())

    st.session_state.passingScorePercent = st.slider("What's the passing score % ?", step=1, min_value=1, max_value=100, value=65)

    # isTimeLimit = st.toggle("Time limit")
    # if isTimeLimit:
    #     TimeLimit = st.number_input("How many minutes?", value=30, step=1)
    # else: TimeLimit = None


    if st.button("Start!", type="primary"):
        st.session_state.shuffled_options = {}
        st.switch_page("pages/quiz.py")
