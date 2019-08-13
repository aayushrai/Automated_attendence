import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import face_recognition
import pandas as pd
import numpy as np
from tkinter.ttk import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkcalendar import Calendar, DateEntry
from time import gmtime, strftime
import os
import sys
import re
import datetime

loop = False
loop2 = False
all_subject = ["unknown", "os", "oops", "java", "python", "data structure"]
LARGE_FONT = ("Open Sans", 14)
os.getcwd()


class startApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.state("zoomed")
        self.frames = {}
        s = Style()
        s.configure('TButton', font=('open sans', 12))
        s.configure('TEntry', font=('open sans', 12))

        menubar = MenuBar(self)
        self.config(menu=menubar)

        for F in (StartPage, App, Table):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class App(tk.Frame):

    def __init__(self, window, controller, video_source=0):
        tk.Frame.__init__(self, window)
        self.video_source = video_source
        self.controller = controller

        cam_frame = tk.Frame(self)
        self.vid = MyVideoCapture(self.video_source)
        self.canvas = tk.Canvas(cam_frame, width=self.vid.width - 3, height=self.vid.height - 3, bg="black", bd=2)
        self.vid.stop_video_capture()
        self.canvas.pack(padx=5, pady=5)
        self.btn_snapshot = Button(cam_frame, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tk.CENTER, pady=8)
        buttons_frame = tk.Frame(cam_frame)
        self.btn_load = Button(buttons_frame, text="Load Image", width=10, command=self.Load_image)
        self.btn_load.pack(anchor=tk.CENTER, side="left", padx=2)
        self.btn_start = Button(buttons_frame, text="Start Cam", width=10, command=self.start_camera)
        self.btn_start.pack(anchor=tk.CENTER, side="left", padx=2)
        self.btn_back = Button(buttons_frame, text="Go Back", width=10,
                               command=lambda: [self.controller.show_frame(StartPage), self.stop_camera()])
        self.btn_back.pack(anchor=tk.CENTER, side="left", padx=2)
        self.btn_stop = Button(buttons_frame, text="Stop Cam", width=10, command=self.stop_camera)
        self.btn_stop.pack(anchor=tk.CENTER, side="left", padx=2)
        buttons_frame.pack(anchor=tk.CENTER, pady=1)
        self.delay = 15
        cam_frame.pack(side="left", anchor="nw")

        cap_frame = tk.Frame(self)
        self.canvas1 = tk.Canvas(self, width=205, height=152, bg="black", bd=2)
        self.canvas1.pack(padx=30, pady=30)
        self.btn_clear = Button(self, text="Clear", command=self.clear_canvas)
        self.btn_clear.pack(pady=10)
        name_frame = tk.Frame(self)
        self.name_label = tk.Label(name_frame, text="    Name :           ", font=LARGE_FONT)
        self.name_label.pack(side="left", pady=5)
        self.name = Entry(name_frame)
        self.name.pack(side="left", padx=5)
        name_frame.pack(pady=5)
        en_frame = tk.Frame(self)
        self.en_label = tk.Label(en_frame, text=" Enrollment : ", font=LARGE_FONT)
        self.en_label.pack(side="left", padx=10)
        self.en = Entry(en_frame)
        self.en.pack(side="left", padx=7, pady=5)
        en_frame.pack()
        self.variable = tk.StringVar(self)
        self.w = OptionMenu(self, self.variable,
                            *list(map(lambda x: x.split(".")[0].upper(), os.listdir("csv//classes//"))))
        self.w.pack(pady=10)
        self.add_student = Button(self, text="Add Student", width=17, command=self.save_data, state="disabled")
        self.add_student.pack(pady=10)
        cap_frame.pack(side="left")

    def snapshot(self):
        # Get a frame from the video source

        if loop:
            ret, frame = self.vid.get_frame()
            if ret:
                cv2.imwrite("1.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                self.update_cap()

    def Load_image(self):
        filename = askopenfilename()
        if filename != "":
            frame = cv2.imread(filename)
            cv2.imwrite("1.jpg", frame)
            self.update_cap2(frame)

    def update(self):
        global loop
        if loop:
            self.ret, self.frame = self.vid.get_frame()
            if self.ret:
                self.face_locations = face_recognition.face_locations(self.frame[:, :, ::-1])
                for (top, right, bottom, left) in self.face_locations:
                    cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)
                self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

            self.after(self.delay, self.update)

    def stop_camera(self):
        global loop
        if loop:
            loop = False
            self.vid.stop_video_capture()
            self.canvas.delete("all")

    def start_camera(self):
        global loop
        if not loop:
            loop = True
            self.vid.start_video_capture()
            self.update()

    def save_data(self):
        self.cls = self.variable.get().lower()
        df = pd.read_csv("csv//classes//" + self.cls + ".csv")
        all_class = pd.read_csv("csv//all.csv")
        name = self.name.get()
        enroll = self.en.get()
        if re.findall('[a-zA-Z]{2}[0-9]{2}[a-zA-Z]{2}[0-9]{6}', enroll):
            if re.findall('[a-zA-Z]+', name):
                    num_row = str(df.shape[0])
                    snap_img = cv2.imread("1.jpg")
                    path = "faces//" + num_row + ".jpg"
                    cv2.imwrite(path, cv2.cvtColor(snap_img, cv2.COLOR_BGR2RGB))
                    face_locations = face_recognition.face_locations(snap_img)
                    face_encodings_str = " ".join(
                        list(map(str, face_recognition.face_encodings(snap_img, face_locations)[0])))
                    df = df.append(
                        {'Name': name, 'Enrollment': enroll, "Image_path": path, "face_encodings": face_encodings_str,
                         "class": self.cls}, ignore_index=True)
                    all_class = all_class.append(
                        {'Name': name, 'Enrollment': enroll, "Image_path": path, "face_encodings": face_encodings_str,
                         "class": self.cls}, ignore_index=True)
                    df.to_csv("csv//classes//" + self.cls + ".csv", index=False)
                    all_class.to_csv("csv//all.csv", index=False)
                    self.add_student["state"] = "disabled"
            else:
                print("invalid Name")
        else:
            print("invalid enrollment number")

    def clear_canvas(self):
        self.canvas1.delete("all")
        self.add_student["state"] = "disabled"

    def update_cap(self):
        ret, frame = self.vid.get_frame()
        if ret:
            self.photo1 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(cv2.resize(frame, (211, 158))))
            self.canvas1.create_image(0, 0, image=self.photo1, anchor=tk.NW)
            self.face_locations = face_recognition.face_locations(frame[:, :, ::-1])
            if len(self.face_locations) == 1:
                self.add_student["state"] = "normal"

    def update_cap2(self, frame):
        self.photo1 = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(cv2.resize(frame, (211, 158))))
        self.canvas1.create_image(0, 0, image=self.photo1, anchor=tk.NW)
        self.face_locations = face_recognition.face_locations(frame[:, :, ::-1])
        if len(self.face_locations) == 1:
            self.add_student["state"] = "normal"


