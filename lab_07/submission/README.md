# Lab 07 — ผลส่งมอบ

ไฟล์ผลทั้งหมดอยู่ใน `lab_07/submission/` (`.gitignore` ของ repo และของ lab_07 ตัด `results/`, `logs/`, `bags/` ออก)

| ผลส่งมอบตาม README "งานส่ง Week07" / ใบงาน | ไฟล์ |
|---|---|
| Question/hypothesis/expected IDs/prediction ก่อนรัน | `01_prediction.md` (2026-11-11 20:15 ก่อนรันและก่อนเติม TODO) |
| 1. Graph 3 roles + micro-ROS/ESP32/Agent extension, topic/unit/QoS, timestamp boundary | `figures/ros_graph.png` |
| 2. Policy ของกลุ่มผ่าน bridge + topic contract + traces/config, 2 conditions × 3 repeats พร้อม misses | `../lamp_week07/student_policy.py` (ตาราง baseline เดียวกับ Lab06), `check_group.txt` / `check_baseline.txt` (PASS), `check_starter_group.txt` (starter FAIL ก่อนเติม), `completed_run/` (C0/C1 × seeds 41–43: `input_trace.csv`, `command_trace.csv`, `events.csv`, `metrics.json`, `config.json`; `summary.json`, `report.html`, `source_snapshot/`, `manifest.json`), `replay_check/` (replay C1_r02 ตรงทุกไบต์) |
| 3. `proposal.json` + proposal 2–3 หน้า | `../proposal.json` (`check_proposal.txt` PASS; `check_proposal_starter.txt` = template FAIL), `proposal.docx` (3 หน้า) |
| ใบงาน | `worksheet.md` |
| กราฟ | `figures/fig1_emotion_fault_timeline.png`, `fig2_latency.png`, `fig3_transport.png` |

## รันซ้ำ

Python 3.11.0 จากโฟลเดอร์ `lab_07`:

```sh
python check_submission.py --contract group > submission/check_group.txt
python check_submission.py --contract baseline > submission/check_baseline.txt
python offline_lab.py --condition all --repeats 3 --output-dir submission/completed_run
python offline_lab.py --condition C1 --repeats 1 --replay submission/completed_run/C1_r02/input_trace.csv --output-dir submission/replay_check
python check_proposal.py proposal.json > submission/check_proposal.txt
python submission/make_figures.py
```

## ส่วนที่ข้าม

- **ROS 2 track ทั้งหมด** (colcon build, รัน `synthetic_inputs` / `interaction` / `output_collector`, `ros2 topic list/info/echo`, `ros2 bag record`, ทดสอบ receipt-stale โดยหยุด publisher): เครื่องนี้เป็น Windows ไม่มี ROS 2 Jazzy และ WSL ไม่มี Linux distribution ตรวจได้เพียง `python -m py_compile lamp_week07/ros_nodes.py lamp_week07/bridge.py` ผ่าน ไม่มีผล ROS/DDS timing
- **micro-ROS / ESP32 / หุ่นยนต์จริง / human scenario 600 s**: เป็นแผนใน proposal เท่านั้น ยังไม่ได้สร้างหรือทดลอง
- ผลใน `completed_run/` เป็น virtual single-process transport ไม่ใช่ ROS/DDS benchmark และไม่ใช่ physical latency
