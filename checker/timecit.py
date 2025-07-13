from src.cli.cli_util import CourseSchedulerCli

import timeit


def func():
    cli: CourseSchedulerCli = CourseSchedulerCli()
    cli.init_cs()
    cli.config.course_lower_limit = 20
    cli.config.credit_limit = 300
    cli.config.enable_required = True
    cli.run_cs(300)
    for i in range(7):
        cli._visual_cli(i)


def main():
    number, time = timeit.Timer(func).autorange()
    print(f"课表总学分300, 单学期课数下限20.\n"
          f"测试全程序运行{number}轮.\n"
          f"全部用时 {time * 1000} ms, "
          f"单点用时 {time * 1000 / number} ms")


if __name__ == '__main__':
    main()
