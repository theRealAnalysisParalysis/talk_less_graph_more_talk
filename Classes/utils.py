import re
from collections import defaultdict
import math
import matplotlib.pyplot as plt
from itertools import cycle
import networkx as nx

def tokenize(s, keep_apostrophes=True):
    s = s.lower()
    if keep_apostrophes:
        s = re.sub(r"[^a-z0-9']+", " ", s)
    else:
        s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.split()


def all_maximal_common_phrases(a_text, b_text, min_k=3, keep_apostrophes=True, jaccard_min=None):
    """
    Return ALL maximal common contiguous token substrings between two texts.
    Now enforces bi-directional maximality and removes phrases contained in others.
    If jaccard_min is set (e.g., 0.9), also drop near-duplicates by Jaccard>=threshold.
    """
    A = tokenize(a_text, keep_apostrophes)
    B = tokenize(b_text, keep_apostrophes)
    n, m = len(A), len(B)

    DP = [[0]*(m+1) for _ in range(n+1)]
    matches = []  # (length, a_end, b_end)

    for i in range(1, n+1):
        ai = A[i-1]
        row = DP[i]
        prev = DP[i-1]
        for j in range(1, m+1):
            if ai == B[j-1]:
                L = prev[j-1] + 1
                row[j] = L
                # Check extendability to the RIGHT (both sides)
                can_extend_right = (i < n and j < m and A[i] == B[j])
                # Check extendability to the LEFT (both sides)
                # left indices in zero-based arrays: start is i-L, j-L; left neighbor is i-L-1, j-L-1
                can_extend_left = (i - L > 0 and j - L > 0 and A[i - L - 1] == B[j - L - 1])
                # Record only if bi-directionally maximal and long enough
                if not can_extend_right and not can_extend_left and L >= min_k:
                    matches.append((L, i, j))
            else:
                row[j] = 0

    # Group exact-equal phrases; keep all spans
    grouped = defaultdict(lambda: {"length": None, "a_spans": [], "b_spans": []})
    for L, i_end, j_end in matches:
        a_start = i_end - L
        b_start = j_end - L
        phrase = " ".join(A[a_start:i_end])
        g = grouped[phrase]
        g["length"] = L
        g["a_spans"].append((a_start, i_end))
        g["b_spans"].append((b_start, j_end))

    # Convert to list and sort by length desc, then phrase
    results = [
        {"phrase": p, "length": info["length"], "a_spans": info["a_spans"], "b_spans": info["b_spans"]}
        for p, info in grouped.items()
    ]
    results.sort(key=lambda x: (-x["length"], x["phrase"]))

    # ----- containment filter: drop any phrase contained in a longer kept phrase -----
    kept = []
    kept_strs = []  # cache of padded strings for fast containment checks
    for r in results:
        cand = r["phrase"]
        cand_padded = f" {cand} "
        # exact containment on token boundaries
        if any(cand_padded in ks for ks in kept_strs):
            continue
        # optional: near-duplicate filter via Jaccard on token sets
        if jaccard_min is not None:
            cset = set(cand.split())
            drop = False
            for k in kept:
                kset = set(k["phrase"].split())
                inter = len(cset & kset)
                union = len(cset | kset) or 1
                jacc = inter / union
                if jacc >= jaccard_min:
                    drop = True
                    break
            if drop:
                continue
        kept.append(r)
        kept_strs.append(f" {r['phrase']} ")

    if kept:
        max_len = kept[0]["length"]
        longest_only = [r for r in kept if r["length"] == max_len]
    else:
        max_len, longest_only = 0, []

    return {"all_maximal": kept, "longest_len": max_len, "longest_only": longest_only}


def timeline_layout(G, order_attr="order", spacing=1.0, y=0.0):
    nodes_sorted = sorted(
        G.nodes(),
        key=lambda n: (G.nodes[n].get(order_attr) is None, G.nodes[n].get(order_attr))
    )
    pos = {n: (i * spacing, y) for i, n in enumerate(nodes_sorted)}
    return pos, nodes_sorted

