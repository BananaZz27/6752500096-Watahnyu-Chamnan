# ใบงาน Lab04 (รายงาน 1–2 หน้า)

ชื่อกลุ่ม ภาคีนกอีก๋อย สมาชิก วทัญญู ชำนาญ วันที่ 11 พฤศจิกายน 2569
Python 3.11.0 · controller SHA-256 `67a3fb88efc59d198b30b03b2cf73d3cd3c417e546c4cbcf2ad50e836d84da68` (ตรงกับ `controller_sha256` ใน `config.json` ทุกชุด)

ที่มาของตัวเลข: `comparison/metrics.json`, `zero|one|spike|fault/metrics.json`, raw CSV และ `evidence.json` (ดึงแถวจาก CSV ด้วย `make_figures.py`)

## A. ก่อนรัน

Block diagram: `figures/block_diagram.png`

- **S → P**: stimulus ที่ผ่านการตรวจ (finite, 0–1) เพิ่มอัตราสร้าง P = k_prod·S ทันทีใน step นั้น
- **H_old → C, R_old → B**: clearance และ binding คำนวณจากสถานะ *เก่า* ตัวเดียวกัน ยิ่ง H สูง การดึง H ออกยิ่งมาก (negative feedback)
- **P − C − B → H**: H_raw = H_old + dt(P − C − B) แล้ว clamp ใน [0, 1] H เป็น state ตัวเดียวที่ถูกเก็บไว้ใช้ step ถัดไป จึงเป็น "ความจำ" ของประวัติ stimulus ทั้งหมดที่ยังไม่ถูกสลายไป
- **H → R**: receptor normalize H เป็น R ใน [0, 1] (ที่นี่ H_min = 0, H_max = 1 จึง R = H)
- **R → phi/stride**: bounded mapping ของ Week 03 แปลง R เป็นพารามิเตอร์ของ CPG ไม่ใช่คำสั่งมอเตอร์

| Comparison | prediction ก่อนรัน (01_prediction.md, 19:51) | เหตุผลจาก term ในสมการ | ผลจริงหลังรัน |
|---|---|---|---|
| C2 vs C1 | ขึ้นเร็วกว่า (rise ≈ 1.05 vs 2.70 s), ชน 1, AUC ≈ 10.7 vs 10.0, recovery เท่ากัน ≈ 2.85 s | P ใหญ่ขึ้น H* = 1.5 > 1; ขาลง P = 0 และ C + B ใช้อัตราเดิม 0.8 /s | rise 1.05 vs 2.70 s, latency 0.10 vs 0.15 s, AUC 10.67 vs 10.00, recovery 2.85 = 2.85 s, clamp 0.290 vs 0 — สอดคล้อง |
| C3 vs C1 | ชน 1, recovery ≈ 5.1 vs 2.85 s, AUC ≈ 11.4 (มากสุด) | C เล็กลง removal รวม 0.45 /s ทั้งขาขึ้นและขาลง | recovery 5.10 vs 2.85 s (ช้ากว่า 2.25 s = 1.79 เท่า), AUC 11.39 (มากสุด), rise 1.45 s — สอดคล้อง |
| C4 vs C1 | ชน 1, recovery ≈ 3.8 s, AUC ≈ 10.75 | ตัด B removal เหลือ 0.6 /s | recovery 3.80 s, AUC 10.75, rise 1.70 s, clamp 0.258 — สอดคล้อง |
| C0 vs C1 | latency = recovery = 0.05 s, rise 0, ไม่มี H, phi TV = 0.400 | R = S ไม่มี state | latency 0.05, rise 0.00, recovery 0.05 s, peak_H/AUC/clamp = N/A, phi TV 0.400 — สอดคล้อง |

Prediction ใดอาจเปลี่ยนเพราะ H มี upper bound = 1: C2, C3, C4 มี peak_H = 1 เท่ากันหมด (วัดได้จริง) peak จึงแยกไม่ได้ว่า production เพิ่มหรือ removal ลด และ AUC ของ C2 เพิ่มเพียง 6.7 % ทั้งที่ k_prod เพิ่ม 50 % เพราะส่วนเกิน 1 ถูก clamp ทิ้ง ต้องดู rise, recovery, AUC และ clamp fraction แทน

## B. เติม code และคำนวณมือ

1. Source equation (เอกสาร Week04 อ้าง Homchanthanakul et al. 2019, DOI 10.1109/IROS40897.2019.8968580): `Hc(t) = β·Hc(t−1) + Hg(t) − Hr(t)`, `Hg(t) = α·f(S(t))`, `Hr(t) = Σ γᵢ·Receptorᵢ(t)`
   Proposed course model (Euler, dt = 0.05 s, H ∈ [0, 1]): `H_raw = H_old + dt(k_prod·S − k_clear·H_old − k_bind·R_old)`, `H_new = clamp(H_raw, 0, 1)`; rate ทุกตัวมีหน่วย normalized H / s ความสัมพันธ์โดยประมาณกับ source: β ≈ 1 − dt·k_clear, Hg ≈ dt·k_prod·S, Hr ≈ dt·k_bind·R (ไม่ได้แทนค่ากันตรง ๆ ตามที่ README กำหนด)
