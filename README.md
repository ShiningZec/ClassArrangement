# Class Arrangement

本项目实现了一个基于本地课程数据库的选课系统，本选课系统同时提供图形化界面(`ui`)和美化了的命令行`cli`。本选课系统设有一个自动选课系统，具有可视化的课程表，同时也允许用户自定义选择课程。

## 部署

你需要安装`customtkinter`。解压源码，随后运行`main.py`。

### 如何使用

#### 一般用户

- 图形化界面：运行`main.py`，输入`1`会启动图形化界面。

- 命令行界面：运行`main.py`，输入`2`会启动图形化界面。

#### 高级用户: 

- 时间测试：运行`main.py`，输入`3`会启动时间测试。

- 接口：本项目以`CourseSchedulerCli`为主要外部接口，这里实现了这些接口：

```py
class CourseSchedulerCli:

    def __init__(self,
                 *,
                 course_file: str = COURSE_FILE,
                 output_file: str = OUTPUT_FILE,
                 cs: CourseScheduler = None): ...

    def init_cs(self): ...
        """init/reset Course Scheduler"""

    def run_cs(self, min_credit: int = 100): ...
        """run/re-run Course Scheduler: will dump schedule.json"""

    def get_schedule_table(self, semester: int) -> List[List[Schedule]]: ...
        """will return a schedule table of that semester.
        
        Args:
            semester:   must be an integer in-between 0 and 7

        Returns:
            List[List[Schedule]:
            the outer list means which day (Mon, Tue, ..., until Sun), the inner list means which time (1, 2, 4, 8, 16, ..., 8192) (mapping the course)
        """

    def call_checker(self): ...
        """Call Checker.main() (with config)"""

    def load_schedule(self, *, schedule_file: str): ...
        """Call load_schedule to (re)load schedule from file"""

    def dump_schedule(self, *, schedule_file: str): ...
        """Call dump_schedule to save all changes to schedule file"""

    def get_course_info(self, *, course_keyword: str) -> Dict[Course, bool]: ...
        """Search courses by Keyword
        
        Args:
            course_keyword: searching keyword,
            matching course_id, course_name, or teacher_name.
        
        Returns:
            Dict[Course, bool]:
            bool: whether attend it
        """

    def add_course(self, *, course_id: str = "", offer_id: str = "") -> int: ...
        """Add course into schedule table

        Args:
            course_id:  the course to be chosen
            offer_id:   the class to be chosen

        Returns:
            int:    status, must be one of the three:
            0:  success.
            1:  false course_id.
            2:  failing due to time conflict or
                not finished prerequired courses.
        """

    def remove_course(self, *, course_id: str = "") -> int: ...
        """Remove course from schedule table

        Args:
            course_id:  the course to be removed

        Returns:
            int:    status, must be one of the three:
            0:  success.
            1:  false course_id.
        """

    def update_course(self, *, course_id: str = "", offer_id: str = "") -> int: ...
        """Update course from schedule table

        Args:
            course_id:  the course to be modified
            offer_id:   the class to set to

        Returns:
            int:    status, must be one of the three:
            0:  success.
            1:  false course_id.
            2:  failing due to time conflict or
                not finished prerequired courses,
                operation took back in the case.
        """

    def set_priority(self, priority, *, course_id: str = "") -> int: ...
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

    def config_set_attribute(self, attrname: str, attrvalue: Any): ...
        """Modify Config Settings (cannot parse mutable object)
        
        Args:
            attrname:   must be one of the four:
            "course_file", "schedule_file", "course_lower_limit", "credit_limit"

            attrvalue:
            a file path should be a string of path (windows format)
            a limit should be a integer value
        """
    
    def config_set_forbid_time(self, timelist: List[int] = None): ...
        """Modify Forbid Time
        
        Args:
            timelist:   a list of seven integers or None.
            if None, will set it to a list of seven zeroes.
        """

    def config_toggle(self, attrname: str) -> bool: ...
        """Toggle Enable/Disable, will return primal status
        
        Args:
            attrname:   must be one of the three:
            "enable_required", "enable_forbid_time", "enable_limit_credit"
        
        Returns:
            bool: primal status
        """
```

## 关于本项目

### 环境

`uv`构建

### TODO List

- 在课表上修改课程信息
- 引入网络数据库
- 引入课程数据库热处理
