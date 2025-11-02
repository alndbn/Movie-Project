# Movie App

A Python application to manage a movie collection.
Movies are fetched automatically from the OMDb API and stored in an SQLite database.
A static website can be generated to display the movies.

---

## Features

- Add movies by title (data from OMDb API)
- Store movies (title, year, rating, poster)
- Delete & update movies
- Statistics (average, median, best/worst)
- Random movie suggestion
- Generate HTML movie gallery

---

## How to Run

-Create and activate a virtual environment (optional but recommended) 
python -m venv .venv
source .venv/bin/activate

-Install dependencies:
pip install -r requirements.txt

-Create a `.env` file in the project folder with:
OMDB_API_KEY=your_api_key_here

-Run the app:
python main.py

---


That's it, enjoy.




