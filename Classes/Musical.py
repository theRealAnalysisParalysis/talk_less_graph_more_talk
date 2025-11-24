import math
from typing import Dict, List, Optional
import os
import networkx as nx
from Classes.HamiltonSong import HamiltonSong
from Classes.utils import tokenize

# Note: this module assumes a `tokenize` function exists elsewhere in the codebase.
# Ensure it is imported here when available.
# ----------------------------
# Motif helpers (for the motif graph)
# ----------------------------
def _top_k_phrases(phrases, k: int | None):
    if k is None or k <= 0:
        return phrases
    # sort by length desc then lexicographically (already likely sorted, but ensure)
    phrases_sorted = sorted(phrases, key=lambda x: (-x["length"], x["phrase"]))
    return phrases_sorted[:k]

def _phrase_score_from_list(phrases, denom: int) -> float:
    return (sum(p["length"] ** 2 for p in phrases) / max(1, denom)) if phrases else 0.0


def _count_ngram_occurrences(tokens: List[str], phrase_tokens: List[str]) -> int:
    if len(phrase_tokens) == 1:
        t0 = phrase_tokens[0]
        return sum(1 for t in tokens if t == t0)
    L = len(phrase_tokens)
    return sum(1 for i in range(len(tokens) - L + 1) if tokens[i:i+L] == phrase_tokens)

def _motif_score(song_a: HamiltonSong,
                 song_b: HamiltonSong,
                 motifs: List[str],
                 idf: Optional[dict] = None,
                 rarity_alpha: float = 1.0) -> float:
    return_motifs = []
    A = song_a.tokens_cache
    B = song_b.tokens_cache
    denom = max(1, min(len(A), len(B)))
    total = 0.0
    for m in motifs:
        mtoks = tokenize(m)
        tfA = _count_ngram_occurrences(A, mtoks)
        tfB = _count_ngram_occurrences(B, mtoks)
        if tfA == 0 or tfB == 0:
            continue
        rarity = (idf.get(m, 1.0) if idf else 1.0) ** rarity_alpha
        total += rarity * min(tfA, tfB)
        return_motifs.append(m)
    return total / denom, return_motifs



