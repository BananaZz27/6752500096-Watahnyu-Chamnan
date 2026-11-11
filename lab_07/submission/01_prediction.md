# Lab 07 — Question, hypothesis, expected set และ prediction ก่อนรัน

บันทึกเมื่อ: 2026-11-11 20:15 (UTC+7) ก่อนรัน `check_submission.py`, `offline_lab.py`, `check_proposal.py` และก่อนเติม TODO ใน `lamp_week07/student_policy.py` (ยังไม่มีโฟลเดอร์ผล)
สิ่งที่ใช้ประกอบการคาด: README, `interface_contract.json`, การอ่านโค้ด `offline_lab.py` / `bridge.py` / `course_model.py` (ไม่ได้รัน) และผลที่วัดแล้วของกลุ่มใน Lab06 (`course_model.py` ของ Lab07 เหมือนของ Lab06 ทุกไบต์)

## สิ่งที่ประกาศก่อนรัน (ข้อ 3 ของใบงาน)

- **Policy:** เติม starter ของ Lab07 ด้วยตาราง baseline เดียวกับ Lab06 (touch → happy ยกเว้น afraid; interested/happy + timeout → normal; normal + idle → sleepy) ตรวจด้วย `--contract group` ตาม README และ `baseline` เพิ่ม
- **Question:** โปรไฟล์ transport ที่มี jitter (0–0.18 s) และ drop (8 % + burst 12.50–12.70 s) เปลี่ยน latency, จำนวน fault และความนิ่งของ emotion state ของ policy เดียวกันเมื่อเทียบกับ transport ideal อย่างไร ใน virtual offline model
- **Hypothesis:** C1 ทำให้ both latency ของ primary inputs เพิ่มขึ้น (≈ เท่ากับ delay ของข้อความที่ตัดสิน, เฉลี่ย ≈ 0.07 s) แต่ยังต่ำกว่า deadline 1 s และทำให้ fault ticks กับ state transitions เพิ่มขึ้นมาก เพราะ sample ที่มาช้า > 0.12 s ถูกนับเป็น stale แล้ว fault บังคับกลับ normal
- **Condition/control:** C0 ideal (delay 0, drop 0) vs C1 composite jitter + drop; คงที่: policy, guarded debounce/hysteresis, poses/RGB, bounds/slew, dt 0.02 s, 22 s, scheduler 0.04 s, source stimuli และ seed คู่ 41/42/43 (C1 เปลี่ยนสองอย่างพร้อมกัน จึงตอบผลของ profile ไม่ใช่ผลแยกของ jitter หรือ drop)
- **Expected input IDs (denominator):** baseline primary 7 IDs `button_01, touch_01, approach_01, clear_01, near_01, clear_02, button_02` ทั้ง C0/C1 และเก็บ all 10 sources
- **Deadline / observation window:** both latency ≤ 1.0 s; หา onset ภายใน trial 22 s เท่านั้น ไม่มี onset = missing (null) ไม่ใช่ 0 และไม่ใช่ deadline fail
- **Metrics:** M1 = primary both latency (median/max, s) และจำนวน pass/miss จาก 7; M2 = state transitions ต่อ trial; เพิ่ม fault ticks /1101, received/dropped/out-of-order
- **Clock/measurement boundary:** virtual clock เดียวของ offline process; latency = first applied simulated motion & RGB − original source time; ไม่ใช่ ROS/DDS หรือ physical onset

## Prediction เชิงตัวเลข

### C0 (ideal transport)

engine ของ Lab07 ใช้ guarded filter และ frame ที่ส่งถึงทันที จึงคาดว่า **เหมือน Lab06 C1 ทุกประการ**: transitions 9 / 10 / 9 (seed 41/42/43), primary 7/7 pass, miss 0, latency button_01 0.14, touch_01 0.10, approach_01 0.04, clear_01 0.04, near_01 0.04 (seed 42: 0.06), clear_02 0.04, button_02 0.10 s → median 0.04 s, max 0.14 s; fault ticks = 20 /1101 (invalid NaN 7 ticks 11.00–11.12 + stale touch 13 ticks 12.00–12.24); received = published = 3303, dropped 0, out-of-order 0

### C1 (jitter + drop)

| Metric | Prediction | เหตุผล |
|---|---|---|
| dropped | ≈ 290 (≈ 8.8 % ของ 3303) | 0.08 × 3303 ≈ 264 + burst 10 ticks × 3 channels ที่ไม่ได้ drop อยู่แล้ว ≈ 28 |
| censored after trial | ≈ 10–20 | ข้อความที่ receipt > 22 s (delay ≤ 0.18 s) |
| mean / max transport age | ≈ 0.074 s / 0.18 s | ค่าเฉลี่ยของ delay choices (0.52/7) |
| out-of-order | ≈ 15–30 % ของ received | ข้อความ delay ยาวถูกข้อความใหม่แซง |
| fault ticks | ≈ 50–70 /1101 | baseline 20 + stale จาก jitter: P(ไม่มีข้อความใน 0.12 s ล่าสุดมาถึง) ≈ 1 % ต่อ channel ต่อ tick → ≈ 3 % ของ ticks ≈ 33 + burst ≈ 5–8 |
| state transitions | ≈ 30–60 (C0 9–10) | fault แต่ละครั้งขณะ interested/happy/afraid/sleepy บังคับ normal แล้ว event เดิม (near/approach/idle) ถูก recognize ใหม่ → +2 transitions |
| primary median / max both latency | ≈ 0.10–0.15 s / ≈ 0.3–0.4 s | C0 + delay ของข้อความที่ตัดสิน (+ drop ทีละ 0.02 s) |
| primary pass ≤ 1 s / miss | 5–7 / 0–2 ต่อ seed | miss เกิดได้ถ้า stale fault ตกในช่วง 0.04 s ระหว่าง decision กับ apply (preempted_by_fault) แล้ว state กลับเป็น normal |

## สิ่งที่ prediction ไม่ครอบคลุม

ROS 2 track (3 processes, DDS, rosbag) รันไม่ได้ในเครื่องนี้ (Windows, ไม่มี ROS 2 และ WSL ไม่มี Linux distribution) จึงไม่มี prediction สำหรับเวลาจริงของ ROS

## บันทึกการแก้สมมติฐาน

(ยังไม่มี — ถ้ามีการแก้หลังเห็นผลจะบันทึกเวลาและเหตุผลไว้ที่นี่ โดยไม่ลบข้อความเดิม)
