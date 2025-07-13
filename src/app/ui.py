from src.cli.cli_util import CourseSchedulerCli

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox


class CourseScheduleApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Course Scheduler App")
        self.geometry("1920x1080")
        # Initialize CLI and schedule cache
        self.cli = CourseSchedulerCli()
        self.schedule_table = None

        # Configure main grid: left sidebar vs right schedule display
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # --- Left side: TabView with 3 tabs ---
        self.tabview = ctk.CTkTabview(master=self)
        self.tabview.add("主页面")
        self.tabview.add("副页面1")
        self.tabview.add("副页面2")
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # --- Right side: Schedule display (8x14 grid including headers) ---
        self.schedule_frame = ctk.CTkFrame(master=self, fg_color="black")
        self.schedule_frame.grid(row=0,
                                 column=1,
                                 sticky="nsew",
                                 padx=5,
                                 pady=5)
        # Configure 8 columns × 14 rows (inc. headers)
        for c in range(8):
            self.schedule_frame.grid_columnconfigure(c, weight=1)
        for r in range(14):
            self.schedule_frame.grid_rowconfigure(r, weight=1)
        # Create label widgets for all cells (empty for now)
        self.schedule_labels = []
        for r in range(14):
            row_labels = []
            for c in range(8):
                label = ctk.CTkLabel(self.schedule_frame,
                                     text="",
                                     font=("宋体", 24),
                                     text_color="white")
                label.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                row_labels.append(label)
            self.schedule_labels.append(row_labels)

        # ---------- Main Page (主页面) ----------
        main_tab = self.tabview.tab("主页面")
        main_tab.columnconfigure((0, 2), weight=1)
        btn_init = ctk.CTkButton(main_tab,
                                 text="读入课程:init_cs",
                                 command=self.init_cs,
                                 font=("宋体", 12))
        btn_init.grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(main_tab, text="").grid(row=0, column=1)  # spacer
        btn_run = ctk.CTkButton(main_tab,
                                text="生成课表:run_cs",
                                command=self.run_cs,
                                font=("宋体", 12))
        btn_run.grid(row=0, column=2, padx=5, pady=5)

        # Semester and Week selection (vertical radios) + display button
        mid_frame = ctk.CTkFrame(main_tab)
        mid_frame.grid(row=1,
                       column=0,
                       columnspan=3,
                       sticky="ew",
                       padx=5,
                       pady=5)
        mid_frame.columnconfigure((0, 1, 2), weight=2)
        # Semester radio buttons (1-8)
        self.sem_var = tk.IntVar(value=0)
        sem_frame = ctk.CTkFrame(mid_frame)
        sem_frame.grid(row=0, column=0, sticky="n")
        for i in range(8):
            rb = ctk.CTkRadioButton(master=sem_frame,
                                    text=str(i + 1),
                                    variable=self.sem_var,
                                    value=i,
                                    font=("宋体", 12))
            rb.pack(anchor="w", pady=2)
        # Week radio buttons (1-20, bit values)
        self.week_var = tk.IntVar(value=2)  # default week = 2**1
        week_frame = ctk.CTkFrame(mid_frame)
        week_frame.grid(row=0, column=1, sticky="n")
        for i in range(20):
            rb = ctk.CTkRadioButton(master=week_frame,
                                    text=str(i + 1),
                                    variable=self.week_var,
                                    value=2**i,
                                    font=("宋体", 12))
            rb.pack(anchor="w", pady=1)
        btn_display = ctk.CTkButton(mid_frame,
                                    text="展示课表:get_schedule_table",
                                    command=self.show_schedule,
                                    font=("宋体", 12))
        btn_display.grid(row=0, column=2, padx=5, pady=5)

        # Check correctness button
        main_tab.columnconfigure((0, 1), weight=2)
        btn_check = ctk.CTkButton(main_tab,
                                  text="检查正确性:call_checker",
                                  command=self.call_checker,
                                  font=("宋体", 12))
        btn_check.grid(row=2, column=0, padx=5, pady=5)
        ctk.CTkLabel(main_tab, text="").grid(row=2, column=1)

        # ---------- Manual Selection Page (副页面1) ----------
        sub1_tab = self.tabview.tab("副页面1")
        # Load existing schedule on entering this tab
        self.cli.load_schedule(schedule_file=None)
        # Search entry (width ~20 chars)
        self.search_entry = ctk.CTkEntry(sub1_tab, width=200, font=("宋体", 12))
        self.search_entry.grid(row=0,
                               column=0,
                               columnspan=4,
                               padx=5,
                               pady=5,
                               sticky="ew")
        sub1_tab.columnconfigure((0, 1, 2, 3), weight=1)
        # Buttons: Search, Add, Remove, Update
        btn_search = ctk.CTkButton(sub1_tab,
                                   text="搜索课程:get_course_info",
                                   command=self.search_courses,
                                   font=("宋体", 12))
        btn_search.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        btn_add = ctk.CTkButton(sub1_tab,
                                text="添加课程:add_course",
                                command=self.add_course,
                                font=("宋体", 12))
        btn_add.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        btn_remove = ctk.CTkButton(sub1_tab,
                                   text="移除课程:remove_course",
                                   command=self.remove_course,
                                   font=("宋体", 12))
        btn_remove.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        btn_update = ctk.CTkButton(sub1_tab,
                                   text="修改课程:update_course",
                                   command=self.update_course,
                                   font=("宋体", 12))
        btn_update.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        # Priority entry + button
        sub1_tab.columnconfigure(0, weight=5)
        sub1_tab.columnconfigure(1, weight=1)
        self.priority_entry = ctk.CTkEntry(sub1_tab,
                                           width=100,
                                           font=("宋体", 12))
        self.priority_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        btn_priority = ctk.CTkButton(sub1_tab,
                                     text="设置优先级:set_priority",
                                     command=self.set_priority,
                                     font=("宋体", 12))
        btn_priority.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        # Output textbox (read-only)
        sub1_tab.rowconfigure(3, weight=1)
        self.output_text = ctk.CTkTextbox(sub1_tab, font=("宋体", 12))
        self.output_text.grid(row=3,
                              column=0,
                              columnspan=4,
                              padx=5,
                              pady=5,
                              sticky="nsew")
        self.output_text.configure(state="disabled")

        # ---------- Settings Page (副页面2) ----------
        settings_tab = self.tabview.tab("副页面2")
        settings_tab.columnconfigure((0, 1), weight=1)
        # File selectors
        btn_course_file = ctk.CTkButton(settings_tab,
                                        text="course.json",
                                        command=self.set_course_file,
                                        font=("宋体", 12))
        btn_course_file.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        btn_schedule_file = ctk.CTkButton(settings_tab,
                                          text="schedule.json",
                                          command=self.set_schedule_file,
                                          font=("宋体", 12))
        btn_schedule_file.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        # Limits entry + buttons
        settings_tab.columnconfigure((0, 1, 2), weight=2)
        self.limit_entry = ctk.CTkEntry(settings_tab,
                                        width=100,
                                        font=("宋体", 12))
        self.limit_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        btn_lower = ctk.CTkButton(settings_tab,
                                  text="设置单学期课程下界",
                                  command=self.set_course_lower,
                                  font=("宋体", 12))
        btn_lower.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        btn_credit = ctk.CTkButton(settings_tab,
                                   text="设置单学期学分上限",
                                   command=self.set_credit_limit,
                                   font=("宋体", 12))
        btn_credit.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        # Checkboxes for enable_required and enable_limit_credit
        self.required_var = tk.BooleanVar(value=False)
        cb_required = ctk.CTkCheckBox(settings_tab,
                                      text="启用策略：尽可能选择必修课",
                                      variable=self.required_var,
                                      command=self.toggle_required,
                                      font=("宋体", 12))
        cb_required.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.limit_credit_var = tk.BooleanVar(value=False)
        cb_limit = ctk.CTkCheckBox(settings_tab,
                                   text="启用单学期学分上限",
                                   variable=self.limit_credit_var,
                                   command=self.toggle_limit_credit,
                                   font=("宋体", 12))
        cb_limit.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        # Forbid-time checkbox matrix
        matrix_frame = ctk.CTkFrame(settings_tab)
        matrix_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        # Top headers and enable_forbid toggle
        self.enable_forbid_var = tk.BooleanVar(value=False)
        cb_forbid = ctk.CTkCheckBox(matrix_frame,
                                    text="启用 forbid",
                                    variable=self.enable_forbid_var,
                                    command=self.toggle_forbid_enable,
                                    font=("宋体", 12))
        cb_forbid.grid(row=0, column=0)
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        for j, day in enumerate(days, start=1):
            lbl = ctk.CTkLabel(matrix_frame, text=day, font=("宋体", 12))
            lbl.grid(row=0, column=j, padx=2, pady=2)
        ctk.CTkLabel(matrix_frame, text="行全选", font=("宋体", 12)).grid(row=0,
                                                                     column=8,
                                                                     padx=2,
                                                                     pady=2)
        # Time slots (rows) and checkboxes
        self.forbid_vars = {}
        for i in range(1, 14):
            ctk.CTkLabel(matrix_frame, text=str(i),
                         font=("宋体", 12)).grid(row=i, column=0, padx=2, pady=2)
            # Day checkboxes
            for j in range(1, 8):
                var = tk.BooleanVar(value=False)
                cb = ctk.CTkCheckBox(
                    matrix_frame,
                    text="",
                    variable=var,
                    onvalue=True,
                    offvalue=False,
                    command=lambda r=i, c=j: self.forbid_cell_changed(r, c))
                cb.grid(row=i, column=j)
                self.forbid_vars[(i, j)] = var
            # Row-select
            var_row = tk.BooleanVar(value=False)
            cb_row = ctk.CTkCheckBox(matrix_frame,
                                     text="",
                                     variable=var_row,
                                     onvalue=True,
                                     offvalue=False,
                                     command=lambda r=i: self.select_row(r))
            cb_row.grid(row=i, column=8)
            self.forbid_vars[(i, 8)] = var_row
        # Column-select (bottom row)
        ctk.CTkLabel(matrix_frame, text="列全选", font=("宋体", 12)).grid(row=14,
                                                                     column=0)
        self.col_vars = {}
        for j in range(1, 8):
            var_col = tk.BooleanVar(value=False)
            cb_col = ctk.CTkCheckBox(matrix_frame,
                                     text="",
                                     variable=var_col,
                                     onvalue=True,
                                     offvalue=False,
                                     command=lambda c=j: self.select_column(c))
            cb_col.grid(row=14, column=j)
            self.col_vars[j] = var_col
        # Global select-all
        var_all = tk.BooleanVar(value=False)
        cb_all = ctk.CTkCheckBox(matrix_frame,
                                 text="全选",
                                 variable=var_all,
                                 onvalue=True,
                                 offvalue=False,
                                 command=self.select_all)
        cb_all.grid(row=14, column=8)
        self.all_select_var = var_all

    # --- Main Page Handlers ---
    def init_cs(self):
        self.cli.init_cs(config=None)

    def run_cs(self):
        self.cli.run_cs(config=None)

    def show_schedule(self):
        sem = self.sem_var.get()
        table = self.cli.get_schedule_table(semester=sem)
        self.schedule_table = table
        # Update headers
        sem_label = ctk.CTkLabel(self.schedule_frame,
                                 text=f"学期{sem+1}-周{self.week_var.get()}",
                                 font=("宋体", 24),
                                 text_color="white")
        sem_label.grid(row=0, column=0, sticky="nsew")
        self.schedule_labels[0][0] = sem_label
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        for j, day in enumerate(days, start=1):
            lbl = ctk.CTkLabel(self.schedule_frame,
                               text=day,
                               font=("宋体", 24),
                               text_color="white")
            lbl.grid(row=0, column=j, sticky="nsew")
            self.schedule_labels[0][j] = lbl
        # Time labels and courses
        for i in range(1, 14):
            lbl = ctk.CTkLabel(self.schedule_frame,
                               text=str(i),
                               font=("宋体", 24),
                               text_color="white")
            lbl.grid(row=i, column=0, sticky="nsew")
            self.schedule_labels[i][0] = lbl
        for j in range(1, 8):
            for i in range(1, 14):
                entry = table[j - 1][i - 1]
                if entry is not None:
                    txt = f"{entry.name}\n{entry.teacher}"
                else:
                    txt = ""
                label = ctk.CTkLabel(self.schedule_frame,
                                     text=txt,
                                     font=("宋体", 24),
                                     text_color="white")
                label.grid(row=i, column=j, sticky="nsew", padx=1, pady=1)
                if entry is not None:
                    label.bind("<Button-1>",
                               lambda e, d=j - 1, t=i - 1: self.
                               on_schedule_click(d, t))
                self.schedule_labels[i][j] = label

    def on_schedule_click(self, day, time):
        entry = self.schedule_table[day][time]
        if entry:
            info = (f"课程 ID: {entry.id}\n"
                    f"名称: {entry.name}\n"
                    f"教学班 ID: {entry.class_id}\n"
                    f"教师: {entry.teacher}\n"
                    f"教学时间: {entry.times}\n"
                    f"教学周次: {entry.weeks}\n"
                    f"是否必修: {entry.required}")
            messagebox.showinfo("课程详情", info, parent=self)

    def call_checker(self):
        self.cli.call_checker(config=None)
        # (Output goes to stdout per spec)

    # --- Manual Page Handlers ---
    def search_courses(self):
        kw = self.search_entry.get()
        results = self.cli.get_course_info(course_keyword=kw)
        self.output_text.configure(state="normal")
        self.output_text.delete("0.0", "end")
        for course, attended in results.items():
            self.output_text.insert(
                "end", f"{course.id}, {course.name}, "
                f"必修={course.required}, 已选={attended}\n")
            for offer in course.offerings:
                self.output_text.insert(
                    "end", f"    {offer.id}, {offer.teacher}, "
                    f"{offer.times}, {offer.weeks}\n")
            self.output_text.insert("end", "\n")
        self.output_text.configure(state="disabled")

    def add_course(self):
        text = self.search_entry.get()
        try:
            course_id, offer_id = [s.strip() for s in text.split(",")]
        except Exception:
            messagebox.showerror("输入错误", "请输入 课程ID, 教学班ID", parent=self)
            return
        status = self.cli.add_course(course_id=course_id, offer_id=offer_id)
        if status == 0:
            self.cli.dump_schedule(schedule_file=None)
            messagebox.showinfo("添加成功", "课程已添加", parent=self)
        else:
            messagebox.showerror("添加失败", f"错误代码: {status}", parent=self)

    def remove_course(self):
        course_id = self.search_entry.get().strip()
        status = self.cli.remove_course(course_id=course_id)
        if status == 0:
            self.cli.dump_schedule(schedule_file=None)
            messagebox.showinfo("移除成功", "课程已移除", parent=self)
        else:
            messagebox.showerror("移除失败", f"错误代码: {status}", parent=self)

    def update_course(self):
        text = self.search_entry.get()
        try:
            course_id, offer_id = [s.strip() for s in text.split(",")]
        except Exception:
            messagebox.showerror("输入错误", "请输入 课程ID, 教学班ID", parent=self)
            return
        status = self.cli.update_course(course_id=course_id, offer_id=offer_id)
        if status == 0:
            self.cli.dump_schedule(schedule_file=None)
            messagebox.showinfo("修改成功", "课程已修改", parent=self)
        else:
            messagebox.showerror("修改失败", f"错误代码: {status}", parent=self)

    def set_priority(self):
        text = self.priority_entry.get()
        try:
            course_id, priority = [s.strip() for s in text.split(",")]
            priority_val = int(priority)
        except Exception:
            messagebox.showerror("输入错误", "请输入 课程ID, 优先级值", parent=self)
            return
        status = self.cli.set_priority(priority_val, course_id=course_id)
        if status >= 0:
            messagebox.showinfo("优先级设置",
                                f"课程 {course_id} 优先级: {status}",
                                parent=self)
            self.cli.dump_schedule(schedule_file=None)
        else:
            messagebox.showerror("失败", f"错误代码: {status}", parent=self)

    # --- Settings Page Handlers ---
    def set_course_file(self):
        path = filedialog.askopenfilename(title="选择 course.json",
                                          filetypes=[("JSON", "*.json")])
        if path:
            self.cli.config_set_attribute("course_file", path)

    def set_schedule_file(self):
        path = filedialog.askopenfilename(title="选择 schedule.json",
                                          filetypes=[("JSON", "*.json")])
        if path:
            self.cli.config_set_attribute("schedule_file", path)

    def set_course_lower(self):
        try:
            num = int(self.limit_entry.get())
        except Exception:
            messagebox.showerror("输入错误", "请输入整数", parent=self)
            return
        self.cli.config_set_attribute("course_lower_limit", num)

    def set_credit_limit(self):
        try:
            num = int(self.limit_entry.get())
        except Exception:
            messagebox.showerror("输入错误", "请输入整数", parent=self)
            return
        self.cli.config_set_attribute("credit_limit", num)

    def toggle_required(self):
        self.cli.config_toggle("enable_required")

    def toggle_limit_credit(self):
        self.cli.config_toggle("enable_limit_credit")

    def toggle_forbid_enable(self):
        if self.enable_forbid_var.get():
            self.cli.config_toggle("enable_forbid_time")
        else:
            self.cli.config_toggle("enable_forbid_time")
            self.cli.config_set_forbid_time(None)

    def forbid_cell_changed(self, r, c):
        self.update_forbid_config()

    def select_row(self, row):
        state = self.forbid_vars[(row, 8)].get()
        for c in range(1, 8):
            self.forbid_vars[(row, c)].set(state)
        self.update_forbid_config()

    def select_column(self, col):
        state = self.col_vars[col].get()
        for r in range(1, 14):
            self.forbid_vars[(r, col)].set(state)
            self.forbid_vars[(r, 8)].set(state)
        self.update_forbid_config()

    def select_all(self):
        state = self.all_select_var.get()
        for key in self.forbid_vars:
            self.forbid_vars[key].set(state)
        for key in self.col_vars:
            self.col_vars[key].set(state)
        self.update_forbid_config()

    def update_forbid_config(self):
        timelist = []
        for j in range(1, 8):
            mask = 0
            for i in range(1, 14):
                if self.forbid_vars[(i, j)].get():
                    mask |= 1 << (i - 1)
            timelist.append(mask)
        self.cli.config_set_forbid_time(timelist)


def main():
    app: CourseScheduleApp = CourseScheduleApp()
    app.mainloop()


if __name__ == '__main__':
    main()
