"""生成 Demo 全部种子数据：静态 JSON 配置 + 历史 CSV"""
import json
import csv
import os
import random
from datetime import date, timedelta

random.seed(42)

OUTDIR = os.path.join(os.path.dirname(__file__), "..", "backend", "app", "seed")
os.makedirs(OUTDIR, exist_ok=True)

# ============================================================
# 1. 基础配置
# ============================================================
SLOTS = ["08:00-11:00", "11:00-14:00", "14:00-17:00", "17:00-20:00"]
SLOT_INDEX = {s: i for i, s in enumerate(SLOTS)}

AREAS = [
    {"code": "aquatic",      "name": "水产区",     "allow_mixed": False, "baseline_min": 2, "baseline_max": 3, "sort_order": 1},
    {"code": "meat",         "name": "肉类区",     "allow_mixed": False, "baseline_min": 2, "baseline_max": 3, "sort_order": 2},
    {"code": "produce",      "name": "果蔬区",     "allow_mixed": True,  "baseline_min": 1, "baseline_max": 2, "sort_order": 3},
    {"code": "cashier",      "name": "收银/前场",  "allow_mixed": True,  "baseline_min": 1, "baseline_max": 2, "sort_order": 4},
    {"code": "replenishment","name": "补货区",     "allow_mixed": True,  "baseline_min": 1, "baseline_max": 2, "sort_order": 5},
]
AREA_CODES = [a["code"] for a in AREAS]

# ============================================================
# 2. 静态 JSON
# ============================================================

# 2a. areas.json
with open(os.path.join(OUTDIR, "areas.json"), "w", encoding="utf-8") as f:
    json.dump(AREAS, f, ensure_ascii=False, indent=2)
print("✅ areas.json")

# 2b. skill_definitions.json
SKILL_DEFS = [
    {"level": "S", "name": "专业师傅",   "description": "可处理高难度专业任务",     "can_independent": 1, "score": 1.0},
    {"level": "A", "name": "熟练员工",   "description": "可独立完成区域常规任务",   "can_independent": 1, "score": 0.9},
    {"level": "B", "name": "可支援员工", "description": "可在监督下承担基础任务",   "can_independent": 0, "score": 0.7},
    {"level": "C", "name": "新手/临时",  "description": "只能做辅助性工作",         "can_independent": 0, "score": 0.0},
]
with open(os.path.join(OUTDIR, "skill_definitions.json"), "w", encoding="utf-8") as f:
    json.dump(SKILL_DEFS, f, ensure_ascii=False, indent=2)
print("✅ skill_definitions.json")

