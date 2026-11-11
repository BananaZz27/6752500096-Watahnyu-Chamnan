# Lab 06 — Prediction, transition table และ expected set ก่อนรัน

บันทึกเมื่อ: 2026-11-11 20:08 (UTC+7) ก่อนรัน `check_submission.py`, `lab06.py` ใด ๆ และก่อนเติม TODO (ยังไม่มีโฟลเดอร์ผล)
สิ่งที่ใช้ประกอบการคาด: README, worksheet, `interface_contract.json` และการอ่านโค้ด `course_model.py` / `lab06.py` (ไม่ได้รัน) ตัวเลขทั้งหมดคำนวณด้วยมือ

## Contract ที่เลือก

**baseline** (`python check_submission.py`) เพื่อให้ผลเทียบกับ protocol และ `primary_*` 7 IDs ของ runner ได้ตรง ๆ ไม่ได้ใช้ group mapping
Expected set ที่ประกาศก่อนรัน = baseline primary 7 IDs: `button_01, touch_01, approach_01, clear_01, near_01, clear_02, button_02` (ใช้ชุดเดียวกันทั้ง C0/C1) อีก 3 sources (`touch_conflict`, `invalid_01`, `stale_01`) เก็บไว้ใน all 10 พร้อม status แต่ไม่คาดว่าจะมี onset ใหม่

## Transition table 5 × 8 (baseline; "hold" = return None)

Priority เมื่อ recognized ใน tick เดียวกัน: fault > near > clear > touch > button > approach > timeout > idle

| current \ event | fault | near | clear | touch | button | approach | timeout | idle |
|---|---|---|---|---|---|---|---|---|
| normal | normal | afraid | normal | happy | interested | interested | hold | sleepy |
| interested | normal | afraid | normal | happy | interested | interested | normal | hold |
| happy | normal | afraid | normal | happy | interested | interested | normal | hold |
| afraid | normal | afraid | normal | hold | hold | hold | hold | hold |
| sleepy | normal | afraid | normal | happy | interested | interested | hold | hold |

ช่องที่คืนค่า state เดิม (เช่น normal + fault, interested + button) จะถูก engine บันทึกเป็น `no_state_change` ไม่ใช่ hold

## ข้อ 1 — bounce/noise กระทบ C0 กับ C1 อย่างไร

เวลาใน model: event recognized ที่ tick t → decision/queue ที่ t → apply ที่ t + 0.04 s (scheduler) และ RGB เปลี่ยนทันทีใน tick ที่ apply ส่วน motion เริ่มขยับใน tick เดียวกัน (slew 0.016 rad/tick) ดังนั้น both latency = (recognized − source) + 0.04 s

| Input | C0 (raw) | C1 (guarded) |
|---|---|---|
| button_01 (bounce 1.00–1.04) | recognized 1.00 → both 0.04 s; bounce ทำให้มี button candidate ซ้ำที่ 1.04 (no_state_change) | debounce นับจาก edge สุดท้าย 1.04 → recognized 1.10 → **0.14 s** |
| touch_01 (3.00) | 0.04 s (ชนะ timeout ของ interested ที่ 3.00 ด้วย priority) | debounce → 3.06 → 0.10 s |
| approach_01 (0.79 ± 0.035 m) | 0.04 s ขึ้นกับ sample แรก ≤ 0.80 แต่ **chatter**: P(≤ 0.80) ≈ 0.64 → approach/clear สลับ ≈ 0.46 ครั้งต่อ tick ≈ 30 ครั้งใน 1.4 s → interested ↔ normal กลับไปกลับมา | hysteresis (exit ≥ 0.95) → เข้าครั้งเดียว latency ≈ 0.04–0.06 s ไม่มี chatter |
| clear_01 (6.40) | ถ้า tick 6.38 approach เป็น false อยู่แล้ว (≈ 36 %) จะไม่มี clear event ของ clear_01 → **miss** (filtered_not_recognized) ไม่อย่างนั้น 0.04 s | 0.04 s |
| near_01 + touch_conflict (7.00, 0.18 ± 0.035 m) | near ชนะ touch ถ้า sample 7.00 ≤ 0.20 (≈ 79 %) แต่ near/clear chatter (≈ 0.34 ต่อ tick ≈ 30 ครั้งใน 2 s) → afraid ↔ normal สลับไปมา และ touch_conflict อาจทำให้ happy ชั่วคราวถ้า near ยังไม่ recognized ที่ 7.00 | afraid ตลอด 7–9 s (exit ≥ 0.28); touch recognized 7.06 ถูก afraid guard → policy_held |
| clear_02 (9.00) | ถ้า tick 8.98 near เป็น false (≈ 21 %) state เป็น normal อยู่แล้ว → clear เป็น no_state_change → miss; ไม่อย่างนั้น 0.04 s | 0.04 s |
| invalid_01 (11.00), stale_01 (12.00) | fault ขณะ normal อยู่แล้ว → no_state_change → ไม่มี onset (N/A ตามเหตุผล) | เหมือน C0 |
| quiet → sleepy | idle ที่ ≈ 15.00 s (6 s หลัง activity สุดท้าย ≈ 9.00 s; fault ไม่ใช่ activity) | เหมือน C0 |
| button_02 (18.00, ไม่มี bounce) | 0.04 s | debounce → 18.06 → 0.10 s |

## สรุปที่คาดต่อ seed (41, 42, 43)

| | C0 raw | C1 guarded |
|---|---|---|
| state transitions | ≈ 60–80 (chatter ช่วง 5–6.4 s และ 7–9 s) | ≈ 9–10 |
| all 10 sources: both onset | ≈ 5–7 | 7 |
| primary 7: ≤ 1 s / missing | ≈ 5–7 / 0–2 (clear_01, clear_02 มีโอกาส miss) | 7 / 0 |
| max observed both latency | ≈ 0.04–0.08 s | ≈ 0.14 s (button_01) |
| no-onset sources | touch_conflict, invalid_01, stale_01 (+ misses) | touch_conflict (policy_held), invalid_01, stale_01 (no_state_change) |

ข้อสรุปที่คาด: C1 แลก latency เพิ่ม ≈ 0.06–0.10 s ใน button/touch (debounce) กับการตัด chatter และ miss ของ clear ที่เกิดจาก noise ใน C0 ทั้งสองแบบยังอยู่ใต้ 1 s ใน simulation ซึ่งเป็นเพียง software model

## Near + touch พร้อมกัน (ใบงาน Word)

ควรเป็น afraid เพราะ near เป็นเหตุการณ์ด้านความปลอดภัยที่ priority สูงกว่า touch และ afraid guard ต้อง hold positive inputs จนกว่าจะ clear/fault แต่ priority ช่วยได้เฉพาะเมื่อ recognized ใน tick เดียวกัน ถ้า touch recognized ก่อน near ระบบอาจเป็น happy ชั่วคราว

## บันทึกการแก้สมมติฐาน

(ยังไม่มี — ถ้ามีการแก้หลังเห็นผลจะบันทึกเวลาและเหตุผลไว้ที่นี่ โดยไม่ลบข้อความเดิม)