class MyVideoCapture:

    def __init__(self, video_source=0):
        self.video_source = video_source
        self.vid1 = cv2.VideoCapture(self.video_source)
        if not self.vid1.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self.width = self.vid1.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid1.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def start_video_capture(self):
        if not self.vid1.isOpened():
            print("start_video_capture")
            self.vid1 = cv2.VideoCapture(self.video_source)

    def stop_video_capture(self):
        if self.vid1.isOpened():
            print("stop_video_capture")
            self.vid1.release()

    def get_frame(self):
        if self.vid1.isOpened():
            ret, frame = self.vid1.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)


class StartPage(tk.Frame):

    def __init__(self, parent, controller, video_source=0):
        tk.Frame.__init__(self, parent)
        # label = tk.Label(self, text="ATTENDANCE MANAGEMENT SYSTEM", font=LARGE_FONT)
        # label.pack(pady=90,padx=10)
        self.video_source = video_source
        self.controller = controller

        button_frame = tk.Frame(self)
        button = Button(button_frame, text="Show Records", command=lambda: controller.show_frame(Table), width=34)
        button.pack(side="left", padx=8)
        # button2 = tk.Button(button_frame, text="Mark Attendence",command = None,width = 30,height = 2)
        # button2.pack(side = "left")
        button3 = Button(button_frame, text="Data Collection",
                         command=lambda: [controller.show_frame(App), self.stop_camera2()], width=33)
        button3.pack(side="left", padx=1)
        button_frame.pack(anchor="nw", pady=6)
        rec_frame = tk.Frame(self)
        self.vid2 = MyVideoCapture(self.video_source)
        self.vid2.stop_video_capture()
        self.canvas = tk.Canvas(rec_frame, width=630, height=470, bg="black", bd=2)
        self.canvas.pack(padx=5, pady=5)
        self.btn_recognition = Button(rec_frame, text="Start Recognition", command=self.start_camera2, width=30)
        self.btn_recognition.pack(anchor=tk.CENTER, expand=True, pady=5)
        buttons_frame = tk.Frame(rec_frame)
        self.btn_load = Button(buttons_frame, text="Load Class", width=15, command=self.load_class)
        self.btn_load.pack(anchor=tk.CENTER, side="left", padx=3)
        self.btn_stop = Button(buttons_frame, text="Stop Cam", width=15, command=self.stop_camera2)
        self.btn_stop.pack(anchor=tk.CENTER, side="left", padx=3)
        buttons_frame.pack(expand=True, anchor=tk.CENTER, pady=1, padx=3)
        self.delay = 15
        rec_frame.pack(side="left", anchor="nw")
        self.known_faces, self.names, self.enrollment, self.c_class = None, None, None, None
        self.t_student = 0
        self.count = 1
        self.present = []
        self.CreateUI()
        self.var = tk.StringVar()
        self.var.set(str("Total Student: " + str(self.t_student)))
        total = tk.Frame(self)
        date_label = tk.Label(total, textvariable=self.var, font=LARGE_FONT).pack(side="left", padx=5, pady=5)
        total.pack()
        if not os.path.exists("records"):
            os.mkdir("records")
        if not os.path.exists("csv"):
            os.mkdir("csv")
        if not os.path.exists("csv\\classes"):
            os.mkdir("csv\\classes")
        if not os.path.exists("csv\\TimeTable"):
            os.mkdir("csv\\TimeTable")
        if not os.path.exists("faces"):
            os.mkdir("faces")
        if not os.path.exists("csv/all.csv"):
            self.record = pd.DataFrame(columns=["Name", "Enrollment", "Image_path", "face_encodings", "class"])
            self.record.to_csv("csv/all.csv", index=False)
        if not os.path.exists("csv/classes/d.csv"):
            self.record = pd.DataFrame(columns=["Name", "Enrollment", "Image_path", "face_encodings", "class"])
            self.record.to_csv("csv/classes/d.csv", index=False)

    def update2(self):
        # Get a frame from the video source
        global loop2, new_faces
        if loop2:
            self.ret, self.frame = self.vid2.get_frame()
            if self.ret:
                self.face_locations = face_recognition.face_locations(self.frame[:, :, ::-1])
                face_encodings = face_recognition.face_encodings(self.frame[:, :, ::-1], self.face_locations)
                faces_names = []
                enrollm = []
                c_cls = []
                if self.known_faces is not None:
                    for face_encoding in face_encodings:
                        name = "unknown"
                        enroll = "unknown"
                        cls = "unknown"
                        match = face_recognition.compare_faces(self.known_faces, face_encoding, tolerance=0.50)
                        for i, matched in enumerate(match):
                            if matched:
                                name = self.names[i]
                                enroll = self.enrollment[i]
                                cls = self.c_class[i]
                        faces_names.append(name)
                        enrollm.append(enroll)
                        c_cls.append(cls)

                for (top, right, bottom, left), nam, en, cl in zip(self.face_locations, faces_names, enrollm, c_cls):
                    if en not in self.present and nam != "unknown":
                        sub, day, date, time = self.time_table(cl)
                        csv_name = "records/{}-{}.csv".format(self.current_class, date.strip())
                        all_csv = "records/all-{}.csv".format(date)
                        self.records = pd.read_csv(csv_name)
                        self.all_records = pd.read_csv(all_csv)
                        self.treeview.insert('', 'end', text=nam,
                                             values=(en.upper(), date, time, cl.upper(), sub.upper()))
                        self.records = self.records.append(
                            {'Name': nam, 'Enrollment': en, "Date": date, "Time": time, "Day": day, "class": cl,
                             "subject": sub}, ignore_index=True)
                        self.all_records = self.all_records.append(
                            {'Name': nam, 'Enrollment': en.upper(), "Date": date, "Time": time, "Day": day, "class": cl,
                             "subject": sub}, ignore_index=True)
                        self.records.to_csv(csv_name, index=False)
                        self.all_records.to_csv(all_csv, index=False)
                        self.present.append(en)
                        self.count += 1
                        self.t_student += 1
                        self.var.set(str("Total Student: " + str(self.t_student)))
                        self.update_idletasks()
                    cv2.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(self.frame, nam, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255),
                                1)
                self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.after(15, self.update2)

    def time_table(self, cl):
        current = datetime.datetime.now().time()
        date1 = datetime.date.today()
        date = date1.strftime("%Y-%m-%d")
        day = date1.strftime("%A")
        subject = "unknown"
        if os.path.exists("csv\\TimeTable\\TT-{}.csv".format(cl.lower())):
            tt = pd.read_csv("csv\\TimeTable\\TT-{}.csv".format(cl.lower()))
            tt.set_index('day', inplace=True)
            times = tt.loc["Time"].values
            col = 9
            for i in range(0, 8):
                start, end = times[i].split("-")
                (SH, SM), (EH, EM) = start.split(":"), end.split(":")
                start = datetime.time(int(SH), int(SM), 0)
                end = datetime.time(int(EH), int(EM), 0)
                if self.time_in_range(start, end, current):
                    subject = tt.loc[day.strip()][i]
                    col = i
                    break
            if col == 9:
                subject = "unknown"

        return subject, day, date, current

    def time_in_range(self, start, end, x):
        if start <= end:
            return start <= x <= end
        else:
            return start <= x or x <= end

    def stop_camera2(self):
        global loop2
        if loop2:
            loop2 = False
            self.vid2.stop_video_capture()
            self.canvas.delete("all")

    def start_camera2(self):
        global loop2
        if not loop2:
            loop2 = True
            self.vid2.start_video_capture()
            self.update2()

    def load_class(self):

        newwin = tk.Toplevel(self)
        display = tk.Label(newwin, text="Select the Class to be loaded", font=LARGE_FONT)
        display.pack()
        variable1 = tk.StringVar(newwin)
        w1 = OptionMenu(newwin, variable1, "ALL",
                        *list(map(lambda x: x.split(".")[0].upper(), os.listdir("csv//classes"))))
        w1.pack(padx=5, pady=5)
        btn_start = Button(newwin, text="Load", width=10,
                           command=lambda: [self.get_encodings_names(variable1.get().lower()), newwin.destroy()])
        btn_start.pack()

    def get_encodings_names(self, class_name):
        self.btn_load["state"] = "normal"
        if class_name != "":
            if class_name == "all":
                df_en = pd.read_csv("csv//all.csv")
            else:
                df_en = pd.read_csv("csv//classes//{}.csv".format(class_name))
            encs = []
            names = []
            enroll = []
            classs = []
            for i in df_en["face_encodings"]:
                enc = list(map(float, i.split()))
                encs.append(enc)
            for j in df_en["Name"]:
                names.append(j)
            for k in df_en["Enrollment"]:
                enroll.append(k)
            for m in df_en["class"]:
                classs.append(m)
            self.known_faces = np.array(encs)
            self.names = names
            self.enrollment = enroll
            self.current_class = class_name
            self.c_class = classs

            if not os.path.exists("records/{}-{}.csv".format(class_name, strftime("%Y-%m-%d", gmtime()))):
                self.record = pd.DataFrame(columns=["Name", "Enrollment", "Date", "Time", "Day", "class", "subject"])
                self.record.to_csv("records/{}-{}.csv".format(class_name, strftime("%Y-%m-%d", gmtime())), index=False)
            if not os.path.exists("records/all-{}.csv".format(strftime("%Y-%m-%d", gmtime()))):
                self.record = pd.DataFrame(columns=["Name", "Enrollment", "Date", "Time", "Day", "class", "subject"])
                self.record.to_csv("records/all-{}.csv".format(strftime("%Y-%m-%d", gmtime())), index=False)

    def CreateUI(self):
        tv = Treeview(self, height=26)
        tv['columns'] = ('Enrollment', "Date", 'Time', "class", "Subject")
        tv.heading("#0", text='Name', anchor='w')
        tv.column("#0", anchor="w", width=150)
        tv.heading('Enrollment', text=' Enrollment No.')
        tv.column('Enrollment', anchor='center', width=140)
        tv.heading('Date', text='Date')
        tv.column('Date', anchor='center', width=80)
        tv.heading('Time', text='Time')
        tv.column('Time', anchor='center', width=100)
        tv.heading('class', text='class')
        tv.column('class', anchor='center', width=80)
        tv.heading('Subject', text='Subject')
        tv.column('Subject', anchor='center', width=80)
        tv.pack(pady=8, padx=8)
        self.treeview = tv