# 2c. area_tasks.json
AREA_TASKS = [
    {"id": "task_aquatic_01", "area_code": "aquatic", "task_code": "fish_butcher",    "task_name": "杀鱼",     "is_professional": 1, "min_skill_level": "S", "priority": 100},
    {"id": "task_aquatic_02", "area_code": "aquatic", "task_code": "aquatic_process", "task_name": "水产处理", "is_professional": 1, "min_skill_level": "A", "priority": 90},
    {"id": "task_aquatic_03", "area_code": "aquatic", "task_code": "weighing",        "task_name": "称重",     "is_professional": 0, "min_skill_level": "B", "priority": 50},
    {"id": "task_aquatic_04", "area_code": "aquatic", "task_code": "cleaning",        "task_name": "清洁",     "is_professional": 0, "min_skill_level": "C", "priority": 20},
    {"id": "task_meat_01",    "area_code": "meat",    "task_code": "meat_cut",        "task_name": "切肉",     "is_professional": 1, "min_skill_level": "S", "priority": 100},
    {"id": "task_meat_02",    "area_code": "meat",    "task_code": "meat_divide",     "task_name": "分割",     "is_professional": 1, "min_skill_level": "A", "priority": 90},
    {"id": "task_meat_03",    "area_code": "meat",    "task_code": "weighing",        "task_name": "称重",     "is_professional": 0, "min_skill_level": "B", "priority": 50},
    {"id": "task_meat_04",    "area_code": "meat",    "task_code": "display",         "task_name": "陈列",     "is_professional": 0, "min_skill_level": "B", "priority": 40},
    {"id": "task_produce_01", "area_code": "produce", "task_code": "restock",         "task_name": "补货",     "is_professional": 0, "min_skill_level": "B", "priority": 70},
    {"id": "task_produce_02", "area_code": "produce", "task_code": "display",         "task_name": "陈列",     "is_professional": 0, "min_skill_level": "B", "priority": 50},
    {"id": "task_produce_03", "area_code": "produce", "task_code": "packing",         "task_name": "打包",     "is_professional": 0, "min_skill_level": "B", "priority": 40},
    {"id": "task_produce_04", "area_code": "produce", "task_code": "weighing",        "task_name": "称重",     "is_professional": 0, "min_skill_level": "B", "priority": 50},
    {"id": "task_cashier_01", "area_code": "cashier", "task_code": "cashier",         "task_name": "收银",     "is_professional": 0, "min_skill_level": "A", "priority": 80},
    {"id": "task_cashier_02", "area_code": "cashier", "task_code": "customer_service","task_name": "顾客服务", "is_professional": 0, "min_skill_level": "B", "priority": 40},
    {"id": "task_repl_01",    "area_code": "replenishment","task_code": "restock_unload", "task_name": "到货卸货", "is_professional": 0, "min_skill_level": "B", "priority": 70},
    {"id": "task_repl_02",    "area_code": "replenishment","task_code": "shelf_restock",  "task_name": "上架补货", "is_professional": 0, "min_skill_level": "B", "priority": 70},
    {"id": "task_repl_03",    "area_code": "replenishment","task_code": "inventory",      "task_name": "库存整理", "is_professional": 0, "min_skill_level": "B", "priority": 40},
]
with open(os.path.join(OUTDIR, "area_tasks.json"), "w", encoding="utf-8") as f:
    json.dump(AREA_TASKS, f, ensure_ascii=False, indent=2)
print("✅ area_tasks.json")

# 2d. modified_reasons.json
REASONS = [
    {"code": "employee_unavailable", "label": "员工实际不可用",     "sort_order": 1},
    {"code": "employee_not_fit",     "label": "员工不适合该区域",   "sort_order": 2},
    {"code": "manager_experience",   "label": "店长经验调整",       "sort_order": 3},
    {"code": "area_leader_request",  "label": "区域负责人要求",     "sort_order": 4},
    {"code": "operation_change",     "label": "临时经营变化",       "sort_order": 5},
    {"code": "other",               "label": "其他",               "sort_order": 6},
]
with open(os.path.join(OUTDIR, "modified_reasons.json"), "w", encoding="utf-8") as f:
    json.dump(REASONS, f, ensure_ascii=False, indent=2)
print("✅ modified_reasons.json")

# ============================================================
# 3. 员工数据（复用之前的逻辑）
# ============================================================
SURNAMES = [
    "张","王","李","刘","陈","杨","黄","赵","周","吴",
    "徐","孙","马","朱","胡","郭","何","高","林","罗",
    "郑","梁","谢","宋","唐","韩","曹","许","邓","冯",
    "程","蔡","彭","潘","袁","董","余","苏","叶","吕",
    "魏","蒋","田","杜","丁","沈","姜","范","江","傅",
]
GIVEN_MALE = "伟强磊军勇杰涛明辉鹏飞超波斌锋浩亮健龙华志国建文成海峰".split()
GIVEN_FEMALE = "芳娟敏静丽霞兰萍玲红莲翠凤春花秋梅雪云美慧".split()
GIVEN_MALE_2 = ["建国","志强","伟民","海涛","文彬","俊杰","晓明","建华","国强","永刚","晓东","志远","明辉","大伟","浩宇"]
GIVEN_FEMALE_2 = ["秀英","桂英","玉兰","秀兰","海燕","红梅","丽华","美玲","晓燕","春梅","雪梅","慧敏","小平","秀梅","玉梅"]

random.shuffle(SURNAMES)

