__author__ = 'ShiningZec'

from .cli_doc import (
    MDOC,
    SEP_DOC,
    SEP_EQUAL,
    SEP_MINUS,
    TABLE_TITLE
)
from src.core.schedule_util import (
    Course,
    CourseScheduler,
    Schedule,
    ScheduleVisualizer
)

from checker import checker

from dataclasses import dataclass
from typing import Any, Dict, List

COURSE_FILE = "data\\course.json"
SCHEDULE_FILE = "data\\schedule.json"
DEFAULT_MIN_CREDIT = 100
DEFAULT_TIMELIST = [0 for _ in range(7)]


@dataclass
class Config:
    course_file: str = COURSE_FILE
    schedule_file: str = SCHEDULE_FILE
    forbid_time: List[int] = None
    course_lower_limit: int = 30
    credit_limit: int = 5000
    enable_required: bool = False
    enable_forbid_time: bool = False
    enable_limit_credit: bool = False


class CourseSchedulerCli:

    def __init__(self,
                 *,
                 course_file: str = COURSE_FILE,
                 schedule_file: str = SCHEDULE_FILE,
                 cs: CourseScheduler = None):
        self.config: Config = Config(course_file=course_file,
                                     schedule_file=schedule_file,
                                     forbid_time=DEFAULT_TIMELIST[:])
        self.course_file = course_file
        self.schedule_file = schedule_file
        if cs is None:
            self.cs: CourseScheduler = CourseScheduler(
                course_file=self.course_file)
        else:
            self.cs = cs
        self.sv: ScheduleVisualizer = ScheduleVisualizer(
            course_file=self.config.course_file,
            schedule_file=self.config.schedule_file,
            cs=cs
        )

    def mainloop(self):
        """Main Loop"""
        try:
            print(MDOC[0])
            while (1):  # Main Menu
                print(MDOC[1])
                buff: str = input(">> ")
                if not buff:
                    continue
                choice: str = buff.strip()[0]

                if choice == '1':  # Init Menu
                    print(MDOC[2])
                    self._submenu_init()

                elif choice == '2':  # Operate Menu
                    print(MDOC[3])
                    self._submenu_oper()

                elif choice == '3':  # Modify Menu
                    print(MDOC[4])
                    self._submenu_mod()

                elif choice == '4':  # Config Menu
                    self._submenu_config()

                elif choice == '0':
                    break
                elif choice == '*':
                    continue
                else:
                    print(f"Bad Choice Input: {choice}")
            print(MDOC[-1])
        except KeyboardInterrupt:
            print()
            print(MDOC[-1])
        print()

    def _submenu_init(self):
        while (1):
            buff: str = input(">> ")
            if not buff:
                continue
            choice: str = buff.strip()[0]
            if choice == '1' or choice == '2':
                try:
                    self.init_cs()
                    print("Success.")
                except Exception:
                    print("Failing: Lack of Config.")
            elif choice == '0':
                break
            elif choice == '*':
                print(MDOC[2])
                continue
            else:
                print(f"Bad Choice Input: {choice}")
            print(SEP_DOC)

    def _submenu_oper(self):
        while (1):
            buff: str = input(">> ")
            if not buff:
                continue
            choice: str = buff.strip()[0]
            if choice == '1':
                buff: str = input(
                    "Input min_credits(default: 100):\n>> ")
                if buff:
                    try:
                        min_credit = int(buff.strip())
                    except Exception:
                        min_credit = DEFAULT_MIN_CREDIT
                else:
                    min_credit = DEFAULT_MIN_CREDIT
                try:
                    config = self.config
                    self.run_cs(min_credit, config=config)
                    print(f"Success: output at {config.schedule_file}")
                except Exception:
                    print("Failing: Can not generate schedule.")
            elif choice == '2':
                buff: str = input(
                    "Input semester-week to visualize(default: 1-1):\n>> "
                )
                if buff:
                    try:
                        parser = buff.strip().split('-')
                        if len(parser) < 1:
                            week_idx: int = 0
                            semester_idx: int = 0
                        elif len(parser) < 2:
                            week_idx = 0
                            semester_idx = int(parser[0]) - 1
                        else:
                            week_idx = int(parser[1]) - 1
                            semester_idx = int(parser[0]) - 1
                        if semester_idx < 0 or semester_idx > 7:
                            semester_idx = 0
                        if week_idx < 0 or week_idx > 20:
                            week_idx = 1
                    except Exception:
                        week_idx = 1
                        semester_idx = 0
                else:
                    week_idx = 1
                    semester_idx = 0
                try:
                    self._visual_cli(semester_idx, weeks=week_idx)
                    print("Success.")
                except Exception:
                    print("Failing: Can not visualize schedule.")
                pass
            elif choice == '3':
                config: Config = self.config
                self.call_checker(config=config)
                print("Call Success")
            elif choice == '0':
                break
            elif choice == '*':
                print(MDOC[3])
                continue
            else:
                print(f"Bad Choice Input: {choice}")
            print(SEP_DOC)

    def _submenu_mod(self):
        while (1):
            buff: str = input(">> ")
            if not buff:
                continue
            choice: str = buff.strip()[0]
            modify_counter: int = 0
            schedule_file = self.config.schedule_file
            self.load_schedule(schedule_file=schedule_file)
            if choice == '1':
                buff: str = input("Kwd-search>> ")
                if not buff:
                    print("Canceled.")
                    print(SEP_DOC)
                    continue
                search_result = self.get_course_info(
                    course_keyword=buff.strip())
                print("Search Result:")
                for course in search_result:
                    print(f"[{course.id}]: {course.name}, "
                          f"{course.required} "
                          f"{"Attend" if search_result[course] else ""}")
                    for offer in course.offerings:
                        print(f"\t[{offer.id}]: Teacher: [{offer.teacher}], "
                              f"times: {offer.times}, weeks: [{offer.weeks}]")
                print("Search End.")
            elif choice == '2':
                buff: str = input("Course-id>> ")
                if not buff:
                    print("Canceled.")
                    print(SEP_DOC)
                    continue
                course_id = buff.strip()
                buff: str = input("Offer-id>> ")
                if not buff:
                    offer_id = "01"
                else:
                    offer_id = buff.strip()
                status: int = self.add_course(course_id=course_id,
                                              offer_id=offer_id)
                if status == 1:
                    print("Failing: Bad course_id or offer_id")
                elif status == 2:
                    print("Failing: Due to Time conflict or "
                          "not finished prerequired courses")
                elif status == 0:
                    print("Success.")
                else:
                    assert False, "Stupid"
            elif choice == '3':
                buff: str = input("Course-id>> ")
                if not buff:
                    print("Canceled.")
                    print(SEP_DOC)
                    continue
                course_id = buff.strip()
                status: int = self.remove_course(course_id=course_id)
                if status == 1:
                    print("Failing: Bad course_id")
                elif status == 0:
                    print("Success.")
                else:
                    assert False, "Stupid"
            elif choice == '4':
                buff: str = input("Course-id>> ")
                if not buff:
                    print("Canceled.")
                    print(SEP_DOC)
                    continue
                course_id = buff.strip()
                buff: str = input("Offer-id>> ")
                if not buff:
                    offer_id = "01"
                else:
                    offer_id = buff.strip()
                status: int = self.update_course(course_id=course_id,
                                                 offer_id=offer_id)
                if status == 1:
                    print("Failing: Bad course_id or offer_id, "
                          "or you will not ever attend it statusly.")
                elif status == 2:
                    print("Failing: Due to time conflict or "
                          "prerequired class not finished, "
                          "operation took back")
                elif status == 0:
                    print("Success.")
                else:
                    assert False, "Stupid"
            elif choice == '5':
                buff: str = input("Course-id>> ")
                if not buff:
                    print("Canceled.")
                    print(SEP_DOC)
                    continue
                course_id = buff.strip()
                buff: str = input("Priority-set-to>> ")
                if not buff:
                    priority: int = 0
                else:
                    try:
                        priority = int(buff.strip().split()[0])
                    except Exception:
                        priority = 0
                primal: int = self.set_priority(priority=priority,
                                                course_id=course_id)
                if primal == -1:
                    print("Failing: Bad course_id")
                    print(SEP_DOC)
                    continue
                if priority == 0:
                    print(f"Query: Current Priority of {course_id} "
                          f"is {primal}")
                else:
                    print(f"Updated: Priority of {course_id} "
                          f"was {primal} and is now set to "
                          f"{priority}")
            elif choice == '0':
                if modify_counter > 0:
                    self.sv.dump_schedule(schedule_file=schedule_file)
                break
            elif choice == '*':
                print(MDOC[4])
                continue
            else:
                print(f"Bad choice: {choice}")
            print(SEP_DOC)

    def _submenu_config(self):
        while (1):
            print(MDOC[5])
            buff: str = input(">> ")
            if not buff:
                continue
            choice: str = buff.strip()[0]
            if choice == '1':
                print(MDOC[6])
                self._submenu_set()
            elif choice == '2':
                print(MDOC[7])
                self._submenu_toggle()
            elif choice == '0':
                break
            elif choice == '*':
                continue
            else:
                print(f"Bad Choice Input: {choice}")
            print(SEP_DOC)

    def _submenu_set(self):
        while (1):
            buff: str = input(">> ")
            if not buff:
                continue
            choice: str = buff.strip()[0]
            if choice == '1':
                buff: str = input("Please input course file path "
                                  "(format: path\\to\\file):\n>> ")
                if not buff:
                    print("Cancelled from setting course file path")
                else:
                    self.config_set_attribute("course_file", buff.strip())
                    print("Successfully changed course "
                          f"file path to \n{self.config.course_file}")
            elif choice == '2':
                buff: str = input("Please input schedule file path "
                                  "(format: path\\to\\file):\n>> ")
                if not buff:
                    print("Cancelled from setting schedule file path")
                else:
                    self.config_set_attribute("schedule_file", buff.strip())
                    print("Successfully changed schedule "
                          f"file path to \n{self.config.schedule_file}")
            elif choice == '3':
                buff: str = input("Please input forbid time (format: "
                                  "7 integers split by space):\n>> ")
                if not buff:
                    print("Cancelled from setting forbid time")
                    print(SEP_DOC)
                    continue
                try:
                    timelist_str: List[str] = buff.strip().split(' ')[:7]
                    timelist = [int(item) for item in timelist_str]
                    while len(timelist) < 7:
                        timelist.append(0)
                    self.config_set_forbid_time(timelist)
                    print("Successfully changed forbid time "
                          f"to \n{self.config.forbid_time}")
                except Exception:
                    print("Failing: Unable to change forbid time")
            elif choice == '4':
                buff: str = input("Please input ClassPerSemLimit (format: "
                                  "1 integer):\n>> ")
                if not buff:
                    print("Cancelled from setting ClassPerSemLimit")
                    print(SEP_DOC)
                    continue
                try:
                    self.config_set_attribute("class_limit",
                                              int(buff.strip().split(' ')[0]))
                    print("Successfully changed ClassPerSemLimit "
                          f"to \n{self.config.course_lower_limit}")
                except Exception:
                    print("Failing: Unable to change ClassPerSemLimit")
            elif choice == '5':
                buff: str = input("Please input CreditPerSemLimit (format: "
                                  "1 integer):\n>> ")
                if not buff:
                    print("Cancelled from setting CreditPerSemLimit")
                    print(SEP_DOC)
                    continue
                try:
                    self.config_set_attribute("credit_limit",
                                              int(buff.strip().split(' ')[0]))
                    print("Successfully changed CreditPerSemLimit "
                          f"to \n{self.config.credit_limit}")
                except Exception:
                    print("Failing: Unable to change CreditPerSemLimit")
            elif choice == '0':
                break
            elif choice == '*':
                print(MDOC[6])
                continue
            else:
                print(f"Bad Choice: {choice}")
            print(SEP_DOC)

    def _submenu_toggle(self):
        while (1):
            buff: str = input(">> ")
            if not buff:
                continue
            choice: str = buff.strip()[0]
            if choice == '1':
                primal: bool = self.config_toggle("enable_required")
                print("Config Require was primally "
                      f"{"Enabled" if primal else "Disabled"}"
                      " and is now set to "
                      f"{"Disabled" if primal else "Enabled"}"
                      )
            elif choice == '2':
                primal: bool = self.config_toggle("enable_forbid_time")
                print("Config ForbidTime was primally "
                      f"{"Enabled" if primal else "Disabled"}"
                      " and is now set to "
                      f"{"Disabled" if primal else "Enabled"}"
                      )
            elif choice == '3':
                primal: bool = self.config_toggle("enable_limit_credit")
                print("Config LimitCreditPerSem was primally "
                      f"{"Enabled" if primal else "Disabled"}"
                      " and is now set to "
                      f"{"Disabled" if primal else "Enabled"}"
                      )
            elif choice == '0':
                break
            elif choice == '*':
                print(MDOC[7])
                continue
            else:
                print(f"Bad Choice: {choice}")
            print(SEP_DOC)

    def init_cs(self, *, config: Config = None):
        """init/reset Course Scheduler"""
        if config is None:
            config: Config = self.config
        self.cs: CourseScheduler = CourseScheduler(
            course_file=config.course_file)
        try:
            self.sv.load_schedule(schedule_file=config.schedule_file)
        except Exception:
            ...

    def run_cs(self, min_credit: int = 100, *, config: Config = None):
        """run/re-run Course Scheduler: will dump schedule.json"""
        if config is None:
            config = self.config
        if config.enable_forbid_time:
            self.cs.set_forbidden_times(config.forbid_time)
        else:
            self.cs.set_forbidden_times(DEFAULT_TIMELIST[:])
        self.cs.schedule_courses(
            min_credits=min_credit,
            course_lower_limit=config.course_lower_limit,
            schedule_file=config.schedule_file,
            enable_required=config.enable_required,
            credit_limit_per_sem=config.credit_limit
            if config.enable_limit_credit else 5000)
        self.sv.load_schedule(schedule_file=config.schedule_file)

    def get_schedule_table(self, semester: int) -> List[List[Schedule]]:
        """will return a schedule table of that semester."""
        return self.sv.get_schedule_table(semester=semester)

    def _visual_cli(self, semester: int, weeks: int = 1):
        schedule_table = self.get_schedule_table(semester)

        print(SEP_EQUAL)
        print(f"SEM {semester + 1}\nWeek {weeks + 1}", TABLE_TITLE, sep='')
        print(SEP_EQUAL)

        for i in range(len(schedule_table[0])):
            print(f"  {i + 1}\t ", end='')
            for j in range(len(schedule_table)):
                if schedule_table[j][i] is not None:
                    if schedule_table[j][i].weeks & (2 ** weeks) == 0:
                        print("[\t\t\t\t]", end='')
                        continue
                    name = schedule_table[j][i].name
                    if name in ("现代CAD技术（A）", "现代CAD技术（B）", "数学分析II",
                                "概率论与数理统计A"):
                        print(f"[    {name}\t\t]", end='')
                    elif name in ("数学分析I"):
                        print(f"[    {name}\t\t\t]", end='')
                    elif len(name) < 5:
                        print(f"[    {name}\t\t\t]", end='')
                    elif len(name) < 9:
                        print(f"[    {name}\t\t]", end='')
                    elif len(name) < 11:
                        print(f"[    {name}\t]", end='')
                    else:
                        print(
                            f"[    {name[0:8]}...{name[-2:]}\t]",
                            end='')
                else:
                    if j >= 5:
                        print("[\t\t]", end='')
                    else:
                        print("[\t\t\t\t]", end='')
            print("\n\t ", end='')
            for j in range(len(schedule_table)):
                if schedule_table[j][i] is not None:
                    if schedule_table[j][i].weeks & (2 ** weeks) == 0:
                        print("[\t\t\t\t]", end='')
                        continue
                    teacher = schedule_table[j][i].teacher
                    if len(teacher) < 5:
                        print(f"[     {teacher}\t\t\t]", end='')
                    else:
                        print(f"[     {teacher}\t\t]", end='')
                else:
                    if j >= 5:
                        print("[\t\t]", end='')
                    else:
                        print("[\t\t\t\t]", end='')
            print()
            if i == 4 or i == 9:
                print(SEP_MINUS)
        else:
            print(SEP_EQUAL)

    def call_checker(self, *, config: Config = None):
        """Call Checker.main() (with config)"""
        if config is None:
            config: Config = self.config
        checker.main(course_file=config.course_file,
                     schedule_file=config.schedule_file)

    def load_schedule(self, *, schedule_file: str = None):
        """Call load_schedule to update schedule"""
        if schedule_file is None:
            self.sv.load_schedule(schedule_file=self.schedule_file)
        else:
            self.sv.load_schedule(schedule_file=schedule_file)

    def dump_schedule(self, *, schedule_file: str = None):
        """Call dump_schedule to save all changes to schedule"""
        if schedule_file is None:
            self.sv.dump_schedule(schedule_file=self.schedule_file)
        else:
            self.sv.dump_schedule(schedule_file=schedule_file)

    def get_course_info(self, *, course_keyword: str) -> Dict[Course, Any]:
        """Search courses by Keyword"""
        return self.sv.get_course_info(course_keyword=course_keyword)

    def add_course(self, *, course_id: str = "", offer_id: str = "") -> int:
        """Add course into schedule table

        Returns:
            int:    status, must be one of the three:
            0:  success.
            1:  false course_id.
            2:  failing due to time conflict or
                not finished prerequired courses.
        """
        return self.sv.add_course(course_id=course_id, offer_id=offer_id)

    def remove_course(self, *, course_id: str = "") -> int:
        """Remove course from schedule table

        Returns:
            int:    status, must be one of the three:
            0:  success.
            1:  false course_id.
        """
        return self.sv.remove_course(course_id=course_id)

    def update_course(self, *, course_id: str = "", offer_id: str = "") -> int:
        """Update course from schedule table

        Returns:
            int:    status, must be one of the three:
            0:  success.
            1:  false course_id.
            2:  failing due to time conflict or
                not finished prerequired courses,
                operation took back in the case.
        """
        return self.sv.update_course(course_id=course_id, offer_id=offer_id)

    def set_priority(self, priority, *, course_id: str = "") -> int:
        """Query or Modify priority of a course

        Args:
            priority:   a integer so treated:
            0,  Query
            Other, Modify to

        Returns:
            int:    status or priority value:
            -1, false course_id
            other, primal one
        """
        return self.sv.set_priority(priority=priority, course_id=course_id)

    def config_set_attribute(self, attrname: str, attrvalue: Any):
        """Modify Config Settings (cannot parse mutable object)"""
        if isinstance(attrvalue, (list, dict)):
            raise ValueError("Attrvalue May not be mutable")
        setattr(self.config, attrname, attrvalue)

    def config_set_forbid_time(self, timelist: List[int] = None):
        """Modify Forbid Time"""
        if timelist is None:
            timelist = DEFAULT_TIMELIST[:]
        while len(timelist) < 7:
            timelist.append(0)
        setattr(self.config, "forbid_time", timelist)

    def config_toggle(self, attrname: str) -> bool:
        """Toggle Enable/Disable, will return primal value"""
        primal: bool = getattr(self.config, attrname)
        if not isinstance(primal, bool):
            raise ValueError(f"{attrname} is not a bool value")
        setattr(self.config, attrname, not primal)
        return primal


def main():
    cli: CourseSchedulerCli = CourseSchedulerCli()
    cli.mainloop()
