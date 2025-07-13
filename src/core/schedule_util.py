from dataclasses import dataclass, field
from typing import Any, Dict, List, Set
import json

COURSE_FILE = "data\\course.json"
SCHEDULE_FILE = "data\\schedule.json"


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
    priority: int = field(default=9)  # 优先级,缺省为9

    def __hash__(self):
        return id.__hash__()


class CourseScheduler:

    def __init__(self, *, course_file: str = COURSE_FILE):
        with open(course_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.courses: Dict[str, Course] = {}
        self.all_required = 0
        for entry in data:
            offerings = [Offering(**off) for off in entry.get('offerings', [])]
            priority = entry.get('priority', 9)  # 默认优先级9
            course = Course(id=entry['id'],
                            name=entry['name'],
                            credit=entry['credit'],
                            semester=entry['semester'],
                            required=entry['required'],
                            prerequisites=entry.get('prerequisites', []),
                            offerings=offerings,
                            priority=priority)
            self.courses[course.id] = course
            self.all_required += 1 if course.required == "Compulsory" else 0
        # 全局禁排时间位图（7天,每天13节课）:contentReference[oaicite:2]{index=2}。0表示不禁排。
        self.forbidden_times = [0] * 7
        for course in self.courses.values():
            self._check_course_priority(course)

    def schedule_courses(self,
                         min_credits: int,
                         course_lower_limit: int = 20,
                         *,
                         schedule_file: str = SCHEDULE_FILE,
                         enable_required: bool = False,
                         credit_limit_per_sem: int = 5000):
        """生成满足至少 min_credits 的选课方案,并输出到 schedule.json。"""
        completed: Set[str] = set()  # 已修课程ID
        credit_accum = 0  # credit accummulation
        semester_idx = 0  # 学期计数,从0开始,偶数秋季、奇数春季
        sel_required = 0  # 已选必修课计数
        schedule = []

        # 按优先级（升序）和学分（降序）预排序课程,方便每学期选课时依此选择
        sorted_courses = sorted(self.courses.values(),
                                key=lambda c:
                                (0 if enable_required and c.required ==
                                 "Compulsory" else 1, c.priority, -c.credit))

        while (semester_idx < 8
               and (not enable_required or sel_required < self.all_required)):
            credit_this_sem = 0
            # 当前学期季节
            current_season = "Autumn" if semester_idx % 2 == 0 else "Spring"
            taken_id_this_sem = []  # 本学期选中的课程的id
            taken_this_sem = []  # 本学期选中的课程Offering

            # 遍历所有课程,选择满足条件的课程
            for course in sorted_courses:
                if ((len(taken_id_this_sem) > course_lower_limit
                     and (credit_this_sem > min_credits // 6))):
                    break
                if course.id in completed:
                    continue
                if course.semester != current_season:
                    continue  # 仅当课程在当前学期开设
                # 检查前置课程是否都已完成
                if any(prereq not in completed or prereq in taken_id_this_sem
                       for prereq in course.prerequisites):
                    continue
                # 检查本学期是否存在学分剩余
                if credit_this_sem + course.credit > credit_limit_per_sem:
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
                    taken_id_this_sem.append(course.id)
                    taken_this_sem.append(chosen_offering)
                    completed.add(course.id)
                    credit_accum += course.credit
                    credit_this_sem += course.credit
                    # 记录排课结果：课程ID、所选班级ID、学期编号
                    schedule.append({
                        "class_id": chosen_offering.id,
                        "course_id": course.id,
                        "semester": semester_idx
                    })
                    if credit_accum >= min_credits:
                        break
            semester_idx += 1

        # 对未被选中的课程,写入空选信息（semester=-1, class_id=""）
        for course in sorted_courses:
            if course.id not in completed:
                schedule.append({
                    "class_id": "",
                    "course_id": course.id,
                    "semester": -1
                })

        # 输出到 schedule.json（格式参见要求:contentReference[oaicite:7]{index=7}）
        with open(schedule_file, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)

    def set_priority(self, course_id: str, priority: int):
        """设置课程的优先级（缺省为9）。"""
        if self.courses.get(course_id, None) is not None:
            primal: int = self.courses[course_id].priority
            self.courses[course_id].priority = priority
            self._check_course_priority(self.courses[course_id])
            return primal
        return -1

    def set_forbidden_times(self, forbidden: List[int]):
        """设置每周7天的禁排时间段（位图）,默认全0表示不限排。"""
        if len(forbidden) == 7:
            self.forbidden_times = forbidden[:]

    def _check_course_priority(self, course: Course):
        """将先修课的优先级上调"""
        prereqs: List[str] = course.prerequisites
        priority: int = course.priority - 1 or 1
        for prereq in prereqs:
            if self.courses.get(prereq, None) is None:
                continue
            if (self.courses[prereq].priority > priority):
                self.courses[prereq].priority = priority
                self._check_course_priority(self.courses[prereq])

    # def add_course(self, course_data: dict):
    #     """新增课程,course_data 与 JSON 中课程结构一致。"""
    #     if course_data['id'] in self.courses:
    #         raise ValueError("课程已存在")
    #     offerings = [
    #         Offering(**off) for off in course_data.get('offerings', [])
    #     ]
    #     priority = course_data.get('priority', 9)
    #     course = Course(id=course_data['id'],
    #                     name=course_data['name'],
    #                     credit=course_data['credit'],
    #                     semester=course_data['semester'],
    #                     required=course_data['required'],
    #                     prerequisites=course_data.get('prerequisites', []),
    #                     offerings=offerings,
    #                     priority=priority)
    #     self.courses[course.id] = course

    # def remove_course(self, course_id: str):
    #     """删除指定 ID 的课程。"""
    #     if course_id in self.courses:
    #         del self.courses[course_id]

    # def update_course(self, course_id: str, **fields):
    #     """更新课程的某些字段,如学分、优先级等。"""
    #     course = self.courses.get(course_id)
    #     if not course:
    #         return
    #     for key, value in fields.items():
    #         if hasattr(course, key):
    #             setattr(course, key, value)

    # def get_course(self, course_id: str) -> Course:
    #     """查询并返回指定 ID 的课程对象。"""
    #     return self.courses.get(course_id)


def is_time_conflict(times1: List[int], times2: List[int]) -> bool:
    """判断两门课程每周7天上课时间是否有冲突。"""
    return any((a & b) != 0 for a, b in zip(times1, times2))


@dataclass
class Schedule:
    id: str
    name: str
    class_id: str
    teacher: str
    times: List[int]
    weeks: int
    required: str


class ScheduleVisualizer:

    def __init__(self,
                 *,
                 course_file: str = COURSE_FILE,
                 schedule_file: str = SCHEDULE_FILE,
                 cs: CourseScheduler = None):
        if cs is None:
            self.cs: CourseScheduler = CourseScheduler(course_file=course_file)
        else:
            self.cs = cs

        # 每一slot是一个semester的课程
        self.completed: Dict[str, int] = dict()
        self.schedules: List[Dict[str, Schedule]] = self.load_schedule(
            schedule_file=schedule_file)

    def load_schedule(self, *, schedule_file: str = SCHEDULE_FILE):
        """Load Schedule from File"""
        schedules: List[Dict[str, Schedule]] = [dict() for _ in range(9)]
        self.completed.clear()

        with open(schedule_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for entry in data:
            course_id: str = entry["course_id"]
            class_id: str = entry["class_id"]
            semester: int = entry["semester"]
            course_info: Course = self.cs.courses[course_id]
            if semester == -1:
                offering_info: Offering = None
            else:
                self.completed[course_id] = semester
                offering_info: Offering = [
                    offering for offering in course_info.offerings
                    if offering.id == class_id
                ][0]
            if offering_info is None:
                schedules[semester][course_id] = Schedule(
                    course_id, course_info.name, class_id, None, None, 0,
                    course_info.required)
                continue
            schedules[semester][course_id] = Schedule(
                course_id, course_info.name, class_id, offering_info.teacher,
                offering_info.times, offering_info.weeks, course_info.required)
        self.schedules = schedules[:]
        return schedules

    def dump_schedule(self, *, schedule_file: str = SCHEDULE_FILE):
        """Dump cached schedule to schedule.json"""
        schedules: List[Dict[str, Any]] = list()
        for semester_idx, this_semester in enumerate(self.schedules):
            for course in this_semester.values():
                if semester_idx == 8:
                    real_idx = -1
                else:
                    real_idx = semester_idx
                schedules.append({
                    "class_id": course.class_id,
                    "course_id": course.id,
                    "semester": real_idx
                })
        # 输出到 schedule.json（格式参见要求:contentReference[oaicite:7]{index=7}）
        with open(schedule_file, 'w', encoding='utf-8') as f:
            json.dump(schedules, f, ensure_ascii=False, indent=2)

    def get_course_info(self,
                        *,
                        course_keyword: str = "") -> Dict[Course, Any]:
        """按照id或课程名称或教师名称查课"""
        if len(course_keyword.strip()) == 0:
            return {}

        result: Dict[Course, bool] = {}
        for course in self.cs.courses.values():
            if course_keyword in course.id:
                result[course] = (course in self.completed)
            elif course_keyword in course.name:
                result[course] = (course in self.completed)
            elif any(course_keyword in offer.teacher
                     for offer in course.offerings):
                result[course] = (course in self.completed)
        return result

    def add_course(self, *, course_id: str = "", offer_id: str = "") -> int:
        """尝试按照课程id(和教学班id)参与课程"""
        if len(course_id) == 0 or len(offer_id) == 0:
            return 1
        course = self.cs.courses.get(course_id, None)
        if course is None:
            return 1
        for offer in course.offerings:
            if offer_id == offer.id:
                break
        else:
            return 1

        if course.prerequisites:
            semester_idx: int = max(
                self.completed.get(prereq, 8)
                for prereq in course.prerequisites)
        else:
            semester_idx = -1
        while semester_idx < 7:
            semester_idx += 1
            season = "Autumn" if semester_idx % 2 == 0 else "Spring"
            if course.semester != season:
                continue
            if any(
                    is_time_conflict(offer.times, primcourse.times)
                    for primcourse in self.schedules[semester_idx].values()):
                continue

            self._add_schedule(course=course,
                               offer=offer,
                               semester=semester_idx)
            self._del_schedule(course_id=course.id, semester=-1)
            self.completed[course_id] = semester_idx
            return 0
        return 2

    def remove_course(self, *, course_id: str = "") -> int:
        """尝试按照课程id删除课程"""
        if len(course_id) == 0:
            return 1
        course = self.cs.courses.get(course_id, None)
        if course is None:
            return 1

        semester_idx: int = self.completed.get(course.id, -1)

        if semester_idx == -1:
            return 0

        self._add_schedule(course=course,
                           offer=Offering(id="",
                                          teacher="",
                                          times=[0 for _ in range(7)],
                                          weeks=0),
                           semester=-1)
        self._del_schedule(course_id=course.id, semester=semester_idx)
        del self.completed[course_id]
        return 0

    def update_course(self, *, course_id: str = "", offer_id: str = "") -> int:
        """更改课程的教学班(根据课程id和教学班id)"""
        if len(course_id) == 0 or len(offer_id) == 0:
            return 1
        course = self.cs.courses.get(course_id, None)
        if course is None:
            return 1
        semester_cache: int = self.completed.get(course.id, -1)
        if semester_cache == -1:
            return 1
        course_cache: Schedule = self.schedules[semester_cache][course.id]
        if course_cache.class_id == offer_id:
            return 0
        status: int = self.remove_course(course_id=course.id)
        assert status == 0, "Strange Error"
        status = self.add_course(course_id=course.id, offer_id=offer_id)
        if status != 0:
            self.add_course(course_id=course.id,
                            offer_id=course_cache.class_id)
            return 2
        return 0

    def set_priority(self, priority: int = 9, *, course_id: str = "") -> int:
        """设置/查询优先级

        Args:
            priority: non-zero: set to priority;
                      zero: query;
                      Defaults to 9.

        Returns:
            int: primal priority
        """
        if len(course_id) == 0:
            return -1
        course = self.cs.courses.get(course_id, None)
        if course is None:
            return -1
        if priority == 0:
            return self.cs.courses[course_id].priority
        elif priority < 0:
            priority = 1
        primal: int = self.cs.set_priority(course_id=course_id,
                                           priority=priority)
        return primal

    def _add_schedule(self, course: Course, offer: Offering, semester: int):
        self.schedules[semester][course.id] = Schedule(
            id=course.id,
            name=course.name,
            class_id=offer.id,
            teacher=offer.teacher,
            times=offer.times[:],
            weeks=offer.weeks,
            required=course.required)

    def _del_schedule(self, course_id: str, semester: int):
        if course_id in self.schedules[semester]:
            del self.schedules[semester][course_id]

    def get_schedule_table(self, *, semester: int) -> List[List[Schedule]]:
        """获取某一学期的课程表"""
        schedules_this_sem: Dict[Schedule] = self.schedules[semester]
        schedule_table: List[List[Schedule]] = [[None for _ in range(13)]
                                                for _i in range(7)]

        for schedule in schedules_this_sem.values():
            for day in range(7):
                time_day = schedule.times[day]
                time_specifier = 0
                while time_specifier < 14:
                    if time_day & (2**time_specifier):
                        schedule_table[day][time_specifier] = schedule
                    time_specifier += 1

        return schedule_table


if __name__ == '__main__':
    cs: CourseScheduler = CourseScheduler(course_file=COURSE_FILE)
    cs.set_forbidden_times([0, 0, 0, 0, 0, 0, 0])
    cs.schedule_courses(schedule_file="data\\schedule.json",
                        min_credits=200,
                        course_lower_limit=1000,
                        enable_required=True,
                        credit_limit_per_sem=5000)
    sv: ScheduleVisualizer = ScheduleVisualizer(cs=cs)
    sv.get_schedule_table(semester=2)