class Table(tk.Frame):

    def __init__(self, parent, controller):
        global all_subject
        Frame.__init__(self, parent)
        table_frame = tk.Frame(self)
        self.go_back = Button(table_frame, text="Go Back", width=15, command=lambda: controller.show_frame(StartPage))
        self.go_back.pack(padx=10, pady=10, side="left")
        text = tk.Text()
        self.date_label = tk.Label(table_frame, text="Date :", font=LARGE_FONT).pack(side="left", padx=5, pady=5)
        self.cal = DateEntry(table_frame, width=12, year=int(strftime("%Y", gmtime())),
                             month=int(strftime("%m", gmtime())), day=int(strftime("%d", gmtime())), background='black',
                             foreground='white', borderwidth=2)
        self.cal.pack(side="left", padx=10, pady=10)
        self.date_label = tk.Label(table_frame, text="Select Class :", font=LARGE_FONT).pack(side="left", padx=5,
                                                                                             pady=5)
        self.variable1 = tk.StringVar(table_frame)
        w1 = OptionMenu(table_frame, self.variable1, "ALL",
                        *list(map(lambda x: x.split(".")[0].upper(), os.listdir("csv//classes")))).pack(side="left",
                                                                                                        padx=10,
                                                                                                        pady=10)
        self.subject = tk.Label(table_frame, text="Subject :", font=LARGE_FONT)
        self.subject.pack(side="left", padx=10, pady=10)
        self.variable2 = tk.StringVar(table_frame)
        subject1 = [""]
        subject1.extend(all_subject)
        self.enter_sub = OptionMenu(table_frame, self.variable2, *subject1)
        self.enter_sub.pack(side="left", padx=10, pady=10)
        self.btn_submit = Button(table_frame, text="Submit", width=15, command=self.LoadTable)
        self.btn_submit.pack(padx=10, pady=10, side="left")
        self.to_csv_ = Button(table_frame, text="To Csv", width=15, command=self.file_save)
        self.to_csv_.pack(padx=10, pady=10)
        table_frame.pack(expand=True, anchor=tk.CENTER, pady=1)
        self.CreateUI()
        self.LoadTable()

    def CreateUI(self):
        tv = Treeview(self, height=40)
        # vsb = Scrollbar(self, orient="vertical", command=tv.yview)
        #  vsb.place(x=400, y=400, height=20)
        # tv.configure(yscrollcommand=vsb.set)
        tv['columns'] = ('Enrollment', "Date", 'Time', "Day", "class", "Subject")
        tv.heading("#0", text='Name', anchor='w')
        tv.column("#0", anchor="w")
        tv.heading('Enrollment', text=' Enrollment No.')
        tv.column('Enrollment', anchor='center', width=150)
        tv.heading('Time', text='Time')
        tv.column('Time', anchor='center', width=150)
        tv.heading('class', text='class')
        tv.heading('Date', text='Date')
        tv.column('Date', anchor='center', width=150)
        tv.column('class', anchor='center', width=150)
        tv.heading('Day', text='Day')
        tv.column('Day', anchor='center', width=150)
        tv.heading('Subject', text='Subject')
        tv.column('Subject', anchor='center', width=150)
        tv.pack(anchor=tk.CENTER)
        self.treeview = tv

    def LoadTable(self):
        clss = self.variable1.get().lower()
        sub = self.variable2.get().strip().lower()
        month, day, year = self.cal.get().split("/")
        self.treeview.delete(*self.treeview.get_children())
        try:
            csv = "all-20{}-{}-{}".format(year.zfill(2), month.zfill(2), day.zfill(2))
            df = pd.read_csv("records/{}.csv".format(csv))
            if clss != "" and clss != "all":
                df = df.loc[df['class'] == clss]
            if sub != "" and sub != "":
                df = df.loc[df['subject'] == sub]
            self.tf = df.copy()
            df = df.values
            for i in range(len(df)):
                self.treeview.insert('', 'end', text=df[i, 0], values=(
                    df[i, 1].upper(), df[i, 2], df[i, 3], df[i, 4], df[i, 5].upper(), df[i, 6].upper()))
        except Exception:
            print("no data")

    def file_save(self):
        dir_name = asksaveasfilename(defaultextension=".csv")
        if dir_name != "":
            self.tf.to_csv(dir_name, index=False)


