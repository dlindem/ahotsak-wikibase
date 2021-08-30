import tkinter as tk

gui = tk.Tk()
def handle_click(event):
    print("The button was clicked!")
button = tk.Button(
text = "Click me",
width = 25,
height = 5
)
button.bind("<Button-1>", handle_click)
button.pack()
gui.mainloop()
