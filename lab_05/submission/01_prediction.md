# Lab 05 — Hypothesis และ prediction ก่อนทดลอง

บันทึกเมื่อ: 2026-11-11 20:01 (UTC+7) ก่อนรัน `lab05.py` และ `contact_demo.py` ใด ๆ (ยังไม่มีโฟลเดอร์ผล)
สิ่งที่ใช้ประกอบการคาด: README/SOURCES/ใบงาน Lab05, อ่านโค้ด `course_model.py`, `lab05.py`, `contact_demo.py` (ไม่ได้รัน) และผลที่วัดแล้วของกลุ่มใน Lab03 (baseline φ = 0.20: 0.625 Hz, 0.0776 m/s; φ = 0.40, stride 0.065: 1.263 Hz, 0.1833 m/s) และ Lab04 (C1: rise 2.70 s, recovery 2.85 s; C4: rise 1.70 s, recovery 3.80 s)
ตัวเลขด้านล่างคำนวณด้วยมือ ไม่ได้มาจากการรัน Lab05

## Architecture (ข้อ 1.1)

S (schedule) → controller (B0 ค่าคงที่ / B1 R = S / B2, B3 hormone H) → R_used → bounded mapping → φ, stride → SO(2) CPG → tripod decoder → stance-anchor body
จุดที่ไม่มี independent sensory feedback: (1) S เป็นตารางเวลาที่กำหนดล่วงหน้า ไม่ขึ้นกับการเคลื่อนที่ของ body, (2) contact มาจาก sign(o₂) ของ decoder ไม่ใช่ sensor, (3) ไม่มีเส้นทางจาก body/terrain กลับเข้า hormone หรือ CPG — ระบบเป็น open loop ทั้งเส้น ส่วน contact mini-lab ใช้สัญญาณสังเคราะห์และไม่ต่อกลับเข้า runner

## Hypothesis หลัก B1 vs B2 (ข้อ 1.2)

**H1:** เมื่อเปลี่ยนจาก direct path (B1) เป็น hormone path (B2) ภายใต้ mapping และ stimulus เดียวกัน
- phi_max_step_rad ลดลงจาก 0.200 rad (B1 กระโดดทั้งช่วงใน 1 step) เหลือ ≈ 0.008 rad (B2 เปลี่ยนไม่เกิน dt·k_prod·0.20 ต่อ step)
- แต่ phi_total_variation_rad แทบไม่ต่าง (B1 0.400, B2 ≈ 0.400) เพราะทั้งคู่ขึ้นและลงเต็มช่วงหนึ่งรอบ
- command latency เพิ่มจาก 0 เป็น 0.15 s, command rise 0 → ≈ 2.70 s, command recovery 0 → ≈ 2.85 s
- on-segment frequency ต่ำกว่า B1 (≈ 1.19 vs ≈ 1.26 Hz) และ on distance น้อยกว่า (≈ 1.70 vs ≈ 1.83 m) เพราะ φ, stride ใช้เวลาไต่ขึ้น ≈ 3 s ส่วน off segment กลับกัน (B2 ≈ 0.89 vs B1 ≈ 0.77 m, frequency ≈ 0.70 vs 0.625 Hz) เพราะ R ค้างหลังปิด stimulus ระยะรวม 30 s ของสองแบบจึงใกล้กันมาก (≈ 3.37 vs ≈ 3.38 m)

## B3 ตัดอะไรออก (ข้อ 1.3)

B3 ตั้ง k_bind = 0 ตัดเฉพาะเทอม binding B = k_bind·R ออกจาก removal ของ H ใน model นี้ ส่วนที่ยังมี memory คือ state H เอง (production สะสม, clearance k_clear = 0.6 /s ยังลดลงช้า ๆ) และ oscillator ของ CPG ซึ่งเป็น state ที่ต่อเนื่องจาก warmup ด้วย ไม่ได้ตัด prior MI_H หรือ hormone memory แบบใน paper

คาด B3: H* = 0.8/0.6 = 1.33 จึงชน 1 ที่ state ≈ 12.30 s, command latency 0.15 s, rise ≈ 1.70 s, recovery ≈ 3.80 s, TV φ ≈ 0.40 rad, max Δφ ≈ 0.008 rad, on distance ≈ 1.75 m, off distance ≈ 0.93 m

## Provenance (ข้อ 1.4)

| ประเภท | รายการ |
|---|---|
| Source equation | release = CI/(1 + exp(−SIF)), SIF = SD ของ SI 6 ขา (Ngamkajornwiwat et al. 2020, Eq. 1–2) |
| Proposed course equation | H(t_k+1) = clamp(H + dt(k_prod·S − k_clear·H − k_bind·R), 0, 1) และ φ = clamp(0.20 + 0.20·R_used, 0.10, 0.45) |
| Expected measurement | segment frequency ของ o₁ (rising crossings, interpolated) และ distance ของ body ใน kinematic model |
| วัดไม่ได้ | Stability / Harmony / Displacement ตาม paper, contact force, energy — ไม่มี dynamics หรือ sensor |

