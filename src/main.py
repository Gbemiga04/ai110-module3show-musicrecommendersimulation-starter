"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import textwrap

from src.recommender import load_songs, recommend_songs

MAX_SCORE = 5.0  # mood 2.0 + energy 1.5 + genre 1.0 + acoustic 0.5

PROFILES = {
    # Starter profile: upbeat pop listener
    "Happy Pop": {
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "favorite_genre": "pop",
        "likes_acoustic": False,
    },
    # My profile: mood-first listener who wants calm, acoustic study music
    "Chill Lofi": {
        "favorite_mood": "chill",
        "target_energy": 0.4,
        "favorite_genre": "lofi",
        "likes_acoustic": True,
    },
    # Loud, dark guitar music
    "Deep Intense Rock": {
        "favorite_mood": "intense",
        "target_energy": 0.9,
        "favorite_genre": "rock",
        "likes_acoustic": False,
    },
    # --- Adversarial / edge-case profiles ---
    # Conflicting: a sad mood usually means low energy
    "Sad but Hyped": {
        "favorite_mood": "sad",
        "target_energy": 0.9,
        "favorite_genre": "blues",
        "likes_acoustic": False,
    },
    # Conflicting: metal is almost never acoustic
    "Acoustic Headbanger": {
        "favorite_mood": "angry",
        "target_energy": 0.95,
        "favorite_genre": "metal",
        "likes_acoustic": True,
    },
    # Genre and mood that don't exist in the catalog
    "Unknown Tastes": {
        "favorite_mood": "dreamy",
        "target_energy": 0.5,
        "favorite_genre": "k-pop",
        "likes_acoustic": False,
    },
    # Bad input: capitalized labels and energy outside 0-1
    "Sloppy Input": {
        "favorite_mood": "Chill",
        "target_energy": 1.5,
        "favorite_genre": "Lofi",
        "likes_acoustic": True,
    },
}


COLUMNS = [("#", 2), ("Song", 24), ("Score", 5), ("Reasons", 46)]


def table_row(cells: list) -> list:
    """Turn one row of cells (each a list of text lines) into padded ASCII table lines."""
    height = max(len(lines) for lines in cells)
    out = []
    for i in range(height):
        parts = []
        for lines, (_, width) in zip(cells, COLUMNS):
            text = lines[i] if i < len(lines) else ""
            parts.append(text.ljust(width))
        out.append("| " + " | ".join(parts) + " |")
    return out


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Print a profile header, an ASCII table of ranked songs with scores and reasons, and a summary line."""
    border = "+" + "+".join("-" * (width + 2) for _, width in COLUMNS) + "+"

    print(f"Profile: {name}")
    print(
        f"  mood={user_prefs['favorite_mood']}  genre={user_prefs['favorite_genre']}  "
        f"energy={user_prefs['target_energy']}  likes_acoustic={user_prefs['likes_acoustic']}"
    )
    print(border)
    print("\n".join(table_row([[title] for title, _ in COLUMNS])))
    print(border.replace("-", "="))

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        song_lines = [song["title"], f"by {song['artist']}", f"{song['genre']} / {song['mood']}"]
        reason_lines = []
        for reason in explanation.split("; "):
            reason_lines.extend(textwrap.wrap(reason, width=COLUMNS[3][1], initial_indent="- ", subsequent_indent="  "))
        print("\n".join(table_row([[str(rank)], song_lines, [f"{score:.2f}"], reason_lines])))
        print(border)

    artists = {song["artist"] for song, _, _ in recommendations}
    genres = {song["genre"] for song, _, _ in recommendations}
    top_song, top_score, _ = recommendations[0]
    print(
        f"Summary: top pick {top_song['title']} ({top_score:.2f} / {MAX_SCORE:.1f}) | "
        f"{len(artists)} artists | {len(genres)} genres\n"
    )


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)


if __name__ == "__main__":
    main()
