from dataclasses import dataclass, field
from typing import List, Dict
import json


@dataclass
class Offering:
    id: str
    teacher: str
    times: List[int]
    # 每周7天上课时间位图（13位二进制表示一天内13节课）:
    # contentReference[oaicite:1]{index=1}
    weeks: int


@dataclass
class Course:
    id: str
    name: str
    credit: int
    semester: str  # 开课学期："Spring" 或 "Autumn"
    required: str  # "Compulsory" 或 "Elective"
    prerequisites: List[str]
    offerings: List[Offering]
    priority: int = field(default=5)  # 优先级，缺省为5


class CourseScheduler:

    def __init__(self, course_file: str):
        with open(course_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.courses: Dict[str, Course] = {}
        for entry in data:
            offerings = [Offering(**off) for off in entry.get('offerings', [])]
            priority = entry.get('priority', 5)  # 默认优先级5
            course = Course(id=entry['id'],
                            name=entry['name'],
                            credit=entry['credit'],
                            semester=entry['semester'],
                            required=entry['required'],
                            prerequisites=entry.get('prerequisites', []),
                            offerings=offerings,
                            priority=priority)
            self.courses[course.id] = course
        # 全局禁排时间位图（7天，每天13节课）:contentReference[oaicite:2]{index=2}。0表示不禁排。
        self.forbidden_times = [0] * 7

    def schedule_courses(self, min_credits: int, output_file: str):
        """生成满足至少 min_credits 的选课方案（最少学期），并输出到 schedule.json。"""
        completed = set()  # 已修课程ID
        credit_accum = 0  # credit accummulation
        semester_idx = 0  # 学期计数，从0开始，偶数秋季、奇数春季
        schedule = []

        # 按优先级（升序）和学分（降序）预排序课程，方便每学期选课时依此选择
        sorted_courses = sorted(self.courses.values(),
                                key=lambda c: (c.priority, -c.credit))

        while credit_accum < min_credits and semester_idx < 8:
            # 当前学期季节
            current_season = "Autumn" if semester_idx % 2 == 0 else "Spring"
            taken_this_sem = []  # 本学期选中的课程Offering

            # 遍历所有课程，选择满足条件的课程
            for course in sorted_courses:
                if course.id in completed:
                    continue
                if course.semester != current_season:
                    continue  # 仅当课程在当前学期开设
                # 检查前置课程是否都已完成
                if any(prereq not in completed
                       for prereq in course.prerequisites):
                    continue
                # 检查是否存在一个班级满足时间条件
                chosen_offering = None
                for off in course.offerings:
                    if is_time_conflict(off.times, self.forbidden_times):
                        continue  # 与禁排时间冲突
                    if any(
                            is_time_conflict(off.times, other.times)
                            for other in taken_this_sem):
                        continue  # 与本学期已选课程冲突
                    chosen_offering = off
                    break
                if chosen_offering:
                    # 选入本学期
                    taken_this_sem.append(chosen_offering)
                    completed.add(course.id)
                    credit_accum += course.credit
                    # 记录排课结果：课程ID、所选班级ID、学期编号
                    schedule.append({
                        "class_id": chosen_offering.id,
                        "course_id": course.id,
                        "semester": semester_idx
                    })
                    if credit_accum >= min_credits:
                        break
            semester_idx += 1

        # 对未被选中的课程，写入空选信息（semester=-1, class_id=""）
        for course in sorted_courses:
            if course.id not in completed:
                schedule.append({
                    "class_id": "",
                    "course_id": course.id,
                    "semester": -1
                })

        # 输出到 schedule.json（格式参见要求:contentReference[oaicite:7]{index=7}）
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)

    def add_course(self, course_data: dict):
        """新增课程，course_data 与 JSON 中课程结构一致。"""
        if course_data['id'] in self.courses:
            raise ValueError("课程已存在")
        offerings = [
            Offering(**off) for off in course_data.get('offerings', [])
        ]
        priority = course_data.get('priority', 5)
        course = Course(id=course_data['id'],
                        name=course_data['name'],
                        credit=course_data['credit'],
                        semester=course_data['semester'],
                        required=course_data['required'],
                        prerequisites=course_data.get('prerequisites', []),
                        offerings=offerings,
                        priority=priority)
        self.courses[course.id] = course

    def remove_course(self, course_id: str):
        """删除指定 ID 的课程。"""
        if course_id in self.courses:
            del self.courses[course_id]

    def update_course(self, course_id: str, **fields):
        """更新课程的某些字段，如学分、优先级等。"""
        course = self.courses.get(course_id)
        if not course:
            return
        for key, value in fields.items():
            if hasattr(course, key):
                setattr(course, key, value)

    def get_course(self, course_id: str) -> Course:
        """查询并返回指定 ID 的课程对象。"""
        return self.courses.get(course_id)

    def set_priority(self, course_id: str, priority: int):
        """设置课程的优先级（缺省为5）。"""
        course = self.get_course(course_id)
        if course:
            course.priority = priority

    def set_forbidden_times(self, forbidden: List[int]):
        """设置每周7天的禁排时间段（位图），默认全0表示不限排。"""
        if len(forbidden) == 7:
            self.forbidden_times = forbidden


def is_time_conflict(times1: List[int], times2: List[int]) -> bool:
    """判断两门课程每周7天上课时间是否有冲突。"""
    return any((a & b) != 0 for a, b in zip(times1, times2))


if __name__ == '__main__':
    cs: CourseScheduler = CourseScheduler(course_file="data\\course.json")
    cs.schedule_courses(min_credits=100, output_file="data\\schedule.json")
