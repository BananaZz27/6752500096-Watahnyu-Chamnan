"""Create the Lab 02 figures from the raw trial CSVs in this folder.

Run from lab_02/:  python submission/make_figures.py

Event times use the same helpers as lab02.py (_crossing_time and
_first_correct_latency), so the markers match summary_trials.csv exactly.
Nothing here changes a raw CSV.
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from lab02 import LabConfig, _crossing_time, _first_correct_latency  # noqa: E402

OUT = HERE / "figures"
CFG = LabConfig()
C_TRUE, C_RAW, C_FILT = "#161616", "#A7ADB1", "#147A8C"
C_THR, C_ENTER, C_EXIT = "#B84A4A", "#147A8C", "#C17824"


def load(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def num(value: str) -> float:
    return math.nan if value == "" else float(value)


def events(rows: list[dict[str, str]]) -> dict[str, float | None]:
    enter_x = _crossing_time(rows, "down", CFG.threshold_m)
    exit_x = _crossing_time(rows, "up", CFG.threshold_m)
    enter_lat = _first_correct_latency(rows, enter_x, "NEAR")
    exit_lat = _first_correct_latency(rows, exit_x, "FAR")
    return {
        "enter_cross": enter_x,
        "exit_cross": exit_x,
        "enter_lat": enter_lat,
        "exit_lat": exit_lat,
        "enter_resp": None if enter_lat is None else enter_x + enter_lat,
        "exit_resp": None if exit_lat is None else exit_x + exit_lat,
    }


def mark_events(ax, ev: dict[str, float | None], labels: bool) -> None:
    """Physical crossing (black dashed) and first correct response (coloured)."""
    for key, colour, name in (("enter", C_ENTER, "enter"), ("exit", C_EXIT, "exit")):
        cross, resp = ev[f"{key}_cross"], ev[f"{key}_resp"]
        ax.axvline(cross, color="black", linestyle="--", linewidth=1.1,
                   label=f"physical crossing of 0.35 m ({name})" if labels else None)
        if resp is not None:
            ax.axvline(resp, color=colour, linestyle="-", linewidth=1.6,
                       label=f"first correct response ({name})" if labels else None)


def trial_figure(csv_path: Path, out_path: Path) -> None:
    """Full 20 s view of one trial with crossing and first-response markers."""
    rows = load(csv_path)
    cond = rows[0]["condition"]
    ev = events(rows)
    t = [float(r["time_s"]) for r in rows]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6.8), sharex=True, constrained_layout=True)
    ax1.plot(t, [float(r["true_distance_m"]) for r in rows], color=C_TRUE, lw=2, label="true distance")
    ax1.plot(t, [num(r["raw_distance_m"]) for r in rows], color=C_RAW, lw=1, alpha=0.9, label="raw (sensor)")
    filtered = [num(r["filtered_distance_m"]) for r in rows]
    if any(not math.isnan(v) for v in filtered):
        ax1.plot(t, filtered, color=C_FILT, lw=1.8,
                 label="filtered (logged, but C1 decides from raw)" if cond == "C1" else "filtered")
    ax1.axhline(CFG.threshold_m, color=C_THR, ls="--", lw=1.3, label="T = 0.35 m")
    if cond == "C2":
        ax1.axhline(CFG.enter_threshold_m, color=C_FILT, ls=":", lw=1.3, label="T_enter = 0.32 m")
        ax1.axhline(CFG.exit_threshold_m, color=C_EXIT, ls=":", lw=1.3, label="T_exit = 0.38 m")
    mark_events(ax1, ev, labels=True)
    ax1.set_ylabel("distance (m)")
    ax1.set_ylim(top=0.82)  # head-room so the legend does not cover the trajectory
    ax1.grid(alpha=0.25)
    ax1.legend(loc="upper center", ncol=3, fontsize=8, frameon=True)

    ax2.plot(t, [float(r["command"]) for r in rows], color=C_EXIT, lw=1.6, label="command u")
    ax2.step(t, [1 if r["state"] == "NEAR" else 0 for r in rows], where="post", color=C_FILT, lw=1.4,
             label="state (NEAR = 1)")
    mark_events(ax2, ev, labels=False)
    for r in rows:
        if r["event_label"] in ("ENTER_NEAR", "EXIT_NEAR"):
            ax2.axvline(float(r["time_s"]), color=C_THR, alpha=0.18, lw=0.8)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("command / state")
    ax2.grid(alpha=0.25)
    ax2.legend(loc="center right", fontsize=8)

    def fmt(value: float | None) -> str:
        return "n/a" if value is None else f"{value:.3f} s"

    fig.suptitle(
        f"{rows[0]['trial_id']}  |  sigma = {rows[0]['noise_sigma_m']} m, delay = {rows[0]['delay_ms']} ms  |  "
        f"latency enter {fmt(ev['enter_lat'])}, exit {fmt(ev['exit_lat'])}",
        fontsize=10,
    )
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def zoom_figure(c1_csv: Path, c2_csv: Path, out_path: Path) -> None:
    """C1 and C2 side by side around the enter and exit crossings."""
    trials = {"C1": load(c1_csv), "C2": load(c2_csv)}
    windows = {"enter": (6.3, 7.8), "exit": (12.6, 14.1)}
    fig, axes = plt.subplots(
        4, 2, figsize=(11, 6.6), constrained_layout=True,
        gridspec_kw={"height_ratios": [3, 1, 3, 1]},
    )
    for col, (kind, (w0, w1)) in enumerate(windows.items()):
        for block, cond in enumerate(("C1", "C2")):
            rows = trials[cond]
            ev = events(rows)
            ax_d, ax_s = axes[2 * block][col], axes[2 * block + 1][col]
            sel = [r for r in rows if w0 <= float(r["time_s"]) <= w1]
            t = [float(r["time_s"]) for r in sel]
            ax_d.plot(t, [float(r["true_distance_m"]) for r in sel], color=C_TRUE, lw=2, label="true")
            ax_d.plot(t, [num(r["raw_distance_m"]) for r in sel], color=C_RAW, lw=1.2, label="raw")
            if cond == "C2":
                ax_d.plot(t, [num(r["filtered_distance_m"]) for r in sel], color=C_FILT, lw=1.8, label="filtered")
                ax_d.axhline(CFG.enter_threshold_m, color=C_FILT, ls=":", lw=1.2, label="T_enter 0.32")
                ax_d.axhline(CFG.exit_threshold_m, color=C_EXIT, ls=":", lw=1.2, label="T_exit 0.38")
            ax_d.axhline(CFG.threshold_m, color=C_THR, ls="--", lw=1.2, label="T 0.35")
            ax_s.step(t, [1 if r["state"] == "NEAR" else 0 for r in sel], where="post", color=C_FILT, lw=1.6)
            for ax in (ax_d, ax_s):
                cross, resp = ev[f"{kind}_cross"], ev[f"{kind}_resp"]
                ax.axvline(cross, color="black", ls="--", lw=1.1)
                if resp is not None:
                    ax.axvline(resp, color=C_ENTER if kind == "enter" else C_EXIT, lw=1.6)
                ax.set_xlim(w0, w1)
                ax.grid(alpha=0.25)
            lat = ev[f"{kind}_lat"]
            ax_d.set_title(
                f"{cond} - {kind}: latency = {'n/a' if lat is None else f'{lat:.3f} s'}  ({rows[0]['trial_id']})",
                fontsize=9,
            )
            ax_d.set_ylabel("distance (m)")
            ax_s.set_yticks([0, 1], ["FAR", "NEAR"])
            ax_s.set_ylim(-0.2, 1.2)
            if block == 1:
                ax_s.set_xlabel("time (s)")
            if col == 0:
                ax_d.legend(fontsize=7, loc="upper right", ncol=2)
    fig.suptitle("Black dashed = physical crossing of 0.35 m; coloured line = first correct response", fontsize=10)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def delay_figure(csv_paths: dict[int, Path], out_path: Path) -> None:
    """C2 state around both crossings for several sensor delays (same trajectory)."""
    windows = {"enter": (6.5, 8.2), "exit": (12.9, 14.6)}
    colours = {0: "#161616", 100: C_EXIT, 300: C_FILT}
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4), constrained_layout=True)
    for ax, (kind, (w0, w1)) in zip(axes, windows.items()):
        for offset, (delay, path) in enumerate(sorted(csv_paths.items())):
            rows = load(path)
            ev = events(rows)
            sel = [r for r in rows if w0 <= float(r["time_s"]) <= w1]
            ax.step([float(r["time_s"]) for r in sel],
                    [(1 if r["state"] == "NEAR" else 0) + 0.04 * offset for r in sel],
                    where="post", color=colours[delay], lw=1.8,
                    label=f"delay {delay} ms: latency {ev[f'{kind}_lat']:.3f} s")
        ax.axvline(events(load(next(iter(csv_paths.values()))))[f"{kind}_cross"],
                   color="black", ls="--", lw=1.1, label="physical crossing")
        ax.set_yticks([0, 1], ["FAR", "NEAR"])
        ax.set_xlabel("time (s)")
        ax.set_title(f"C2, sigma = 0 m - {kind}", fontsize=9)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8, loc="center left" if kind == "enter" else "center right")
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def block(ax, x, y, w, h, text, face="#F1F4F6", edge="#3A4A55", fs=8.8, lw=1.3):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=face, ec=edge, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.4)


def path(ax, points, colour="#3A4A55", dashed=False, lw=1.5):
    """Polyline with an arrow head on the last segment."""
    style = "--" if dashed else "-"
    for p0, p1 in zip(points[:-2], points[1:-1]):
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=colour, lw=lw, ls=style, solid_capstyle="butt")
    ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle="-|>", mutation_scale=14,
                                 lw=lw, color=colour, linestyle=style, shrinkA=0, shrinkB=0))


def label(ax, x, y, text, colour="#3A4A55", ha="center", va="bottom", fs=7.6):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color=colour, linespacing=1.25)


def block_diagram(out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(16.2, 7.8))
    ax.set_xlim(0, 16.2)
    ax.set_ylim(0, 7.8)
    ax.axis("off")
    ink, red, purple, grey = "#3A4A55", C_THR, "#6B4C9A", "#7A8A94"

    ax.text(0.5, 7.55, "Sensorimotor loop in the Lab 02 simulator  (dt = 0.02 s, 1001 samples per 20 s trial)",
            fontsize=11, fontweight="bold", color=ink, va="center")

    # Row A: main signal chain
    ya, ha_, w, gap = 4.7, 1.3, 2.3, 0.9
    xs = [0.5 + i * (w + gap) for i in range(5)]
    block(ax, xs[0], ya, w, ha_, "Physical world\nhand / object\ntrue distance d(t)", face="#E8F1F4")
    block(ax, xs[1], ya, w, ha_, "Sensor model\n+ noise n ~ N(0, sigma^2)\n+ delay tau", face="#FBEFD9")
    block(ax, xs[2], ya, w, ha_, "Validity check\nmissing / non-finite /\nout of 0.02-4.0 m", face="#F1F4F6")
    block(ax, xs[3], ya, w, ha_, "Low-pass filter (TODO 1)\ny[k] = b*x[k] + (1-b)*y[k-1]\nbeta = 0.25", face="#E3F2EC", fs=8.2)
    block(ax, xs[4], ya, w, ha_, "Decision rule\nC1 / C2 / C3\nstate: FAR / NEAR", face="#E3F2EC")
    ymid = ya + ha_ / 2
    for i, text in enumerate(["true_\ndistance_m", "raw_\ndistance_m", "valid = 1", "filtered_\ndistance_m"]):
        path(ax, [(xs[i] + w, ymid), (xs[i + 1], ymid)])
        label(ax, xs[i] + w + gap / 2, ymid + 0.1, text)

    # Row B: actuator, invalid path, C0 timer
    yb, hb = 2.5, 1.2
    block(ax, xs[4], yb, w, hb, "Actuator (lamp)\nnormalized command u\nin [-0.6, 0.6]", face="#FBEFD9")
    path(ax, [(xs[4] + w / 2, ya), (xs[4] + w / 2, yb + hb)], colour=ink)
    label(ax, xs[4] + w / 2 - 0.1, 4.05, "state, command", ha="right")

    block(ax, xs[2], yb, w, hb, "valid = 0\nsafe_command() = 0\nstate kept, event = INVALID",
          face="#F8E4E4", edge=red, fs=8.2)
    path(ax, [(xs[2] + w / 2, ya), (xs[2] + w / 2, yb + hb)], colour=red)
    label(ax, xs[2] + w / 2 + 0.12, 4.05, "valid = 0", colour=red, ha="left")
    path(ax, [(xs[2] + w, yb + hb / 2), (xs[4], yb + hb / 2)], colour=red)
    label(ax, (xs[2] + w + xs[4]) / 2, yb + hb / 2 + 0.08, "u = 0 (stale / invalid sample)", colour=red)

    block(ax, 0.5, yb, 5.2, hb,
          "C0 open loop: timer only\nNEAR for 4 <= t < 16 s, no sensor,\nno feedback", face="#EFEFEF", fs=8.4)
    y_route = 2.05
    path(ax, [(3.1, yb), (3.1, y_route), (xs[4] + w * 0.8, y_route), (xs[4] + w * 0.8, yb)], colour=grey)
    label(ax, 8.6, y_route + 0.06, "C0: state, command from the timer (bypasses sensor, validity check and filter)", colour=grey)

    # Row C: decision rules
    yc, hc, wc = 0.35, 1.35, 4.85
    block(ax, 0.5, yc, wc, hc,
          "C1 single threshold  (TODO 2)\nuses raw distance\nraw < T = 0.35 m -> NEAR, u = 0.6;  else FAR, u = 0",
          face="#FFFFFF", fs=8.2)
    block(ax, 0.5 + wc + 0.3, yc, wc, hc,
          "C2 filter + hysteresis  (TODO 3)\nFAR -> NEAR if filtered < 0.32 m\nNEAR -> FAR if filtered > 0.38 m; else keep state",
          face="#FFFFFF", fs=8.2)
    block(ax, 0.5 + 2 * (wc + 0.3), yc, wc, hc,
          "C3 proportional + clamp  (TODO 4)\nu = clamp(Kp*(0.35 - filtered), -0.6, 0.6),  Kp = 2\nstate = NEAR if filtered < 0.35 m",
          face="#FFFFFF", fs=8.2)

    # feedback path (concept only)
    xr = xs[4] + w
    path(ax, [(xr, yb + hb / 2), (16.0, yb + hb / 2), (16.0, 6.7), (xs[0] + w / 2, 6.7), (xs[0] + w / 2, ya + ha_)],
         colour=purple, dashed=True)
    label(ax, 8.2, 6.78,
          "feedback: lamp motion / light changes what the sensor sees.  NOT simulated in Lab 02:\n"
          "true_distance_m follows a fixed 20 s trajectory, so the command does not change the next sample",
          colour=purple, fs=8.4)
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    cmp_dir = HERE / "student_comparison" / "trials"
    full_dir = HERE / "c2_full" / "trials"
    trial_figure(cmp_dir / "C1_n0.01_d000_r01.csv", OUT / "fig1_C1_trial.png")
    trial_figure(cmp_dir / "C2_n0.01_d000_r01.csv", OUT / "fig2_C2_trial.png")
    zoom_figure(cmp_dir / "C1_n0.01_d000_r01.csv", cmp_dir / "C2_n0.01_d000_r01.csv",
                OUT / "fig3_C1_vs_C2_zoom.png")
    delay_figure({d: full_dir / f"C2_n0.00_d{d:03d}_r01.csv" for d in (0, 100, 300)},
                 OUT / "fig4_C2_delay.png")
    block_diagram(OUT / "block_diagram.png")
    print("figures written to:", OUT)


if __name__ == "__main__":
    main()
