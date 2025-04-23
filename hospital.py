import tkinter as tk
from tkinter import ttk, messagebox
import pymysql

class HospitalManagement:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Management System")
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.width}x{self.height}+0+0")

        # Title Label
        title = tk.Label(self.root, text="Hospital Management System", bd=4, relief="raised", bg="gray", fg="white", font=("Elephant", 40, "italic"))
        title.pack(side="top", fill="x")

        # Admission Form Frame
        admitFrame = tk.Frame(self.root, bd=5, relief="ridge", bg=self.clr(150, 150, 230))
        admitFrame.place(width=self.width/3, height=self.height-180, x=20, y=100)

        # Entry Fields
        labels = {
            "Enter_ID": "id",
            "Enter_Name": "name",
            "b_group": "b_group",
            "disease": "disease",
            "medicine": "medicine",
            "point": "point",
            "addr": "addr"
        }
        self.entries = {}

        for i, (label_text, col_name) in enumerate(labels.items()):
            label = tk.Label(admitFrame, text=label_text + ":", bg=self.clr(150, 150, 230), font=("Arial", 15, "bold"))
            label.grid(row=i, column=0, padx=20, pady=5, sticky="w")
            entry = tk.Entry(admitFrame, width=20, bd=3, font=("Arial", 15, "bold"))
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[col_name] = entry  # Map entry fields to column names

        # Buttons Frame
        btnFrame = tk.Frame(admitFrame, bg=self.clr(150, 150, 230))
        btnFrame.grid(row=len(labels), column=0, columnspan=2, pady=20)

        buttons = [
            ("Admit", self.admitFun, "light gray"),
            ("Delete", self.deleteFun, "red"),
            ("Search", self.searchFun, "yellow"),
            ("Refresh", self.updateTable, "green"),
            ("Discharge", self.dischargeFun, "blue"),
        ]

        for i, (text, command, color) in enumerate(buttons):
            tk.Button(btnFrame, text=text, command=command, width=15, bd=3, bg=color, font=("Arial", 13, "bold")).grid(row=i//3, column=i%3, padx=5, pady=5)

        # Details Table Frame
        self.detFrame = tk.Frame(self.root, bd=5, relief="ridge", bg=self.clr(150, 230, 120))
        self.detFrame.place(width=self.width - self.width/3 - 60, height=self.height-180, x=self.width/3+40, y=100)

        self.table = ttk.Treeview(self.detFrame, columns=("ID", "Name", "b_group", "disease", "point", "medicine", "addr"), show='headings')
        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, width=100)
        self.table.pack(fill="both", expand=True)

        self.updateTable()

    # Database Connection
    def dbFun(self):
        self.con = pymysql.connect(host="localhost", user="root", password="sami123", database="rec")
        self.cur = self.con.cursor()

    # Admit New Patient
    def admitFun(self):
        data = {key: entry.get().strip() for key, entry in self.entries.items()}
        if all(data.values()):
            try:
                self.dbFun()
                self.cur.execute("SELECT id FROM hospital1 WHERE id=%s", (data["id"],))
                if self.cur.fetchone():
                    messagebox.showerror("Error", "ID already exists. Use a unique ID!")
                    return

                self.cur.execute("""
                    INSERT INTO hospital1 (id, name, b_group, disease, point, medicine, addr)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    data["id"], data["name"], data["b_group"],
                    data["disease"], data["point"], data["medicine"], data["addr"]
                ))
                self.con.commit()
                messagebox.showinfo("Success", f"Patient {data['name']} admitted successfully!")
                self.clearFun()
                self.updateTable()
            except Exception as e:
                messagebox.showerror("Error", f"Database Error: {e}")
            finally:
                self.con.close()
        else:
            messagebox.showerror("Error", "Please Fill All Input Fields!")

    # **Fixed Search Function**
    def searchFun(self):
        search_data = {key: entry.get().strip() for key, entry in self.entries.items() if entry.get().strip()}
        if not search_data:
            messagebox.showerror("Error", "Please enter at least one search field!")
            return

        try:
            self.dbFun()
            query = "SELECT * FROM hospital1 WHERE " + " AND ".join(f"{key}=%s" for key in search_data.keys())
            self.cur.execute(query, tuple(search_data.values()))
            rows = self.cur.fetchall()
            self.con.close()

            self.table.delete(*self.table.get_children())
            if rows:
                for row in rows:
                    self.table.insert("", tk.END, values=row)
            else:
                messagebox.showerror("Error", "No matching records found!")
        except Exception as e:
            messagebox.showerror("Error", f"Search Error: {e}")

    # Discharge Patient
    def dischargeFun(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a record to discharge!")
            return
        item = self.table.item(selected_item)
        selected_id = item["values"][0]

        try:
            self.dbFun()
            self.cur.execute("DELETE FROM hospital1 WHERE id=%s", (selected_id,))
            self.con.commit()
            messagebox.showinfo("Success", f"Patient with ID {selected_id} discharged!")
            self.updateTable()
        except Exception as e:
            messagebox.showerror("Error", f"Could not discharge: {e}")
        finally:
            self.con.close()

    # Delete Patient Record
    def deleteFun(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a record to delete!")
            return
        item = self.table.item(selected_item)
        selected_id = item["values"][0]
        try:
            self.dbFun()
            self.cur.execute("DELETE FROM hospital1 WHERE id=%s", (selected_id,))
            self.con.commit()
            messagebox.showinfo("Success", f"Record with ID {selected_id} deleted!")
            self.updateTable()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete: {e}")
        finally:
            self.con.close()

    # Refresh Table
    def updateTable(self):
        try:
            self.dbFun()
            self.cur.execute("SELECT id, name, b_group, disease, point, medicine, addr FROM hospital1")
            rows = self.cur.fetchall()
            self.con.close()
            self.table.delete(*self.table.get_children())
            for row in rows:
                self.table.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Database Error: {e}")

    # Clear Input Fields
    def clearFun(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    # RGB to Hex Color Converter
    def clr(self, r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

root = tk.Tk()
obj = HospitalManagement(root)
root.mainloop()
