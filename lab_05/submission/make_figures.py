"""Figures for Lab 05, built only from the raw CSV / metrics in this folder.

Run from lab_05/:  python submission/make_figures.py
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
OUT = HERE / "figures"
CONDS = ("B0", "B1", "B2", "B3")
COLOUR = {"B0": "#6b6b6b", "B1": "#2a78d6", "B2": "#eb6834", "B3": "#1baf7a"}
LABEL = {"B0": "B0 fixed R = 0", "B1": "B1 direct R = S", "B2": "B2 hormone", "B3": "B3 binding ablation"}
INK, MUTED, GRID, ON = "#161616", "#6b6b6b", "#e4e4e4", "#eef3f6"
LEGS = ("LF", "RM", "LH", "RF", "LM", "RH")

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "axes.axisbelow": True,
})


def load(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        out = []
        for r in csv.DictReader(handle):
            row = {}
            for k, v in r.items():
                try:
                    row[k] = None if v == "" else float(v)
                except ValueError:
                    row[k] = v
            out.append(row)
        return out


def col(rows, key):
    return [r[key] for r in rows]


def cycle_freq(states):
    """Per-cycle frequency from interpolated rising crossings of o1 (same rule as lab05.py)."""
    t = []
    for a, b in zip(states, states[1:]):
        if a["o1"] <= 0 < b["o1"]:
            f = -a["o1"] / (b["o1"] - a["o1"])
            t.append(a["state_time_s"] + f * (b["state_time_s"] - a["state_time_s"]))
    return [(x + y) / 2 for x, y in zip(t, t[1:])], [1 / (y - x) for x, y in zip(t, t[1:])]


def fig_comparison():
    d = HERE / "comparison"
    iv = {c: load(d / f"{c}_intervals.csv") for c in CONDS}
    st = {c: load(d / f"{c}_states.csv") for c in CONDS}
    fig, axes = plt.subplots(3, 1, figsize=(9, 7), sharex=True, gridspec_kw={"height_ratios": [1, 1, 1]})
    for ax in axes:
        ax.axvspan(10, 20, color=ON, lw=0, zorder=0)
    for c in CONDS:
        axes[0].step(col(iv[c], "command_time_s"), col(iv[c], "phi_rad"), where="post", color=COLOUR[c], lw=1.7,
                     ls="--" if c == "B1" else "-", label=LABEL[c])
        x, f = cycle_freq(st[c])
        axes[1].plot(x, f, color=COLOUR[c], lw=1.4, marker="o", ms=3, ls="--" if c == "B1" else "-")
        base = col(st["B0"], "body_x_m")
        axes[2].plot(col(st[c], "state_time_s"), [a - b for a, b in zip(col(st[c], "body_x_m"), base)],
                     color=COLOUR[c], lw=1.7, ls="--" if c == "B1" else "-")
    axes[0].set_ylabel("φ command (rad)\nused in [t_k, t_k+1)")
    axes[0].legend(loc="upper left", fontsize=8, ncol=2)
    axes[0].set_ylim(0.17, 0.46)
    axes[1].set_ylabel("cycle frequency (Hz)\n1 / o₁ period")
    axes[2].set_ylabel("body x − body x of B0 (m)")
    axes[2].set_xlabel("time (s)   — shaded: S = 1 for input/command time [10, 20)")
    m = json.loads((d / "metrics.json").read_text(encoding="utf-8"))
    txt = "  ".join(f"{c}: {m[c]['distance_m']:.3f} m" for c in CONDS)
    axes[2].text(0.02, 0.9, "total distance 0–30 s\n" + txt, transform=axes[2].transAxes, fontsize=7.5,
                 color=INK, va="top", ha="left")
    fig.suptitle("Comparison (mapping both, step): command, CPG frequency and kinematic body position", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_comparison.png", dpi=200)
    plt.close(fig)


def fig_one_factor():
    runs = (("comparison", "both"), ("phi_only", "phi-only"), ("stride_only", "stride-only"))
    seg = {}
    for d, name in runs:
        m = json.loads((HERE / d / "metrics.json").read_text(encoding="utf-8"))
        seg[name] = {c: m[c]["segments"]["on"] for c in CONDS}
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.2))
    width = 0.2
    for ax, key, title, fmt in ((axes[0], "frequency_hz", "on-segment frequency (Hz)", "{:.3f}"),
                                (axes[1], "distance_m", "on-segment distance [10, 20) s (m)", "{:.3f}")):
        for j, c in enumerate(CONDS):
            vals = [seg[name][c][key] for _, name in runs]
            xs = [i + (j - 1.5) * width for i in range(len(runs))]
            ax.bar(xs, vals, width=width * 0.92, color=COLOUR[c], label=LABEL[c])
            for x, v in zip(xs, vals):
                ax.text(x, v, fmt.format(v), ha="center", va="bottom", fontsize=6.3, rotation=90, color=INK)
        ax.set_xticks(range(len(runs)))
        ax.set_xticklabels([n for _, n in runs])
        ax.set_title(title, fontsize=9)
        ax.grid(axis="x", visible=False)
        ax.set_ylim(0, max(seg[n][c][key] for _, n in runs for c in CONDS) * 1.3)
    axes[0].legend(loc="upper right", fontsize=7, ncol=1)
    fig.suptitle("One factor at a time: φ sets frequency, stride sets distance per cycle (same B0–B3 schedule)", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig2_one_factor.png", dpi=200)
    plt.close(fig)


def fig_fault():
    d = HERE / "fault"
    fig, axes = plt.subplots(2, 1, figsize=(8, 4.6), sharex=True)
    for c in ("B1", "B2", "B3"):
        iv = [r for r in load(d / f"{c}_intervals.csv") if 14.5 <= r["command_time_s"] <= 16.5]
        axes[0].step(col(iv, "command_time_s"), col(iv, "phi_rad"), where="post", color=COLOUR[c], lw=1.7,
                     marker="o", ms=2.5, label=LABEL[c], ls="--" if c == "B1" else "-")
        if c != "B1":
            stt = [r for r in load(d / f"{c}_states.csv") if 14.5 <= r["state_time_s"] <= 16.5]
            axes[1].plot(col(stt, "state_time_s"), col(stt, "h"), color=COLOUR[c], lw=1.7, marker="o", ms=2.5)
    for ax in axes:
        ax.axvspan(15.0, 15.05, color="#f4d8d8", lw=0, zorder=0)
    axes[0].set_ylabel("φ command (rad)")
    axes[0].legend(loc="lower right", fontsize=8)
    axes[0].text(15.08, 0.3, "command 15.00: fault = 1 → R_used = 0,\nφ = 0.20, stride = 0.055 (before CPG update)",
                 fontsize=7.5, color="#b84a4a")
    axes[1].set_ylabel("H state")
    axes[1].set_xlabel("time (s) — red band = interval [15.00, 15.05) with S = NaN")
    axes[1].text(15.12, 0.45, "state 15.05: H = 0\nstate 15.10: H = 0.04 (B2)", fontsize=7.5, color="#b84a4a")
    fig.suptitle("Fault profile: one NaN input at 15.00 s", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig3_fault.png", dpi=200)
    plt.close(fig)


def fig_contact():
    d = HERE / "contact"
    cases = ("matched", "gain-offset", "mixed-delay", "all-inverted", "constant", "fault")
    colours = dict(zip(cases, ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#6b6b6b", "#e87ba4")))
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.3))
    for case in cases:
        rows = load(d / f"{case}.csv")
        t = col(rows, "sample_time_s")
        axes[0].plot(t, [r["sif"] if r["sif"] is not None else float("nan") for r in rows], color=colours[case],
                     lw=1.6, label=case)
    axes[0].set_title("SIF (population SD of 6 SI); gaps = unavailable", fontsize=9)
    axes[0].set_xlabel("sample time (s)")
    axes[0].set_ylim(-0.05, 0.6)
    axes[0].axvspan(15.0, 17.45, color="#f4d8d8", lw=0, zorder=0)
    axes[0].text(15.1, 0.2, "fault case:\nno SIF\n15.00–17.45 s", fontsize=7, color="#b84a4a")
    axes[0].legend(loc="center left", fontsize=7, ncol=1)
    axes[0].text(29.5, 0.04, "matched, gain-offset, all-inverted, fault: SIF = 0 (overlap)\nconstant: no valid SIF at all",
                 ha="right", fontsize=6.8, color=MUTED)
    rows = load(d / "mixed-delay.csv")
    seg = [r for r in rows if 5 <= r["sample_time_s"] <= 7]
    t = col(seg, "sample_time_s")
    axes[1].plot(t, col(seg, "LF_expected"), color=INK, lw=1.6, label="LF expected = actual (SI = 1)")
    axes[1].plot(t, col(seg, "RF_expected"), color=MUTED, lw=1.6, label="RF expected")
    axes[1].plot(t, col(seg, "RF_actual"), color=colours["mixed-delay"], lw=1.6, ls="--", label="RF actual, 0.25 s late (SI ≈ 0)")
    axes[1].set_title("mixed-delay: synthetic 1 Hz contact proxy", fontsize=9)
    axes[1].set_xlabel("sample time (s)")
    axes[1].legend(loc="lower left", fontsize=7)
    axes[1].set_ylim(-0.35, 1.05)
    fig.suptitle("Contact mini-lab (synthetic signals, proposed paired Pearson; not fed back to the controller)", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig4_contact.png", dpi=200)
    plt.close(fig)


def _box(ax, x, y, w, h, text, fc="#ffffff", fs=8.2, ec=INK, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
                                fc=fc, ec=ec, lw=1.2, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.35)


def _arrow(ax, p, q, label=None, dy=0.12, colour=INK, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=12, lw=1.2, color=colour, ls=ls))
    if label:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, label, ha="center", fontsize=7.3, color=MUTED)


def fig_block():
    fig, ax = plt.subplots(figsize=(11, 3.3))
    ax.set_xlim(0, 13.4)
    ax.set_ylim(0, 3.9)
    ax.axis("off")
    y, h = 1.5, 0.9
    _box(ax, 0.1, y, 1.3, h, "S schedule\n0 / 1 / 0\n(no sensing)", fc="#f3f3f3")
    _box(ax, 1.9, y, 2.0, h, "controller\nB0: R = 0   B1: R = S\nB2/B3: hormone H")
    _box(ax, 4.4, y, 1.9, h, "bounded mapping\nφ, stride_half", fs=8)
    _box(ax, 6.8, y, 1.6, h, "SO(2) CPG\nα = 1.10")
    _box(ax, 8.9, y, 1.7, h, "tripod decoder\ncontact = sign(o₂)")
    _box(ax, 11.1, y, 2.2, h, "stance-anchor body\n(no mass, force,\nslip, CoM)", fc="#f3f3f3")
    _arrow(ax, (1.4, y + h / 2), (1.9, y + h / 2))
    _arrow(ax, (3.9, y + h / 2), (4.4, y + h / 2), "R_used")
    _arrow(ax, (6.3, y + h / 2), (6.8, y + h / 2), "φ")
    _arrow(ax, (8.4, y + h / 2), (8.9, y + h / 2), "o₁, o₂")
    _arrow(ax, (10.6, y + h / 2), (11.1, y + h / 2))
    ax.add_patch(FancyArrowPatch((5.6, y), (9.6, y), connectionstyle="arc3,rad=0.3", arrowstyle="-|>",
                                 mutation_scale=12, lw=1.0, color=MUTED, ls="--"))
    ax.text(7.6, 0.75, "stride_half", ha="center", fontsize=7.3, color=MUTED)
    # missing feedback
    ax.add_patch(FancyArrowPatch((12.2, y + h), (2.9, y + h), connectionstyle="arc3,rad=0.15", arrowstyle="-|>",
                                 mutation_scale=12, lw=1.2, color="#b84a4a", ls=":"))
    ax.text(7.6, 3.6, "MISSING: no body / terrain / contact-sensor feedback to S or to the hormone (open loop)",
            ha="center", fontsize=8, color="#b84a4a")
    ax.text(6.7, 0.2, "contact mini-lab: synthetic expected vs actual → SI, SIF, release (separate; not connected to this chain)",
            ha="center", fontsize=7.5, color=MUTED)
    fig.tight_layout()
    fig.savefig(OUT / "block_diagram.png", dpi=200)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    fig_comparison()
    fig_one_factor()
    fig_fault()
    fig_contact()
    fig_block()
    print("ok")


if __name__ == "__main__":
    main()
