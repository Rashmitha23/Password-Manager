#Importing required Libraries
import sqlite3, hashlib
import base64
from tkinter import *
from tkinter import simpledialog
from functools import partial
from cryptography.hazmat.backends import default_backend



backend = default_backend()
salt = b'2444'

#creating database, here I used sqlite

with sqlite3.connect('password_manager.db') as db:
    cursor = db.cursor()

#Creating table name called masterpassword to store user's master passwords only in encryption form.

cursor.execute("""
CREATE TABLE IF NOT EXISTS masterpassword(
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT NOT NULL
);
""")


#Creating table name called vault to store user's requried website passwords only in encryption form.

cursor.execute("""
CREATE TABLE IF NOT EXISTS vault(
id INTEGER PRIMARY KEY,
website TEXT NOT NULL,
username TEXT NOT NULL,
password TEXT NOT NULL);
""")

#Creating PopUp window

def popUp(text):
    answer = simpledialog.askstring("input string", text)

    return answer

#Initiating window and title as Password Manager

window = Tk()
window.update()

window.title("Password Manager")



#creating first GUI Screen(login page)
def firstTimeScreen():
    cursor.execute('DELETE FROM vault')
        
    for widget in window.winfo_children():
        widget.destroy()
        
    #creating text entries and buttons with various sizes and colors.

    window.geometry('600x250')
    lbl = Label(window, text="Enter username")
    lbl.config(anchor=CENTER)
    lbl.pack(pady=5)

    txt = Entry(window, width=20, bg='#90EE90')
    txt.pack()
    txt.focus()

    lbl1 = Label(window, text="enter password")
    lbl1.config(anchor=CENTER)
    lbl1.pack(pady=5)
    
    txt1 = Entry(window, width=20,  bg='#90EE90')
    txt1.pack()
    
    lbl2 = Label(window, text="enter confirm password")
    lbl2.config(anchor=CENTER)
    lbl2.pack(pady=5)

    txt2 = Entry(window, width=20, bg='#90EE90')
    txt2.pack()
   
    def savePassword():
        if txt1.get() == txt2.get():
            sql = "DELETE FROM masterpassword WHERE id = 1"
            cursor.execute(sql)
            entered_password = txt.get()
            entered_hashed_password = hashlib.sha256(entered_password.encode()).hexdigest()
            cursor.execute('SELECT * FROM masterpassword WHERE id = 1 AND password = ?', (entered_hashed_password,))
            
            master_password = txt1.get()
            hashed_password = hashlib.sha256(master_password.encode()).hexdigest()
            insert_password = """INSERT INTO masterpassword(username, password) VALUES(?, ?) """
            cursor.execute(insert_password, ('admin', hashed_password))
            db.commit()
            vaultScreen()
        else:
            lbl.config(text="Passwords doesnot match", fg='red')
            
        

    btn = Button(window, text="Save Master Password", command=savePassword, bg='#90EE90', fg='black' )
    btn.pack(pady=10)
    

#Now, login screen creation.
def loginScreen():
    for widget in window.winfo_children():
        widget.destroy()

    window.geometry('600x250')
    lbl = Label(window, text="Enter username")
    lbl.config(anchor=CENTER)
    lbl.pack(pady=10)
    
    txt = Entry(window, width=20, bg='#90EE90')
    txt.pack()
    txt.focus()
    
    lbl = Label(window, text="Enter password")
    lbl.config(anchor=CENTER)
    lbl.pack(pady=10)

    txt = Entry(window, width=20, bg='#90EE90')
    txt.pack()
    txt.focus()

    lbl1 = Label(window)
    lbl1.config(anchor=CENTER)
    lbl1.pack(side=TOP)
    def getMasterPassword(entered_password):
        entered_hashed_password = hashlib.sha256(entered_password.encode()).hexdigest()
        cursor.execute('SELECT * FROM masterpassword WHERE id = 1 AND password = ?', (entered_hashed_password,))
        return cursor.fetchall()

    def checkPassword():
        entered_password = txt.get()
        password = getMasterPassword(entered_password)

        if password:
            vaultScreen()
        else:
            txt.delete(0, 'end')
            lbl1.config(text="Wrong Password", fg='red')
    btn = Button(window, text="Submit", command=checkPassword, bg='#90EE90', fg='black')
    btn.pack(pady=3)

