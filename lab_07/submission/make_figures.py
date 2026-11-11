"""Figures for Lab 07 from completed_run/ (offline virtual transport) plus the ROS graph diagram.

Run from lab_07/:  python submission/make_figures.py
Nothing here changes a recorded trace.
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
RUN = HERE / "completed_run"
OUT = HERE / "figures"
STATES = ("normal", "interested", "happy", "afraid", "sleepy")
CCOL = {"C0": "#2a78d6", "C1": "#eb6834"}
INK, MUTED, GRID = "#161616", "#6b6b6b", "#e4e4e4"
PRIMARY = ["button_01", "touch_01", "approach_01", "clear_01", "near_01", "clear_02", "button_02"]

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "axes.axisbelow": True,
})


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def summary():
    return json.loads((RUN / "summary.json").read_text(encoding="utf-8"))


def fig_timeline():
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 5.4), sharex=True, gridspec_kw={"height_ratios": [1, 1, 0.6]})
    for ax, cond in zip(axes[:2], ("C0", "C1")):
        rows = load(RUN / f"{cond}_r02" / "command_trace.csv")
        t = [float(r["time_s"]) for r in rows]
        ax.step(t, [STATES.index(r["emotion"]) for r in rows], where="post", color=CCOL[cond], lw=1.2)
        ax.set_yticks(range(5))
        ax.set_yticklabels(STATES, fontsize=7.5)
        ax.invert_yaxis()
        m = next(x for x in summary() if x["condition"] == cond and x["seed"] == 42)
        ax.set_title(f"{cond} {'ideal transport' if cond == 'C0' else 'jitter 0–0.18 s + drop 8 % + burst 12.5–12.7 s'} — "
                     f"{m['state_transitions']} transitions, {m['fault_ticks']} fault ticks", fontsize=8.5, loc="left")
        faults = [float(r["time_s"]) for r in rows if r["fault_channels"]]
        axes[2].eventplot([faults], lineoffsets=[0 if cond == "C0" else 1], linelengths=0.7, colors=[CCOL[cond]], linewidths=1.0)
    axes[2].set_yticks([0, 1])
    axes[2].set_yticklabels(["C0 fault", "C1 fault"], fontsize=7.5)
    axes[2].set_xlabel("virtual time (s), seed 42 (same source stimuli)")
    axes[2].text(11.0, 1.55, "shared invalid (11 s) and stale (12 s) probes", fontsize=7, color=MUTED, ha="center")
    fig.suptitle("Same policy and stimuli: receipt jitter makes samples older than 0.12 s → stale faults force neutral, then events re-fire",
                 fontsize=9.3)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_emotion_fault_timeline.png", dpi=200)
    plt.close(fig)


def fig_latency():
    fig, ax = plt.subplots(figsize=(9.5, 3.3))
    for m in summary():
        c = m["condition"]
        out = {o["input_id"]: o for o in m["source_outcomes"]}
        for i, iid in enumerate(PRIMARY):
            x = i + (-0.22 if c == "C0" else 0.22) + (m["seed"] - 42) * 0.07
            lat = out[iid]["both_latency_s"]
            if lat is None:
                ax.plot(x, 0.3, marker="x", color=CCOL[c], ms=7, mew=1.8)
            else:
                ax.plot(x, lat, "o", color=CCOL[c], ms=5, markeredgecolor="white", mew=0.6)
    ax.axhline(0.3, color=MUTED, lw=0.5, ls=":")
    ax.text(6.5, 0.307, "× = missing (no both onset)", ha="right", fontsize=7.5, color=MUTED)
    ax.set_xticks(range(len(PRIMARY)))
    ax.set_xticklabels(PRIMARY, fontsize=8)
    ax.set_ylim(0, 0.33)
    ax.set_ylabel("both latency (s)")
    ax.plot([], [], "o", color=CCOL["C0"], label="C0 ideal")
    ax.plot([], [], "o", color=CCOL["C1"], label="C1 jitter + drop")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.set_title("Primary 7 × seeds 41/42/43 (left→right per colour); deadline 1 s, observation window 22 s", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig2_latency.png", dpi=200)
    plt.close(fig)


def fig_transport():
    s = [m for m in summary() if m["condition"] == "C1"]
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.0), gridspec_kw={"width_ratios": [1.25, 1]})
    keys = (("accepted", "accepted", "#2a78d6"), ("discarded_out_of_order", "out-of-order (discarded)", "#eda100"),
            ("transport_dropped", "dropped", "#d03b3b"), ("censored_after_trial", "censored > 22 s", "#6b6b6b"))
    for i, m in enumerate(s):
        left = 0
        for k, lab, col in keys:
            axes[0].barh(i, m[k], left=left, color=col, label=lab if i == 0 else None, height=0.6)
            if m[k] > 150:
                axes[0].text(left + m[k] / 2, i, str(m[k]), ha="center", va="center", fontsize=7, color="white")
            left += m[k]
    axes[0].set_yticks(range(len(s)))
    axes[0].set_yticklabels([f"C1 seed {m['seed']}" for m in s], fontsize=8)
    axes[0].set_xlabel("messages on 3 input topics (published = 3303)")
    axes[0].legend(loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=2, fontsize=7)
    axes[0].grid(axis="y", visible=False)
    ages = [float(r["transport_age_s"]) for r in load(RUN / "C1_r02" / "input_trace.csv") if r["transport_age_s"] not in ("", None)]
    vals = sorted(set(ages))
    axes[1].bar([f"{v:.2f}" for v in vals], [ages.count(v) for v in vals], color="#eb6834", width=0.65)
    axes[1].set_title("C1 seed 42: transport age of received messages", fontsize=8.5)
    axes[1].set_xlabel("receipt − publish (s)")
    axes[1].axvline(4.5, color="#b84a4a", lw=0.8, ls=":")
    axes[1].text(4.6, max(ages.count(v) for v in vals) * 0.9, "> 0.12 s: stale\non arrival", fontsize=7, color="#b84a4a")
    axes[1].grid(axis="x", visible=False)
    fig.suptitle("C1 transport: about half of received messages arrive after a newer one and are discarded", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig3_transport.png", dpi=200)
    plt.close(fig)


def _box(ax, x, y, w, h, text, fc="#ffffff", ec=INK, fs=7.6, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06", fc=fc, ec=ec, lw=1.2, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.3)


def _arrow(ax, p, q, label=None, colour=INK, ls="-", dy=0.1, fs=6.6):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=11, lw=1.1, color=colour, ls=ls))
    if label:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, label, ha="center", fontsize=fs, color=MUTED)


def fig_graph():
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 7.2)
    ax.axis("off")
    # Lab07 source (implemented)
    _box(ax, 0.2, 3.9, 2.5, 1.5, "synthetic_inputs\n(week07_inputs)\nLab07 role 1\n— or ESP32 sensors via\nmicro-ROS (planned)")
    _box(ax, 5.2, 3.9, 2.9, 1.5, "interaction\n(week07_interaction)\nLab07 role 2: filter + FSM\n+ pose/RGB, 50 Hz timer\nstate: H/emotion")
    _box(ax, 11.4, 3.9, 3.3, 1.5, "output_collector\n(week07_output_collector)\nLab07 role 3: receipt log\n— or servo/LED driver (planned)")
    for i, (topic, typ) in enumerate((("/lamp/input/button", "Bool"), ("/lamp/input/touch", "Bool"), ("/lamp/input/distance", "Float32 [m]"))):
        y = 5.15 - i * 0.5
        _arrow(ax, (2.7, y), (5.2, y))
        ax.text(3.95, y + 0.06, f"{topic}  {typ}", ha="center", fontsize=6.4, color=INK)
    for i, (topic, typ) in enumerate((("/lamp/interaction", "String event"), ("/lamp/emotion", "String state"),
                                      ("/lamp/servo_command", "Float32MultiArray rad [tilt, extend, nod]"),
                                      ("/lamp/rgb_command", "ColorRGBA 0–1, a = 1"))):
        y = 5.25 - i * 0.4
        _arrow(ax, (8.1, y), (11.4, y))
        ax.text(9.75, y + 0.05, f"{topic}  {typ}", ha="center", fontsize=6.1, color=INK)
    ax.text(7.5, 6.95, "Seven /lamp application topics · QoS RELIABLE, KEEP_LAST depth 10, VOLATILE on every pub/sub (ROS 2 Jazzy, Ubuntu 24.04)",
            ha="center", fontsize=8.2, color=INK)
    ax.text(7.5, 6.55, "Boundaries: no Header on any of the 7 messages → each node logs perf_counter_ns in its own sidecar CSV (same host only); "
            "source→physical latency = N/A", ha="center", fontsize=7.3, color="#b84a4a")
    # Planned extension
    _box(ax, 0.2, 0.35, 2.5, 1.6, "ESP32 firmware\n(micro-ROS client)\nToF distance, touch pad,\nbutton, 3 servos, RGB LED", fc="#f3f3f3", ls="--")
    _box(ax, 3.4, 0.6, 2.3, 1.1, "micro-ROS Agent\n(host, serial/UDP)", fc="#f3f3f3", ls="--")
    _box(ax, 6.4, 0.35, 2.6, 1.6, "ahm_node (planned)\nH: production–clearance\n–binding → R\nsubscribes interaction", fc="#f3f3f3", ls="--")
    _box(ax, 9.7, 0.35, 2.4, 1.6, "so2_cpg_node (planned)\nα, φ(R) → o₁, o₂\n→ nod rhythm", fc="#f3f3f3", ls="--")
    _box(ax, 12.6, 0.35, 2.1, 1.6, "logger / rosbag2\n+ camera & photodiode\n(physical onset)", fc="#f3f3f3", ls="--")
    _arrow(ax, (2.7, 1.15), (3.4, 1.15), colour=MUTED, ls="--")
    _arrow(ax, (4.55, 1.7), (4.55, 3.85), "same 3 input topics\n(replaces role 1)", colour=MUTED, ls="--", dy=0.0)
    _arrow(ax, (6.65, 3.85), (7.4, 1.95), colour=MUTED, ls="--")
    ax.text(7.5, 2.95, "/lamp/interaction", fontsize=6.4, color=MUTED, ha="left")
    _arrow(ax, (9.0, 1.15), (9.7, 1.15), colour=MUTED, ls="--")
    ax.text(9.35, 2.15, "R: new topic,\nversioned contract", ha="center", fontsize=6.4, color=MUTED)
    _arrow(ax, (10.9, 1.95), (7.6, 3.85), colour=MUTED, ls="--")
    ax.text(9.95, 2.95, "nod / emotion modulation", fontsize=6.4, color=MUTED, ha="left")
    ax.text(7.5, 0.05, "Dashed = Mini Project extension planned in proposal.json; NOT implemented or run in Lab07", ha="center",
            fontsize=7.5, color=MUTED)
    fig.tight_layout()
    fig.savefig(OUT / "ros_graph.png", dpi=200)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    fig_timeline()
    fig_latency()
    fig_transport()
    fig_graph()
    print("ok")


if __name__ == "__main__":
    main()
