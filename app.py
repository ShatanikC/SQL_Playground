import streamlit as st
import sqlite3
import pandas as pd
import os
from streamlit_monaco_editor import st_monaco

st.set_page_config(page_title="SQL Learning Platform", layout="wide")
st.title("SQL Learning & Playground")

DB_DIR = "databases"
os.makedirs(DB_DIR, exist_ok=True)

# DB connection 
if "playground_db" not in st.session_state:
    st.session_state.playground_db = sqlite3.connect(
        os.path.join(DB_DIR, "playground.sqlite"), check_same_thread=False
    )

# Tab Creation
with st.container():
    tab1, tab2, tab3 = st.tabs(["Playground", "Learn SQL", "Quizzes"])
# Tab 1
with tab1:
    st.header("SQL Playground")
    conn = st.session_state.playground_db
    csv_file = st.file_uploader("Upload CSV", type=["csv"],help='Please Upload a CSV file type only')
    if csv_file:
        try:
            df = pd.read_csv(csv_file)
            table_name = st.text_input("Table name:", "uploaded_table",max_chars=50,help='Please enter a Proper Table Name for the uploaded data')
            if st.button("Create Table"):
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                st.success(f"Table '{table_name}' created.")
        except Exception as e:
            st.error(f"Failed to upload: {e}")
    st.markdown("SQL Editor")
    if "playground_query" not in st.session_state:
        st.session_state.playground_query = "SELECT * FROM employees;"
    query = st_monaco(
        language="sql",
        height="150px",
        value=st.session_state.playground_query,
        key="playground_monaco",
    )
    if st.button("Run Query"):
        st.session_state.playground_query = query 
        try:
            df = pd.read_sql_query(query, conn)
            st.success("Query successful")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error: {e}")

# Tab 2
with tab2:
    st.header("Learn SQL")
    if "learning_db" not in st.session_state:
        conn = sqlite3.connect(os.path.join(DB_DIR, "learning.sqlite"), check_same_thread=False)
        st.session_state.learning_db = conn
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS employees (id INTEGER, name TEXT, role TEXT, salary INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS departments (id INTEGER, name TEXT)")
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM employees")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO employees VALUES (?, ?, ?, ?)",
                [
                    (1, "Alice", "Engineer", 100000),
                    (2, "Bob", "Manager", 120000),
                    (3, "Charlie", "Analyst", 90000),
                ],
            )
            cursor.executemany(
                "INSERT INTO departments VALUES (?, ?)",
                [
                    (1, "Engineering"),
                    (2, "HR"),
                    (3, "Finance"),
                ],
            )
            conn.commit()
    conn = st.session_state.learning_db
    st.markdown("Example Table: `employees`")
    if st.checkbox("Show table preview"):
        df = pd.read_sql_query("SELECT * FROM employees", conn)
        st.dataframe(df)
    examples = {
        "List all employees": "SELECT * FROM employees;",
        "Find employees with salary > 100000": "SELECT * FROM employees WHERE salary > 100000;",
        "Count total employees": "SELECT COUNT(*) FROM employees;",
    }
    selected = st.selectbox("Choose a learning query:", list(examples.keys()))
    st.code(examples[selected], language="sql")
    if st.button("Run Example Query"):
        try:
            df = pd.read_sql_query(examples[selected], conn)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error: {e}")

