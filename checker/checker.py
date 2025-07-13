import json
import sys
# from pathlib import Path
from itertools import combinations
from typing import Dict

COURSE_FILE = "data\\course.json"
SCHEDULE_FILE = "data\\schedule.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class ClassInfo:
    __slots__ = ("times", "weeks")

    def __init__(self, times, weeks):
        self.times = times
        self.weeks = weeks


class CourseInfo:
    __slots__ = ("name", "credit", "prereq", "required", "classes")

    def __init__(self):
        self.name = ""
        self.credit = 0
        self.prereq = []
        self.required = ""
        self.classes = {}


def wrap(cid):
    name = course_map.get(cid, CourseInfo()).name
    return f"{cid}（{name}）" if name else cid


def overlap(a: ClassInfo, b: ClassInfo) -> bool:
    if a.weeks & b.weeks == 0:
        return False
    return any(ta & tb for ta, tb in zip(a.times, b.times))


def main(*,
         course_file: str = COURSE_FILE,
         schedule_file: str = SCHEDULE_FILE):
    try:
        courses_raw = load_json(course_file)
        schedule_raw = load_json(schedule_file)
    except FileNotFoundError as e:
        sys.exit(f"文件缺失: {e.filename}")

    all_required: int = 0
    sel_required: int = 0

    courses: Dict[str, CourseInfo] = {}
    for course_raw in courses_raw:
        course_id = course_raw.get("course_id") or course_raw.get("id")
        if not course_id:
            continue
        course_info = CourseInfo()
        course_info.name = course_raw.get("course_name") or course_raw.get(
            "name", "")
        course_info.credit = int(course_raw.get("credit", 0))
        course_info.prereq = list(course_raw.get("prerequisites", []))
        course_info.required = course_raw.get("required", "")

        all_required += 1 if course_info.required == "Compulsory" else 0

        for off in course_raw.get("offerings", []):
            cls_id = off.get("class_id") or off.get("id")
            if not cls_id:
                continue
            times = [int(x) for x in off.get("times", [0] * 7)]
            weeks = int(off.get("weeks", 0))
            course_info.classes[cls_id] = ClassInfo(times, weeks)

        courses[course_id] = course_info

    selecteds = {}
    for e in schedule_raw:
        course_id = e.get("course_id") or e.get("id")
        if not course_id:
            continue
        semester = int(e.get("semester", -1))
        cls_id = e.get("class_id") or e.get("class") or ""
        selecteds[course_id] = (semester, cls_id)
        if courses.get(course_id, None) is not None:
            if semester >= 0:
                sel_required += 1 if courses[
                    course_id].required == "Compulsory" else 0

    errors = []
    total_credit = 0

    for course_id, (sem, cls) in selecteds.items():
        if sem < 0:
            continue
        if course_id not in courses:
            errors.append(f"课程 {course_id} 不存在于 {COURSE_FILE}")
            continue
        if cls not in courses[course_id].classes:
            errors.append(f"课程 {wrap(course_id)} 的班号 {cls} 不在 offerings 中")

    for course_id, (sem, _) in selecteds.items():
        if sem < 0:
            continue
        for pre in courses[course_id].prereq:
            p_sem = selecteds.get(pre, (-1, ""))[0]
            if p_sem < 0:
                errors.append(f"课程 {wrap(course_id)} 缺少先修课 {wrap(pre)}")
            elif p_sem >= sem:
                errors.append(f"课程 {wrap(course_id)} 的先修课 {wrap(pre)} "
                              f"学期 {p_sem} 需早于本课学期 {sem}")

    sem_table = {}
    for course_id, (sem, cls) in selecteds.items():
        if sem < 0 or course_id not in courses:
            continue
        ci = courses[course_id].classes.get(cls)
        if not ci:
            continue
        sem_table.setdefault(sem, []).append((course_id, ci))

    for sem, lst in sem_table.items():
        for (cid1, c1), (cid2, c2) in combinations(lst, 2):
            if overlap(c1, c2):
                errors.append(f"学期 {sem} 内 {wrap(cid1)} 与 {wrap(cid2)} 时间冲突")

    for course_id, (sem, _) in selecteds.items():
        if sem >= 0 and course_id in courses:
            total_credit += courses[course_id].credit

    if errors:
        print("✘ 发现以下问题：")
        for e in errors:
            print("  -", e)
        print(f"总学分: {total_credit}")
        sys.exit(1)
    else:
        print("✔ 选课方案合法")
        print(f"总学分: {total_credit}")
    print(f"选中必修课: {sel_required}/{all_required}"
          f"({sel_required*1000//all_required/10}%)")


if __name__ == '__main__':
    main()
