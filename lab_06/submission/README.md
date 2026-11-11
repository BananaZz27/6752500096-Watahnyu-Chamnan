# Lab 06 — ผลส่งมอบ

ไฟล์ทั้งหมดอยู่ใน `lab_06/submission/` (ไม่ใช้ `results/` เพราะ `.gitignore` ตัด `results/` ออก)

| ผลส่งมอบตาม README / ใบงาน | ไฟล์ |
|---|---|
| Prediction + transition table + expected set ก่อนรัน | `01_prediction.md` (2026-11-11 20:08 ก่อนรันและก่อนเติม TODO) |
| ใบงานที่กรอกข้อ 1–9 | `worksheet.md` |
| `student_policy.py` (contract baseline) | `../student_policy.py` |
| ผล checker | `check_starter_baseline.txt` (starter, FAIL 7 ช่องตามที่ตั้งใจ), `check_baseline.txt` (PASS), `check_group.txt` (PASS) |
| C0/C1 × 3 paired seeds: config/raw/events/metrics/manifest | `completed/` (`raw_C*_rNN.csv`, `events_C*_rNN.csv`, `inputs_rNN.csv`, `source_inputs_rNN.csv`, `config.json`, `metrics.json`, `metrics.csv`, `report.html`, `trace_*.svg`, `source_snapshot/`, `manifest.json`) |
| Replay ของ `inputs_r01.csv` | `replay/` (raw/events C1 เหมือน `completed/` ทุกไบต์) |
| FSM diagram | `figures/fsm_diagram.png` |
| กราฟ | `figures/fig1_state_timeline.png`, `fig2_latency.png`, `fig3_event_chain.png` |
| รายงาน 1–2 หน้า | `report.docx` (2 หน้า) |

## รันซ้ำ

Python 3.11.0 จากโฟลเดอร์ `lab_06`:

```sh
python check_submission.py > submission/check_baseline.txt
python check_submission.py --contract group > submission/check_group.txt
python lab06.py --policy student --condition all --repeats 3 --output-dir submission/completed
python lab06.py --policy student --condition C1 --repeats 1 --replay submission/completed/inputs_r01.csv --output-dir submission/replay
python submission/make_figures.py
```

runner ปฏิเสธ directory ที่ไม่ว่าง ให้ใช้ชื่อใหม่ถ้ารันซ้ำ (`check_starter_baseline.txt` มาจากการรัน checker กับ starter ก่อนเติม TODO)

## ส่วนที่ข้าม

ส่วน "ก่อนต่อหุ่นยนต์จริง" ของใบงาน Word (สอบเทียบแกนจริง, e-stop, วัด onset ด้วยกล้อง/photodiode) ไม่ได้ทำเพราะไม่มีหุ่นยนต์โคมไฟ ผลทั้งหมดเป็น simulated command onset ไม่ใช่ physical latency และไม่ได้ทำงานเสริม (learning preference, sound, phone)
