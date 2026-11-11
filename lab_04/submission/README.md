# Lab 04 — ผลส่งมอบ

ไฟล์ทั้งหมดอยู่ใน `lab_04/submission/` (ไม่ใช้ `results/` เพราะ `.gitignore` ของ repo ตัด `results/` ออก ทำให้ raw CSV ไม่ถูก push)

| ผลส่งมอบตาม README / checklist ของใบงาน | ไฟล์ |
|---|---|
| Prediction ก่อนทดลอง (เวลาบันทึก) | `01_prediction.md` (2026-11-11 19:51 ก่อนเติมโค้ดและก่อนรัน) |
| ใบงานที่กรอกครบ A–E | `worksheet.md` (ต้นฉบับเปล่าอยู่ที่ `../worksheet.md`) |
| code | `../student_hormone.py` (SHA-256 `67a3fb88…84da68`) |
| ผล checker | `check_submission_output.json` (ผ่าน 13 / 13) |
| comparison CSV 5 ไฟล์ + config + metrics | `comparison/` (`C0_step.csv` … `C4_step.csv`, `config.json`, `metrics.json`, `metrics.csv`, `report.html` และ SVG ของ runner) |
| extreme CSV 4 ไฟล์ + config + metrics | `zero/`, `one/`, `spike/`, `fault/` (C1) |
| ทดลองส่ง contract ของ Week03 | `contract_week03/` (C1 step กับ `../lab_03/submission/week4_bridge/handoff_contract.json`, CSV ตรงกับ `comparison/C1_step.csv` ทุกไบต์) |
| กราฟ | `figures/fig1_step_timeline.png`, `fig2_transition_zoom.png`, `fig3_metrics.png`, `fig4_extreme_inputs.png` |
| Block diagram | `figures/block_diagram.png` |
| metric table | `comparison/metrics.csv` และตารางใน `worksheet.md` / `report.docx` |
| แถวหลักฐานที่อ้างในรายงาน | `evidence.json` |
| รายงาน 1–2 หน้า | `report.docx` (2 หน้า) |

`make_figures.py` อ่านเฉพาะ raw CSV และ `metrics.json` แล้วสร้างกราฟกับ `evidence.json` ไม่แก้ไฟล์ผลดิบ

## รันซ้ำ

จากโฟลเดอร์ `lab_04` (deterministic ไม่ใช้ random seed ผลจะเหมือนเดิม):

```sh
python check_submission.py --student-file student_hormone.py > submission/check_submission_output.json
python lab04.py --controller-source student --condition all --profile step --output-dir submission/comparison
python lab04.py --controller-source student --condition C1 --profile zero  --output-dir submission/zero
python lab04.py --controller-source student --condition C1 --profile one   --output-dir submission/one
python lab04.py --controller-source student --condition C1 --profile spike --output-dir submission/spike
python lab04.py --controller-source student --condition C1 --profile fault --output-dir submission/fault
python lab04.py --controller-source student --condition C1 --profile step --contract ../lab_03/submission/week4_bridge/handoff_contract.json --output-dir submission/contract_week03
python submission/make_figures.py
```

หมายเหตุ

- `lab04.py` หยุดถ้า output directory ไม่ว่าง ให้ใช้ directory ใหม่ หรือใส่ `--overwrite` เมื่อตั้งใจแทนที่
- บน Windows ตั้ง `PYTHONUTF8=1` ก่อนรันเพื่อให้ภาษาไทยใน JSON แสดงถูก
- ทดสอบเพิ่มว่า runner ปฏิเสธ contract ที่ถูกแก้ (ใช้ไฟล์ชั่วคราว ไม่ได้เก็บไว้): phi gain 0.30 → `ValueError: Week03 mapping changed: phi_rad`, alpha 1.3 → `ValueError: Week03 fixed parameters changed`
- Lab04 ไม่มีส่วนที่ต้องใช้อุปกรณ์พิเศษ ทุกขั้นในคู่มือทำครบ
