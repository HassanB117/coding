import tkinter as tk
from time import strftime

# Create a window
root = tk.Tk()
root.title("Digital Clock")

# Function to update time
def time():
    string = strftime('%H:%M:%S %p')
    label.config(text=string)
    label.after(1000, time)  # Update time every 1000 milliseconds (1 second)

# Label to display time
label = tk.Label(root, font=('calibri', 40, 'bold'), background='purple', foreground='white')
label.pack(anchor='center')

# Call the time function initially
time()

# Run the tkinter event loop
root.mainloop()