# Tab 3
with tab3:
    DB_DIR = "databases"
    DB_EASY = os.path.join(DB_DIR, "quiz_easy.sqlite")
    DB_MEDIUM = os.path.join(DB_DIR, "quiz_medium.sqlite")
    DB_HARD = os.path.join(DB_DIR, "quiz_hard.sqlite")
    difficulty = st.selectbox("Select difficulty:", ["easy", "medium", "hard"])
    # Difficulty Level
    if difficulty == "easy":
        db_path = DB_EASY
    elif difficulty == "medium":
        db_path = DB_MEDIUM
    else:  # hard
        db_path = DB_HARD
    # Connect to Database
    if f"conn_{difficulty}" not in st.session_state:
        st.session_state[f"conn_{difficulty}"] = sqlite3.connect(db_path, check_same_thread=False)
    conn = st.session_state[f"conn_{difficulty}"]
    # Load quizzes 
    QUIZ_DB = os.path.join(DB_DIR, f"{difficulty}_quizzes.sqlite")
    quiz_conn = sqlite3.connect(QUIZ_DB)
    quiz_cursor = quiz_conn.cursor()
    quiz_cursor.execute(f"SELECT * FROM {difficulty}_quizzes ORDER BY id")
    quizzes = quiz_cursor.fetchall()
    # Session states
    if "current_quiz_index" not in st.session_state:
        st.session_state.current_quiz_index = 0
    if "quiz_query" not in st.session_state:
        st.session_state.quiz_query = ""
    current_index = st.session_state.current_quiz_index
    col1, col2 = st.columns([3, 2])
    with col1:
        if current_index < len(quizzes):
            quiz_row = quizzes[current_index]
            quiz_id, question, expected_query, validation_query = quiz_row
            st.header("SQL Quizzes")
            st.markdown(f"**Question: {question}**")

            user_query = st.text_area(
                "Write your SQL query here:",
                value=st.session_state.quiz_query,
                height=150,
                key="quiz_text_area"
            )
            if st.button("Submit Answer"):
                st.session_state.quiz_query = user_query
                try:
                    expected_df = pd.read_sql_query(validation_query, conn)
                    user_df = pd.read_sql_query(user_query, conn)
                    # Compare Dataframes
                    pd.testing.assert_frame_equal(
                        user_df.reset_index(drop=True),
                        expected_df.reset_index(drop=True),
                        check_dtype=False,
                        check_like=True
                    )
                    st.success("Correct! Moving on to next question...")
                    st.session_state.quiz_query = ""
                except AssertionError as e:
                    st.error("Not quite. Try again or compare your result below:")
                    st.markdown("**Your Result:**")
                    st.dataframe(user_df)
                    st.markdown("**Expected Result:**")
                    st.dataframe(expected_df)
                    st.text(f"Debug: {e}")
                except Exception as e:
                    st.error(f"Error in your query: {e}")
            if st.session_state.quiz_query == "":
                if st.button("Next Question"):
                    st.session_state.current_quiz_index += 1
                    st.session_state.quiz_query = ""  
                    st.rerun()            
                if st.button("Previous Question") and  st.session_state.current_quiz_index!=0:
                    st.session_state.current_quiz_index -= 1
                    st.session_state.quiz_query = ""  
                    st.rerun()          
        else:
            st.success("You've completed all the quizzes!")

    with col2:
        st.subheader("Table Preview")
        # Difficulty Level
        if difficulty == "easy":
            st.markdown("**employees**")
            employees_df = pd.read_sql_query("SELECT * FROM employees", conn)
            st.dataframe(employees_df)
        elif difficulty == "medium":
            st.markdown("**employees**")
            employees_df = pd.read_sql_query("SELECT * FROM employees", conn)
            st.dataframe(employees_df)
            st.markdown("**departments**")
            departments_df = pd.read_sql_query("SELECT * FROM departments", conn)
            st.dataframe(departments_df)
            st.markdown("**projects**")
            projects_df = pd.read_sql_query("SELECT * FROM projects", conn)
            st.dataframe(projects_df)
        else:  # hard
            st.markdown("**employees**")
            employees_df = pd.read_sql_query("SELECT * FROM employees", conn)
            st.dataframe(employees_df)
            st.markdown("**departments**")
            departments_df = pd.read_sql_query("SELECT * FROM departments", conn)
            st.dataframe(departments_df)
            st.markdown("**projects**")
            projects_df = pd.read_sql_query("SELECT * FROM projects", conn)
            st.dataframe(projects_df)
