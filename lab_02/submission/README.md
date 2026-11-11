# Lab 02 — ผลส่งมอบ

ไฟล์ทั้งหมดอยู่ใน `lab_02/submission/` (ไม่ใช้ `results/` เพราะ `.gitignore` ของ repo ตัด `results/` ออก ทำให้ raw CSV ไม่ถูก push)

| # | ผลส่งมอบตามคู่มือ | ไฟล์ |
|---|---|---|
| 1 | Prediction ก่อนทดลอง | `01_prediction.md` (บันทึก 2026-11-11 18:26 ก่อนรันโหมด student) |
| 2 | Block diagram ของ sensorimotor loop | `figures/block_diagram.png` |
| 3 | `student_controller.py` ที่เติม TODO 1–4 | `../student_controller.py` |
| 4 | ผลตรวจ `grade_submission.py` | `student_grade.json` (PASS 10 / FAIL 0) |
| 4 | `run_config.json`, raw CSV ทุก trial, `summary_aggregate.csv` | `student_comparison/` (ขั้น A, 20 trials), `c2_short/` (15), `c2_full/` (45), `c1_full/` (45) |
| 5 | กราฟตัวแทน C1 และ C2 พร้อม physical crossing และ first correct response | `figures/fig1_C1_trial.png`, `figures/fig2_C2_trial.png` (ทั้ง 20 s), `figures/fig3_C1_vs_C2_zoom.png` (ซูมรอบ crossing), `figures/fig4_C2_delay.png` |
| 6 | รายงาน 1–2 หน้า | `report.docx` |

`make_figures.py` สร้างกราฟทั้งหมดจาก raw CSV (เหตุการณ์ crossing และ first response ใช้ฟังก์ชันเดียวกับ `lab02.py`)

## รันซ้ำ

จากโฟลเดอร์ `lab_02` (ใช้ seed เดิม ผลจะเหมือนเดิม):

```sh
python3 grade_submission.py --student-file student_controller.py --out submission/student_grade.json
python3 lab02.py --controller-source student --student-file student_controller.py --protocol controller-comparison --out submission/student_comparison
python3 lab02.py --controller-source student --student-file student_controller.py --protocol robustness-short --condition C2 --out submission/c2_short
python3 lab02.py --controller-source student --student-file student_controller.py --protocol robustness-full --condition C2 --out submission/c2_full
python3 lab02.py --controller-source student --student-file student_controller.py --protocol robustness-full --condition C1 --out submission/c1_full
python3 submission/make_figures.py
```

หมายเหตุ

- ถ้าโฟลเดอร์ผลมีอยู่แล้ว `lab02.py` ต้องใส่ `--overwrite` และ `grade_submission.py` ไม่เขียนทับไฟล์ `--out` เดิม (ลบหรือเปลี่ยนชื่อก่อน)
- `run_config.json` เก็บ path ของเครื่องที่รัน ใช้ค่า `student_file_sha256` ยืนยันว่าเป็นไฟล์ `student_controller.py` เดียวกัน
- `c1_full` เป็นการรันเพิ่มนอกคู่มือ เพื่อทดสอบ prediction ข้อ 1 (ชุด robustness ของ C2 ไม่มีข้อมูล C1)
- หลังเติม TODO แล้ว unit test 2 ข้อที่ตรวจว่า starter ยังไม่เสร็จ (`test_unfinished_starter_fails_before_writing_results`, `test_diagnostic_report_identifies_unfinished_starter`) จะ FAIL ตามที่ออกแบบไว้ ส่วนอีก 10 ข้อผ่าน
