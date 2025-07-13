import customtkinter as ctk
from tkinter import filedialog, messagebox
# CourseSchedulerCli is provided externally
try:
    from src.cli.cli_util import CourseSchedulerCli
except ImportError:
    # Placeholder for CourseSchedulerCli if not available
    class CourseSchedulerCli:
        def __init__(self, *args, **kwargs):
            pass
        def init_cs(self): pass
        def run_cs(self, min_credit=100): pass
        def get_schedule_table(self, semester): return [[None]*13 for _ in range(7)]
        def call_checker(self): pass
        def load_schedule(self, *, schedule_file): pass
        def dump_schedule(self, *, schedule_file): pass
        def get_course_info(self, *, course_keyword): return {}
        def add_course(self, *, course_id="", offer_id=""): return 0
        def remove_course(self, *, course_id=""): return 0
        def update_course(self, *, course_id="", offer_id=""): return 0
        def set_priority(self, priority, *, course_id=""): return -1
        def config_set_attribute(self, attrname, attrvalue): pass
        def config_set_forbid_time(self, timelist=None): pass
        def config_toggle(self, attrname): return False

#---Initialization and Main Window---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CourseSchedulerApp:
    def __init__(self):
        # Main window
        self.root = ctk.CTk()
        self.root.title("Course Scheduler")
        self.root.geometry("1920x1080")
        self.root.resizable(False, False)
        # Fonts
        self.font_cn = ("SimSun", 12)
        self.font_en = ("Times New Roman", 12)
        # Colors
        self.bg_color = "#1f1f1f"
        self.separator_color = "#3f3f3f"
        # Scheduler CLI and state
        self.cli = CourseSchedulerCli()
        self.schedule_table = None

        # Layout: left panel (640px), separator (10px), right panel (1270px)
        self.root.grid_columnconfigure(0, minsize=640)
        self.root.grid_columnconfigure(1, minsize=10)
        self.root.grid_columnconfigure(2, minsize=1270)
        self.left_panel = ctk.CTkFrame(self.root, width=640)
        self.left_panel.grid(row=0, column=0, rowspan=1, sticky="nsew")
        self.separator = ctk.CTkFrame(self.root, width=10, fg_color=self.separator_color)
        self.separator.grid(row=0, column=1, rowspan=1, sticky="nsew")
        self.right_panel = ctk.CTkFrame(self.root, width=1270, fg_color=self.bg_color)
        self.right_panel.grid(row=0, column=2, rowspan=1, sticky="nsew")

        # Pages dictionary
        self.pages = {}
        # Create navigation and pages
        self.create_left_navigation()
        self.create_pages()
        # Create schedule display area
        self.create_schedule_display()
        # Show default page (main)
        self.show_page("main")
        self.root.mainloop()

    #---Left Panel Navigation Buttons---
    def create_left_navigation(self):
        nav_frame = ctk.CTkFrame(self.left_panel)
        nav_frame.pack(fill="x", pady=(10, 0))
        pages = [("主页面", "main"), ("副页面1", "sub1"), ("副页面2", "sub2")]
        self.page_buttons = {}
        for (text, key) in pages:
            btn = ctk.CTkButton(nav_frame, text=text, font=self.font_cn,
                                command=lambda k=key: self.show_page(k))
            btn.pack(side="left", padx=5, pady=5)
            self.page_buttons[key] = btn

    #---Create Page Frames---
    def create_pages(self):
        for key in ["main", "sub1", "sub2"]:
            frame = ctk.CTkFrame(self.left_panel)
            frame.pack_forget()
            self.pages[key] = frame
        # Build contents
        self.build_main_page(self.pages["main"])
        self.build_subpage1(self.pages["sub1"])
        self.build_subpage2(self.pages["sub2"])

    #---Show Selected Page---
    def show_page(self, page):
        # Hide all
        for f in self.pages.values():
            f.pack_forget()
        # Show chosen
        frame = self.pages.get(page)
        if frame:
            frame.pack(fill="both", expand=True, padx=10, pady=10)
        # If Subpage1 is selected, auto-load schedule
        if page == "sub1":
            try:
                # Attempt to load schedule (file if configured)
                self.cli.load_schedule(schedule_file=None)
                self.schedule_table = self.cli.get_schedule_table(self.sem_var.get())
                self.display_schedule()
            except Exception as e:
                messagebox.showerror("错误", f"加载课表失败: {str(e)}")

    #---Main Page Contents---
    def build_main_page(self, parent):
        col1 = ctk.CTkFrame(parent, width=210)
        col2 = ctk.CTkFrame(parent, width=210)
        col3 = ctk.CTkFrame(parent, width=210)
        col1.pack(side="left", fill="y", padx=5, pady=5)
        col2.pack(side="left", fill="y", padx=5, pady=5)
        col3.pack(side="left", fill="y", padx=5, pady=5)
        # Column1: buttons and input
        btn_init = ctk.CTkButton(col1, text="读入课程", font=self.font_cn, command=self.init_cs)
        btn_init.pack(pady=5)
        self.min_credit_var = ctk.StringVar(value="100")
        entry_credit = ctk.CTkEntry(col1, placeholder_text="最低学分", textvariable=self.min_credit_var)
        entry_credit.pack(pady=5)
        btn_run = ctk.CTkButton(col1, text="生成课表", font=self.font_cn, command=self.run_cs)
        btn_run.pack(pady=5)
        btn_show = ctk.CTkButton(col1, text="展示课表", font=self.font_cn, command=self.get_schedule_table)
        btn_show.pack(pady=5)
        btn_check = ctk.CTkButton(col1, text="检查正确性", font=self.font_cn, command=self.call_checker)
        btn_check.pack(pady=5)
        # Column2: semester radio 1-8
        self.sem_var = ctk.IntVar(value=0)
        ctk.CTkLabel(col2, text="学期", font=self.font_cn).pack()
        for i in range(8):
            rb = ctk.CTkRadioButton(col2, text=str(i+1), variable=self.sem_var, value=i, font=self.font_cn)
            rb.pack(anchor="w")
        # Column3: weeks radio 1-20
        self.week_var = ctk.IntVar(value=1)
        ctk.CTkLabel(col3, text="周次", font=self.font_cn).pack()
        for i in range(20):
            rb = ctk.CTkRadioButton(col3, text=str(i+1), variable=self.week_var, value=i, font=self.font_cn)
            rb.pack(anchor="w")

    #---Subpage1 (Course Management)---
    def build_subpage1(self, parent):
        col1 = ctk.CTkFrame(parent, width=210)
        col2 = ctk.CTkFrame(parent, width=420)
        col1.pack(side="left", fill="y", padx=5, pady=5)
        col2.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        # Search inputs and buttons
        ctk.CTkLabel(col1, text="课程ID/关键字:", font=self.font_cn).pack(pady=2, anchor="w")
        self.search_course_var = ctk.StringVar()
        entry_course = ctk.CTkEntry(col1, textvariable=self.search_course_var)
        entry_course.pack(pady=2)
        ctk.CTkLabel(col1, text="教学班ID:", font=self.font_cn).pack(pady=2, anchor="w")
        self.search_offer_var = ctk.StringVar()
        entry_offer = ctk.CTkEntry(col1, textvariable=self.search_offer_var)
        entry_offer.pack(pady=2)
        btn_search = ctk.CTkButton(col1, text="搜索课程", font=self.font_cn, command=self.search_courses)
        btn_search.pack(pady=5)
        btn_add = ctk.CTkButton(col1, text="添加课程", font=self.font_cn, command=self.add_course)
        btn_add.pack(pady=2)
        btn_remove = ctk.CTkButton(col1, text="移除课程", font=self.font_cn, command=self.remove_course)
        btn_remove.pack(pady=2)
        btn_update = ctk.CTkButton(col1, text="修改课程", font=self.font_cn, command=self.update_course)
        btn_update.pack(pady=2)
        ctk.CTkLabel(col1, text="优先级:", font=self.font_cn).pack(pady=2, anchor="w")
        self.priority_var = ctk.StringVar()
        entry_prio = ctk.CTkEntry(col1, textvariable=self.priority_var)
        entry_prio.pack(pady=2)
        btn_query = ctk.CTkButton(col1, text="查询优先级", font=self.font_cn, command=self.query_priority)
        btn_query.pack(pady=2)
        btn_setprio = ctk.CTkButton(col1, text="设置优先级", font=self.font_cn, command=self.set_priority)
        btn_setprio.pack(pady=2)
        # Output text area
        self.output_text = ctk.CTkTextbox(col2)
        self.output_text.configure(state="disabled", font=self.font_cn)
        self.output_text.pack(fill="both", expand=True)

    #---Subpage2 (Configuration)---
    def build_subpage2(self, parent):
        frame = parent
        # Group1: File selection and limits
        grp1 = ctk.CTkFrame(frame)
        grp1.pack(fill="x", pady=5)
        btn_course_file = ctk.CTkButton(grp1, text="课程文件(course.json)", width=150,
                                       font=self.font_cn, command=self.select_course_file)
        btn_course_file.pack(padx=(20,0), pady=2, anchor="w")
        btn_schedule_file = ctk.CTkButton(grp1, text="课表文件(schedule.json)", width=150,
                                          font=self.font_cn, command=self.select_schedule_file)
        btn_schedule_file.pack(padx=(20,0), pady=2, anchor="w")
        self.single_limit_var = ctk.StringVar()
        entry_limit = ctk.CTkEntry(grp1, textvariable=self.single_limit_var, width=150)
        entry_limit.pack(padx=(20,0), pady=2, anchor="w")
        btn_course_lower = ctk.CTkButton(grp1, text="设置单学期课程下界", width=150,
                                         font=self.font_cn, command=self.set_course_lower)
        btn_course_lower.pack(padx=(20,0), pady=2, anchor="w")
        btn_credit_upper = ctk.CTkButton(grp1, text="设置单学期学分上限", width=150,
                                         font=self.font_cn, command=self.set_credit_upper)
        btn_credit_upper.pack(padx=(20,0), pady=2, anchor="w")
        # Group2: Strategy checkboxes
        grp2 = ctk.CTkFrame(frame)
        grp2.pack(fill="x", pady=5)
        self.cb_required = ctk.CTkCheckBox(grp2, text="启用策略：尽可能选择必修课", font=self.font_cn,
                                           command=lambda: self.toggle_strategy("enable_required"))
        self.cb_required.pack(anchor="w", padx=20, pady=2)
        self.cb_limit = ctk.CTkCheckBox(grp2, text="启用单学期学分上限", font=self.font_cn,
                                        command=lambda: self.toggle_strategy("enable_limit_credit"))
        self.cb_limit.pack(anchor="w", padx=20, pady=2)
        self.cb_forbid = ctk.CTkCheckBox(grp2, text="启用禁课时段", font=self.font_cn,
                                         command=lambda: self.toggle_strategy("enable_forbid_time"))
        self.cb_forbid.pack(anchor="w", padx=20, pady=2)
        # Group3: Forbid time grid
        grp3 = ctk.CTkFrame(frame)
        grp3.pack(fill="both", expand=True, padx=10, pady=5)
        days = ["周一","周二","周三","周四","周五","周六","周日"]
        # Header row: blank, days, blank
        ctk.CTkLabel(grp3, text="", width=70).grid(row=0, column=0)
        for j, d in enumerate(days):
            ctk.CTkLabel(grp3, text=d, width=70, font=self.font_cn).grid(row=0, column=j+1)
        ctk.CTkLabel(grp3, text="行全选", width=70, font=self.font_cn).grid(row=0, column=8)
        # Checkboxes for each time slot
        self.forbid_vars = [[ctk.IntVar(value=0) for _ in range(7)] for _ in range(13)]
        self.row_vars = [ctk.IntVar(value=0) for _ in range(13)]
        self.col_vars = [ctk.IntVar(value=0) for _ in range(7)]
        self.all_var = ctk.IntVar(value=0)
        for i in range(13):
            ctk.CTkLabel(grp3, text=str(i+1), width=70, font=self.font_cn).grid(row=i+1, column=0)
            for j in range(7):
                cb = ctk.CTkCheckBox(grp3, text="", variable=self.forbid_vars[i][j],
                                    command=self.update_forbid_time)
                cb.grid(row=i+1, column=j+1)
            # Row select checkbox
            cb_row = ctk.CTkCheckBox(grp3, text="", variable=self.row_vars[i],
                                     command=lambda r=i: self.toggle_row(r))
            cb_row.grid(row=i+1, column=8)
        # Bottom row: column selects and all-select
        ctk.CTkLabel(grp3, text="", width=70).grid(row=14, column=0)
        for j in range(7):
            cb_col = ctk.CTkCheckBox(grp3, text="", variable=self.col_vars[j],
                                     command=lambda c=j: self.toggle_column(c))
            cb_col.grid(row=14, column=j+1)
        cb_all = ctk.CTkCheckBox(grp3, text="", variable=self.all_var, command=self.toggle_all)
        cb_all.grid(row=14, column=8)

    #---Schedule Display Grid on Right Panel---
    def create_schedule_display(self):
        self.sch_frame = ctk.CTkFrame(self.right_panel, fg_color=self.bg_color)
        self.sch_frame.pack(fill="both", expand=True)
        # Header: semester-week label at top-left
        self.sem_week_label = ctk.CTkLabel(self.sch_frame, text=f"{self.sem_var.get()+1}-{self.week_var.get()+1}",
                                           width=120, height=70, fg_color=self.bg_color,
                                           text_color="white", font=self.font_cn)
        self.sem_week_label.grid(row=0, column=0)
        # Weekday headers
        days = ["周一","周二","周三","周四","周五","周六","周日"]
        for j, day in enumerate(days):
            w = 180 if j < 5 else 120
            lbl = ctk.CTkLabel(self.sch_frame, text=day, width=w, height=70,
                               fg_color=self.bg_color, text_color="white", font=self.font_cn)
            lbl.grid(row=0, column=j+1)
        # Time slot labels and empty course cells
        self.cell_labels = {}
        for i in range(1, 14):
            lbl_time = ctk.CTkLabel(self.sch_frame, text=str(i), width=120, height=70,
                                    fg_color=self.bg_color, text_color="white", font=self.font_cn)
            lbl_time.grid(row=i, column=0)
            for j in range(7):
                w = 180 if j < 5 else 120
                lbl = ctk.CTkLabel(self.sch_frame, text="", width=w, height=70,
                                   fg_color=self.bg_color, text_color="white",
                                   font=self.font_cn, justify="center")
                lbl.grid(row=i, column=j+1)
                self.cell_labels[(i, j)] = lbl

    #---Main Page Callbacks---
    def init_cs(self):
        try:
            self.cli.init_cs()
            messagebox.showinfo("提示", "课程已读入")
        except Exception as e:
            messagebox.showerror("错误", f"读取课程失败: {str(e)}")

    def run_cs(self):
        try:
            min_credit = int(self.min_credit_var.get())
        except:
            messagebox.showerror("错误", "请输入有效最低学分")
            return
        try:
            self.cli.run_cs(min_credit=min_credit)
            messagebox.showinfo("提示", "课表已生成")
        except Exception as e:
            messagebox.showerror("错误", f"生成课表失败: {str(e)}")

    def get_schedule_table(self):
        try:
            semester = self.sem_var.get()
            self.schedule_table = self.cli.get_schedule_table(semester)
            self.display_schedule()
        except Exception as e:
            messagebox.showerror("错误", f"获取课表失败: {str(e)}")

    def call_checker(self):
        try:
            self.cli.call_checker()
            messagebox.showinfo("提示", "检查完成")
        except Exception as e:
            messagebox.showerror("错误", f"检查失败: {str(e)}")

    #---Course Search and Management (Subpage1)---
    def search_courses(self):
        keyword = self.search_course_var.get()
        try:
            results = self.cli.get_course_info(course_keyword=keyword)
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
            return
        self.output_text.configure(state="normal")
        self.output_text.delete("0.0", "end")
        for course, attended in results.items():
            line1 = f"{course.id}, {course.name}, {course.required}, {'已选' if attended else '未选'}\n"
            self.output_text.insert("end", line1)
            for off in course.offerings:
                line = f"    {off.id}, {off.teacher}, {off.times}, {off.weeks}\n"
                self.output_text.insert("end", line)
        self.output_text.configure(state="disabled")

    def add_course(self):
        cid = self.search_course_var.get()
        oid = self.search_offer_var.get()
        status = self.cli.add_course(course_id=cid, offer_id=oid)
        if status == 0:
            self.cli.dump_schedule(schedule_file=None)
            messagebox.showinfo("提示", "添加成功")
        else:
            messagebox.showerror("错误", f"添加失败，状态码: {status}")

    def remove_course(self):
        cid = self.search_course_var.get()
        status = self.cli.remove_course(course_id=cid)
        if status == 0:
            self.cli.dump_schedule(schedule_file=None)
            messagebox.showinfo("提示", "移除成功")
        else:
            messagebox.showerror("错误", f"移除失败，状态码: {status}")

    def update_course(self):
        cid = self.search_course_var.get()
        oid = self.search_offer_var.get()
        status = self.cli.update_course(course_id=cid, offer_id=oid)
        if status == 0:
            self.cli.dump_schedule(schedule_file=None)
            messagebox.showinfo("提示", "修改成功")
        else:
            messagebox.showerror("错误", f"修改失败，状态码: {status}")

    def query_priority(self):
        cid = self.search_course_var.get()
        prio = self.cli.set_priority(0, course_id=cid)
        if prio == -1:
            messagebox.showerror("错误", "课程ID无效")
        else:
            messagebox.showinfo("提示", f"当前优先级: {prio}")

    def set_priority(self):
        cid = self.search_course_var.get()
        try:
            p = int(self.priority_var.get())
        except:
            messagebox.showerror("错误", "请输入有效优先级")
            return
        status = self.cli.set_priority(p, course_id=cid)
        if status == -1:
            messagebox.showerror("错误", "课程ID无效")
        else:
            self.cli.dump_schedule(schedule_file=None)
            messagebox.showinfo("提示", "优先级已设置")

    #---Configuration Callbacks (Subpage2)---
    def select_course_file(self):
        path = filedialog.askopenfilename(title="选择课程文件")
        if path:
            self.cli.config_set_attribute("course_file", path)

    def select_schedule_file(self):
        path = filedialog.askopenfilename(title="选择课表文件")
        if path:
            self.cli.config_set_attribute("schedule_file", path)

    def set_course_lower(self):
        try:
            val = int(self.single_limit_var.get())
        except:
            messagebox.showerror("错误", "请输入有效数字")
            return
        self.cli.config_set_attribute("course_lower_limit", val)
        messagebox.showinfo("提示", "已设置课程下界")

    def set_credit_upper(self):
        try:
            val = int(self.single_limit_var.get())
        except:
            messagebox.showerror("错误", "请输入有效数字")
            return
        self.cli.config_set_attribute("credit_limit", val)
        messagebox.showinfo("提示", "已设置学分上限")

    def toggle_strategy(self, attr):
        try:
            prev = self.cli.config_toggle(attr)
            status = "启用" if not prev else "禁用"
            messagebox.showinfo("提示", f"{status}策略 {attr}")
        except Exception as e:
            messagebox.showerror("错误", f"操作失败: {str(e)}")

    def update_forbid_time(self):
        timelist = []
        for j in range(7):
            mask = 0
            for i in range(13):
                if self.forbid_vars[i][j].get() == 1:
                    mask |= (1 << i)
            timelist.append(mask)
        self.cli.config_set_forbid_time(timelist)

    def toggle_row(self, r):
        val = self.row_vars[r].get()
        for c in range(7):
            self.forbid_vars[r][c].set(val)
        self.update_forbid_time()

    def toggle_column(self, c):
        val = self.col_vars[c].get()
        for r in range(13):
            self.forbid_vars[r][c].set(val)
        self.update_forbid_time()

    def toggle_all(self):
        val = self.all_var.get()
        for r in range(13):
            self.row_vars[r].set(val)
            for c in range(7):
                self.forbid_vars[r][c].set(val)
        for c in range(7):
            self.col_vars[c].set(val)
        self.update_forbid_time()

    #---Display Schedule on Right Panel---
    def display_schedule(self):
        # Update semester-week label
        self.sem_week_label.configure(text=f"{self.sem_var.get()+1}-{self.week_var.get()+1}")
        if not self.schedule_table:
            return
        # Clear grid
        for lbl in self.cell_labels.values():
            lbl.configure(text="")
            lbl.bind("<Button-1>", "")
        # Fill with schedule data
        for day in range(7):
            if day >= len(self.schedule_table):
                continue
            for slot_idx, sched in enumerate(self.schedule_table[day]):
                if not sched:
                    continue
                name = sched.name
                teacher = sched.teacher
                # Format name
                if day < 5:  # Mon-Fri
                    disp = (name[:5] + "..." + name[-3:]) if len(name) > 9 else name
                else:  # Sat-Sun
                    disp = (name[:5] + "...") if len(name) > 6 else name
                text = disp + "\n" + teacher
                lbl = self.cell_labels.get((slot_idx+1, day))
                if lbl:
                    lbl.configure(text=text)
                    # Bind click to show details
                    lbl.bind("<Button-1>", lambda e, s=sched: self.show_schedule_details(s))

    def show_schedule_details(self, sched):
        info = (f"课程ID: {sched.id}\n名称: {sched.name}\n班级ID: {sched.class_id}\n"
                f"教师: {sched.teacher}\n时段: {sched.times}\n周次: {sched.weeks}\n必修: {sched.required}")
        top = ctk.CTkToplevel(self.root)
        top.title("课程信息")
        top.geometry("400x300")
        lbl = ctk.CTkLabel(top, text=info, font=self.font_en,
                           fg_color=self.bg_color, text_color="white", justify="left")
        lbl.pack(fill="both", expand=True, padx=10, pady=10)


def main():
    app = CourseSchedulerApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()
