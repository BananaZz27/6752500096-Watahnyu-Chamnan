# ใบงาน Lab06 — Student

ชื่อกลุ่ม ภาคีนกอีก๋อย สมาชิก วทัญญู ชำนาญ วันที่ 11 พฤศจิกายน 2569 · Python 3.11.0 · contract **baseline**

**แบบจำลองทั้งหมดใน runner เป็น proposed course model** ผลเป็น simulation ไม่ใช่ข้อมูลจาก robot และไม่มี learning
ตัวเลขมาจาก `completed/metrics.json`, `completed/events_C*_rNN.csv`, `completed/raw_C*_rNN.csv`

## 1. Prediction ก่อนรัน

อยู่ใน `01_prediction.md` (บันทึก 2026-11-11 20:08 ก่อนรัน checker/runner และก่อนเติม TODO) สรุป: C0 จะ chatter รอบ threshold ระยะ (≈ 60–80 transitions ต่อ seed) และอาจ miss clear_01/clear_02, C1 จะเปลี่ยน state ครั้งเดียวต่อ interaction (≈ 9–10 transitions) แต่ช้ากว่าใน button/touch 0.06–0.10 s จาก debounce; input ที่ไม่ควรมี onset ใหม่คือ touch_conflict (afraid guard / priority), invalid_01 และ stale_01 (fault ขณะ normal อยู่แล้ว)

## 2. FSM

`figures/fsm_diagram.png` — guard: near จากทุก state → afraid; afraid ออกได้เฉพาะ clear/fault; interested/happy timeout 2 s → normal; normal ไม่มี interaction 6 s → sleepy; recovery สู่ normal ทุกทาง = clear, fault (และ timeout จาก interested/happy)

## 3. ตาราง 5 × 8 (ช่อง "hold" = policy คืน None)

| current \ event | fault | near | clear | touch | button | approach | timeout | idle |
|---|---|---|---|---|---|---|---|---|
| normal | normal | afraid | normal | happy | interested | interested | hold | sleepy |
| interested | normal | afraid | normal | happy | interested | interested | normal | hold |
| happy | normal | afraid | normal | happy | interested | interested | normal | hold |
| afraid | normal | afraid | normal | hold | hold | hold | hold | hold |
| sleepy | normal | afraid | normal | happy | interested | interested | hold | hold |

Priority (tick เดียวกัน): fault > near > clear > touch > button > approach > timeout > idle ตัวที่แพ้ถูกบันทึก `discarded_priority`

## 4. Checker และ failed case

- Starter (ก่อนเติม): `check_starter_baseline.txt` — FAIL 7 ช่อง: interested/happy + timeout = None, normal + idle = None, normal/interested/happy/sleepy + touch = None
- Failed case ที่ช่วยแก้ logic: **sleepy + touch** ต้องเป็น happy ไม่ใช่เฉพาะ normal + touch — แสดงว่า touch ต้องเป็นกฎของทุก state ยกเว้น afraid (ซึ่ง guard ไว้ก่อนแล้ว) และ timeout/idle ต้องมีเงื่อนไข state ด้วย ไม่อย่างนั้น sleepy + timeout หรือ interested + idle จะเปลี่ยน state ผิด
- หลังเติม: `check_baseline.txt` PASS 0 failures (40 pairs) และ `check_group.txt` PASS (ใช้ baseline เป็นหลัก)

## 5. C0/C1 × 3 paired seeds (all 10 external inputs)

| Condition/seed | All external inputs | Both onset | ≤1s both observed | No both onset/status | Max observed latency [s] | State transitions |
|---|---:|---:|---:|---|---:|---:|
| C0/41 | 10 | 7 | 7 | 3: touch_conflict discarded_priority; invalid_01, stale_01 no_state_change | 0.24 | 67 |
| C1/41 | 10 | 7 | 7 | 3: touch_conflict policy_held; invalid_01, stale_01 no_state_change | 0.14 | 9 |
| C0/42 | 10 | 6 | 6 | 4: clear_01 filtered_not_recognized; touch_conflict preempted_before_apply; invalid_01, stale_01 no_state_change | 0.18 | 72 |
| C1/42 | 10 | 7 | 7 | 3: เหมือน C1/41 | 0.14 | 10 |
| C0/43 | 10 | 6 | 6 | 4: clear_02 no_state_change; touch_conflict discarded_priority; invalid_01, stale_01 no_state_change | 0.04 | 63 |
| C1/43 | 10 | 7 | 7 | 3: เหมือน C1/41 | 0.14 | 9 |

