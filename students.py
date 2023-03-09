import tkinter as tk
from tkinter import messagebox

import pymongo

from subjectform import SubjectForm
from teacherform import TeacherForm

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient['enrollmentsystem']
collection = mydb["students"]

sId = 0
cId = 0

dbList = list()
cloneEnrollList = list()


def callback(event):
    li = list()
    li = event.widget._values
    studentId.set(dbList[li[1]][0])
    studentName.set(dbList[li[1]][1])
    studentEmail.set(dbList[li[1]][2])
    studentProgram.set(dbList[li[1]][3])
    global sId
    sId = dbList[li[1]][0]
    createSubjectGrid(1)
    createSubjectGrid(0)


def callback2(event):
    li = list()
    li = event.widget._values
    global cId
    cId = cloneEnrollList[li[1]][0]


def createGrid(x):
    dbList.clear()
    dbList.append(["ID", "NAME", "EMAIL", "PROGRAM", "TOTAL UNITS"])
    studentsCursor = collection.aggregate(
        [
            {"$match": {}},
            {
                "$lookup": {
                    "from": "courses",
                    "localField": "enrolled",
                    "foreignField": "id",
                    "as": "subjects",
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "studid": 1,
                    "studname": 1,
                    "studemail": 1,
                    "studcourse": 1,
                    "totalUnits": {"$sum": "$subjects.units"},
                }
            },
        ]
    )
    for entry in studentsCursor:
        entryId = entry["studid"]
        entryName = entry["studname"]
        entryEmail = entry["studemail"]
        entryProgram = entry["studcourse"]
        entryTotalUnits = entry["totalUnits"]
        dbList.append([entryId, entryName, entryEmail, entryProgram, entryTotalUnits])

    for i in range(len(dbList)):
        for j in range(len(dbList[0])):
            mgrid = tk.Entry(window, width=10)
            mgrid.insert(tk.END, dbList[i][j])
            mgrid._values = mgrid.get(), i
            mgrid.grid(column=j + 6, row=i + 7)
            mgrid.bind("<Button-1>", callback)

    if x == 1:
        for label in window.grid_slaves():
            if int(label.grid_info()["row"] > 6):
                label.grid_forget()


def createSubjectGrid(x):
    enrolledList = list()
    enrolledList.append(["ID", "CODE", "DESCRIPTION", "UNITS", "SCHEDULE"])

    coursesCursor = collection.aggregate(
        [
            {"$match": {"studid": sId}},
            {
                "$lookup": {
                    "from": "subject",
                    "localField": "enrolled",
                    "foreignField": "id",
                    "as": "subjects",
                }
            },
            {"$unwind": {"path": "$subjects", "preserveNullAndEmptyArrays": True}},
            {"$project": {"_id": 0, "subjects": 1}},
        ]
    )
    for entry in coursesCursor:
        if len(entry) == 0:
            break
        entrySubId = entry["subjects"]["id"]
        entrySubCode = entry["subjects"]["code"]
        entrySubDesc = entry["subjects"]["description"]
        entrySubUnits = entry["subjects"]["units"]
        entrySubSched = entry["subjects"]["schedule"]
        enrolledList.append(
            [entrySubId, entrySubCode, entrySubDesc, entrySubUnits, entrySubSched]
        )
        global cloneEnrollList
        cloneEnrollList = enrolledList

    for i in range(len(enrolledList)):
        for j in range(len(enrolledList[0])):
            mgrid = tk.Entry(window, width=10)
            mgrid.insert(tk.END, enrolledList[i][j])
            mgrid._values = mgrid.get(), i
            mgrid.grid(column=j + 15, row=i + 7)
            mgrid.bind("<Button-1>", callback2)

    if x == 1:
        for label in window.grid_slaves():
            if int(label.grid_info()["row"] > 7) and int(
                label.grid_info()["column"] > 14
            ):
                label.grid_forget()


def save():
    option = messagebox.askokcancel("Save", "Save entry to record?")
    if option:
        newId = collection.count_documents({})
        if newId > 0:
            newId = collection.find_one(sort=[("id", -1)])["id"]
        id = newId + 1
        studentId.set(id)
        insertDict = {
            "studid": int(studentId.get()),
            "studname": nameField.get(),
            "studemail": emailField.get(),
            "studcourse": programField.get(),
        }
        collection.insert_one(insertDict)
        createGrid(1)
        createGrid(0)