PLAN = [
    ("aquatic",       10,  2, 2, 4, 2),
    ("meat",          12,  2, 3, 5, 2),
    ("produce",       22,  0, 4, 14, 4),
    ("cashier",       28,  0, 4, 18, 6),
    ("replenishment", 20,  0, 3, 13, 4),
    ("all",            8,  0, 0, 0, 8),
]

NON_PROF_TASKS = {
    ac: [t for t in AREA_TASKS if t["area_code"] == ac and not t["is_professional"]]
    for ac in AREA_CODES
}
PROF_TASKS = {
    ac: [t for t in AREA_TASKS if t["area_code"] == ac and t["is_professional"]]
    for ac in AREA_CODES
}

def gen_name(seed, style):
    surname = SURNAMES[seed % len(SURNAMES)]
    if style == "lao":
        return f"老{surname}"
    if style == "xiao":
        return f"小{surname}"
    r = (seed * 7 + 13) % 100
    if r < 10:
        return f"老{surname}"
    elif r < 25:
        return f"小{surname}"
    else:
        given = random.choice(GIVEN_MALE + GIVEN_MALE_2 + GIVEN_FEMALE + GIVEN_FEMALE_2)
        return f"{surname}{given}"

def level_order(lv):
    return {"S": 4, "A": 3, "B": 2, "C": 1}.get(lv, 0)

def pick_level(seed, force_high=False):
    if force_high:
        return ["S","S","A","A","A"][seed % 5]
    r = (seed * 3 + 7) % 100
    if r < 5: return "S"
    if r < 20: return "A"
    if r < 80: return "B"
    return "C"

employees = []
employee_skills = []
emp_id = 0
name_seed = 0

for area_code, total, pc, rc, mc, fc in PLAN:
    types = (["professional"]*pc + ["regional"]*rc + ["mixed"]*mc + ["floating"]*fc)
    random.shuffle(types)
    for i in range(total):
        emp_id += 1
        name_seed += 1
        t = types[i]
        prof = t == "professional"
        main = area_code if area_code != "all" else random.choice(AREA_CODES)
        limit = 40 if t == "professional" else random.choice([36, 40] if t != "floating" else [28, 32, 36])
        name = gen_name(name_seed, "lao" if (prof or t == "regional") else ("xiao" if t == "floating" and name_seed % 3 == 0 else "auto"))

        eid = f"emp_{emp_id:03d}"
        employees.append({
            "id": eid, "name": name, "main_area": main,
            "employee_type": t, "weekly_hours_limit": limit,
            "can_mixed": 1 if t in ("mixed", "floating") else 0, "is_active": 1,
        })

        skills = []
        # 本区域任务
        if prof:
            for tk in PROF_TASKS.get(area_code, []):
                skills.append((eid, tk["task_code"], pick_level(name_seed + emp_id, True), round(random.uniform(0.85, 1.0), 2)))
            for tk in NON_PROF_TASKS.get(area_code, []):
                lv = pick_level(name_seed + emp_id + 1)
                if lv in ("S","A","B"):
                    skills.append((eid, tk["task_code"], lv, round(random.uniform(0.7, 0.95), 2)))
        elif area_code == "all":
            for ac in AREA_CODES:
                tasks = NON_PROF_TASKS[ac][:random.randint(1, 3)]
                for tk in tasks:
                    lv = pick_level(name_seed + emp_id + hash(tk["task_code"]) % 100)
                    if lv in ("S","A","B"):
                        skills.append((eid, tk["task_code"], lv, round(random.uniform(0.5, 0.9), 2)))
        else:
            for tk in NON_PROF_TASKS.get(area_code, []):
                lv = pick_level(name_seed + emp_id)
                if lv in ("S","A","B") or random.random() < 0.3:
                    skills.append((eid, tk["task_code"], lv, round(random.uniform(0.6, 1.0), 2)))

        # 跨区技能（用于混排/流动）
        if t in ("mixed", "floating"):
            for oac in AREA_CODES:
                if oac == area_code or area_code == "all":
                    continue
                if random.random() < 0.4:
                    tasks = NON_PROF_TASKS[oac]
                    if tasks:
                        tk = random.choice(tasks)
                        lv = pick_level(name_seed + emp_id + hash(oac) % 100)
                        if lv in ("S","A","B"):
                            skills.append((eid, tk["task_code"], lv, round(random.uniform(0.3, 0.7), 2)))

        # 去重
        seen = {}
        for s in skills:
            k = (s[0], s[1])
            if k not in seen or level_order(s[2]) > level_order(seen[k][2]):
                seen[k] = s
        for s in seen.values():
            employee_skills.append({
                "id": f"esk_{len(employee_skills)+1:04d}",
                "employee_id": s[0], "task_code": s[1],
                "skill_level": s[2], "area_familiarity": s[3],
            })

