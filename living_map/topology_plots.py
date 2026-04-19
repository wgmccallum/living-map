"""Visualization for mastery filtration and persistent homology.

Generates matplotlib figures for:
  - Mastery curves (per-vertex µ_v(t))
  - Persistence barcodes
  - Betti curves β_n(t)
  - Staged quotient summaries
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure

from .topology import (
    FiltrationResult,
    FrameComplex,
    LearnerScenario,
    MasteryFunction,
    QuotientStage,
    StagedResult,
)


# ── Color palettes ──

_PHASE_COLORS = {
    "phase1": "#2196F3",  # blue
    "phase2": "#FF9800",  # orange
    "phase3": "#4CAF50",  # green
    "terminal": "#9C27B0",  # purple
    "other": "#607D8B",   # gray
}

_DIM_COLORS = {
    0: "#2196F3",   # blue
    1: "#E91E63",   # pink
    2: "#4CAF50",   # green
    3: "#FF9800",   # orange
    4: "#9C27B0",   # purple
}


def _classify_vertex(vertex_id: str) -> str:
    """Rough phase classification for coloring."""
    if vertex_id.startswith("["):
        return "other"
    try:
        num = int(vertex_id.replace("CNM-", "").split(",")[0])
    except ValueError:
        return "other"
    if num < 520:
        return "phase1"
    elif num < 600:
        return "phase2"
    elif num < 700:
        return "terminal"
    else:
        return "phase3"


# ── Mastery Curves ──


def plot_mastery_curves(
    scenario: LearnerScenario,
    t_max: float = 5.0,
    highlight: list[str] | None = None,
    title: str | None = None,
    n_points: int = 300,
) -> Figure:
    """Plot mastery curves µ_v(t) for all vertices in a scenario.

    If highlight is given, those vertices are drawn with thick colored lines
    and the rest are drawn in light gray.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    times = [t_max * i / n_points for i in range(n_points + 1)]

    highlight_set = set(highlight) if highlight else None

    # Draw background curves first
    for vid, mf in sorted(scenario.mastery_functions.items()):
        if highlight_set and vid not in highlight_set:
            values = [mf.evaluate(t) for t in times]
            ax.plot(times, values, color="#D0D0D0", linewidth=0.7, alpha=0.6)

    # Draw highlighted curves on top
    for vid, mf in sorted(scenario.mastery_functions.items()):
        if highlight_set is None or vid in highlight_set:
            values = [mf.evaluate(t) for t in times]
            color = _PHASE_COLORS.get(_classify_vertex(vid), "#607D8B")
            ax.plot(times, values, color=color, linewidth=2.0, label=vid)

    ax.set_xlabel("Time")
    ax.set_ylabel("Mastery µ(v, t)")
    ax.set_xlim(0, t_max)
    ax.set_ylim(-0.02, 1.05)
    ax.axhline(y=scenario.theta, color="red", linestyle="--", linewidth=0.8,
               label=f"θ = {scenario.theta}")
    if highlight_set and len(highlight_set) <= 12:
        ax.legend(fontsize=8, loc="lower right")
    ax.set_title(title or f"Mastery Curves — {scenario.name}")
    fig.tight_layout()
    return fig


def plot_mastery_comparison(
    scenarios: list[LearnerScenario],
    vertices: list[str],
    t_max: float = 5.0,
    n_points: int = 300,
) -> Figure:
    """Plot mastery curves for selected vertices across multiple scenarios (side by side)."""
    n = len(scenarios)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 5), sharey=True)
    if n == 1:
        axes = [axes]
    times = [t_max * i / n_points for i in range(n_points + 1)]

    for ax, scenario in zip(axes, scenarios):
        # Background: all vertices in gray
        for vid, mf in scenario.mastery_functions.items():
            if vid not in vertices:
                values = [mf.evaluate(t) for t in times]
                ax.plot(times, values, color="#D0D0D0", linewidth=0.5, alpha=0.5)
        # Foreground: selected vertices
        for vid in vertices:
            mf = scenario.mastery_functions.get(vid)
            if mf:
                values = [mf.evaluate(t) for t in times]
                color = _PHASE_COLORS.get(_classify_vertex(vid), "#607D8B")
                ax.plot(times, values, color=color, linewidth=2.0, label=vid)

        ax.set_xlabel("Time")
        ax.set_xlim(0, t_max)
        ax.set_ylim(-0.02, 1.05)
        ax.axhline(y=scenario.theta, color="red", linestyle="--", linewidth=0.8)
        ax.set_title(scenario.name)
        if len(vertices) <= 10:
            ax.legend(fontsize=7, loc="lower right")

    axes[0].set_ylabel("Mastery µ(v, t)")
    fig.tight_layout()
    return fig


