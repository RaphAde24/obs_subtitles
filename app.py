from tkinter import *
import cv2
from PIL import Image, ImageTk
from vosk import Model, KaldiRecognizer
import pyaudio

# Vosk model path (you can download one from https://alphacephei.com/vosk/models)


class CameraApp:
    def __init__(self, root):
        MODEL_PATH = "assets/audio_model/vosk-model-small-en-us-0.15"

# Initialize Vosk
        self.model = Model(MODEL_PATH)
        self.rec = KaldiRecognizer(self.model, 16000) 

        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        self.stream.start_stream()

        self.cur_subs = StringVar()

        # Initialisiere die Hauptanwendung
        self.root = root
        self.root.title("Camera App")
        self.root.geometry("1920x1080")
        self.root.bind('<Escape>', lambda e: self.quit_app())

        # Kamera-Setup
        self.vid = cv2.VideoCapture(0)
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        frame_width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        frame_height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.h_w=frame_height/frame_width
        fps = self.vid.get(cv2.CAP_PROP_FPS)
        print(frame_height, frame_width,fps)
        self.prev_width=800
        self.prev_height=int(self.h_w*self.prev_width)
        
        #subtitles
        self.cur_subs.set("beispiel text")

        self.root.columnconfigure(0,weight=1)
        self.root.columnconfigure(1,weight=0)
        self.root.rowconfigure((0),weight=1)
        left_frame=Frame(self.root, bg="#222831")
        left_frame.grid(row=0,column=0, sticky="nswe")
        
        right_frame=Frame(self.root, bg="blue")
        right_frame.grid(row=0,column=1, sticky="nswe")
        
        cameraframe=Frame(right_frame, bg="green",width=self.prev_width,height=self.prev_height)
        cameraframe.grid(row=0,column=0)
        # Label für die Videoanzeige
        self.label_widget = Label(right_frame,borderwidth=0)
        

        # Button zum Starten des Streams
        self.start_button = Button(left_frame, text="Open Camera", command=self.start_preview)
        self.start_button.grid(row=0,column=0)

    def start_preview(self):
        self.label_widget.grid(row=0,column=0)
        self.open_camera()
        self.update_text()

    def open_camera(self):

        # Lese ein Frame von der Kamera
        ret, frame = self.vid.read()
        
        if not ret:
            print("Kamera konnte kein Frame lesen. Versuche, sie neu zu initialisieren...")
            self.vid.release()
            self.vid = cv2.VideoCapture(0)
            self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            return

        if ret:
            # Konvertiere das Bild in das richtige Farbformat
            preview_frame = cv2.resize(frame, (self.prev_width, self.prev_height))
            opencv_image = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGBA)

            text = self.cur_subs.get()
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.5
            thickness = 1
            color = (255, 255, 255)  # Weiß

            # Textgröße berechnen
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            text_width, text_height = text_size

            # Position berechnen, um den Text zu zentrieren
            text_x = (self.prev_width - text_width) // 2
            text_y = (self.prev_height - text_height)

            # Text auf das Bild zeichnen
            pre_image = cv2.putText(opencv_image, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

            captured_image = Image.fromarray(pre_image)
            # Konvertiere das Bild in ein PhotoImage-Objekt
            photo_image = ImageTk.PhotoImage(image=captured_image)

            # Zeige das Bild im Label an
            self.label_widget.photo_image = photo_image
            self.label_widget.configure(image=photo_image)

        self.label_widget.after(10, self.open_camera)
    
    def update_text(self):
        data = self.stream.read(4000, exception_on_overflow=False)
        if self.rec.AcceptWaveform(data):
            result = self.rec.Result()  # This is still a JSON string
            # But Vosk always puts the full text under "text"
            text_start = result.find('"text" : "') + len('"text" : "')
            text_end = result.find('"', text_start)
            spoken_text = result[text_start:text_end] if text_start != -1 and text_end != -1 else ""
            self.cur_subs.set(spoken_text)
        else:
            partial = self.rec.PartialResult()
            partial_start = partial.find('"partial" : "') + len('"partial" : "')
            partial_end = partial.find('"', partial_start)
            partial_text = partial[partial_start:partial_end] if partial_start != -1 and partial_end != -1 else ""
            self.cur_subs.set(partial_text)

        root.after(250, self.update_text)  # Call again after 100ms
        
    def quit_app(self):
        # Beende die Anwendung und gib die Kamera frei
        if self.vid.isOpened():
            self.vid.release()
        self.root.quit()


if __name__ == "__main__":
    root = Tk()
    app = CameraApp(root)
    root.mainloop()