2. receptor(H = 0.2, H_min = 0.1, H_max = 0.5) = (0.2 − 0.1)/(0.5 − 0.1) = **0.25** — ย้ายจุดศูนย์ไปที่ H_min หารด้วยช่วง แล้ว clamp ไว้ใน [0, 1] ค่าที่ไม่ finite หรือ H_max ≤ H_min → ValueError
3. `step` เก็บ H_old และ R_old = receptor(H_old) ก่อน แล้วคำนวณ P, C, B จากค่าเหล่านั้น อัปเดต H ครั้งเดียว (`student_hormone.py`)
4. คำนวณมือ C1 (k_prod 0.8, k_clear 0.6, k_bind 0.2), H_old = 0, S = 1:

| input_time_s | time_s | P | C | B | H_raw | H | R | phi | stride_half |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|10.00|10.05| 0.8 | 0.6×0 = 0 | 0.2×0 = 0 | 0 + 0.05×0.8 = 0.0400 | 0.0400 | 0.0400 | 0.2080 | 0.05540 |
|10.05|10.10| 0.8 | 0.6×0.04 = 0.024 | 0.2×0.04 = 0.008 | 0.04 + 0.05×0.768 = 0.0784 | 0.0784 | 0.0784 | 0.21568 | 0.055784 |

   ตรงกับ `comparison/C1_step.csv` แถว time_s 10.05 และ 10.10 ทุกช่อง (`evidence.json` → `C1_first_on_updates`)
5. `check_submission.py`: ผ่าน **13 / 13** case (`check_submission_output.json`) ไม่มี case ที่ต้องแก้

แถว CSV ที่เลือกสอดคล้องกับ time convention อย่างไร? แถว k+1 คือ state *หลัง* ใช้ input ช่วง [k·dt, (k+1)·dt) stimulus เปิดที่ input_time 10.00 จึงเห็นผลครั้งแรกในแถว time_s 10.05 สองแถวแรกของไฟล์ (time 0.00, 0.05) ยังเป็นช่วง S = 0 และแถว 10.00 ยังเป็น H = 0 (ผลของ input 9.95 ที่ S = 0)

## C. Controlled comparison

dt 0.05 s, duration 30 s (601 rows / 600 updates), H0 = 0, stimulus S = 1 ช่วง [10, 20) s, contract เดียวกัน, controller SHA-256 เดียวกัน

| Condition | peak_H | AUC_H (H·s) | latency s | rise s | recovery s | upper clamp fraction | phi TV rad | stride TV m | fault |
|---|---|---|---|---|---|---|---|---|---|
|C0| N/A (ไม่มี H) | N/A | 0.05 | 0.00 | 0.05 | N/A | 0.4000 | 0.0200 | 0 |
|C1| 0.9997 | 10.00 | 0.15 | 2.70 | 2.85 | 0.000 | 0.3998 | 0.0200 | 0 |
|C2| 1.0000 | 10.67 | 0.10 | 1.05 | 2.85 | 0.290 | 0.3999 | 0.0200 | 0 |
|C3| 1.0000 | 11.39 | 0.15 | 1.45 | 5.10 | 0.273 | 0.3979 | 0.0199 | 0 |
|C4| 1.0000 | 10.75 | 0.15 | 1.70 | 3.80 | 0.258 | 0.3995 | 0.0200 | 0 |

lower clamp fraction = 0 ทุก condition เวลาที่วัดมีความละเอียด 0.05 s

- **C3 ฟื้นช้ากว่า C1 เท่าไร?** recovery 5.10 − 2.85 = **2.25 s** (5.10 / 2.85 = 1.79 เท่า) ตรงกับอัตราส่วน removal 0.80 / 0.45 = 1.78
- **C2/C3 peak เท่ากันหรือไม่ และ metric ใดแยกได้?** peak_H = 1.0000 เท่ากัน (ทั้งคู่ชน clamp: C2 ที่ 11.35 s, C3 ที่ 11.85 s) แยกได้ด้วย recovery (2.85 vs 5.10 s), AUC (10.67 vs 11.39), rise (1.05 vs 1.45 s) และ clamp fraction (0.290 vs 0.273)
- **C0 มี H หรือไม่?** ไม่มี: ช่อง h/raw/p/c/b ใน `C0_step.csv` ว่างทุกแถว และเป็น null ใน JSON (ไม่ใช่ 0)
- **TV ที่ต่ำกว่าพิสูจน์คุณภาพ gait ได้หรือไม่?** ไม่ได้ phi TV ของทุก condition ≈ 0.40 rad (ต่างกันไม่ถึง 0.6 %) เพราะทุกระบบขึ้นและลงเต็มช่วงหนึ่งครั้ง TV ไม่บอกความเร็วของการเปลี่ยน (C0 เปลี่ยน 0.2 rad ใน step เดียว) และ Lab04 ไม่ได้รัน CPG หรือวัด body motion คุณภาพ gait ต้องวัดใน Week05

