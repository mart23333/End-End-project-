
#import required libraries
import sqlite3
from datetime import datetime


DB_NAME = "quiz_knight.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
# create users table to store user information and scores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            high_score INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0
        )
    """)
# create scores table to store individual quiz attempts and details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            time_taken INTEGER NOT NULL,
            date_played TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_user(username):
    conn = connect_db()
    cursor = conn.cursor()
# add new user to the users table, ignoring duplicates
    cursor.execute("""
        INSERT OR IGNORE INTO users (username)
        VALUES (?)
    """, (username,))

    conn.commit()
    conn.close()

# save quiz attempt details to the scores table and update user statistics in the users table
def save_score(username, score, total_questions, correct_answers, time_taken):
    conn = connect_db()
    cursor = conn.cursor()

    date_played = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# insert new score record for the quiz attempt
    cursor.execute("""
        INSERT INTO scores (
            username,
            score,
            total_questions,
            correct_answers,
            time_taken,
            date_played
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        username,
        score,
        total_questions,
        correct_answers,
        time_taken,
        date_played
    ))
# update user overall statistics after a quiz attempt
    cursor.execute("""
        UPDATE users
        SET
            games_played = games_played + 1,
            total_score = total_score + ?,
            high_score = CASE
                WHEN ? > high_score THEN ?
                ELSE high_score
            END
        WHERE username = ?
    """, (score, score, score, username))

    conn.commit()
    conn.close()

# retrieve top users for the leaderboard, ordered by high score 
def get_leaderboard(limit=10):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT username, high_score, games_played, total_score
        FROM users
        ORDER BY high_score DESC
        LIMIT ?
    """, (limit,))

    results = cursor.fetchall()
    conn.close()

    return results

# retrieve recent quiz attempts for a specific user, ordered by most recent first
def get_user_history(username):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT score, total_questions, correct_answers, time_taken, date_played
        FROM scores
        WHERE username = ?
        ORDER BY id DESC
        LIMIT 10
    """, (username,))

    results = cursor.fetchall()
    conn.close()

    return results