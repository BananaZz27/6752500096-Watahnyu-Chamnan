"""Figures for Lab 06, built only from the raw/events CSV and metrics.json in completed/.

Run from lab_06/:  python submission/make_figures.py
Nothing here changes a raw CSV.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
RUN = HERE / "completed"
OUT = HERE / "figures"
STATES = ("normal", "interested", "happy", "afraid", "sleepy")
SCOL = {"normal": "#3c5a8c", "interested": "#eda100", "happy": "#1baf7a", "afraid": "#d03b3b", "sleepy": "#6a5aa8"}
CCOL = {"C0": "#eb6834", "C1": "#2a78d6"}
INK, MUTED, GRID = "#161616", "#6b6b6b", "#e4e4e4"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "axes.axisbelow": True,
})


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def fnum(x):
    return None if x in ("", None) else float(x)


def fig_states():
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 5.6), sharex=True, gridspec_kw={"height_ratios": [1.1, 1, 1]})
    raw0 = load(RUN / "raw_C0_r01.csv")
    t = [float(r["time_s"]) for r in raw0]
    d = [fnum(r["distance_m"]) for r in raw0]
    ax = axes[0]
    ax.plot(t, [x if x is not None else float("nan") for x in d], color=INK, lw=0.9, label="distance (seed 41, same input for C0/C1)")
    for y, lab, ls in ((0.20, "near enter 0.20", "-"), (0.28, "C1 near exit 0.28", "--"), (0.80, "approach enter 0.80", "-"),
                       (0.95, "C1 approach exit 0.95", "--")):
        ax.axhline(y, color="#b84a4a" if "near" in lab else "#a27100", lw=0.8, ls=ls)
        ax.text(21.9, y + 0.02, lab, ha="right", fontsize=6.8, color=MUTED)
    ax.set_ylabel("distance (m)")
    ax.set_ylim(0, 1.45)
    for x0, lab in ((1, "button"), (3, "touch"), (7, "touch"), (12, "stale"), (18, "button")):
        ax.annotate(lab, (x0, 1.32), fontsize=6.8, color=MUTED, ha="center")
    ax.annotate("NaN", (11, 1.32), fontsize=6.8, color="#b84a4a", ha="center")
    for ax, cond in zip(axes[1:], ("C0", "C1")):
        raw = load(RUN / f"raw_{cond}_r01.csv")
        ys = [STATES.index(r["state"]) for r in raw]
        ax.step(t, ys, where="post", color=CCOL[cond], lw=1.2)
        ax.set_yticks(range(len(STATES)))
        ax.set_yticklabels(STATES, fontsize=7.5)
        ax.invert_yaxis()
        m = next(x for x in json.loads((RUN / "metrics.json").read_text())["runs"] if x["condition"] == cond and x["repeat"] == 1)
        ax.set_title(f"{cond} {'raw (no debounce/hysteresis)' if cond == 'C0' else 'guarded (debounce 0.06 s, hysteresis)'} — "
                     f"{m['state_transition_count']} state transitions", fontsize=8.5, loc="left")
    axes[2].set_xlabel("time (s)")
    fig.suptitle("Seed 41: same synthetic input, C0 chatters around the thresholds while C1 changes state once per interaction", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_state_timeline.png", dpi=200)
    plt.close(fig)


def fig_latency():
    runs = json.loads((RUN / "metrics.json").read_text())["runs"]
    ids = ["button_01", "touch_01", "approach_01", "clear_01", "near_01", "clear_02", "button_02"]
    fig, ax = plt.subplots(figsize=(9.5, 3.4))
    for run in runs:
        c, rep = run["condition"], run["repeat"]
        out = {s["input_id"]: s for s in run["source_outcomes"]}
        for i, iid in enumerate(ids):
            x = i + (-0.22 if c == "C0" else 0.22) + (rep - 2) * 0.07
            lat = out[iid]["both_latency_s"]
            if lat is None:
                ax.plot(x, 0.30, marker="x", color=CCOL[c], ms=7, mew=1.8)
            else:
                ax.plot(x, lat, marker="o", color=CCOL[c], ms=5, markeredgecolor="white", mew=0.6)
    ax.axhline(0.30, color=MUTED, lw=0.5, ls=":")
    ax.text(6.5, 0.307, "× = no both onset (miss)", ha="right", fontsize=7.5, color=MUTED)
    ax.set_xticks(range(len(ids)))
    ax.set_xticklabels(ids, fontsize=8)
    ax.set_ylabel("both latency (s)\nsource → first applied motion & RGB")
    ax.set_ylim(0, 0.33)
    ax.plot([], [], "o", color=CCOL["C0"], label="C0 raw")
    ax.plot([], [], "o", color=CCOL["C1"], label="C1 guarded")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.set_title("Primary 7 sources × 3 paired seeds (41, 42, 43 left→right within each colour); all values far below the 1 s limit",
                 fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig2_latency.png", dpi=200)
    plt.close(fig)


def fig_chain():
    raw = [r for r in load(RUN / "raw_C1_r01.csv") if 0.94 <= float(r["time_s"]) <= 1.4]
    t = [float(r["time_s"]) for r in raw]
    fig, axes = plt.subplots(3, 1, figsize=(8, 4.6), sharex=True)
    axes[0].step(t, [float(r["button"]) for r in raw], where="post", color=INK, lw=1.4)
    axes[0].set_ylabel("button raw")
    axes[0].set_ylim(-0.1, 1.2)
    axes[1].step(t, [STATES.index(r["state"]) for r in raw], where="post", color=CCOL["C1"], lw=1.4)
    axes[1].set_yticks([0, 1])
    axes[1].set_yticklabels(["normal", "interested"])
    axes[1].set_ylim(-0.3, 1.3)
    axes[1].set_ylabel("FSM state")
    axes[2].plot(t, [float(r["tilt_rad"]) for r in raw], color=INK, lw=1.4, marker="o", ms=2.5, label="tilt applied (rad)")
    rgb_on = [1 if r["rgb_r"] == "255" else 0 for r in raw]
    axes[2].step(t, [0.12 * v for v in rgb_on], where="post", color="#eda100", lw=1.4, label="RGB = interested (scaled)")
    axes[2].set_ylabel("output")
    axes[2].legend(loc="upper left", fontsize=7.5)
    axes[2].set_xlabel("time (s)")
    for x, lab in ((1.00, "source 1.00"), (1.04, "last bounce edge 1.04"), (1.10, "recognized / decision / queued 1.10"),
                   (1.14, "applied, motion + RGB onset 1.14")):
        for a in axes:
            a.axvline(x, color="#b84a4a", lw=0.7, ls=":")
        yl = {1.00: 0.8, 1.04: 0.5, 1.10: 0.8, 1.14: 0.2}[x]
        axes[0].text(x + 0.004, yl, lab, fontsize=6.5, color="#b84a4a", va="center",
                     bbox=dict(fc="white", ec="none", pad=0.5))
    fig.suptitle("One event end-to-end (C1, seed 41, button_01): both latency = 1.14 − 1.00 = 0.14 s", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig3_event_chain.png", dpi=200)
    plt.close(fig)


def _node(ax, xy, name):
    x, y = xy
    ax.add_patch(FancyBboxPatch((x - 0.8, y - 0.32), 1.6, 0.64, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="#ffffff", ec=SCOL[name], lw=2))
    ax.text(x, y, name, ha="center", va="center", fontsize=9, color=INK)


def _edge(ax, a, b, label, rad=0.0, dx=0.0, dy=0.12, colour=INK, ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=12, lw=1.1, color=colour, ls=ls,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=4, shrinkB=4))
    ax.text((a[0] + b[0]) / 2 + dx, (a[1] + b[1]) / 2 + dy, label, ha="center", fontsize=7, color=MUTED)


def fig_fsm():
    import math
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.2, 5.6)
    ax.axis("off")
    P = {"interested": (1.5, 4.4), "happy": (7.5, 4.4), "normal": (4.5, 2.4), "sleepy": (1.5, 0.4), "afraid": (10.9, 2.4)}
    for n, xy in P.items():
        _node(ax, xy, n)

    def arrow(a, b, label, off=0.0, at=None, colour=INK, shrink=30):
        (x1, y1), (x2, y2) = (P[a] if isinstance(a, str) else a), (P[b] if isinstance(b, str) else b)
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        ax.add_patch(FancyArrowPatch((x1 + nx * off, y1 + ny * off), (x2 + nx * off, y2 + ny * off), arrowstyle="-|>",
                                     mutation_scale=12, lw=1.1, color=colour,
                                     shrinkA=shrink if isinstance(a, str) else 0, shrinkB=shrink if isinstance(b, str) else 0))
        if label:
            ax.text(*at, label, ha="center", va="center", fontsize=7.2, color=MUTED,
                    bbox=dict(fc="white", ec="none", pad=0.6))

    arrow("interested", "happy", "touch", off=0.12, at=(4.5, 4.85))
    arrow("happy", "interested", "button / approach", off=0.12, at=(4.5, 3.95))
    arrow("normal", "interested", "button / approach", off=0.12, at=(2.3, 3.0))
    arrow("interested", "normal", "timeout 2 s", off=0.12, at=(3.55, 3.8))
    arrow("normal", "happy", "touch", off=-0.12, at=(6.55, 2.95))
    arrow("happy", "normal", "timeout 2 s", off=-0.12, at=(5.45, 3.8))
    arrow("normal", "sleepy", "idle 6 s", at=(3.35, 1.25))
    arrow("sleepy", "interested", "button /\napproach", at=(0.75, 2.4))
    ax.plot([2.3, 7.5], [0.4, 0.4], color=INK, lw=1.1)
    arrow((7.5, 0.4), "happy", "touch", at=(7.95, 1.5))
    arrow("afraid", "normal", "clear / fault", at=(9.0, 2.65))
    ax.text(10.9, 3.6, "near from ANY state → afraid\n(priority: only fault is higher)", ha="center", fontsize=7.8, color="#d03b3b")
    ax.text(10.9, 1.35, "afraid holds touch / button /\napproach / timeout / idle", ha="center", fontsize=7.5, color=MUTED)
    ax.text(10.2, 0.2, "clear or fault from ANY state → normal;\ninvalid/stale input also forces neutral output", ha="center",
            fontsize=7.5, color=MUTED)
    ax.text(6.2, 5.45, "Baseline transition table (student_policy.py); priority fault > near > clear > touch > button > approach > timeout > idle",
            ha="center", fontsize=8, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "fsm_diagram.png", dpi=200)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    fig_states()
    fig_latency()
    fig_chain()
    fig_fsm()
    print("ok")


if __name__ == "__main__":
    main()