# ── Persistence Barcodes ──


def plot_barcode(
    result: FiltrationResult,
    max_dimension: int = 3,
    title: str | None = None,
    t_max: float | None = None,
) -> Figure:
    """Plot persistence barcode, grouped and colored by dimension."""
    if t_max is None:
        t_max = result.time_range[1]

    # Group bars by dimension
    bars_by_dim: dict[int, list[tuple[float, float]]] = {}
    for dim, (birth, death) in result.persistence_pairs:
        if dim > max_dimension:
            continue
        bars_by_dim.setdefault(dim, []).append((birth, death))

    # Count total bars for layout
    total_bars = sum(len(bars) for bars in bars_by_dim.values())
    if total_bars == 0:
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.text(0.5, 0.5, "No persistence pairs", ha="center", va="center")
        return fig

    fig, ax = plt.subplots(figsize=(10, max(3, total_bars * 0.15 + 1)))

    y = 0
    y_ticks = []
    y_labels = []
    dim_boundaries = []

    for dim in range(max_dimension + 1):
        bars = bars_by_dim.get(dim, [])
        if not bars:
            continue

        dim_boundaries.append(y)
        color = _DIM_COLORS.get(dim, "#999999")

        # Sort: permanent bars first (by birth), then finite (by birth)
        permanent = sorted([(b, d) for b, d in bars if d == float("inf")])
        finite = sorted([(b, d) for b, d in bars if d != float("inf")])

        for birth, death in finite + permanent:
            end = t_max * 1.05 if death == float("inf") else death
            ax.barh(y, end - birth, left=birth, height=0.7,
                    color=color, alpha=0.8, edgecolor="none")
            if death == float("inf"):
                ax.plot(t_max * 1.05, y, marker=">", color=color, markersize=4)
            y += 1

        mid_y = dim_boundaries[-1] + len(bars) / 2 - 0.5
        y_ticks.append(mid_y)
        y_labels.append(f"H{dim} ({len(bars)})")
        y += 1  # gap between dimensions

    ax.set_xlabel("Time")
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    ax.set_xlim(-0.05, t_max * 1.1)
    ax.set_ylim(-0.5, y)
    ax.invert_yaxis()

    # Dimension color legend
    handles = [mpatches.Patch(color=_DIM_COLORS.get(d, "#999"), label=f"H{d}")
               for d in range(max_dimension + 1) if d in bars_by_dim]
    ax.legend(handles=handles, fontsize=8, loc="upper right")

    ax.set_title(title or "Persistence Barcode")
    fig.tight_layout()
    return fig


def plot_barcode_comparison(
    results: list[tuple[str, FiltrationResult]],
    max_dimension: int = 2,
    t_max: float | None = None,
) -> Figure:
    """Plot barcodes for multiple scenarios side by side."""
    n = len(results)
    fig, axes = plt.subplots(1, n, figsize=(7 * n, 6))
    if n == 1:
        axes = [axes]

    effective_tmax = t_max or max(r.time_range[1] for _, r in results)

    for ax, (name, result) in zip(axes, results):
        bars_by_dim: dict[int, list[tuple[float, float]]] = {}
        for dim, (birth, death) in result.persistence_pairs:
            if dim > max_dimension:
                continue
            bars_by_dim.setdefault(dim, []).append((birth, death))

        y = 0
        y_ticks = []
        y_labels = []

        for dim in range(max_dimension + 1):
            bars = bars_by_dim.get(dim, [])
            if not bars:
                continue
            color = _DIM_COLORS.get(dim, "#999")
            start_y = y
            permanent = sorted([(b, d) for b, d in bars if d == float("inf")])
            finite = sorted([(b, d) for b, d in bars if d != float("inf")])
            for birth, death in finite + permanent:
                end = effective_tmax * 1.05 if death == float("inf") else death
                ax.barh(y, end - birth, left=birth, height=0.7,
                        color=color, alpha=0.8, edgecolor="none")
                if death == float("inf"):
                    ax.plot(effective_tmax * 1.05, y, ">", color=color, ms=4)
                y += 1
            y_ticks.append(start_y + len(bars) / 2 - 0.5)
            y_labels.append(f"H{dim} ({len(bars)})")
            y += 1

        ax.set_xlabel("Time")
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        ax.set_xlim(-0.05, effective_tmax * 1.1)
        ax.set_ylim(-0.5, y)
        ax.invert_yaxis()
        ax.set_title(name)

    fig.tight_layout()
    return fig


# ── Betti Curves ──


