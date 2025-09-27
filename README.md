# SQL Quiz App with Streamlit

This project is a web-based interactive SQL quiz application built using [Streamlit](https://streamlit.io/). It allows users to practice SQL queries at different difficulty levels — Easy, Medium, and Hard — and validate their answers in real-time against sample databases.

## Features

- Choose from **Easy**, **Medium**, or **Hard** difficulty levels
- Backed by **SQLite databases** for quiz questions and validation
- Validates your SQL answers against expected output
- Uses Streamlit `session_state` for tracking progress
- Fully dynamic and interactive UI
- Modular structure for quizzes and database loading

## Project Structure

sql-quiz-app/
├── app.py # Main Streamlit app
├── requirements.txt # Python dependencies
├── README.md # You're here!
├── databases/
│ ├── quiz_easy.sqlite # DB for easy level
│ ├── quiz_medium.sqlite # DB for medium level
│ ├── quiz_hard.sqlite # DB for hard level
│ ├── easy_quizzes.sqlite # Quiz questions for easy level
│ ├── medium_quizzes.sqlite # Quiz questions for medium level
│ └── hard_quizzes.sqlite # Quiz questions for hard level
└── .streamlit/