def draw_timeline(G, order_attr="order", spacing=1.0, label_offset=0.18,
                  edge_rad_base=0.15, edge_width_attr="weight",
                  arcs_above=True, fontsize=9, height=0):

    pos, nodes_sorted = timeline_layout(G, order_attr=order_attr, spacing=spacing, y=height)
    ax = plt.gca()

    # --- draw EDGES first ---
    sign = -1.0 if arcs_above else 1.0   # negative → arc bends UP
    edgelist = list(G.edges())
    widths = (
        [max(0.8, 2.0 * float(G[u][v].get(edge_width_attr, 1.0))) for u, v in edgelist]
        if edge_width_attr is not None else None
    )

    def edge_rad(u, v):
        d = abs(pos[v][0] - pos[u][0])
        return sign * (edge_rad_base + 0.015 * d)

    # draw one-by-one so each can have its own curvature
    for k, (u, v) in enumerate(edgelist):
        arts = nx.draw_networkx_edges(
            G, pos, edgelist=[(u, v)],
            arrows=True, arrowstyle="-|>", min_target_margin=6, min_source_margin=6,
            connectionstyle=f"arc3,rad={edge_rad(u, v)}",
            width=(widths[k] if widths else 1.5),
            alpha=0.9, ax=ax
        )
        # Disable clipping on returned artist(s)
        if arts is not None:
            # can be a LineCollection or a list of FancyArrowPatch
            try:
                arts.set_clip_on(False)
            except AttributeError:
                for a in arts:
                    a.set_clip_on(False)

    # --- draw NODES on top ---
    nx.draw_networkx_nodes(G, pos, node_size=320, linewidths=0.8, edgecolors="black")

    # --- labels: below baseline, 45°
    for n, (x, y) in pos.items():
        ax.text(x, y - label_offset, n, rotation_mode="anchor",
                rotation=45, ha="right", va="top", fontsize=fontsize,
                transform=None)
    # --- generous limits so nothing is cropped
    xs = [x for x, _ in pos.values()]
    min_x, max_x = min(xs), max(xs)
    span = max(max_x - min_x, 1.0)
    top_pad = span * 0.7 + 5.0          # big headroom for arcs above
    bottom_pad = label_offset + 0.8      # room for rotated labels

    ax.set_xlim(min_x - spacing * 0.5, max_x + spacing * 0.5)
    ax.set_ylim(-bottom_pad, top_pad)
    ax.axis("off")
    plt.tight_layout()
    plt.show()



