import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv into a list of dicts, converting numeric columns to int/float."""
    print(f"Loading songs from {csv_path}...")
    int_fields = {"id"}
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness"}

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user prefs (mood, energy closeness, genre, acoustic fit) and return (score, reasons)."""
    score = 0.0
    reasons = []

    # Mood is the main signal: +2.0 for an exact match
    if song["mood"] == user_prefs["favorite_mood"]:
        score += 2.0
        reasons.append(f"mood match: {song['mood']} (+2.0)")

    # Energy rewards closeness to the target, not higher or lower values
    energy_points = 1.5 * (1 - abs(song["energy"] - user_prefs["target_energy"]))
    score += energy_points
    reasons.append(f"energy {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} (+{energy_points:.2f})")

    # Genre is a smaller bonus: +1.0 for an exact match
    if song["genre"] == user_prefs["favorite_genre"]:
        score += 1.0
        reasons.append(f"genre match: {song['genre']} (+1.0)")

    # Acoustic fit: reward acoustic songs for acoustic fans, electronic songs otherwise
    if user_prefs.get("likes_acoustic", False):
        acoustic_points = 0.5 * song["acousticness"]
        label = "acoustic sound"
    else:
        acoustic_points = 0.5 * (1 - song["acousticness"])
        label = "electronic sound"
    score += acoustic_points
    reasons.append(f"{label} (+{acoustic_points:.2f})")

    return score, reasons

ARTIST_PENALTY = 1.0  # per song by the same artist already in the list
GENRE_PENALTY = 0.5   # per song of the same genre already in the list

def diversity_penalty(song: Dict, selected: List[Tuple[Dict, float, List[str]]]) -> Tuple[float, List[str]]:
    """Return the points to subtract for repeating an artist or genre already picked, plus reasons."""
    artist_repeats = sum(1 for picked, _, _ in selected if picked["artist"] == song["artist"])
    genre_repeats = sum(1 for picked, _, _ in selected if picked["genre"] == song["genre"])

    penalty = 0.0
    reasons = []
    if artist_repeats:
        points = ARTIST_PENALTY * artist_repeats
        penalty += points
        reasons.append(f"diversity: {song['artist']} already listed (-{points:.1f})")
    if genre_repeats:
        points = GENRE_PENALTY * genre_repeats
        penalty += points
        reasons.append(f"diversity: {song['genre']} already listed (-{points:.1f})")
    return penalty, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, diversity: bool = True) -> List[Tuple[Dict, float, str]]:
    """Score every song, then pick the top k one at a time, penalizing repeated artists/genres when diversity is on."""
    # Judge every song with score_song
    scored = [(song, *score_song(user_prefs, song)) for song in songs]

    # Highest score first; ties go to the song closer to the target energy
    target = user_prefs["target_energy"]
    ranked = sorted(
        scored,
        key=lambda item: (item[1], -abs(item[0]["energy"] - target)),
        reverse=True,
    )

    if not diversity:
        return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked[:k]]

    # Greedy re-rank: each pick is the best song after subtracting penalties
    # for artists and genres already in the list
    selected = []
    remaining = list(ranked)
    while remaining and len(selected) < k:
        def adjusted(item):
            song, score, _ = item
            return (score - diversity_penalty(song, selected)[0], -abs(song["energy"] - target))

        best = max(remaining, key=adjusted)
        remaining.remove(best)
        song, score, reasons = best
        penalty, penalty_reasons = diversity_penalty(song, selected)
        selected.append((song, score - penalty, reasons + penalty_reasons))

    return [(song, score, "; ".join(reasons)) for song, score, reasons in selected]