class Musical:
    """
    Manages a set of HamiltonSong objects, their order/acts, and builds graphs.
    """
    def __init__(self, base_dir: str, song_order: Dict[str, int]):
        """
        song_order.json keys: filename including '.txt' (e.g., 'My Shot.txt') -> 1-based order index.
        """
        self.base_dir = base_dir
        self.song_order = song_order
        self.songs: List[HamiltonSong] = []

    def load_songs(self, names: List[str]):
        """
        Create HamiltonSong objects, attach order/act metadata, read & preprocess.
        `names` are song base names without .txt.
        """
        self.songs = []
        for name in names:
            filepath = os.path.join(self.base_dir, f"{name}")
            order = self.song_order.get(f"{name}")
            act = 1 if (order is not None and order <= 23) else 2
            song = HamiltonSong(name=name, filepath=filepath, song_location=order, act_number=act)
            song.read_file()
            song.preprocess_text()
            self.songs.append(song)
    
    def _compute_motif_tfidf(self, motifs: List[str], rarity_alpha: float = 1.0):
        """
        Compute TF (per song) and IDF (across songs) for each motif.

        Returns:
            motif_tf: dict[song_name][motif] = count of motif occurrences
            motif_idf: dict[motif] = IDF(k)^rarity_alpha
        """
        motif_tf = {song.name: {} for song in self.songs}
        motif_doc_count = {m: 0 for m in motifs}
        
        for song in self.songs:
            tokens = tokenize(song.lyrics)
            for m in motifs:
                m_tokens = tokenize(m)
                L = len(m_tokens)
                # Count occurrences
                tf = sum(
                    1 for i in range(len(tokens) - L + 1)
                    if tokens[i:i + L] == m_tokens
                )
                motif_tf[song.name][m] = tf
                if tf > 0:
                    motif_doc_count[m] += 1
        
        N = len(self.songs)
        motif_idf = {}
        for m in motifs:
            n_k = motif_doc_count[m]
            # standard smoothed IDF: log((N + 1) / (1 + n_k)) + 1
            idf = math.log((N + 1) / (1 + n_k)) + 1
            motif_idf[m] = idf ** rarity_alpha
        
        return motif_tf, motif_idf
    
    def create_song_graph_phrase_only(self,
                                      min_k: int = 3,
                                      jaccard_min: Optional[float] = None,
                                      weight_threshold: float = 0.0,
                                      directed: bool = False,
                                      respect_story_order: bool = False):
        """
        Phrase-only graph (your original formula).
        """
        G = nx.DiGraph() if directed else nx.Graph()
        for s in self.songs:
            G.add_node(s.name, act=s.act_number, order=s.song_location)

        n = len(self.songs)
        for i in range(n):
            for j in range(i + (0 if directed else 1), n):
                a, b = self.songs[i], self.songs[j]
                if a.name == b.name:
                    continue

                if directed and respect_story_order:
                    if a.song_location is None or b.song_location is None or a.song_location >= b.song_location:
                        continue
                    w, phrases = a.connection_to(b, min_k=min_k, jaccard_min=jaccard_min)
                    if w >= weight_threshold:
                        G.add_edge(a.name, b.name, weight=w)
                elif directed and not respect_story_order:
                    w_ab, phrases = a.connection_to(b, min_k=min_k, jaccard_min=jaccard_min)
                    w_ba, phrases = b.connection_to(a, min_k=min_k, jaccard_min=jaccard_min)
                    if w_ab >= weight_threshold:
                        G.add_edge(a.name, b.name, weight=w_ab)
                    if w_ba >= weight_threshold:
                        G.add_edge(b.name, a.name, weight=w_ba)
                else:
                    w, phrases = a.connection_to(b, min_k=min_k, jaccard_min=jaccard_min)
                    if w >= weight_threshold:
                        G.add_edge(a.name, b.name, weight=w)
        return G


    def create_song_graph_with_motifs(self,
                                      motifs: List[str],
                                      motif_weight: float = 0.5,
                                      motif_rarity_alpha: float = 1.0,
                                      min_k: int = 3,
                                      jaccard_min: Optional[float] = None,
                                      weight_threshold: float = 0.0,
                                      directed: bool = False):
        """
        Phrase + Motif graph.
        Edge weight = phrase_score + motif_weight * motif_score
        (motif_score is IDF-weighted min-TF overlap over curated 1–2-gram motifs).
        """
        G = nx.DiGraph() if directed else nx.Graph()
        for s in self.songs:
            G.add_node(s.name, act=s.act_number, order=s.song_location)
        del s
        
        motif_tf, motif_idf = self._compute_motif_tfidf(
            motifs=motifs, rarity_alpha=motif_rarity_alpha
        )
        
        n = len(self.songs)
        for i in range(n):
            for j in range(i + 1, n):  # always skip self; one unordered pair
                a, b = self.songs[i], self.songs[j]

                # compute score (optionally take max of a→b and b→a if your scoring is asymmetric)
                ps_ab, ph_ab = a.connection_to(b, min_k=min_k, jaccard_min=jaccard_min)
                ps_ba, ph_ba = b.connection_to(a, min_k=min_k, jaccard_min=jaccard_min)
                phrase_score = max(ps_ab, ps_ba)
                phrases = (ph_ab if ps_ab >= ps_ba else ph_ba)
                
                m_ab, mh_ab = _motif_score(a, b, motifs=motifs, idf=motif_idf, rarity_alpha=motif_rarity_alpha)
                m_ba, mh_ba = _motif_score(b, a, motifs=motifs, idf=motif_idf, rarity_alpha=motif_rarity_alpha)
                motif_score = max(m_ab, m_ba)
                phrases += (mh_ab if m_ab >= m_ba else mh_ba)
                
                w = phrase_score + motif_weight * motif_score
                if w <= 0 or w < weight_threshold:
                    continue
                
                if directed:
                    if a.song_location is None or b.song_location is None:
                        continue
                    # orient earlier → later; break ties by index
                    if (a.song_location, i) < (b.song_location, j):
                        G.add_edge(a.name, b.name, weight=round(w, 6), phrases=" | ".join(phrases))
                    elif (b.song_location, j) < (a.song_location, i):
                        G.add_edge(b.name, a.name, weight=round(w, 6), phrases=" | ".join(phrases))
                    # equal locations → skip
                else:
                    G.add_edge(a.name, b.name, weight=round(w, 6), phrases=" | ".join(phrases))
        
        return G
