# --- deps expected in scope ---
import os, re, string
from time import process_time_ns

import networkx as nx
from typing import Dict, List, Optional

from Classes.utils import all_maximal_common_phrases, tokenize


class LyricsPreprocessor:
    """
    Helper class encapsulating lyric-cleaning steps used in preprocessing.
    Mirrors the existing underscore-prefixed helpers as static methods.
    """

    @staticmethod
    def _remove_doubles(s: str) -> str:
        s = re.sub(r" +", " ", s)
        s = re.sub(r"\n+", "\n", s)
        return s

    @staticmethod
    def _remove_speaker_pattern(s: str) -> str:
        return re.sub(r"\[.*?]", "", s)

    @staticmethod
    def _remove_tabs(s: str) -> str:
        return s.replace("\t", " ")

    @staticmethod
    def _remove_punctuation(s: str) -> str:
        punctuation = string.punctuation + "’—‘"
        translator = str.maketrans("", "", punctuation)
        return s.translate(translator)

    @staticmethod
    def _remove_empty_lines(s: str) -> str:
        lines = [line for line in s.splitlines() if line.strip()]
        return " ".join(lines)


def _remove_doubles(s: str) -> str:
    s = re.sub(r" +", " ", s)
    s = re.sub(r"\n+", "\n", s)
    return s


def _remove_speaker_pattern(s: str) -> str:
    return re.sub(r"\[.*?]", "", s)


def _remove_tabs(s: str) -> str:
    return s.replace("\t", " ")


def _remove_punctuation(s: str) -> str:
    punctuation = string.punctuation + "’—‘"
    translator = str.maketrans("", "", punctuation)
    return s.translate(translator)


def _remove_empty_lines(s: str) -> str:
    lines = [line for line in s.splitlines() if line.strip()]
    return "\n".join(lines)


class HamiltonSong:
    """
    Represents a Hamilton song with cleaned lyrics and metadata.
    Phrase-only connection_to() uses shared maximal phrases (>= min_k).
    """
    def __init__(self, name: str, filepath: str, song_location: Optional[int] = None, act_number: Optional[int] = None):
        self.name = name.split(".txt")[0]
        self.filepath = filepath

        # metadata (can be set by Musical)
        self.song_location = song_location
        self.act_number = act_number

        # Raw & processed
        self.lyrics_raw = ""
        self.lyrics = ""              # cleaned (lowercase, no stage tags, etc.)
        self.text_for_ngraming = ""   # 1 long string (joined lines)

        # caches
        self._tokens_cache = None
        self._token_count = None

    def __repr__(self):
        return f"HamiltonSong({self.name})"

    # ---------- I/O ----------
    def read_file(self):
        with open(self.filepath, "r", encoding="utf8") as f:
            self.lyrics_raw = f.read()
        text = self.lyrics_raw.replace(self.name, "", 1)
        if "Last Update" in text:
            text = text[: text.find("Last Update")]
        self.lyrics = text

    def preprocess_text(self):
        if not self.lyrics and self.lyrics_raw:
            self.lyrics = self.lyrics_raw

        s = self.lyrics
        s = LyricsPreprocessor._remove_speaker_pattern(s)
        s = LyricsPreprocessor._remove_doubles(s)
        s = LyricsPreprocessor._remove_punctuation(s)
        s = LyricsPreprocessor._remove_empty_lines(s)
        s = LyricsPreprocessor._remove_tabs(s)
        s = s.lower().strip()

        self.lyrics = s
        self.text_for_ngraming = "".join(self.lyrics.split("\n"))

        self._tokens_cache = tokenize(self.lyrics)
        self._token_count = len(self._tokens_cache)

    # ---------- utilities ----------
    @property
    def token_count(self) -> int:
        if self._token_count is None:
            self._tokens_cache = tokenize(self.lyrics)
            self._token_count = len(self._tokens_cache)
        return self._token_count

    # ---------- phrase-only connection ----------
    def connection_to(self, other: "HamiltonSong", min_k: int = 3, jaccard_min: Optional[float] = None) -> float:
        """
        Strength = sum(len(phrase)^2) / min(token_count(self), token_count(other))
        Uses all_maximal_common_phrases (>= min_k).
        """
        if not self.lyrics or not other.lyrics:
            raise ValueError("Call read_file() and preprocess_text() first for both songs.")

        res = all_maximal_common_phrases(
            self.lyrics,
            other.lyrics,
            min_k=min_k,
            keep_apostrophes=True,
            jaccard_min=jaccard_min
        )
        
        phrases = res["all_maximal"]
        if not phrases:
            return 0.0, []

        total_weight = sum(p["length"] ** 2 for p in phrases)
        denom = max(1, min(self.token_count, other.token_count))
        return round(total_weight / denom, 6), [x['phrase'] for x in phrases]
    
    @property
    def tokens_cache(self):
        return self._tokens_cache
