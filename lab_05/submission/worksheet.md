# ใบงาน Lab 05 — Prediction, timing, evidence

ชื่อกลุ่ม ภาคีนกอีก๋อย สมาชิก วทัญญู ชำนาญ วันที่ 11 พฤศจิกายน 2569 · Python 3.11.0

**ขอบเขต:** main runner เป็น proposed course model ใช้ scheduled stimulus และ kinematic body; contact demo ใช้ synthetic signals ไม่ใช่ ALCS terrain experiment ของ paper
ตัวเลขทั้งหมดมาจาก `*/metrics.json`, `*/segment_metrics.csv` และ raw CSV ในโฟลเดอร์นี้ prediction อยู่ใน `01_prediction.md` (บันทึก 20:01 ก่อนรัน)

## 1. ก่อนรัน: hypothesis และ architecture

1. Diagram: `figures/block_diagram.png` — S schedule → controller (B0/B1/B2/B3) → R_used → bounded mapping → φ (→ CPG) และ stride_half (→ decoder) → SO(2) CPG → tripod decoder → stance-anchor body จุดที่ไม่มี independent sensory feedback: S เป็นตารางเวลาที่ไม่ขึ้นกับ body, contact = sign(o₂) จาก decoder ไม่ใช่ sensor และไม่มีเส้นทางจาก body/terrain กลับเข้า hormone หรือ CPG (open loop ทั้งเส้น)
2. Hypothesis H1 (B1 vs B2): phi_max_step ลดจาก 0.200 เหลือ ≈ 0.008 rad แต่ phi TV แทบไม่ต่าง (≈ 0.400 rad), command latency 0 → 0.15 s, recovery 0 → ≈ 2.85 s, on frequency ต่ำกว่า (≈ 1.19 vs 1.26 Hz) และ on distance น้อยกว่า (≈ 1.70 vs 1.83 m) แต่ off distance มากกว่า (≈ 0.89 vs 0.77 m) จนระยะรวม 30 s ใกล้กัน
3. B3 ตัด binding term B = k_bind·R ออกจาก removal ของ H (ใน model นี้เท่านั้น) สิ่งที่ยังมี memory: state H (production สะสม, clearance 0.6 /s) และ state ของ oscillator ที่ต่อเนื่องจาก warmup
4. Provenance:

| ประเภท | รายการ |
|---|---|
| Source equation | release = CI/(1 + exp(−SIF)), SIF = SD ของ SI 6 ขา (Ngamkajornwiwat et al. 2020, Eq. 1–2) |
| Proposed course equation | H(t_k+1) = clamp(H + dt(k_prod·S − k_clear·H − k_bind·R), 0, 1); φ = clamp(0.20 + 0.20·R_used, 0.10, 0.45) |
| Expected measurement | segment frequency ของ o₁ (rising crossings) และ distance ของ body ใน kinematic model |
| Metric ที่วัดไม่ได้ | Stability / Harmony / Displacement ตาม paper (Eq. 8–14) — `paper_*` = null ใน metrics.json |

## 2. รัน comparison และตรวจเวลา

`comparison/B2_intervals.csv` (และ `B2_states.csv`):

| command/input time | state end time | H_start | H_end | R_used | φ ที่ใช้ | stride_half ที่ใช้ |
|---|---|---|---|---|---|---|
| 10.00 | 10.05 | 0 | 0.0400 | 0 | 0.200 | 0.0550 |
| 10.05 | 10.10 | 0.0400 | 0.0784 | 0.0400 | 0.208 | 0.05540 |
| 20.00 | 20.05 | 0.99972 | 0.95973 | 0.99972 | 0.39994 | 0.064997 |

