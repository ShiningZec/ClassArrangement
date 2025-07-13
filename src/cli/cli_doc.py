__author__ = 'Hoshino-0102'

from typing import List

HELP_DOC = """
Hoshino-0102's CLI Tool
"""

ENTRANCE_DOC = """This is a Entrance. Welcome."""

MAINMENU_DOC = """===Main Menu===
[1] Init   \t Read data from custom file
[2] Operate\t Generate schedule and visualize it
[3] Modify \t Modify class information(CRUD)
[4] Config \t Modify Global Settings

[0] Exit
[*] Show This Dialog"""

INITMENU_DOC = """---Init Menu---
[1] ReadData      \t Read data from custom file
[2] Clear&ReadData\t Caution: Will erase preceeding operates

[0] to =Main Menu=
[*] Show This Dialog"""

OPERMENU_DOC = """---Operate Menu---
[1] GenerateSchedule \t Will dump "schedule.json"
[2] VisualizeSchedule\t Will visualize "schedule.json"
[3] CheckSchedule    \t Will call "checker.main()"

[0] to =Main Menu=
[*] Show This Dialog"""

MODIMENU_DOC = """---Modify Menu---
[1] GetClassInfo     \t Get course info by id or name
[2] AddCourse        \t Add course into schedule (must through id)
[3] RemoveCourse     \t Remove course from schedule (must through id)
[4] ModifyCourse     \t Modify course schedule (must through id)
[5] SetCoursePriority\t

[0] to =Main Menu=
[*] Show This Dialog"""

CONFMENU_DOC = """---Config Menu---
[1] Set Variables        \t Has Sub Menu
[2] Toggle Enable/Disable\t Has Sub Menu

[0] to =Main Menu=
[*] Show This Dialog"""

SETVARMENU_DOC = """---Set Variables---
[1] CoursePathtoFile  \t Format: "path\\to\\file"
[2] SchedulePathtoFile\t Format: "path\\to\\file"
[3] ForbidTime        \t
[4] ClassPerSemLimit  \t
[5] CreditPerSemLimit \t

[0] to -Config Menu-
[*] Show This Dialog"""

TOGGLEMENU_DOC = """---Toggle Enable/Disable---
                     \t If Enabled:
[1] Require          \t Will try to select Compulsory classes first
[2] ForbidTime       \t Will try to prevent classes in the duration
[3] LimitCreditPerSem\t Will limit get-able credits per semester

[0] to -Config Menu-
[*] Show This Dialog"""

SEP_DOC = """---[0] Exit---[*] Back---"""

EXIT_DOC = """Exit from CLI of class arrangement."""

MDOC: List[str] = [
    ENTRANCE_DOC, MAINMENU_DOC, INITMENU_DOC, OPERMENU_DOC, MODIMENU_DOC,
    CONFMENU_DOC, SETVARMENU_DOC, TOGGLEMENU_DOC, EXIT_DOC
]

TABLE_TITLE = ("\t    Mon.\t\t\t    Tue.\t\t\t    Wed.\t\t\t    Thur.\t\t\t"
               "    Fri.\t\t\t    Sat.\t    Sun.")

SEP_EQUAL = (
    "==================================================================="
    "==================================================================="
    "===================================================================")

SEP_MINUS = (
    "-------------------------------------------------------------------"
    "-------------------------------------------------------------------"
    "-------------------------------------------------------------------")

if __name__ == "__main__":
    print(TABLE_TITLE)