## D. Extreme tests และ handoff

| Profile | Input | H และ R ที่สังเกต | fault และคำสั่ง | หลักฐาน |
|---|---|---|---|---|
| zero | S = 0 ตลอด | H = R = 0 ทุกแถว, AUC 0 | fault 0, phi = 0.20 ทุกแถว, TV 0 | `zero/C1_zero.csv` (max H = 0) |
| one | S = 1 ตลอด | H = 0.9997 ที่ 10.00 s, 1 − 2×10⁻¹¹ ที่ 30 s, peak < 1, ไม่มี clamp | fault 0, phi → 0.40 TV 0.200 rad | `one/C1_one.csv`, metrics: upper clamp 0 |
| spike | S = 1 ที่ input 10.00 s | H = R = 0.04 ที่ 10.05 แล้ว × 0.96 ต่อ step (0.0384 ที่ 10.10) | fault 0, phi สูงสุด 0.208 rad, TV 0.016 rad | แถว 10.05 |
| fault | step + NaN ที่ input 15.00 s | H = 0.9831 ที่ 15.00 → 0 ที่ 15.05 → 0.04 ที่ 15.10 → 0.9824 ที่ 20.00 | fault = 1 เฉพาะแถว 15.05 (fault_count 1), phi 0.20, stride 0.055 ในแถวนั้น, TV 0.786 rad | แถว 15.00/15.05/15.10 |

Spike มี on interval **1 แถว** (input_time 10.00) นาน **0.05 s** หลัง fault ระบบ reset แล้วกลับมาสะสมได้: แถว 15.00 H = 0.9831 (fault 0), แถว 15.05 stimulus = nan, fault 1, H = R = raw = 0, phi 0.20, stride 0.055, แถว 15.10 fault 0, H = 0.04 (เท่ากับ update แรกจาก H = 0)

การตรวจ bounded mapping:

| R | phi (rad) | stride_half (m) | อยู่ใน bounds หรือไม่ |
|---|---|---|---|
| 0 | 0.20 | 0.055 | อยู่ (phi 0.10–0.45, stride 0.040–0.070) |
| 1 | 0.40 | 0.065 | อยู่ |

Contract ที่ใช้: `handoff_contract.json` ที่แจก และทดลองส่ง contract จาก Lab03 ของกลุ่ม (`../lab_03/submission/week4_bridge/handoff_contract.json`) ผ่าน `--contract` → ☑ ตรงเดิม runner ยอมรับ และ CSV ของ C1 เหมือนชุดหลักทุกไบต์ (`contract_week03/`) ทดสอบเพิ่มด้วย contract ที่แก้ใน scratch (ไม่ได้เก็บไว้): phi gain 0.30 → `ValueError: Week03 mapping changed: phi_rad`, alpha 1.3 → `ValueError: Week03 fixed parameters changed`

Software bounds ต่างจาก actuator limits และ emergency stop อย่างไร: software bounds (clamp H, clamp phi/stride, fault reset) อยู่ในโค้ดและป้องกันได้เฉพาะค่าที่โค้ดเห็น ถ้าโปรแกรมค้าง ข้อมูลเสีย หรือ CPG/driver ทำงานผิด ก็ไม่ช่วย actuator limits คือข้อจำกัดทางกายภาพ/ใน driver (มุมข้อต่อ แรงบิด ความเร็ว กระแส) ส่วน emergency stop คือการตัดพลังงานด้วยฮาร์ดแวร์ที่ไม่ขึ้นกับซอฟต์แวร์ ทั้งสามชั้นต้องมีแยกกัน Lab04 มีเฉพาะชั้นแรก

Lab04 ยังไม่ได้ทดสอบ: การรัน CPG และ gait จริงด้วย phi/stride จาก hormone, body motion และ stability, stimulus จาก sensor จริงที่มี noise / delay, H_min/H_max ที่ไม่ใช่ 0/1, การทำงานแบบ real time และผลบนหุ่นยนต์จริง ก่อนอ้างผลกับหุ่นยนต์ต้องเก็บ gait metric (Week05), ข้อมูล actuator และการทดสอบความปลอดภัยด้วยฮาร์ดแวร์

## E. สรุป

ดู `report.docx` (3 ส่วนตามใบงาน) คำสั่งรันซ้ำและ hash อยู่ใน `README.md` และ `*/config.json`