def draw_timeline_1(
    G,
    order_attr="order",
    # node sizing
    base_node_size=220,          # minimum node area (points^2)
    size_per_degree=90,          # extra area per 1 degree
    # spacing control (linked to node size)
    min_gap=0.75,                # baseline gap between consecutive nodes (data units)
    gap_per_sqrt_size=0.02,      # extra gap per sqrt(node_size) so big nodes push neighbors away
    # edges
    edge_rad_base=0.15,
    edge_width_attr="weight",
    arcs_above=True,
    # labels
    label_offset=0.18,
    fontsize=9,
    height=0,
    # communities coloring
    communities=None,            # optional: pass in an iterable of sets; if None → detect
    cmap=None,                    # optional: list/iterable of colors; if None → good defaults
):
    """
    Timeline layout with node size = degree and spacing coupled to node size.
    Colors nodes by community (greedy modularity if not provided).

    Notes:
    - 'gap_per_sqrt_size' is applied to sqrt(points^2) (=points). It's a heuristic but
      works well visually without fighting Matplotlib's unit system.
    """
    ax = plt.gca()

    # ----- ORDER: get nodes in timeline order
    # If you already have your own 'timeline_layout', keep using it just to get the order.
    # Otherwise, sort by attribute and build positions here.
    nodes_sorted = sorted(G.nodes(), key=lambda n: G.nodes[n].get(order_attr, 0))

    # ----- NODE SIZE: area proportional to degree
    deg = dict(G.degree()) if not isinstance(G, nx.DiGraph) else {n: G.degree(n) for n in G.nodes()}
    node_size = {n: base_node_size + size_per_degree * max(0, deg.get(n, 0)) for n in G.nodes()}

    # ----- X positions with spacing that depends on node size (bigger nodes → bigger gaps)
    x = {}
    cur = 0.0
    for i, n in enumerate(nodes_sorted):
        if i == 0:
            x[n] = cur
        else:
            # gap = baseline + extra driven by node size of *previous* node (feels natural)
            prev = nodes_sorted[i-1]
            gap = min_gap + gap_per_sqrt_size * math.sqrt(node_size[prev])
            cur += gap
            x[n] = cur

    # center the sequence around 0 for nicer axes
    if nodes_sorted:
        shift = 0.5 * (x[nodes_sorted[0]] + x[nodes_sorted[-1]])
        for n in x:
            x[n] -= shift

    pos = {n: (x[n], height) for n in nodes_sorted}

    # ----- COMMUNITIES → colors
    if communities is None:
        # detect on undirected to match visual intuition
        und = G.to_undirected()
        try:
            comms = list(nx.algorithms.community.greedy_modularity_communities(und))
        except Exception:
            # fallback: single community
            comms = [set(G.nodes())]
    else:
        comms = list(communities)

    # palette
    if cmap is None:
        # readable, varied; extend if needed
        base_colors = [
            "#8bd3e6", "#80b1d3", "#c4cbe4", "#a6cee3", "#b2df8a", "#fb9a99",
            "#fdbf6f", "#cab2d6", "#1f78b4", "#33a02c", "#6a3d9a", "#ff7f00",
            "#b15928", "#a6a6a6"
        ]
    else:
        base_colors = list(cmap)

    color_cycle = cycle(base_colors)
    node_color_map = {}
    for comm, color in zip(comms, color_cycle):
        for n in comm:
            node_color_map[n] = color
    # any stragglers (shouldn't happen)
    for n in G.nodes():
        node_color_map.setdefault(n, "#a6a6a6")

    node_colors = [node_color_map[n] for n in G.nodes()]
    node_sizes = [node_size[n] for n in G.nodes()]

    # ----- EDGES (curved “arc3” above or below)
    sign = -1.0 if arcs_above else 1.0
    edgelist = list(G.edges())
    widths = (
        [max(0.8, 2.0 * float(G[u][v].get(edge_width_attr, 1.0))) for u, v in edgelist]
        if edge_width_attr is not None else None
    )

    def edge_rad(u, v):
        d = abs(pos[v][0] - pos[u][0])
        return sign * (edge_rad_base + 0.015 * d)

    for k, (u, v) in enumerate(edgelist):
        arts = nx.draw_networkx_edges(
            G, pos, edgelist=[(u, v)],
            arrows=True, arrowstyle="-|>", min_target_margin=6, min_source_margin=6,
            connectionstyle=f"arc3,rad={edge_rad(u, v)}",
            width=(widths[k] if widths else 1.5),
            alpha=0.9, ax=ax
        )
        if arts is not None:
            try:
                arts.set_clip_on(False)
            except AttributeError:
                for a in arts:
                    a.set_clip_on(False)

    # ----- NODES
    nx.draw_networkx_nodes(
        G, pos,
        node_size=node_sizes,
        node_color=node_colors,
        linewidths=0.9, edgecolors="black"
    )

    # ----- LABELS: below baseline, 45°
    for n, (xx, yy) in pos.items():
        ax.text(xx, yy - label_offset, n, rotation=45, ha="right", va="top", fontsize=fontsize)

    # ----- Limits so nothing is cropped
    xs = [xx for xx, _ in pos.values()] or [0.0]
    min_x, max_x = min(xs), max(xs)
    span = max(max_x - min_x, 1.0)
    top_pad = span * 0.7 + 5.0
    bottom_pad = label_offset + 0.8

    ax.set_xlim(min_x - 0.6, max_x + 0.6)
    ax.set_ylim(-bottom_pad, top_pad)
    ax.axis("off")
    plt.tight_layout()
    plt.show()
