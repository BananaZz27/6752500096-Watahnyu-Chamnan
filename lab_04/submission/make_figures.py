"""Figures and extra evidence for Lab 04, built only from the raw CSVs in this folder.

Run from lab_04/:  python submission/make_figures.py

Writes submission/figures/*.png and submission/evidence.json (key rows quoted
in the report: first on updates, clamp onsets, spike and fault rows, mapping
at R = 0 and R = 1). Nothing here changes a raw CSV.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
sys.path.insert(0, str(LAB))
from lab04 import load_contract, mapping  # noqa: E402

OUT = HERE / "figures"
CONDS = ("C0", "C1", "C2", "C3", "C4")
COLOUR = {"C0": "#6b6b6b", "C1": "#2a78d6", "C2": "#eb6834", "C3": "#1baf7a", "C4": "#eda100"}
LABEL = {"C0": "C0 direct R = S", "C1": "C1 baseline", "C2": "C2 k_prod 1.2",
         "C3": "C3 k_clear 0.25", "C4": "C4 k_bind 0"}
INK, MUTED, GRID, ON = "#161616", "#6b6b6b", "#e4e4e4", "#eef3f6"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "axes.axisbelow": True,
})


def load(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    out = []
    for r in rows:
        out.append({k: (None if v == "" else float(v)) for k, v in r.items()})
    return out


def col(rows, key):
    return [r[key] for r in rows]


def shade_on(ax, a=10, b=20):
    ax.axvspan(a, b, color=ON, zorder=0, lw=0)


def fig_timeline(data):
    fig, axes = plt.subplots(3, 1, figsize=(9, 7.0), sharex=True,
                             gridspec_kw={"height_ratios": [1.3, 1.0, 1.0]})
    ax = axes[0]
    shade_on(ax)
    for c in CONDS:
        rows = data[c]
        ax.plot(col(rows, "time_s"), col(rows, "r"), color=COLOUR[c], lw=1.8,
                ls="--" if c == "C0" else "-", label=LABEL[c], drawstyle="steps-post" if c == "C0" else "default")
    ax.set_ylabel("receptor R\n(= H for C1–C4)")
    ax.set_ylim(-0.03, 1.08)
    ax.axhline(1.0, color="#b84a4a", lw=0.8, ls=":")
    ax.text(29.8, 1.02, "H upper bound = 1", ha="right", fontsize=7.5, color="#b84a4a")
    ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.5), fontsize=8)
    ax.text(15, 0.08, "S = 1 for input time [10, 20) s", ha="center", fontsize=8, color=MUTED)

    ax = axes[1]
    shade_on(ax)
    rows = data["C1"]
    t = col(rows, "time_s")
    p, c_, b = col(rows, "p"), col(rows, "c"), col(rows, "b")
    net = [x - y - z for x, y, z in zip(p, c_, b)]
    ax.plot(t, p, color=INK, lw=1.6, label="P = k_prod·S")
    ax.plot(t, c_, color=MUTED, lw=1.6, ls="--", label="C = k_clear·H_old")
    ax.plot(t, b, color=MUTED, lw=1.6, ls=":", label="B = k_bind·R_old")
    ax.plot(t, net, color=COLOUR["C1"], lw=1.6, label="net P − C − B")
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set_ylabel("C1 rate\n(normalized H / s)")
    ax.legend(loc="lower left", ncol=2, fontsize=7.5)

    ax = axes[2]
    shade_on(ax)
    for c in CONDS:
        rows = data[c]
        ax.plot(col(rows, "time_s"), col(rows, "phi_rad"), color=COLOUR[c], lw=1.5,
                ls="--" if c == "C0" else "-", drawstyle="steps-post" if c == "C0" else "default")
    ax.set_ylabel("phi command (rad)")
    ax.set_xlabel("state time_s (s)  — row k+1 is the state after input interval [k·dt, (k+1)·dt)")
    ax.set_ylim(0.18, 0.42)
    fig.suptitle("Step profile: receptor output, C1 rate terms and bounded phi (dt = 0.05 s, H0 = 0)", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_step_timeline.png", dpi=200)
    plt.close(fig)


def fig_zoom(data, metrics):
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.4), sharey=True)
    for ax, (a, b, title) in zip(axes, ((9.8, 13.2, "stimulus on (10 s)"), (19.8, 26.0, "stimulus off (20 s)"))):
        for c in CONDS:
            rows = [r for r in data[c] if a <= r["time_s"] <= b]
            ax.plot(col(rows, "time_s"), col(rows, "r"), color=COLOUR[c], lw=1.6, marker="o", ms=2.2,
                    ls="--" if c == "C0" else "-", label=LABEL[c])
        ax.axhline(0.1, color=MUTED, lw=0.7, ls=":")
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("time_s (s)")
    for c in ("C1", "C2", "C3", "C4"):
        m = metrics[c]
        axes[1].plot(20 + m["recovery_s"], 0.1 * m["peak_r"], marker="v", color=COLOUR[c], ms=7,
                     markeredgecolor="white")
        if c == "C2":
            continue  # identical recovery to C1, labelled together
        text = "C1, C2: " if c == "C1" else f"{c}: "
        dx, ha = (-0.12, "right") if c == "C1" else (0.0, "center")
        axes[1].text(20 + m["recovery_s"] + dx, 0.1 * m["peak_r"] + 0.05, f"{text}{m['recovery_s']:.2f} s",
                     ha=ha, fontsize=7.5, color=INK)
    axes[0].text(11.6, 0.03, "R = 0.1 (latency level)", ha="left", fontsize=7, color=MUTED)
    axes[0].set_ylabel("receptor R")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=8)
    axes[1].text(25.9, 0.6, "▼ = recovery: first state with\nR ≤ 10 % of on-window peak", ha="right",
                 fontsize=7.5, color=MUTED)
    fig.suptitle("Zoom on the transitions (dots = logged states every 0.05 s)", fontsize=10)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(OUT / "fig2_transition_zoom.png", dpi=200)
    plt.close(fig)


def fig_metrics(metrics):
    items = [("auc_h_left", "AUC_H (H·s)", "{:.2f}"), ("rise_10_90_s", "rise 10–90 % (s)", "{:.2f}"),
             ("recovery_s", "recovery (s)", "{:.2f}"), ("upper_clamp_fraction", "upper clamp fraction", "{:.3f}")]
    fig, axes = plt.subplots(1, 4, figsize=(10, 2.7))
    for ax, (key, title, fmt) in zip(axes, items):
        vals = [metrics[c][key] for c in CONDS]
        top = max(v for v in vals if v is not None)
        for i, (c, v) in enumerate(zip(CONDS, vals)):
            if v is None:
                ax.text(i, top * 0.04, "N/A", ha="center", va="bottom", fontsize=7.5, color=MUTED)
                continue
            ax.bar(i, v, color=COLOUR[c], width=0.62)
            ax.text(i, v, fmt.format(v), ha="center", va="bottom", fontsize=7.5, color=INK)
        ax.set_xticks(range(len(CONDS)))
        ax.set_xticklabels(CONDS, fontsize=8)
        ax.set_title(title, fontsize=9)
        ax.set_ylim(0, top * 1.22 if top > 0 else 1)
        ax.set_xlim(-0.7, len(CONDS) - 0.3)
        ax.grid(axis="x", visible=False)
    fig.suptitle("Step-profile metrics from comparison/metrics.json (peak_H = 1 for C2–C4, so peak cannot separate them)",
                 fontsize=9.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig3_metrics.png", dpi=200)
    plt.close(fig)


def fig_extreme(ext):
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 5.2), sharex=True)
    spec = [("zero", "zero: S = 0 for 30 s"), ("one", "one: S = 1 for 30 s"),
            ("spike", "spike: S = 1 for one input interval at 10.00 s"),
            ("fault", "fault: step, but S = NaN at input time 15.00 s")]
    for ax, (name, title) in zip(axes.flat, spec):
        rows = ext[name]
        t = col(rows, "time_s")
        s = [0.0 if r["stimulus"] is None or r["stimulus"] != r["stimulus"] else r["stimulus"] for r in rows]
        ax.step(t, s, where="pre", color=MUTED, lw=1.0, ls="--", label="S (input of the row)")
        ax.plot(t, col(rows, "h"), color=COLOUR["C1"], lw=1.8, label="H (C1)")
        faults = [r["time_s"] for r in rows if r["fault"] == 1]
        for ft in faults:
            ax.axvline(ft, color="#b84a4a", lw=1.0)
            ax.text(21.0, 0.55, f"fault = 1 at {ft:.2f} s\nH = R = 0, then\nH = 0.04 at {ft + 0.05:.2f} s",
                    fontsize=7.5, color="#b84a4a")
        ax.set_title(title, fontsize=9)
        ax.set_ylim(-0.05, 1.1)
        if name == "spike":
            ins = ax.inset_axes([0.45, 0.35, 0.5, 0.55])
            seg = [r for r in rows if 9.8 <= r["time_s"] <= 12]
            ins.plot(col(seg, "time_s"), col(seg, "h"), color=COLOUR["C1"], marker="o", ms=2)
            ins.set_title("zoom: peak H = 0.04 at 10.05 s", fontsize=7)
            ins.tick_params(labelsize=6.5)
    axes[0, 0].legend(loc="upper left", fontsize=7.5)
    for ax in axes[1]:
        ax.set_xlabel("time_s (s)")
    fig.suptitle("Extreme inputs, condition C1", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig4_extreme_inputs.png", dpi=200)
    plt.close(fig)


def _box(ax, x, y, w, h, text, fc="#ffffff", fs=8.3):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
                                fc=fc, ec=INK, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.35)


def _arrow(ax, p, q, label=None, dx=0.0, dy=0.1, style="-|>", colour=INK, ls="-", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=12, lw=1.2, color=colour,
                                 ls=ls, connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((p[0] + q[0]) / 2 + dx, (p[1] + q[1]) / 2 + dy, label, ha="center", fontsize=7.3, color=MUTED)


def fig_block():
    fig, ax = plt.subplots(figsize=(11, 3.6))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    _box(ax, 0.1, 2.6, 1.4, 0.8, "stimulus S\n(validated:\nfinite, 0–1)", fc="#f3f3f3")
    _box(ax, 2.0, 2.75, 1.5, 0.5, "P = k_prod·S")
    _box(ax, 2.0, 1.75, 1.5, 0.5, "C = k_clear·H_old")
    _box(ax, 2.0, 0.75, 1.5, 0.5, "B = k_bind·R_old")
    _box(ax, 4.1, 1.55, 1.9, 0.9, "H_raw = H_old\n+ dt (P − C − B)")
    _box(ax, 6.6, 1.65, 1.3, 0.7, "clamp\n[0, 1] → H_new")
    _box(ax, 8.5, 1.65, 1.3, 0.7, "receptor\nR = norm(H)")
    _box(ax, 10.4, 1.45, 2.5, 1.1, "bounded mapping\nphi = clamp(0.20+0.20R)\nstride = clamp(0.055+0.010R)", fs=7.6)
    _box(ax, 0.1, 0.75, 1.4, 1.0, "memory\nH_old ← H_new\n(one state)", fc="#f3f3f3")
    _arrow(ax, (1.5, 3.0), (2.0, 3.0))
    _arrow(ax, (3.5, 3.0), (4.6, 2.45), "+", dx=0.1)
    _arrow(ax, (3.5, 2.0), (4.1, 2.0), "−", dy=0.05)
    _arrow(ax, (3.5, 1.0), (4.6, 1.55), "−", dx=0.1)
    _arrow(ax, (6.0, 2.0), (6.6, 2.0))
    _arrow(ax, (7.9, 2.0), (8.5, 2.0), "H_new")
    _arrow(ax, (9.8, 2.0), (10.4, 2.0), "R_new")
    ax.plot([7.25, 7.25, 0.8], [1.65, 0.3, 0.3], color=MUTED, lw=1.2, ls="--")
    _arrow(ax, (0.8, 0.3), (0.8, 0.75), colour=MUTED, ls="--")
    ax.text(4.0, 0.08, "H_new is stored and becomes H_old of the next step", ha="center", fontsize=7.3, color=MUTED)
    _arrow(ax, (1.5, 1.5), (2.0, 1.9), colour=MUTED, ls="--")
    _arrow(ax, (1.5, 1.0), (2.0, 1.0), colour=MUTED, ls="--")
    ax.text(11.65, 3.2, "→ Week 03 CPG (phi, stride)\nnot run in Lab 04", ha="center", fontsize=7.8, color=MUTED)
    ax.text(0.8, 2.25, "invalid S → fault = 1,\nH = R = 0", ha="center", fontsize=6.8, color="#b84a4a")
    ax.text(6.5, 3.95, "C and B use the same OLD state; H is updated once per step; C0 bypasses all of this with R = S",
            ha="center", fontsize=8, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / "block_diagram.png", dpi=200)
    plt.close(fig)


def evidence(data, ext):
    def pick(rows, t, keys=("time_s", "input_time_s", "stimulus", "h", "r", "raw", "p", "c", "b", "fault",
                            "phi_rad", "stride_half_m")):
        r = next(x for x in rows if abs(x["time_s"] - t) < 1e-9)
        return {k: r[k] for k in keys}

    contract = load_contract(LAB / "handoff_contract.json")
    out = {
        "C1_first_on_updates": [pick(data["C1"], 10.0), pick(data["C1"], 10.05), pick(data["C1"], 10.1)],
        "C1_first_off_update": [pick(data["C1"], 20.0), pick(data["C1"], 20.05)],
        "upper_clamp_onset": {},
        "spike_rows_with_S_1": [r["input_time_s"] for r in ext["spike"][1:] if r["stimulus"] == 1.0],
        "spike_peak_row": pick(ext["spike"], 10.05),
        "fault_rows": [pick(ext["fault"], t) for t in (15.0, 15.05, 15.1)],
        "one_profile": {"h_at_10s": pick(ext["one"], 10.0)["h"], "h_at_30s": pick(ext["one"], 30.0)["h"],
                        "upper_clamp_rows": sum(r["upper_clamp"] for r in ext["one"])},
        "zero_profile": {"max_h": max(col(ext["zero"], "h")), "phi_values": sorted(set(col(ext["zero"], "phi_rad")))},
        "mapping_endpoints": {"R=0": mapping(0.0, contract), "R=1": mapping(1.0, contract)},
    }
    for c in ("C2", "C3", "C4"):
        rows = data[c]
        first = next(r for r in rows if r["upper_clamp"] == 1)
        out["upper_clamp_onset"][c] = {"time_s": first["time_s"], "input_time_s": first["input_time_s"],
                                       "raw": first["raw"], "updates_clamped": sum(r["upper_clamp"] for r in rows)}
    (HERE / "evidence.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main():
    OUT.mkdir(exist_ok=True)
    data = {c: load(HERE / "comparison" / f"{c}_step.csv") for c in CONDS}
    metrics = {m["condition"]: m for m in json.loads((HERE / "comparison" / "metrics.json").read_text(encoding="utf-8"))}
    ext = {p: load(HERE / p / f"C1_{p}.csv") for p in ("zero", "one", "spike", "fault")}
    fig_timeline(data)
    fig_zoom(data, metrics)
    fig_metrics(metrics)
    fig_extreme(ext)
    fig_block()
    print(json.dumps(evidence(data, ext), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
