import cv2
import pytesseract
from deep_translator import GoogleTranslator
from PIL import ImageGrab
import numpy as np
import threading
import time
from tkinter import Tk, Label, StringVar, OptionMenu, Button, Frame

# ตั้งค่าเส้นทาง pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ตัวแปรสำหรับพื้นที่ Crop
crop_rect = [0, 0, 0, 0]  # [x1, y1, x2, y2]
dragging = False  # สถานะการลาก

def select_crop_area():
    global crop_rect, dragging

    # ฟังก์ชันสำหรับ Mouse Event
    def draw_rectangle(event, x, y, flags, param):
        global crop_rect, dragging
        if event == cv2.EVENT_LBUTTONDOWN:  # กดคลิกซ้ายเพื่อเริ่มเลือก
            crop_rect[0], crop_rect[1] = x, y
            dragging = True
        elif event == cv2.EVENT_MOUSEMOVE and dragging:  # ลากเมาส์
            temp_image = image.copy()
            cv2.rectangle(temp_image, (crop_rect[0], crop_rect[1]), (x, y), (0, 255, 0), 2)
            cv2.imshow("Select Area", temp_image)
        elif event == cv2.EVENT_LBUTTONUP:  # ปล่อยคลิกซ้าย
            crop_rect[2], crop_rect[3] = x, y
            dragging = False
            cv2.destroyWindow("Select Area")

    # จับภาพหน้าจอ
    screen = ImageGrab.grab()
    image = np.array(screen)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # เปิดหน้าต่างให้ผู้ใช้เลือกพื้นที่
    cv2.imshow("Select Area", image)
    cv2.setMouseCallback("Select Area", draw_rectangle)
    cv2.waitKey(0)  # รอจนกว่าจะปิดหน้าต่าง

class TranslatorApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("Real-Time Translator")
        self.root.geometry("600x250")
        self.root.attributes('-topmost', True)  # ซ้อนทับหน้าจอ

        # สร้างกรอบหลักสำหรับ UI
        self.main_frame = Frame(self.root)
        self.main_frame.pack(pady=10)

        # ตัวแปรสำหรับเลือกภาษา
        self.selected_language = StringVar(self.root)
        self.selected_language.set("th")  # ค่าเริ่มต้นเป็นภาษาไทย
        self.languages = {
            "English": "en",
            "Thai": "th",
            "Japanese": "ja",
            "Chinese": "zh-CN",
            "Korean": "ko",
            "French": "fr",
            "German": "de",
            "Spanish": "es"
        }

        # Label สำหรับแสดงข้อความแปล
        self.result_label = Label(self.main_frame, text="Translated Text: ", wraplength=500, justify="left", font=("Arial", 12))
        self.result_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Dropdown Menu สำหรับเลือกภาษา
        self.language_menu = OptionMenu(
            self.main_frame, self.selected_language, *self.languages.values()
        )
        self.language_menu.grid(row=1, column=0, pady=10, sticky="w")

        # ปุ่มสำหรับเริ่มการเลือกพื้นที่ Crop
        self.select_area_button = Button(self.main_frame, text="Select Area", command=select_crop_area, width=20)
        self.select_area_button.grid(row=2, column=0, pady=10)

        # ปุ่มสำหรับเริ่มการแปล
        self.start_button = Button(self.main_frame, text="Start Translation", command=self.start_translation, width=20)
        self.start_button.grid(row=3, column=0, pady=10)

        # ปุ่มสำหรับหยุดการแปล
        self.stop_button = Button(self.main_frame, text="Stop Translation", command=self.stop_translation, width=20)
        self.stop_button.grid(row=4, column=0, pady=10)

        # เริ่ม GUI
        self.root.mainloop()

    def start_translation(self):
        self.running = True
        threading.Thread(target=self.translate_loop).start()

    def stop_translation(self):
        self.running = False
        self.result_label.config(text="Translated Text: ")  # เคลียร์ข้อความที่แสดง

    def translate_loop(self):
        global crop_rect
        while self.running:
            # จับภาพหน้าจอเฉพาะพื้นที่ที่เลือก
            if crop_rect[2] > crop_rect[0] and crop_rect[3] > crop_rect[1]:  # ตรวจสอบว่ากรอบถูกต้อง
                img = ImageGrab.grab(bbox=tuple(crop_rect))
                img_np = np.array(img)

                # OCR อ่านข้อความ
                text = pytesseract.image_to_string(img_np, lang="eng")

                # แปลข้อความ
                if text.strip():
                    target_language = self.selected_language.get()  # รับค่าภาษาจาก Dropdown
                    translated_text = GoogleTranslator(source='en', target=target_language).translate(text)
                    self.result_label.config(text=f"Translated Text: {translated_text}")
                else:
                    self.result_label.config(text="Translated Text: No text detected")

            time.sleep(1)  # หน่วงเวลาแปลทุก 1 วินาที

# เรียกโปรแกรม
if __name__ == "__main__":
    TranslatorApp()