Primary expected 7 (ประกาศก่อนรัน): C0 ผ่าน ≤ 1 s 7/7, 6/7, 6/7 (miss 0/1/1); C1 7/7 ทุก seed (miss 0) · command clamp count = 0 ทุก run · ทุก onset ที่วัดได้ ≤ 0.24 s

## 6. ตรวจหนึ่ง event ตลอดเส้นทาง (C1, seed 41, button_01) — `figures/fig3_event_chain.png`

| Input ID | Source s | Recognized s | Decision s | Actual apply s | Motion onset s | RGB onset s | Both latency s | Status/reason |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| button_01 (C1/41) | 1.00 | 1.10 | 1.10 (queued 1.10) | 1.14 | 1.14 | 1.14 | 0.14 | responded |
| button_01 (C0/41) | 1.00 | 1.00 | 1.00 | 1.04 | 1.04 | 1.04 | 0.04 | responded (+ candidate ซ้ำที่ 1.04 = no_state_change) |

คำนวณเอง: raw button 1 ที่ 1.00, 0 ที่ 1.02, 1 ตั้งแต่ 1.04 (bounce) → debounce 0.06 s นับจาก edge สุดท้าย 1.04 → recognized 1.10 → scheduler 0.04 s → apply 1.14 (raw_C1_r01.csv: tilt 0 → 0.016 rad, RGB 60,90,140 → 255,180,0 ที่แถว 1.14) → both = 1.14 − 1.00 = 0.14 s ตรงกับ events CSV

## 7. กรณีพิเศษ

- **near + touch ที่ 7 s:** C1/41 near recognized 7.00 → afraid (apply 7.04); touch recognized 7.06 → `policy_held` (afraid guard) C1/42 sample 7.00 ยังไม่ ≤ 0.20 m จึงเกิด approach (id near_01) → interested ที่ 7.00 แล้ว near ที่ 7.02 แทนที่ก่อน apply (`preempted_before_apply`) → afraid apply 7.06 (latency 0.06 s) C0/42 touch ชนะที่ 7.00 (happy) แต่ถูก near/clear chatter preempt ก่อน apply ทั้งหมด afraid apply ครั้งแรกที่ 7.18 s
- **stale/invalid:** invalid_01 (11.00, NaN) และ stale_01 (12.00, อายุ sample 0.5 s > 0.12 s) → fault ขณะ state = normal → `no_state_change` ไม่มี onset (N/A) และ output ถูกบังคับเป็นท่ากลางตลอดช่วง fault
- **quiet → sleepy:** idle event source 15.00 (6 s หลัง clear_02 ที่ 9.00; fault ไม่นับเป็น activity) → sleepy apply 15.04 ทุก run
- **recovery button_02 (18.00):** sleepy → interested, C1 0.10 s (debounce), C0 0.04 s แล้ว timeout → normal ที่ 20.06 (C1)
- ความต่างของ status: `discarded_priority` = แพ้ event อื่นใน tick เดียวกัน (ไม่เคยถูกพิจารณา); `policy_held` = ชนะแต่ policy/afraid guard คืน None; `no_state_change` = policy คืน state เดิม จึงไม่มี expression ใหม่; `preempted_before_apply` = state เปลี่ยนและเข้าคิวแล้ว แต่ถูก transition ถัดไปล้างคิวก่อนถึงเวลา apply; `censored_end` = รอ apply ไม่ทันจบ trial (ไม่พบใน run นี้)

## 8. Replay

`python lab06.py --policy student --condition C1 --repeats 1 --replay submission/completed/inputs_r01.csv --output-dir submission/replay` → `raw_C1_r01.csv` และ `events_C1_r01.csv` เหมือนต้นฉบับทุกไบต์ (ตรวจด้วย `cmp`) policy/config/source ไม่ได้เปลี่ยน; metrics ของ replay มี seed = null ตามที่ README กำหนด

## 9. รายงาน

`report.docx` (2 หน้า) — prediction, protocol, FSM/table, กราฟ, latency table, ผล C0/C1, negative result และ hardware limitation

## ส่วนที่ทำไม่ได้ในเครื่องนี้ (ข้าม)

ใบงาน Word ส่วน "ก่อนต่อหุ่นยนต์จริง": การสอบเทียบศูนย์/ทิศทาง/ขีดจำกัดของแกนจริง, วิธีหยุดฉุกเฉิน, และการวัด latency จริงด้วยกล้อง/photodiode — ไม่มีหุ่นยนต์โคมไฟในงานนี้ จึงไม่ได้ทำ ผลทั้งหมดเป็น simulated command onset เท่านั้น