B1 command latency (0 s) กับ state latency (0.05 s) ต่างกันเพราะ B1 ใช้ S_k ทันทีใน interval เดียวกัน: `B1_intervals.csv` command 10.00 มี r_used = 1, φ = 0.40 แต่ `B1_states.csv` บันทึก state หลัง update แถว 10.00 ยังเป็น r = 0 และ r = 1 ปรากฏที่ state 10.05 ความต่าง 0.05 s คือ offset ของการ log (= dt) ไม่ใช่ hardware latency

ตรวจ warmup/initial states ใน `comparison/config.json`: ทุก condition (B0–B3) เริ่มด้วย o₁ = −0.026965, o₂ = −0.560863, body_x = 0, R = 0 (H = 0 สำหรับ B2/B3, null สำหรับ B0/B1) — เหมือนกันทุกตัว และ pre segment [0, 10) ให้ 0.6249 Hz, 0.7763 m เท่ากันทุก condition

## 3. เปรียบเทียบผลและข้อจำกัด

| condition | TV φ (rad) | max Δφ/step (rad) | TV stride (m) | cmd latency (s) | cmd recovery (s) | on frequency (Hz) | on distance (m) |
|---|---|---|---|---|---|---|---|
| B0 | 0 | 0 | 0 | N/A (B0 ไม่มี timing) | N/A | 0.6249 | 0.7787 |
| B1 | 0.4000 | 0.2000 | 0.0200 | 0.00 | 0.00 | 1.2684 | 1.8252 |
| B2 | 0.3998 | 0.0080 | 0.0200 | 0.15 | 2.85 | 1.2028 | 1.7063 |
| B3 | 0.3995 | 0.0080 | 0.0200 | 0.15 | 3.80 | 1.2258 | 1.7275 |

ค่าเพิ่ม: rise 10–90 % = 0 / 2.70 / 1.70 s (B1/B2/B3), state latency 0.05 / 0.15 / 0.15 s, off distance 0.7776 / 0.7760 / 0.9000 / 0.9563 m, off frequency 0.6249 / 0.6249 / 0.6982 / 0.7290 Hz, distance 30 s 2.333 / 3.378 / 3.383 / 3.460 m, support 3 ทุก segment, command clamp count 0, H upper clamp fraction B3 = 0.258 (B2 = 0)

1. **สนับสนุน:** max Δφ ลดจาก 0.200 เป็น 0.008 rad, TV เกือบเท่ากัน (0.4000 vs 0.3998), latency 0.15 s, recovery 2.85 s, on frequency 1.203 Hz (คาด ≈ 1.19), on distance 1.706 m (คาด ≈ 1.70), off distance 0.900 m (คาด ≈ 0.89) **ไม่สนับสนุน / null:** ระยะรวม 30 s ของ B2 มากกว่า B1 เล็กน้อย (3.383 vs 3.378 m, +0.15 %) ขณะที่คาดว่าน้อยกว่าเล็กน้อย (≈ 3.37 vs 3.38) — ความต่างเล็กกว่าความแม่นของการประมาณ จึงสรุปได้เพียงว่า "ไม่ต่างกันในทางปฏิบัติ" hormone path ย้ายระยะทางจากช่วง on ไปช่วง off แทนที่จะเพิ่มหรือลด
2. **ไม่ยืนยัน** model ไม่มีมวล แรง CoM, friction หรือ actuator ขาดข้อมูล: ground reaction force, CoM เทียบ support polygon (stability margin), joint torque/power (energy), slip และการเดินบนพื้นจริง
3. **ไม่เท่ากัน** bounds เหมือนกัน (0.10–0.45 rad) แต่ peak R_used ต่างกัน: B1 = 1.0000, B2 = 0.9997 (ไม่ถึง 1 เพราะ H* = 1 พอดี), B3 = 1.0000 (ชน clamp ของ H ที่ 12.30 s) และ trace ต่างกันมาก (fig1): mean φ ช่วง on = 0.400 / 0.375 / 0.382 rad
4. ค่าเฉลี่ย 30 s จะผสม pre/on/off ที่มี φ ต่างกัน และกลบ transient หลังเปิด/ปิด: B2 off frequency 0.698 Hz ต่างจาก pre 0.625 Hz เพราะ R ยังค้าง (fig1 กลาง) แม้แต่ช่วง on ของ B2 ก็ยังมี transient ≈ 3 s จึงไม่เรียกว่า steady state