def plot_betti_curves(
    result: FiltrationResult,
    max_dimension: int = 3,
    title: str | None = None,
) -> Figure:
    """Plot Betti curves β_n(t) for each dimension."""
    fig, ax = plt.subplots(figsize=(10, 4))

    for dim in range(max_dimension + 1):
        curve = result.betti_curves.get(dim, [])
        if not curve:
            continue
        times, values = zip(*curve)
        if max(values) == 0:
            continue
        color = _DIM_COLORS.get(dim, "#999")
        ax.plot(times, values, color=color, linewidth=1.5, label=f"β{dim}")

    ax.set_xlabel("Time")
    ax.set_ylabel("Betti number")
    ax.set_xlim(result.time_range)
    ax.legend(fontsize=9)
    ax.set_title(title or "Betti Curves")
    fig.tight_layout()
    return fig


def plot_betti_comparison(
    results: list[tuple[str, FiltrationResult]],
    dimensions: list[int] | None = None,
) -> Figure:
    """Plot Betti curves for multiple scenarios, one subplot per dimension."""
    if dimensions is None:
        dimensions = [1, 2]

    n_dims = len(dimensions)
    fig, axes = plt.subplots(1, n_dims, figsize=(6 * n_dims, 4), sharey=False)
    if n_dims == 1:
        axes = [axes]

    linestyles = ["-", "--", "-.", ":"]
    colors_per_scenario = ["#2196F3", "#E91E63", "#4CAF50", "#FF9800"]

    for ax, dim in zip(axes, dimensions):
        for i, (name, result) in enumerate(results):
            curve = result.betti_curves.get(dim, [])
            if not curve:
                continue
            times, values = zip(*curve)
            ax.plot(times, values,
                    color=colors_per_scenario[i % len(colors_per_scenario)],
                    linestyle=linestyles[i % len(linestyles)],
                    linewidth=1.5, label=name)
        ax.set_xlabel("Time")
        ax.set_ylabel(f"β{dim}(t)")
        ax.set_title(f"β{dim} comparison")
        ax.legend(fontsize=8)

    fig.tight_layout()
    return fig


# ── Staged Quotient Summary ──


def plot_staged_summary(
    staged: StagedResult,
    t_max: float = 5.0,
) -> Figure:
    """Visualize the staged quotient pipeline: schemas ordered by realization
    time, showing effective vertex count and the time window during which
    each schema's simplicial complex is "active" (edges/faces appearing but
    not yet fully realized).
    """
    # Sort stages by realization time
    stages = sorted(staged.stages, key=lambda s: s.realization_time)
    n = len(stages)

    fig, ax = plt.subplots(figsize=(12, max(4, n * 0.45 + 1.5)))

    for i, stage in enumerate(stages):
        # Find the earliest birth time in this stage's filtration (first edge/vertex appears)
        earliest = float("inf")
        for dim, (birth, _) in stage.filtration_result.persistence_pairs:
            if birth < earliest:
                earliest = birth
        if earliest == float("inf"):
            earliest = 0.0

        real_t = min(stage.realization_time, t_max * 1.05)

        # Bar from earliest activity to realization
        bar_start = earliest
        bar_len = real_t - bar_start

        # Color by effective vertex count (darker = more vertices = more complex)
        nv = len(stage.effective_vertices)
        intensity = min(nv / 20.0, 1.0)  # normalize to ~20 max
        color = plt.cm.YlOrRd(0.25 + 0.65 * intensity)

        ax.barh(i, bar_len, left=bar_start, height=0.7,
                color=color, alpha=0.85, edgecolor="#666", linewidth=0.5)

        # Realization marker
        if stage.realization_time <= t_max:
            ax.plot(real_t, i, "k|", markersize=10, markeredgewidth=1.5)

        # Right-side annotation
        n_h1 = len(stage.filtration_result.finite_bars(1))
        label = f"{stage.schema_id}  |V|={nv}  H₁={n_h1}"
        ax.text(real_t + 0.08, i, label, va="center", fontsize=7,
                family="monospace")

    # Y-axis: schema names, ordered by realization time
    ax.set_yticks(range(n))
    ax.set_yticklabels([s.schema_name[:35] for s in stages], fontsize=7.5)
    ax.set_xlim(0, t_max * 1.4)
    ax.set_ylim(n - 0.5, -0.5)
    ax.set_xlabel("Time", fontsize=10)
    ax.set_title("Schema Realization Timeline (ordered by realization time)", fontsize=11)

    # Colorbar for vertex count
    sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd,
                                norm=plt.Normalize(vmin=2, vmax=20))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.6, pad=0.15)
    cbar.set_label("|V| (effective vertices)", fontsize=8)

    fig.tight_layout()
    return fig


# ── Convenience: save figure ──


def save_figure(fig: Figure, path: str | Path, dpi: int = 150) -> None:
    """Save a matplotlib figure and close it."""
    fig.savefig(str(path), dpi=dpi, bbox_inches="tight")
    plt.close(fig)