def delete():
    option = messagebox.askokcancel("Delete", "Delete record entry?")
    if option:
        delQuery = {"id": int(idField.get())}
        collection.delete_one(delQuery)
        createGrid(1)
        createGrid(0)


def update():
    option = messagebox.askokcancel("Update", "Update an entry?")
    if option:
        idQuery = {"id": int(idField.get())}
        updateValues = {
            "$set": {
                "name": nameField.get(),
                "email": emailField.get(),
                "program": programField.get(),
            }
        }
        collection.update_one(idQuery, updateValues)
        createGrid(1)
        createGrid(0)


def studentFilter():
    for label in window.grid_slaves():
        if int(label.grid_info()["row"] > 6):
            label.grid_forget()

    filterId = int(idFilterField.get())

    idOption = str()

    dbList.clear()
    dbList.append(["ID", "NAME", "EMAIL", "PROGRAM"])
    if idFilterOption.get() == ">":
        idOption = "$gt"
    elif idFilterOption.get() == ">=":
        idOption = "$gte"
    elif idFilterOption.get() == "<":
        idOption = "$lt"
    elif idFilterOption.get() == "<=":
        idOption = "$lte"
    elif idFilterOption.get() == "!=":
        idOption = "$ne"
    elif idFilterOption.get() == "=":
        idOption = "$eq"
    nameStart = f"^{nameStartFilter.get()}"
    nameEnd = f"{nameEndFilter.get()}$"
    mailStart = f"^{mailStartFilter.get()}"
    program = f"^{programFilter.get()}"
    studentsCursor = collection.find(
        {
            "studid": {idOption: filterId},
            "$and": [{"studname": {"$regex": nameStart}}, {"studname": {"$regex": nameEnd}}],
            "studemail": {"$regex": mailStart},
            "studcourse": {"$regex": program},
        }
    )
    for entry in studentsCursor:
        studid = str(entry["studid"])
        studname = str(entry["studname"].encode("utf-8").decode("utf-8"))
        studemail = str(entry["studemail"].encode("utf-8").decode("utf-8"))
        studcourse = str(entry["studcourse"].encode("utf-8").decode("utf-8"))
        dbList.append([studid,studname,studemail,studcourse])

    for i in range(len(dbList)):
        for j in range(len(dbList[0])):
            mgrid = tk.Entry(window, width=10)
            mgrid.insert(tk.END, dbList[i][j])
            mgrid._values = mgrid.get(), i
            mgrid.grid(column=j + 6, row=i + 7)
            mgrid.bind("<Button-1>", callback)


# TODO: Create enroll and drop functionality
def enrollSub():
    cId = SubjectForm.cId
    option = messagebox.askokcancel("Enroll", f"Enroll subject #{cId}")
    if option:
        searchQuery = {"studid": sId}
        updateQuery = {"$push": {"enrolled": cId}}
        collection.update_one(searchQuery, updateQuery)
        createGrid(1)
        createGrid(0)
        createSubjectGrid(1)
        createSubjectGrid(0)


def dropSub():
    option = messagebox.askokcancel("Drop", f"Drop subject #{cId}")
    if option:
        searchQuery = {"studid": sId}
        updateQuery = {"$pull": {"enrolled": cId}}
        collection.update_one(searchQuery, updateQuery)
        createGrid(1)
        createGrid(0)
        createSubjectGrid(1)
        createSubjectGrid(0)


# ! Window
window = tk.Tk()
window.title("Students Form")
window.geometry("1000x750")
window.configure(bg="#EEFCDF")
createGrid(0)


# ! End of Window

# ! Menubar
menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Subjects", command=SubjectForm.subjectform)
filemenu.add_command(label="Teachers", command=TeacherForm.teacherform)
filemenu.add_separator()
filemenu.add_command(label="Close", command=window.quit())

editmenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Edit", menu=editmenu)
editmenu.add_command(label="Undo", command=SubjectForm.subjectform)
editmenu.add_separator()
editmenu.add_command(label="Cut", command=TeacherForm.teacherform)

window.config(menu=menubar)

# ! End of Menubar

# ! Labels
titleBar = tk.Label(
    window,
    text="Students Enlistment Form",
    width=30,
    height=1,
    bg="white",
    anchor="center",
    font="Courier 14",
)
titleBar.grid(column=1, row=1, columnspan=2)

idLabel = tk.Label(
    window,
    text="Student ID:",
    width=15,
    height=1,
    bg="white",
    
)
idLabel.grid(column=1, row=2)