## 4. เปลี่ยนหนึ่งปัจจัยและตรวจ fault

รันทั้งสองแบบ (`phi_only/`, `stride_only/`) prediction ใน `01_prediction.md`

| | phi-only | stride-only |
|---|---|---|
| สิ่งที่เปลี่ยน | φ ตาม R_used | stride_half ตาม R_used |
| สิ่งที่คงที่ | stride_half = 0.055 m ทุก interval (TV stride = 0) | φ = 0.20 rad ทุก interval (TV φ = 0) |
| metric หลัก | on frequency, on distance | on frequency, on distance |
| prediction | f B1 ≈ 1.26 Hz เท่า both, on distance B1 ≈ 1.55 m | f = 0.625 Hz ทุก condition, on distance B1 ≈ 0.92 m |
| ผล | f B1/B2/B3 = 1.268 / 1.203 / 1.226 Hz (เท่า both ทุกหลัก), on distance 1.549 / 1.467 / 1.478 m | f = 0.6249 Hz ทุก condition และทุก segment, on distance 0.915 / 0.902 / 0.907 m |

ผลและข้อจำกัด causal claim: ภายใน model นี้ φ เป็นตัวกำหนด frequency ทั้งหมด (stride ไม่เปลี่ยน frequency เลย) ส่วน stride เปลี่ยนระยะต่อรอบ: both/phi-only ของ B1 = 1.825/1.549 = 1.178 ≈ 0.065/0.055 = 1.182 claim นี้จำกัดอยู่ใน kinematic model ที่ระยะต่อรอบเป็นสัดส่วนกับ stride โดยนิยาม และไม่มี slip จึงไม่ได้พิสูจน์ว่าบนหุ่นยนต์จริงจะเป็นแบบเดียวกัน

Fault profile (`fault/B2_intervals.csv`, `B2_states.csv`):

| field | B2 value |
|---|---|
| fault at command 15.00 | 1 (stimulus_raw = NaN) |
| H_used / R_used | 0 / 0 (H_state_start = 0.9831) |
| φ / stride ที่ใช้ | 0.20 rad / 0.055 m |
| H state 15.05 | 0 |
| H state 15.10 | 0.04 |

Fallback ทำ **ก่อน** command: ในแถว command 15.00 ค่า h_state_start = 0.9831 แต่ h_used = r_used = 0 และ φ = 0.20 ถูกใช้ใน interval [15.00, 15.05) เลย (ไม่รอ command ถัดไป) ผลข้างเคียงที่วัดได้: fallback สร้าง command jump ใหญ่ที่สุดของ trial ใน hormone conditions — max Δφ ของ B2 เพิ่มจาก 0.008 เป็น 0.1965 rad และ B3 เป็น 0.200 rad (เท่า direct path) และ TV φ เป็น 0.786 / 0.800 rad หลังจากนั้น H ต้องสะสมใหม่ ≈ 3 s on frequency ของ B2 จึงลดเหลือ 1.113 Hz (จาก 1.203) Policy นี้ยังไม่รับรอง hardware safety เพราะเป็นเพียงโค้ดใน simulation: ไม่มี actuator limit, ไม่มี watchdog/e-stop ที่ไม่ขึ้นกับซอฟต์แวร์ ไม่ได้ทดสอบ fault แบบอื่น (ค่าค้าง, drift, หลาย sample) และการกระโดดของคำสั่งเองอาจเป็นอันตรายต่อขาจริง

## 5. Contact mini-lab

