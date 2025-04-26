import customtkinter

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x150")
    	
       # self.grid_columnconfigure(1,2)=
        

    def button_callbck(self):
        print("button clicked")

app = App()
app.mainloop()