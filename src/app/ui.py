__author__ = 'ShiningZec'

# from src.cli import cli_util

# import tkinter
# import tkinter.messagebox
import customtkinter as ctk

# initialize CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class ClassArrangementApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SmartNavigation")
        self.geometry("1920x1080")

        # main grids：L-R
        self.grid_columnconfigure(0, weight=1)  # L
        self.grid_columnconfigure(1, weight=2)  # R
        self.grid_rowconfigure(0, weight=1)

        # L: U-D
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.left_frame.grid_rowconfigure(0, weight=20)  # L-U
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_rowconfigure(2, weight=10)  # L-D
        self.left_frame.grid_columnconfigure(0, weight=1)

        # L-U Frame
        self.listbox_a_frame = ctk.CTkFrame(self.left_frame)
        self.listbox_a_frame.grid(row=0, column=0, sticky="nsew")

        self.listbox_a_frame.grid_rowconfigure(0, weight=1)
        self.listbox_a_frame.grid_columnconfigure(0, weight=1)

        # L-U illustration
        text_font = ctk.CTkFont(weight="bold", size=28)

        self.listbox_a = ctk.CTkTextbox(self.listbox_a_frame,
                                        wrap="none",
                                        font=text_font)
        self.listbox_a.grid(row=0, column=0, sticky="nsew")

        self.listbox_a.configure(state="disabled")

        # L-D Frame
        self.listbox_b_frame = ctk.CTkFrame(self.left_frame)
        self.listbox_b_frame.grid(row=2, column=0, sticky="nsew")

        self.listbox_b_frame.grid_rowconfigure(0, weight=1)
        self.listbox_b_frame.grid_columnconfigure(0, weight=1)

        # L-D illustration
        help_font = ctk.CTkFont(weight="bold", size=24)

        self.listbox_b = ctk.CTkTextbox(self.listbox_b_frame,
                                        wrap="none",
                                        font=help_font)
        self.listbox_b.grid(row=0, column=0, sticky="nsew")

        self.listbox_b.configure(state="disabled")

        # R CLI
        bash_font = ctk.CTkFont(family="Consolas", size=24)

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=9)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.label_cmd = ctk.CTkLabel(self.right_frame,
                                      text="Terminal",
                                      font=ctk.CTkFont(weight="bold", size=24))
        self.label_cmd.grid(row=0, column=0, sticky="w", padx=5, pady=(2, 0))

        self.command_entry = ctk.CTkEntry(
            self.right_frame,
            placeholder_text="Enter Command Line...",
            font=bash_font)
        self.command_entry.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.command_entry.bind("<Return>", self.execute_command)
        self.command_entry.bind("<Control-d>", self.keyboard_interruption)

        self.command_output = ctk.CTkTextbox(self.right_frame,
                                             wrap="word",
                                             height=500,
                                             font=bash_font)
        self.command_output.grid(row=2,
                                 column=0,
                                 sticky="nsew",
                                 padx=5,
                                 pady=5)

        self.command_output.configure(state="disabled")

        # TODO
        # self.cli = cli.Cli(node_file, edge_file)

        # Start
        self.list_a_data = "Welcome"
        self.list_b_data = "Helpit"

        # 启动数据刷新线程
        self.update_data()

    def update_data(self):
        # 这里可以接入实时数据源
        self.listbox_a.configure(state="normal")
        self.listbox_b.configure(state="normal")

        self.listbox_a.delete("1.0", "end")
        self.listbox_a.insert("end", self.list_a_data)

        self.listbox_b.delete("1.0", "end")
        self.listbox_b.insert("end", self.list_b_data)

        self.listbox_a.configure(state="disabled")
        self.listbox_b.configure(state="disabled")

    def execute_command(self, event):
        self.command_output.configure(state="normal")
        command = self.command_entry.get().strip()
        if not command:
            self.command_output.insert("0.0", "> \n")
            return

        self.command_output.insert("0.0", f"> {command}\n\n")

        # TODO
        # try:
        #     outputCLI = self.cli.execute_command(command)
        #     if outputCLI[0] is not None:
        #         self.command_output.insert("0.0", outputCLI[0] + "\n")
        #     if outputCLI[1] is not None:
        #         self.list_a_data = outputCLI[1]
        #     if outputCLI[2] is not None:
        #         self.list_b_data = outputCLI[2]
        #     self.update_data()
        # except Exception as e:
        #     self.command_output.insert("0.0", f"Error: {e}\n")

        self.command_entry.delete(0, "end")

        self.command_output.configure(state="disabled")

    def keyboard_interruption(self, event):
        self.destroy()


if __name__ == "__main__":
    app = ClassArrangementApp()
    app.mainloop()