idLabel = tk.Label(
    window,
    text="Student Name:",
    width=15,
    height=1,
    bg="white",
    
)
idLabel.grid(column=1, row=3)

idLabel = tk.Label(
    window,
    text="Student E-mail:",
    width=15,
    height=1,
    bg="white",
    
)
idLabel.grid(column=1, row=4)

idLabel = tk.Label(
    window,
    text="Student Course:",
    width=15,
    height=1,
    bg="white",
    
)
idLabel.grid(column=1, row=5)

# ! End of Labels

# ! Enter Fields
studentId = tk.StringVar()
idField = tk.Entry(window, textvariable=studentId, state=tk.DISABLED)
idField.grid(column=2, row=2)

studentName = tk.StringVar()
nameField = tk.Entry(window, textvariable=studentName, width=40)
nameField.grid(column=2, row=3)

studentEmail = tk.StringVar()
emailField = tk.Entry(window, textvariable=studentEmail, width=40)
emailField.grid(column=2, row=4)

studentProgram = tk.StringVar()
programField = tk.Entry(window, textvariable=studentProgram, width=40)
programField.grid(column=2, row=5)

# ! End of Enter Fields

# ! Buttons
saveBtn = tk.Button(text="Save", command=save, width=25)
saveBtn.grid(column=1, row=6)

updateBtn = tk.Button(text="Update", command=update, width=25)
updateBtn.grid(column=2, row=6)

deleteBtn = tk.Button(text="Delete", command=delete, width=25)
deleteBtn.grid(column=3, row=6)

filterBtn = tk.Button(text="Filter", command=studentFilter, width=10, bg="white")
filterBtn.grid(column=10, row=6)

# ! End of Buttons

# ! Filters
filterLabel = tk.Label(
    window, text="Filters", bg="white", font="Courier", width=30
)
filterLabel.grid(column=6, row=2, columnspan=5)
# * ID Filter Option Menu
idFilterLabel = tk.Label(window, text="ID", bg="white")
idFilterLabel.grid(column=6, row=4)
idFilterOptions = [">", ">=", "<", "<=", "!=", "="]
idFilterOption = tk.StringVar(window)
idFilterOption.set(idFilterOptions[0])
idFilterDrpDwn = tk.OptionMenu(window, idFilterOption, *idFilterOptions)
idFilterDrpDwn.grid(column=6, row=5)

# * ID Filter Text Field
idFilter = tk.IntVar()
idFilterField = tk.Entry(window, textvariable=idFilter, width=10)
idFilterField.grid(column=6, row=6)

# * Name Start Text Field
nameStartLabel = tk.Label(window, text="Name Start", bg="white")
nameStartLabel.grid(column=7, row=3)
nameStartFilter = tk.StringVar()
nameStartFilterField = tk.Entry(window, textvariable=nameStartFilter, width=10)
nameStartFilterField.grid(column=7, row=4)

# * Name End Text Field
nameEndLabel = tk.Label(window, text="Name End", bg="white")
nameEndLabel.grid(column=7, row=5)
nameEndFilter = tk.StringVar()
nameEndFilterField = tk.Entry(window, textvariable=nameEndFilter, width=10)
nameEndFilterField.grid(column=7, row=6)

# * Mail Start Text Field
mailStartLabel = tk.Label(window, text="Mail Start", bg="white")
mailStartLabel.grid(column=8, row=5)
mailStartFilter = tk.StringVar()
mailStartFilterField = tk.Entry(window, textvariable=mailStartFilter, width=10)
mailStartFilterField.grid(column=8, row=6)

# * Program Text Field
programLabel = tk.Label(window, text="Program", bg="white")
programLabel.grid(column=9, row=5)
programFilter = tk.StringVar()
programFilterField = tk.Entry(window, textvariable=programFilter, width=10)
programFilterField.grid(column=9, row=6)

# ! End of Filters

# ! Subjects Table

# * Label/Title
subjectsLabel = tk.Label(
    window, text="Courses", bg="white", font="Courier", width=30
)
subjectsLabel.grid(column=14, row=2, columnspan=6)

# * Buttons
# TODO: Add "enroll" and "drop" buttons
enrollBtn = tk.Button(text="Enroll", command=enrollSub, width=10, bg="white")
enrollBtn.grid(row=5, column=15)

dropBtn = tk.Button(text="Drop", command=dropSub, width=10, bg="white")
dropBtn.grid(row=5, column=16)


# ! End of Subjects Table
window.mainloop()