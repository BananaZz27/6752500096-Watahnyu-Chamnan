# Lab 05 — ผลส่งมอบ

ไฟล์ทั้งหมดอยู่ใน `lab_05/submission/` (ไม่ใช้ `results/` เพราะ `.gitignore` ของ repo ตัด `results/` ออก)

Lab05 เป็น working scaffold: ไม่มี TODO ให้เติมโค้ด runner ไม่โหลดไฟล์นักศึกษา งานคือ prediction, การทดลอง และการวิเคราะห์

| ผลส่งมอบตามใบงาน | ไฟล์ |
|---|---|
| Prediction / hypothesis ก่อนรัน | `01_prediction.md` (2026-11-11 20:01 ก่อนรัน) |
| ใบงานที่กรอกครบข้อ 1–6 | `worksheet.md` |
| Comparison raw states/intervals + config/metrics/manifest | `comparison/` (B0–B3, mapping both, step) |
| One-factor runs | `phi_only/`, `stride_only/` |
| Fault raw CSV | `fault/` (B0–B3) |
| Extreme inputs (B2) | `zero/`, `one/`, `spike/` |
| Contact metrics + CSV ทุก case | `contact/` (อภิปราย `mixed-delay.csv`, `fault.csv`, `constant.csv`) |
| กราฟ | `figures/fig1_comparison.png`, `fig2_one_factor.png`, `fig3_fault.png`, `fig4_contact.png` |
| Block diagram | `figures/block_diagram.png` |
| รายงาน 2–3 หน้า | `report.docx` (3 หน้า) |

ทุก run มี `config.json`, `metrics.json`, `metrics.csv`, `segment_metrics.csv` (main runner), `source_snapshot/`, `report.html` (เปิด offline ได้) และ `manifest.json` (SHA-256 ของทุกไฟล์ใน run นั้น)

## รันซ้ำ

Python 3.11.0 จากโฟลเดอร์ `lab_05` (deterministic ไม่มี random; runner ปฏิเสธ directory ที่ไม่ว่าง ให้ใช้ชื่อใหม่ถ้ารันซ้ำ):

```sh
python lab05.py --condition all --profile step --mapping both --output-dir submission/comparison
python lab05.py --mapping phi-only --output-dir submission/phi_only
python lab05.py --mapping stride-only --output-dir submission/stride_only
python lab05.py --condition B2 --profile zero --output-dir submission/zero
python lab05.py --condition B2 --profile one --output-dir submission/one
python lab05.py --condition B2 --profile spike --output-dir submission/spike
python lab05.py --condition all --profile fault --output-dir submission/fault
python contact_demo.py --output-dir submission/contact
python submission/make_figures.py
```

`make_figures.py` อ่านเฉพาะ raw CSV / metrics ในโฟลเดอร์นี้ ไม่แก้ไฟล์ผลดิบ

หมายเหตุ: Lab05 ไม่มีส่วนที่ต้องใช้อุปกรณ์พิเศษ ทุกขั้นในใบงานทำครบ (รวม one-factor ทั้งสองแบบและ extreme profiles)
