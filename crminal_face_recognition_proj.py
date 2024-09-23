import cv2
import numpy as np
import face_recognition
import os
import datetime as dt
import json
import customtkinter as ctk
from PIL import Image
import tkinter.messagebox as tkmb
import time

class CriminalRecognition:
    def __init__(self, path):
        self.path = path
        self.images = []
        self.criminal_name = []
        self.criminal_id = []
        self.case = False
        self.myList = os.listdir(self.path)

        for cl in self.myList:
            curImg = cv2.imread(f'{self.path}/{cl}')
            self.images.append(curImg)
            ospath = os.path.splitext(cl)[0]
            s = ospath.split('.')
            self.criminal_name.append(s[0])
            self.criminal_id.append(s[1])

        self.encodeListKnown = self.find_encodings(self.images)

    def find_encodings(self, images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    def criminal_no(self, index):
        return self.criminal_id[index]

    def recognize(self):
        cap = cv2.VideoCapture(0)
        print("enter the key 'a' to close the camera:")
        while True:
            success, img = cap.read()
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    if not self.case:
                        a = self.criminal_no(matchIndex)
                        print(a)
                        self.case = True

                    name = self.criminal_name[matchIndex].upper()
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(img, "Criminal", (20, 450), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 4)

            cv2.imshow('Webcam', img)

            if cv2.waitKey(1) == ord('a'):
                break

        cap.release()
        cv2.destroyAllWindows()
class CriminalRecord(CriminalRecognition):

    def __init__(self):
        self.db = {}
        self.file_path = "criminal_records.json"

    def load_records(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.db = json.load(f)
                return self.db

    def save_records(self):
        with open(self.file_path, "w") as f:
            json.dump(self.db, f, indent=2)

    def create_record(self):
        print("Criminal Information:")
        record_gui=InputApp
        id_rec=record_gui.save_record()
        ID = int(id_rec[0])
        name = id_rec[1]
        address = id_rec[2]
        offence = id_rec[3]
        sentencing = int(id_rec[4])
        register_date = dt.date.today().strftime("%Y-%m-%d")
        self.db[ID] = {
            "Name": name,
            "Address": address,
            "Offence": offence,
            "Date of Registration": register_date,
            "Time to be Served": f"{sentencing} year(s)"
        }

        self.save_records()
        print("New data recorded.")

    

    def remove_record(self):
        ID = int(input("Enter the criminal ID to remove: "))
        if ID in self.db:
            del self.db[ID]
            self.save_records()
            print("Record successfully deleted.")
        else:
            print("Record not found.")

    def find_record(self):
        ID = int(input("Enter the criminal ID to find: "))
        record = self.db.get(ID)
        if record:
            print(json.dumps(record, indent=2))
        else:
            print("Record not found.")
    
    

    def facial_recog(self):
        print("facial recognition activated")
        recognizer = CriminalRecognition('criminals')
        recognizer.recognize()
        index=0
        criminal_id=str(recognizer.criminal_no(index))
        data=self.load_records()
        if criminal_id not in data:
            print("id not found")
        else:
            print(f"criminal id:{criminal_id}")
            cur_id=data.get(criminal_id)
            records=(json.dumps(cur_id, indent=2))
            print(records)
            return records

    def display_all(self):
        for ID, record in self.db.items():
            print("\nCriminal ID:", ID)
            display=(json.dumps(record, indent=2))
            return display


class SlidePanel(ctk.CTkFrame):
            def __init__(self, parent, start_pos, end_pos):
                super().__init__(master=parent)
                self.start_pos = start_pos + 0.04
                self.end_pos = end_pos - 0.03
                self.width = abs(start_pos - end_pos)
                self.pos = self.start_pos
                self.in_start_pos = True
                self.place(relx=self.start_pos, rely=0.05, relwidth=self.width, relheight=0.9)

            def animate(self):
                if self.in_start_pos:
                    self.animate_forward()
                else:
                    self.animate_backwards()

            def animate_forward(self):
                if self.pos > self.end_pos:
                    self.pos -= 0.008
                    self.place(relx=self.pos, rely=0.05, relwidth=self.width, relheight=0.9)
                    self.after(10, self.animate_forward)
                else:
                    self.in_start_pos = False

            def animate_backwards(self):
                if self.pos < self.start_pos:
                    self.pos += 0.008
                    self.place(relx=self.pos, rely=0.05, relwidth=self.width, relheight=0.9)
                    self.after(10, self.animate_backwards)
                else:
                    self.in_start_pos = True


class InputApp:
        def __init__(self, root):
            self.root = root
            ctk.set_appearance_mode("dark")
            self.root.title("Criminal Detection")
            self.root.geometry('600x400')

            self.records_count = 0
            self.current_record = 0

            self.setup_initial_frame()

        def setup_initial_frame(self):
            self.initial_frame = ctk.CTkFrame(master=self.root, height=400, width=400,border_width=10)
            self.initial_frame.pack(pady=10, padx=10, fill='both', expand=True)
            self.label = ctk.CTkLabel(master=self.initial_frame, text="Criminal record",font=("Arial",40),anchor="n")
            self.label.pack(padx=12,pady=10,fill="both")

            self.initial_frame2 = ctk.CTkFrame(master=self.initial_frame, height=400, width=400,border_width=5)
            self.initial_frame2.pack(pady=10, padx=10,expand="true")

            self.records_entry = ctk.CTkEntry(master=self.initial_frame2,placeholder_text="enter the number of criminals",
                                            height=50,width=200)
            self.records_entry.pack(padx=10,pady=10)

            self.submit_button = ctk.CTkButton(master=self.initial_frame2, text="Submit", command=self.set_record_count)
            self.submit_button.pack(padx=10,pady=10)

        def set_record_count(self):
            try:
                self.records_count = int(self.records_entry.get())
                self.initial_frame.destroy()
                self.setup_record_frame()
            except ValueError:
                self.label.configure(text="Please enter a valid number.")

        def setup_record_frame(self):
            if hasattr(self, 'record_frame'):
                self.record_frame.destroy()

            self.record_frame = ctk.CTkScrollableFrame(
                master=self.root, width=400, height=400, corner_radius=10,
                orientation="vertical", label_text=f"Record {self.current_record + 1}",
                label_font=("Arial", 20)
            )
            self.record_frame.pack(pady=20, padx=40, fill='both', expand=True)

            self.id_label = ctk.CTkLabel(master=self.record_frame, text="ID", fg_color="transparent")
            self.id_label.pack(pady=12, padx=10)
            self.id_entry = ctk.CTkEntry(master=self.record_frame, placeholder_text="Enter the criminal ID", width=200)
            self.id_entry.pack()

            self.name_label = ctk.CTkLabel(master=self.record_frame, text="Name", fg_color="transparent")
            self.name_label.pack(pady=12, padx=10)
            self.name_entry = ctk.CTkEntry(master=self.record_frame, placeholder_text="Enter the criminal's name", width=200)
            self.name_entry.pack()

            self.address_label = ctk.CTkLabel(master=self.record_frame, text="Address", fg_color="transparent")
            self.address_label.pack(pady=12, padx=10)
            self.address_entry = ctk.CTkEntry(master=self.record_frame, placeholder_text="Enter the criminal's address", width=200)
            self.address_entry.pack()

            self.offense_label = ctk.CTkLabel(master=self.record_frame, text="Offense", fg_color="transparent")
            self.offense_label.pack(pady=12, padx=10)
            self.offense_entry = ctk.CTkEntry(master=self.record_frame, placeholder_text="Enter the offense committed", width=200)
            self.offense_entry.pack()

            self.sentencing_label = ctk.CTkLabel(master=self.record_frame, text="Sentencing", fg_color="transparent")
            self.sentencing_label.pack(pady=10, padx=10)
            self.sentencing_entry = ctk.CTkEntry(master=self.record_frame, placeholder_text="Enter the time to be served (in years)", width=250)
            self.sentencing_entry.pack()

            self.submit_button = ctk.CTkButton(master=self.record_frame, text="Submit", command=self.caller)
            self.submit_button.pack(pady=10)
        
        def caller(self):
            print("function called")
            self.save_record()
            print("svae called")
            self.record_number()
            print("recods called")


        def save_record(self):
            id_rec=self.id_entry.get()
            name_rec=self.name_entry.get()
            address_rec=self.address_entry.get()
            offence_rec=self.offense_entry.get()
            secent_rec=self.sentencing_entry.get()
            print("called")
            return id_rec,name_rec,address_rec,offence_rec,secent_rec
        

        def record_number(self):

            self.current_record += 1
            print("current record incrimented and called")
            if self.current_record < self.records_count:
                self.setup_record_frame()
            else:
                self.root.destroy()
        






class MainGUI:
    def __init__(self):
        self.main_window = None
        self.face_window()

    def face_window(self):
        self.main_window = ctk.CTk()
        self.main_window.title("Welcome")
        self.main_window.geometry("500x500")
        ctk.set_appearance_mode("dark")

        def show_msg(event=None):
            self.main_window.destroy()
            self.login_page()

        # Load and place the image
        face_img = ctk.CTkImage(light_image=Image.open("C:/Users/hp/vscode/assets/python logo.jpg"),
                                dark_image=Image.open("C:/Users/hp/vscode/assets/python logo.jpg"),
                                size=(400, 400))
        img_label = ctk.CTkLabel(self.main_window, text="", image=face_img)
        img_label.place(relx=0.5, rely=0.3, anchor="center")

        # Add instruction label
        label = ctk.CTkLabel(self.main_window, text="Press Enter to continue", fg_color="transparent", font=("Arial", 20), height=30, width=100)
        label.place(relx=0.5, rely=0.8, anchor="center")

        # Bind the "Enter" key to the show_msg function
        self.main_window.bind("<Return>", show_msg)

        self.main_window.mainloop()

    def login_page(self):
        def login():
            username = "aditya"
            password = "12345"
            if user_entry.get() == username and user_pass.get() == password:
                print("pass")
                app.destroy()
                self.new_window()
            elif user_entry.get() == username and user_pass.get() != password:
                tkmb.showwarning(title='Wrong password', message='Please check your password')
            elif user_entry.get() != username and user_pass.get() == password:
                tkmb.showwarning(title='Wrong username', message='Please check your username')
            else:
                tkmb.showerror(title="Login Failed", message="Invalid Username and password")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        app = ctk.CTk()
        app.geometry("600x400")
        app.title("Modern Login UI using Customtkinter")
        label = ctk.CTkLabel(app, text="This is the main UI page")
        frame = ctk.CTkFrame(master=app)
        frame.pack(pady=20, padx=40, fill='both', expand=True)
        label = ctk.CTkLabel(master=frame, text='WELCOME', font=("Arial", 20))
        label.pack(pady=12, padx=10)
        user_entry = ctk.CTkEntry(master=frame, placeholder_text="Username")
        user_entry.pack(pady=12, padx=10)
        user_pass = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
        user_pass.pack(pady=12, padx=10)
        button = ctk.CTkButton(master=frame, text='Login', command=login)
        button.pack(pady=12, padx=10)
        app.mainloop()

    def new_window(self):
        record_manager = CriminalRecord()
        record_manager.load_records()
        def show_label():
            label = ctk.CTkLabel(window, text="Press 'a' to close", fg_color="transparent", font=("Arial", 8), height=30, width=100)
            label.place(relx=0.5, rely=0.97, anchor='center')

        def new_record():
            window1 = ctk.CTk()
            ctk.set_appearance_mode("dark") 
            app = InputApp(window1)  # Create an instance of InputApp
            window1.mainloop()      

        def add_record():
            window2 = ctk.CTk()
            window2.title('Animated Widgets')
            window2.geometry('600x400')
            ctk.set_appearance_mode("dark")
            frame = ctk.CTkScrollableFrame(master=window2, width=400, height=400, corner_radius=10, orientation="vertical", label_text="Add/update the data base", label_font=("Arial", 20))
            frame.pack(pady=20, padx=40, fill='both', expand=True)
    
            id_label = ctk.CTkLabel(master=frame, text="ID", fg_color="transparent")
            id_entry = ctk.CTkEntry(master=frame, placeholder_text="enter the criminal id", width=200)
            name_label = ctk.CTkLabel(master=frame, text="Name", fg_color="transparent")
            name = ctk.CTkEntry(master=frame, placeholder_text="enter the criminals name", width=200)
            address_label = ctk.CTkLabel(master=frame, text="Address", fg_color="transparent")
            address = ctk.CTkEntry(master=frame, placeholder_text="enter the criminals address", width=200)
            offense_label = ctk.CTkLabel(master=frame, text="Offense", fg_color="transparent")
            offense = ctk.CTkEntry(master=frame, placeholder_text="enter the offense committed", width=200)
            sentencing_label = ctk.CTkLabel(master=frame, text="Sentencing", fg_color="transparent")
            sentencing = ctk.CTkEntry(master=frame, placeholder_text="Enter the time to be served (in years): ", width=250)

            id_label.pack(pady=12, padx=10)
            id_entry.pack()
            name_label.pack(pady=12, padx=10)
            name.pack()
            address_label.pack(pady=12, padx=10)
            address.pack()
            offense_label.pack(pady=12, padx=10)
            offense.pack()
            sentencing_label.pack(pady=12, padx=10)
            sentencing.pack()

            window2.mainloop()


        def delete_record():
            
            window3 = ctk.CTk()
            window3.title('delete records')
            window3.geometry('600x400')
            ctk.set_appearance_mode("dark")
            frame=ctk.CTkFrame(window3,width=200,height=200)
            frame.pack(pady=20, padx=40, fill='both', expand=True)

            frame2=ctk.CTkFrame(window3,width=200,height=200)
            frame2.pack(pady=20, padx=40, fill='both', expand=True)
            ID_lable=ctk.CTkLabel(master=frame,text="Delete criminal record",font=("Arial",20))
            ID=ctk.CTkEntry(master=frame,placeholder_text="enter the criminal id to be deleted",width=200,height=50)
        
            ID_lable.pack(pady=12, padx=10)
            ID.pack()
            window3.mainloop()

        def find_record():
            def button():
                lab=ctk.CTkLabel(master=frame,text="pressed")
                lab.pack(pady=12, padx=10)
            window3 = ctk.CTk()
            window3.title('find records')
            window3.geometry('600x400')
            ctk.set_appearance_mode("dark")
            frame=ctk.CTkFrame(window3,width=200,height=200)
            frame.pack(pady=20, padx=40, fill='both', expand=True)

            frame2=ctk.CTkFrame(window3,width=200,height=200)
            frame2.pack(pady=20, padx=40, fill='both', expand=True)

            ID_lable=ctk.CTkLabel(master=frame,text="Find criminal record",font=("Arial",20))
            ID=ctk.CTkEntry(master=frame,placeholder_text="enter the criminal id to be found",width=200,height=50)
            ID.bind("<Return>",button)
            ID_lable.pack(pady=12, padx=10)
            ID.pack()
            window3.mainloop()
        
        def display_records():
            window4 = ctk.CTk()
            window4.title('Find Records')
            window4.geometry('600x400')
            ctk.set_appearance_mode("dark")

            # Create a frame within the window
            frame = ctk.CTkFrame(window4, width=200, height=200)
            frame.pack(pady=20, padx=40, fill='both', expand=True)
            ctk.CTkLabel(master=frame, text=f"All Criminal Records", font=("Arial", 30, 'bold'))

            # Get the JSON data string from the record manager
            data_string = record_manager.display_all()
            data_dict = json.loads(data_string)
           

            for key, value in data_dict.items():
                key_label = ctk.CTkLabel(master=frame, text=f"{key} : {value}", font=("Arial", 20, 'bold'))
                key_label.pack(anchor='w', pady=5, padx=10,fill="y")
                
            window4.mainloop()


        
        def call_fun():
            show_label()
            data_string=record_manager.facial_recog()
            def exit():
                frame.pack_forget()
            data_dict = json.loads(data_string)
            frame = ctk.CTkScrollableFrame(master=window, width=40, height=400, corner_radius=10, orientation="vertical", label_text="Facial recognition", label_font=("Arial", 20))
            frame.pack(pady=40, padx=20,expand="true",fill="both")
           

            for key, value in data_dict.items():
                key_label = ctk.CTkLabel(master=frame, text=f"{key} : {value}", font=("Arial", 20, 'bold'))
                key_label.pack(anchor='w', pady=5, padx=10,fill="y")

            

            ctk.CTkButton(frame, text='exit',
                           corner_radius=10, 
                           fg_color="red",
                           command=exit).pack(expand=True, fill='both', pady=10)
        def Exit_window():
            window.destroy()

    

        
        window = ctk.CTk()
        window.title('Criminal dectection system')
        window.geometry('600x400')
        ctk.set_appearance_mode("dark")
        
        animated_panel = SlidePanel(window, 1.0, 0.7)
        ctk.CTkLabel(animated_panel, text='MENU').pack(expand=True, fill='both', padx=2, pady=10)
        ctk.CTkButton(animated_panel, text='Create a new criminal record', corner_radius=0, command=new_record).pack(expand=True, fill='both', pady=10)
        ctk.CTkButton(animated_panel, text='Add/update criminal record', corner_radius=0, command=add_record).pack(expand=True, fill='both', pady=10)
        ctk.CTkButton(animated_panel, text='Delete a given record', corner_radius=0, command=delete_record).pack(expand=True, fill='both', pady=10)
        ctk.CTkButton(animated_panel, text='Search a given record', corner_radius=0,command=find_record).pack(expand=True, fill='both', pady=10)
        ctk.CTkButton(animated_panel, text='Display all the records', corner_radius=0,command=display_records).pack(expand=True, fill='both', pady=10)
        ctk.CTkButton(animated_panel, text='EXIT', corner_radius=0,command=Exit_window).pack(expand=True, fill='both', pady=10)

        button_x = 0.5
        rec_button = ctk.CTkButton(window, text="Facial recognition", font=("Arial", 20), height=100, width=100, anchor="center", command=call_fun)
        rec_button.place(relx=button_x, rely=0.5, x=-85, y=-130)
        button = ctk.CTkButton(window, text='More options', command=animated_panel.animate)
        button.place(relx=button_x, rely=0.5, anchor='center')
        

        window.mainloop()
        return new_record,add_record,delete_record,find_record
    
    

if __name__ == "__main__":
    MainGUI()