## ตารางคาดการณ์ comparison (mapping both, step)

| condition | TV φ (rad) | max Δφ/step (rad) | TV stride (m) | cmd latency (s) | cmd recovery (s) | on frequency (Hz) | on distance (m) |
|---|---|---|---|---|---|---|---|
| B0 | 0 | 0 | 0 | N/A | N/A | ≈ 0.625 | ≈ 0.78 |
| B1 | 0.400 | 0.200 | 0.020 | 0 | 0 | ≈ 1.26 | ≈ 1.83 |
| B2 | ≈ 0.400 | ≈ 0.008 | ≈ 0.020 | 0.15 | ≈ 2.85 | ≈ 1.19 | ≈ 1.70 |
| B3 | ≈ 0.400 | ≈ 0.008 | ≈ 0.020 | 0.15 | ≈ 3.80 | ≈ 1.22 | ≈ 1.75 |

- B1 state latency = 0.05 s (post-update log) แต่ command latency = 0 เพราะ B1 ใช้ S_k ทันทีใน interval เดียวกัน
- B2 timing: command 10.00 ใช้ R = 0 (φ 0.20), state 10.05 H = 0.04, command 10.05 ใช้ φ 0.208, stride 0.0554 ตาม README; command 20.00 ใช้ H(20.00) ≈ 0.9997 (φ ≈ 0.3999)
- ทุก condition: pre segment เหมือนกัน (≈ 0.625 Hz, ≈ 0.78 m) เพราะ warmup และ R = 0 เหมือนกัน; support = 3 ตลอด; command clamp count = 0

## One-factor (ข้อ 4) — รันทั้งสองแบบ

- **phi-only** (stride คงที่ 0.055 m): frequency on ของ B1 ≈ 1.26 Hz เท่ากับ both แต่ on distance ลดเหลือ ≈ 1.83 × 0.055/0.065 ≈ 1.55 m
- **stride-only** (φ คงที่ 0.20 rad): frequency ทุก segment ≈ 0.625 Hz เท่า B0 และ on distance ของ B1 ≈ 0.78 × 0.065/0.055 ≈ 0.92 m
- ข้อสรุปที่คาด: φ คุม frequency, stride คุมระยะต่อรอบ ผลของ both ≈ ผลคูณของสองปัจจัย

## Fault profile (ข้อ 4)

ทุก condition ที่ command 15.00: fault = 1, R_used = 0, φ = 0.20, stride = 0.055 (fallback ก่อน command); B2 H_used = 0, state 15.05 H = 0, state 15.10 H = 0.04
ผลข้างเคียงที่คาด: fallback ทำให้ B2/B3 เกิด command jump ใหญ่ที่สุดของ trial (B2 Δφ ≈ 0.197 rad จาก H ≈ 0.983, B3 Δφ = 0.200 rad เพราะ H = 1) ซึ่งทำลายความค่อยเป็นค่อยไปที่ hormone ให้; TV φ ของ B1 = 0.800, B2 ≈ 0.79

## Extreme (B2)

zero: เหมือน B0 ทุกประการ; one: R ขึ้นจาก 0 ตั้งแต่ t = 0 เข้าใกล้ 1; spike: peak H = 0.04 (state 10.05), max φ = 0.208 rad, TV φ ≈ 0.016 rad

## Contact mini-lab (ข้อ 5)

window 50 samples รวม current → valid ครั้งแรก sample 49 = 2.45 s, valid rows = 600 − 49 = 551

| case | SI ต่อขา | mean SIF | MAE | valid rows | อนุมานไม่ได้ |
|---|---|---|---|---|---|
| matched | 1 ทุกขา | 0 | 0 | 551 | ความถูกต้องของ contact จริง |
| gain-offset | 1 ทุกขา (affine ไม่เปลี่ยน Pearson) | 0 | ≈ 0.16 | 551 | amplitude/offset error |
| mixed-delay | 1 สามขา, ≈ 0 สามขา (delay ¼ คาบ) | ≈ 0.5 (release ≈ 0.62) | ≈ 0.22 | 551 | ทิศของ delay / ขาไหน delay |
| all-inverted | −1 ทุกขา | 0 (release 0.5) | ≈ 0.64 | 551 | ว่าทุกขาผิดเฟส |
| constant | N/A (variance 0) | N/A | 0 | 0 | — ไม่ใช่ SI = 0 |
| fault | 1 ทุกขาเมื่อ valid | 0 | 0 | 501 (ไม่ valid 50 rows: sample 300–349) | ค่าที่หายไป |

paired Pearson ใน demo เป็น proposed course definition ไม่ใช่ Eq. (3) ตามที่พิมพ์ และยังไม่ต่อ C_g/HR/MI_H

## บันทึกการแก้สมมติฐาน

(ยังไม่มี — ถ้ามีการแก้หลังเห็นผลจะบันทึกเวลาและเหตุผลไว้ที่นี่ โดยไม่ลบข้อความเดิม)