#The function vaultscreen will gives users to add passwords and username for particular website.
def vaultScreen():
    for widget in window.winfo_children():
        widget.destroy()

    def addEntry():
        text1 = "Website"
        text2 = "Username"
        text3 = "Password"
        website = popUp(text1)
        username = popUp(text2)
        password = popUp(text3)
        #Storing in database
        insert_fields = """INSERT INTO vault(website, username, password) 
        VALUES(?, ?, ?) """
        cursor.execute(insert_fields, (website, username, password))
        db.commit()

        vaultScreen()
    #If user want to delete the entry, user can do and the function removeEntry will update in the database.
    def removeEntry(input):
        cursor.execute("DELETE FROM vault WHERE id = ?", (input,))
        db.commit()
        vaultScreen()
    # ... (previous code)

    def updateEntry(entry_id):
        # Fetch the current entry details
        cursor.execute("SELECT * FROM vault WHERE id = ?", (entry_id,))
        current_entry = cursor.fetchone()

        # Create a new window for updating the entry
        update_window = Tk()
        update_window.title("Update Entry")

        # Add entry fields to update entry details
        website_var = StringVar(update_window, value=current_entry[1])
        username_var = StringVar(update_window, value=current_entry[2])
        password_var = StringVar(update_window, value=current_entry[3])

        lbl1 = Label(update_window, text="Website")
        lbl1.grid(row=0, column=0)
        entry1 = Entry(update_window, textvariable=website_var)
        entry1.grid(row=0, column=1)

        lbl2 = Label(update_window, text="Username")
        lbl2.grid(row=1, column=0)
        entry2 = Entry(update_window, textvariable=username_var)
        entry2.grid(row=1, column=1)

        lbl3 = Label(update_window, text="Password")
        lbl3.grid(row=2, column=0)
        entry3 = Entry(update_window, textvariable=password_var)
        entry3.grid(row=2, column=1)

        def saveChanges():
            # Update the entry details in the database
            updated_website = website_var.get()
            updated_username = username_var.get()
            updated_password = password_var.get()

            cursor.execute("""
                UPDATE vault
                SET website=?, username=?, password=?
                WHERE id=?
            """, (updated_website, updated_username, updated_password, entry_id))

            db.commit()
            update_window.destroy()
            vaultScreen()

        # Add a button to save changes
        btn_save = Button(update_window, text="Save Changes", command=saveChanges)
        btn_save.grid(row=3, column=0, columnspan=2, pady=10)
    


    # Function to perform search
    def searchEntries():
        search_query = search_var.get().lower()
        cursor.execute("SELECT * FROM vault WHERE LOWER(website) LIKE ? OR LOWER(username) LIKE ? OR LOWER(password) LIKE ?", 
                       ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
        results = cursor.fetchall()

        # Clear the existing entries on the screen
        for widget in window.winfo_children():
            widget.destroy()

        # Display the search results
        displayEntries(results)

    def displayEntries(entries):
        lbl_website = Label(window, text="Website", font=("Arial", 12))
        lbl_website.grid(row=2, column=0, padx=80)
        lbl_username = Label(window, text="Username", font=("Arial", 12))
        lbl_username.grid(row=2, column=1, padx=80)
        lbl_password = Label(window, text="Password", font=("Arial", 12))
        lbl_password.grid(row=2, column=2, padx=80)

        # Display entries
        for i, entry in enumerate(entries, start=3):
            lbl1 = Label(window, text=entry[1], font=("Arial", 12))
            lbl1.grid(column=0, row=i)
            lbl2 = Label(window, text=entry[2], font=("Arial", 12))
            lbl2.grid(column=1, row=i)
            lbl3 = Label(window, text=entry[3], font=("Arial", 12))
            lbl3.grid(column=2, row=i)

            # Buttons for delete and update
            btn_delete = Button(window, text="Delete", command=partial(removeEntry, entry[0]), bg='#90EE90', fg='black')
            btn_delete.grid(column=3, row=i, pady=10, padx=50)

            btn_update = Button(window, text="Update", command=lambda e=entry[0]: updateEntry(e), bg='#90EE90', fg='black')
            btn_update.grid(column=4, row=i, pady=10, padx=50)

    # Add a search bar and button
    search_var = StringVar()
    search_entry = Entry(window, textvariable=search_var, width=30, bg='#90EE90')
    search_entry.grid(row=1, column=1, padx=10, pady=10)

    search_button = Button(window, text="Search", command=searchEntries, bg='#90EE90', fg='black')
    search_button.grid(row=1, column=2, pady=10)

    # Display all entries initially
    cursor.execute('SELECT * FROM vault')
    displayEntries(cursor.fetchall())



        

    #creating window screen for passwords storage for user.
    window.geometry('750x550')
    window.resizable(height=None, width=None)
    
    
    #Button to add new entry.
    btn = Button(window, text="Add a New Entry", command=addEntry, bg='#90EE90', fg='black')
    btn.grid(column=1, pady=(10,20))
    

    # Here, I used grid to create columns for website,username,password.
    lbl = Label(window, text="Website")
    lbl.grid(row=2, column=0, pady=(20,10))
    lbl = Label(window, text="Username")
    lbl.grid(row=2, column=1, pady=(20,10))
    lbl = Label(window, text="Password")
    lbl.grid(row=2, column=2, pady=(20,10))
    #To Retrive data.
    cursor.execute('SELECT * FROM vault')
    if (cursor.fetchall() != None):
        i = 0
        while True:
            cursor.execute('SELECT * FROM vault')
            array = cursor.fetchall()

            if (len(array) == 0):
                break
            lbl1 = Label(window, text=(array[i][1]), font=("Arial", 12))
            lbl1.grid(column=0, row=(i+3))
            lbl2 = Label(window, text=(array[i][2]), font=("Arial", 12))
            lbl2.grid(column=1, row=(i+3))
            lbl3 = Label(window, text=(array[i][3]), font=("Arial", 12))
            lbl3.grid(column=2, row=(i+3))
            # Creating button to delete and update entries.
            btn = Button(window, text="Delete", command=  partial(removeEntry, array[i][0]), bg='#90EE90', fg='black')
            btn.grid(column=3, row=(i+3), pady=10, padx=50)
            # Inside the vaultScreen function, update the "Update" button command
            btn_update = Button(window, text="Update", command=lambda i=array[i][0]: updateEntry(i), bg='#90EE90', fg='black')
            btn_update.grid(column=4, row=(i+3), pady=10, padx=50)
                    
            i = i +1
            cursor.execute('SELECT * FROM vault')
            if (len(cursor.fetchall()) <= i):
                break
#Using a database cursor, this line runs a SQL query to select all records (SELECT *) from the "masterpassword" table. 
cursor.execute('SELECT * FROM masterpassword')
#All of the output from the SQL query that was run in the previous stage is retrieved by this line. The if statement determines whether any results exist. The program moves on to the next line if the condition evaluates to True and there are records in the "masterpassword" database goes to login page.
if (cursor.fetchall()):
    loginScreen()
#else goes to creating masterpassword page(firstscreen).
else:
    firstTimeScreen()
window.mainloop()
