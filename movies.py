import random
from statistics import median
from movie_storage import movie_storage_sql as storage
from dotenv import load_dotenv
import os
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")


def command_list_movies():
    """Retrieve and display all movies from the database."""
    movies = storage.list_movies()
    print(f"{len(movies)} movies in total")
    for title, data in movies.items():
        print(f"{title} ({data['year']}): {data['rating']}")


def print_menu():
    """Show the main menu."""
    print("********** My Movies Database **********\n")
    print("Menu:")
    print("1. List movies")
    print("2. Add movie")
    print("3. Delete movie")
    print("4. Update movie")
    print("5. Stats")
    print("6. Random movie")
    print("7. Search movie")
    print("8. Movies sorted by rating")
    print("9. Generate website")
    print("0. Exit\n")


def pause():
    """Wait for Enter so output is readable."""
    input("Press enter to continue\n")


def get_valid_title():
    """Ask until we get a non-empty title."""
    while True:
        title = input("Enter movie name: ").strip()
        if title:
            return title
        print("Title cannot be empty.")


def get_valid_rating():
    """Ask until we get a float between 0 and 10."""
    while True:
        try:
            rating = float(input("Enter movie rating (0-10): ").strip())
            if 0 <= rating <= 10:
                return rating
            print("Rating must be between 0 and 10.")
        except ValueError:
            print("Please enter a number like 7.5")


def get_valid_year():
    """Ask until we get a year in a simple valid range."""
    while True:
        try:
            year = int(input("Enter year of release: ").strip())
            if 1888 <= year <= 2100:
                return year
            print("Please enter a year between 1888 and 2100.")
        except ValueError:
            print("Please enter digits only (e.g. 1999).")




def action_add_movie():
    """Add new movie by title using OMDb (Title, Year, Rating, Poster)."""
    import requests
    movies = storage.list_movies()
    title_input = get_valid_title()

    if title_input in movies:
        print(f"Movie '{title_input}' already exists.\n")
        pause()
        return

    try:
        resp = requests.get(
            "http://www.omdbapi.com/",
            params={"apikey": OMDB_API_KEY, "t": title_input},
            timeout=10
        )
        data = resp.json()
    except requests.RequestException:
        print("Network/API error. Please check your internet connection.\n")
        pause()
        return

    if not data or data.get("Response") == "False":
        print("Could not find this title via OMDb.\n")
        pause()
        return

    omdb_title = data.get("Title") or title_input

    year_str = str(data.get("Year", "")).strip()
    year = int(year_str[:4]) if year_str[:4].isdigit() else 0

    imdb_str = data.get("imdbRating", "N/A")
    try:
        rating = float(imdb_str) if imdb_str not in (None, "N/A") else 0.0
    except ValueError:
        rating = 0.0

    poster_url = data.get("Poster")
    if poster_url in (None, "N/A"):
        poster_url = ""

    storage.add_movie(omdb_title, year, rating, poster_url)
    print(f"Movie '{omdb_title}' added.\n")
    pause()


def action_delete_movie():
    """Delete by title (no error if missing)."""
    title = get_valid_title()
    storage.delete_movie(title)
    print(f"Movie '{title}' deleted (if it existed).\n")
    pause()


def action_update_movie():
    """Update rating by title."""
    title = get_valid_title()
    new_rating = get_valid_rating()
    storage.update_movie(title, new_rating)
    print(f"Movie '{title}' updated.\n")
    pause()


def action_stats():
    """Show avg, median, and all best/worst (handles ties)."""
    movies = storage.list_movies()
    if not movies:
        print("No movies in the database.\n")
        pause()
        return

    ratings = []
    for info in movies.values():
        ratings.append(info["rating"])

    avg = sum(ratings) / len(ratings)
    med = median(ratings)
    max_r = max(ratings)
    min_r = min(ratings)

    best_titles = []
    worst_titles = []
    for title, info in movies.items():
        if info["rating"] == max_r:
            best_titles.append(title)
        if info["rating"] == min_r:
            worst_titles.append(title)

    print(f"Average rating: {avg:.2f}")
    print(f"Median rating: {med:.2f}")
    print(f"Best rating: {max_r} — {', '.join(best_titles)}")
    print(f"Worst rating: {min_r} — {', '.join(worst_titles)}\n")
    pause()


def action_random_movie():
    """Pick one random movie."""
    movies = storage.list_movies()
    if not movies:
        print("No movies available.\n")
        pause()
        return
    title, info = random.choice(list(movies.items()))
    print(f"Your movie for tonight: {title} ({info['year']}), rated {info['rating']}\n")
    pause()


def action_search_movie():
    """Search by substring (case-insensitive)."""
    movies = storage.list_movies()
    query = input("Enter part of movie name: ").strip().lower()
    print()
    found_any = False
    for title, info in movies.items():
        if query in title.lower():
            print(f"{title}: {info['rating']} ({info['year']})")
            found_any = True
    if not found_any:
        print("No matches found.")
    print()
    pause()


def action_sorted_by_rating():
    """Show movies sorted by rating (highest first)."""
    movies = storage.list_movies()
    items_list = list(movies.items())
    sorted_items = sorted(items_list, key=lambda item: item[1]["rating"], reverse=True)
    for title, info in sorted_items:
        print(f"{title}: {info['rating']} ({info['year']})")
    print()
    pause()


def film_database():
    """Route menu choices to actions."""
    while True:
        print_menu()
        choice = input("Enter choice (0-9): ").strip()
        print()

        if choice == "1":
            command_list_movies()
        elif choice == "2":
            action_add_movie()
        elif choice == "3":
            action_delete_movie()
        elif choice == "4":
            action_update_movie()
        elif choice == "5":
            action_stats()
        elif choice == "6":
            action_random_movie()
        elif choice == "7":
            action_search_movie()
        elif choice == "8":
            action_sorted_by_rating()
        elif choice == "9":
            command_generate_website()
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid choice. Please enter 0–8.\n")
            pause()

from pathlib import Path


def _render_movie_card(title: str, year: int, poster_url: str) -> str:
    """Return one movie card HTML snippet for the template grid."""
    poster = poster_url or "https://via.placeholder.com/200x300?text=No+Image"
    return (
        f'<div class="movie">'
        f'  <img class="movie-poster" src="{poster}" alt="Poster for {title}">'
        f'  <div class="movie-title">{title}</div>'
        f'  <div class="movie-year">{year}</div>'
        f'</div>'
    )


def command_generate_website():
    """Generate index.html from the template (title only for step 1)."""
    template_path = Path("static/index_template.html")
    output_path = Path("static/index.html")


    html = template_path.read_text(encoding="utf-8")


    html = html.replace("__TEMPLATE_TITLE__", "My Movie App")  # Titel kannst du später parametrisieren


    movies = storage.list_movies()
    if movies:
        cards = []
        for title, info in movies.items():
            year = info.get("year", 0)
            poster_url = info.get("poster_url", "")
            cards.append(_render_movie_card(title, year, poster_url))
        grid_html = "\n".join(cards)
    else:
        grid_html = "<p>No movies yet. Add some in the app.</p>"

    html = html.replace("__TEMPLATE_MOVIE_GRID__", grid_html)

    output_path.write_text(html, encoding="utf-8")

    print("Website was generated successfully.")