with open(os.path.join(OUTDIR, "employees.json"), "w", encoding="utf-8") as f:
    json.dump(employees, f, ensure_ascii=False, indent=2)
print(f"✅ employees.json ({len(employees)} people)")

with open(os.path.join(OUTDIR, "employee_skills.json"), "w", encoding="utf-8") as f:
    json.dump(employee_skills, f, ensure_ascii=False, indent=2)
print(f"✅ employee_skills.json ({len(employee_skills)} records)")

# ============================================================
# 4. 历史数据 CSV（4 周历史 + 1 周 Demo 天气/节假日）
# ============================================================

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Demo 目标周：2026-07-13 (Mon) ~ 2026-07-19 (Sun)
DEMO_WEEK_START = date(2026, 7, 13)
# 历史数据：前 4 周 2026-06-15 ~ 2026-07-12
HIST_START = date(2026, 6, 15)
HIST_END = date(2026, 7, 12)

def daterange(start, end):
    for n in range((end - start).days + 1):
        yield start + timedelta(n)

# ---------- 4a. historical_sales.csv ----------
with open(os.path.join(OUTDIR, "historical_sales.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["date", "slot", "area_code", "sales_amount", "transaction_count"])
    for d in daterange(HIST_START, HIST_END):
        wd = d.weekday()
        base_factor = [1.0, 1.0, 1.0, 1.05, 1.2, 1.4, 1.3][wd]  # Mon→Sun factor
        for si, slot in enumerate(SLOTS):
            slot_factor = [0.8, 1.0, 0.7, 1.2][si]
            for ac in AREA_CODES:
                # 每区域销售差异
                area_base = {"aquatic": 1800, "meat": 2500, "produce": 1500, "cashier": 800, "replenishment": 600}[ac]
                # 时段偏好
                slot_ac_factor = {
                    ("aquatic", 0): 1.5, ("meat", 0): 1.4,
                    ("produce", 3): 1.4, ("cashier", 1): 1.3, ("cashier", 3): 1.4,
                    ("replenishment", 0): 1.3, ("replenishment", 3): 1.2,
                }
                saf = slot_ac_factor.get((ac, si), 1.0)
                noise = random.uniform(0.85, 1.15)
                amount = round(area_base * base_factor * slot_factor * saf * noise, 2)
                txn = max(1, round(amount / random.uniform(50, 90)))
                w.writerow([d.isoformat(), slot, ac, amount, txn])
print(f"✅ historical_sales.csv")

# ---------- 4b. historical_traffic.csv ----------
with open(os.path.join(OUTDIR, "historical_traffic.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["date", "slot", "customer_count"])
    for d in daterange(HIST_START, HIST_END):
        wd = d.weekday()
        base = [200, 200, 210, 220, 260, 350, 320][wd]
        for si, slot in enumerate(SLOTS):
            sf = [0.7, 1.0, 0.6, 1.3][si]
            noise = random.uniform(0.85, 1.15)
            w.writerow([d.isoformat(), slot, max(1, round(base * sf * noise))])
print(f"✅ historical_traffic.csv")

# ---------- 4c. online_orders.csv ----------
with open(os.path.join(OUTDIR, "online_orders.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["date", "slot", "order_count", "picking_count"])
    for d in daterange(HIST_START, HIST_END):
        wd = d.weekday()
        base = [25, 25, 28, 30, 40, 55, 50][wd]
        for si, slot in enumerate(SLOTS):
            sf = [0.5, 0.8, 0.7, 1.5][si]
            noise = random.uniform(0.85, 1.15)
            orders = max(1, round(base * sf * noise))
            picking = max(1, round(orders * random.uniform(0.7, 0.95)))
            w.writerow([d.isoformat(), slot, orders, picking])
print(f"✅ online_orders.csv")

# ---------- 4d. holidays.csv ----------
HOLIDAYS = [
    # 历史期间的节日
    ("2026-06-20", "周末", "weekend", 1),
    ("2026-06-21", "周末", "weekend", 1),
    ("2026-06-27", "周末", "weekend", 1),
    ("2026-06-28", "周末", "weekend", 1),
    ("2026-07-04", "周末", "weekend", 1),
    ("2026-07-05", "周末", "weekend", 1),
    ("2026-07-11", "周末", "weekend", 1),
    ("2026-07-12", "周末", "weekend", 1),
    # Demo 周的周末
    ("2026-07-18", "周末", "weekend", 1),
    ("2026-07-19", "周末", "weekend", 1),
]
with open(os.path.join(OUTDIR, "holidays.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["date", "holiday_name", "holiday_type", "is_weekend"])
    for h in HOLIDAYS:
        w.writerow(h)
print(f"✅ holidays.csv")

# ---------- 4e. weather.csv ----------
# Demo 周天气：周五降雨，其他晴/多云
DEMO_WEATHER = {
    date(2026, 7, 13): ("cloudy", 28, 0, 2),   # Mon
    date(2026, 7, 14): ("cloudy", 29, 0, 2),   # Tue
    date(2026, 7, 15): ("sunny",  31, 0, 1),   # Wed
    date(2026, 7, 16): ("sunny",  32, 0, 1),   # Thu
    date(2026, 7, 17): ("rainy",  26, 3, 2),   # Fri ← 降雨
    date(2026, 7, 18): ("cloudy", 27, 0, 2),   # Sat
    date(2026, 7, 19): ("sunny",  30, 0, 1),   # Sun
}

with open(os.path.join(OUTDIR, "weather.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["date", "slot", "weather_type", "temperature", "rain_level", "wind_level"])
    for d in daterange(HIST_START, HIST_END):
        # 历史天气按季节规律随机生成（夏季）
        wd = d.weekday()
        wt = random.choices(["sunny", "cloudy", "rainy"], weights=[5, 3, 1])[0]
        temp = random.randint(24, 33)
        rain = random.randint(0, 1) if wt == "rainy" else 0
        if wt == "rainy":
            rain = random.randint(1, 4)
        wind = random.randint(1, 3)
        for slot in SLOTS:
            w.writerow([d.isoformat(), slot, wt, temp, rain, wind])
    # Demo 周
    for d in daterange(DEMO_WEEK_START, date(2026, 7, 19)):
        wt_info = DEMO_WEATHER.get(d, ("sunny", 28, 0, 1))
        wt, temp, rain, wind = wt_info
        for slot in SLOTS:
            w.writerow([d.isoformat(), slot, wt, temp, rain, wind])
print(f"✅ weather.csv")

# ============================================================
# 统计汇总
# ============================================================
from collections import Counter
tc = Counter(e["employee_type"] for e in employees)
ac = Counter(e["main_area"] for e in employees)
print(f"\n--- Complete ---")
print(f"Employees: {len(employees)} (pro={tc['professional']}, reg={tc['regional']}, mixed={tc['mixed']}, float={tc['floating']})")
print(f"By area: {dict(ac)}")
print(f"Skills: {len(employee_skills)}")
print(f"\nAll files in {OUTDIR}:")
for fn in sorted(os.listdir(OUTDIR)):
    sz = os.path.getsize(os.path.join(OUTDIR, fn))
    print(f"  {fn:40s} {sz:>8,} bytes")