`contact/metrics.json` (mean SI/SIF ใช้ rows ที่ valid ครบ 6 ขา, MAE ใช้ finite pairs ทั้ง trial):

| case | SI ของแต่ละขาโดยทั่วไป | SIF | absolute error | valid rows | สิ่งที่อนุมานไม่ได้ |
|---|---|---|---|---|---|
| matched | 1 ทุกขา | 0 | 0 | 551 | ว่า expected model ถูกต้องเทียบพื้นจริง |
| gain-offset | 1 ทุกขา | 0 | 0.1628 | 551 | ขนาด amplitude/offset error |
| mixed-delay | LF, RM, LH = 1; RF, LM, RH = 0.000 | 0.5000 (release 0.622) | 0.2260 | 551 | ขาไหน delay และ delay ไปทางใด |
| all-inverted | −1 ทุกขา | 0 (release 0.5) | 0.6314 | 551 | ว่าทุกขาผิดเฟสหมด |
| constant | N/A ทุกขา (zero_variance) | N/A | 0 | 0 | — |
| fault | 1 ทุกขาเมื่อ valid | 0 | 0 | 501 | ค่าที่หายไปของ LF |

1. Pearson วัดเฉพาะความสัมพันธ์เชิงเส้นหลังลบค่าเฉลี่ยและหารด้วย SD actual = 0.2 + 0.5·expected เป็น affine ที่ slope บวก จึงได้ SI = 1 พอดี ทั้งที่ MAE = 0.163
2. SIF คือ SD ของ SI ระหว่างขา ถ้าทุกขาผิดเหมือนกัน (SI = −1 ทั้งหก) ค่าก็เท่ากันหมด SD = 0 release ที่ SIF = 0 = 1/(1 + e⁰) = **0.5** เท่ากับกรณี matched — SIF/release แยก "ถูกหมด" กับ "ผิดหมด" ไม่ได้ ต้องดู SI และ MAE ร่วม
3. ควรเป็น **N/A** variance = 0 ทำให้ Pearson หารด้วยศูนย์ ไม่นิยาม ไม่ใช่ "ไม่สัมพันธ์" (SI = 0) runner บันทึก validity = zero_variance และ valid rows = 0
4. Window เริ่ม valid ที่ sample 49 = 2.45 s fault ที่ sample 300 (15.00 s) ทำให้ LF ไม่ valid **50 rows** (15.00–17.45 s, validity = nonfinite_window) ไม่นับ startup 49 rows → valid rows 551 − 50 = 501
5. Paired Pearson ใน demo เป็น **proposed course definition** ไม่ใช่ reproduction ของ Eq. (3) ตามที่พิมพ์ และ **ยังไม่ต่อ** C_g/HR/MI_H (คำนวณ release ตาม Eq. 1, CI = 1 เท่านั้น) ไม่ส่งกลับเข้า main runner

## 6. ส่งงานและ exit ticket

ไฟล์และคำสั่งรันซ้ำอยู่ใน `README.md` ทุก run มี config, metrics, raw states/intervals, source snapshot และ `manifest.json` (SHA-256)

- **Claim ที่ข้อมูลรองรับ:** ใน kinematic course model นี้ hormone path (B2) ลด max Δφ ต่อ step จาก 0.200 เป็น 0.008 rad โดย TV φ เท่าเดิม (0.400 vs 0.3998 rad) และแลกด้วย command latency 0.15 s, rise 2.70 s, recovery 2.85 s (comparison/metrics.json, window [10, 20) และ [20, 30))
- **Claim ที่ยังรองรับไม่ได้:** "hormone path ทำให้เดินนิ่งขึ้น / ปลอดภัยขึ้น / ประหยัดพลังงาน" — ต้องมี body dynamics และวัด stability margin (CoM vs support polygon), ground reaction force, joint torque/energy และ Stability/Harmony/Displacement ตามนิยามของ paper บนพื้นจริง พร้อม feedback จาก contact sensor จริง
