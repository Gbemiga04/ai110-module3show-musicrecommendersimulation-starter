"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

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
}


def print_recommendations(name: str, user_prefs: dict, recommendations: list) -> None:
    """Print a profile header and each ranked song with its score and reasons."""
    print("=" * 64)
    print(f"Profile: {name}")
    print(
        f"  mood={user_prefs['favorite_mood']}  genre={user_prefs['favorite_genre']}  "
        f"energy={user_prefs['target_energy']}  likes_acoustic={user_prefs['likes_acoustic']}"
    )
    print("=" * 64)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} - {song['artist']}")
        print(f"   Score: {score:.2f} / {MAX_SCORE:.1f}   ({song['genre']}, {song['mood']})")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(name, user_prefs, recommendations)


if __name__ == "__main__":
    main()