class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        fileMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File", font=LARGE_FONT, underline=0, menu=fileMenu)
        fileMenu.add_command(label="New Class", font=LARGE_FONT, underline=1, command=self.creat_new_class)
        fileMenu.add_command(label="Delete Class", font=LARGE_FONT, underline=1, command=self.Delete_class)
        fileMenu.add_command(label="Add TimeTable", font=LARGE_FONT, underline=1, command=self.add_time_table)
        fileMenu.add_command(label="Add Subject", font=LARGE_FONT, underline=1, command=self.add_subject)
        fileMenu.add_command(label="Delete Subject", font=LARGE_FONT, underline=1, command=self.delete_subject)
        fileMenu.add_command(label="Enrolled Students", font=LARGE_FONT, underline=1, command=self.enrolled_win)

    def creat_new_class(self):
        newwin = tk.Toplevel(self)
        display = tk.Label(newwin, text="Enter New Class Name")
        display.pack(padx=5, pady=5)
        w1 = tk.Entry(newwin)
        w1.pack(padx=5, pady=5)
        btn_start = Button(newwin, text="Creat", width=10,
                           command=lambda: [self.creat_csv(w1.get().lower()), newwin.destroy()])
        btn_start.pack(padx=5, pady=5)

    def creat_csv(self, name):
        if not os.path.exists("csv//classes//{}.csv".format(name)):
            self.record = pd.DataFrame(columns=["Name", "Enrollment", "Image_path", "face_encodings", "class"])
            self.record.to_csv("csv//classes//{}.csv".format(name), index=False)
        else:
            newwin2 = tk.Toplevel(self)
            display2 = tk.Label(newwin2, text="Class Already Exists, Try Another Name")
            display2.pack(padx=5, pady=5)

    def Delete_class(self):
        newwin = tk.Toplevel(self)
        display = tk.Label(newwin, text="Select Class ", font=LARGE_FONT)
        display.pack(padx=5, pady=5)
        variable1 = tk.StringVar(newwin)
        w1 = OptionMenu(newwin, variable1, *list(map(lambda x: x.split(".")[0].upper(), os.listdir("csv//classes"))))
        w1.pack(padx=5, pady=5)
        btn_start = Button(newwin, text="Delete", width=10,
                           command=lambda: [self.delete_csv(variable1.get().lower()), newwin.destroy()])
        btn_start.pack(padx=5, pady=5)

    def delete_csv(self, name):
        if os.path.exists("csv//classes//{}.csv".format(name)):
            os.remove("csv//classes//{}.csv".format(name))
        else:
            print("Already Deleted")

    def add_subject(self):
        newwin = tk.Toplevel(self)
        display = tk.Label(newwin, text="Enter New Subject Name")
        display.pack(padx=5, pady=5)
        w1 = tk.Entry(newwin)
        w1.pack(padx=5, pady=5)
        btn_start = Button(newwin, text="Create", width=10,
                           command=lambda: [self.add_subject_in_list(w1.get().lower()), newwin.destroy()])
        btn_start.pack(padx=5, pady=5)

    def delete_subject(self):
        global all_subject
        newwin = tk.Toplevel(self)
        display = tk.Label(newwin, text="Select Subject ", font=LARGE_FONT)
        display.pack(padx=5, pady=5)
        variable1 = tk.StringVar(newwin)
        w1 = OptionMenu(newwin, variable1, *all_subject)
        w1.pack(padx=5, pady=5)
        btn_start = Button(newwin, text="Delete", width=10,
                           command=lambda: [self.delete_subject_from_list(variable1.get().lower()), newwin.destroy()])
        btn_start.pack(padx=5, pady=5)

    def delete_subject_from_list(self, sub):
        global all_subject
        all_subject.remove(sub.lower())

    def add_subject_in_list(self, sub):
        global all_subject
        all_subject.append(sub)

    def add_time_table(self):
        global all_subject
        newwin = tk.Tk()
        self.rows = []
        self.day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        l = tk.Label(newwin, text="Day")
        l.grid(row=0, column=0, sticky="w")
        self.lec = ["8:30-9:25", "9:30-10:25", "10:30-11:20", "11:25-12:15", "13:15-14:5", "14:10-15:00", "15:5-16:0",
                    "16:5-17:0"]
        for k in range(1, 6):
            l = tk.Label(newwin, text=self.day[k - 1])
            l.grid(row=k, column=0, sticky="w")
        for q in range(4, 33, 4):
            l1 = tk.Label(newwin, text=self.lec[int((q - 4) / 4)])
            l1.grid(row=0, column=q, sticky="NSEW", columnspan=4)

        for i in range(1, 6):
            cols = []
            for j in range(4, 33, 4):
                variable1 = tk.StringVar(newwin)
                e = OptionMenu(newwin, variable1, *all_subject)
                e.grid(row=i, column=j, sticky="NSEW", columnspan=4, padx=5)
                cols.append(variable1)
            self.rows.append(cols)
        self.date_label = tk.Label(newwin, text="Select Class :", font=LARGE_FONT).grid(row=34, column=8, pady=5)
        self.variable3 = tk.StringVar(newwin)
        self.w3 = tk.OptionMenu(newwin, self.variable3,
                                *list(map(lambda x: x.split(".")[0].upper(), os.listdir("csv//classes"))))
        self.w3.grid(row=34, column=12, pady=5)
        Button(newwin, text='ADD', command=lambda: [self.onPress()]).grid(row=34, column=16, pady=5)
        newwin.mainloop()

    def onPress(self):
        self.cl = self.variable3.get().lower()
        if self.cl == "":
            newwin2 = tk.Toplevel(self)
            display2 = tk.Label(newwin2, text="!!!!!!!!!Please Select The Class!!!!!!!!!", font=LARGE_FONT,
                                highlightcolor="Red")
            display2.pack(padx=5, pady=5)
        else:
            rows = self.rows
            if os.path.exists("csv\\TimeTable\\TT-{}.csv".format(self.cl)):
                os.remove("csv\\TimeTable\\TT-{}.csv".format(self.cl))

            record = pd.DataFrame(columns=["day", "1", "2", "3", "4", "5", "6", "7", "8"])
            record.to_csv("csv\\TimeTable\\TT-{}.csv".format(self.cl), index=False)
            lec = self.lec

            T_table = pd.read_csv("csv\\TimeTable\\TT-{}.csv".format(self.cl))
            c = 0

            T_table = T_table.append(
                {"day": "Time", "1": lec[0], "2": lec[1], "3": lec[2], "4": lec[3], "5": lec[4], "6": lec[5],
                 "7": lec[6], "8": lec[7]}, ignore_index=True)
            for row in rows:
                T_table = T_table.append(
                    {"day": self.day[c], "1": row[0].get(), "2": row[1].get(), "3": row[2].get(), "4": row[3].get(),
                     "5": row[4].get(), "6": row[5].get(), "7": row[6].get(), "8": row[7].get()}, ignore_index=True)
                c += 1
            T_table.to_csv("csv\\TimeTable\\TT-{}.csv".format(self.cl), index=False)

    def enrolled_win(self):
        self.enrolled = tk.Toplevel(self)
        self.enrolled_f = tk.Frame(self.enrolled)
        self.var = tk.StringVar(self.enrolled_f)
        w1 = OptionMenu(self.enrolled_f, self.var, " ",
                        *list(map(lambda x: x.split(".")[0].upper(), os.listdir("csv//classes")))).pack(side="left",
                                                                                                        padx=10,
                                                                                                        pady=10)
        btn_submit = Button(self.enrolled_f, text="Submit", width=15, command=self.LoadStudents)
        btn_submit.pack(padx=10, pady=10)
        self.enrolled_f.pack()
        tv = Treeview(self.enrolled, height=26)
        tv['columns'] = ('Enrollment', "class")
        tv.heading("#0", text='Name', anchor='w')
        tv.column("#0", anchor="w", width=150)
        tv.heading('Enrollment', text=' Enrollment No.')
        tv.column('Enrollment', anchor='center', width=140)
        tv.heading('class', text='class')
        tv.column('class', anchor='center', width=80)
        tv.pack(pady=8, padx=8)
        self.treeview = tv

    def LoadStudents(self):
        self.treeview.delete(*self.treeview.get_children())
        csv = self.var.get()
        if csv != " ":
            df = pd.read_csv("csv\\classes\\{}.csv".format(csv))
            df = df[["Name", "Enrollment", "class"]].values
            for i in range(len(df)):
                self.treeview.insert('', 'end', text=df[i, 0], values=(df[i, 1].upper(), df[i, 2]))


app = startApp()
app.mainloop()
