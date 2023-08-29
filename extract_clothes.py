import os

folder_path = '/home/cuongvt/AIoT-tech/Virtual-try-on/SE-Virtual-try-on/dataset/VITON-HD/test/image'

with open('demo.txt', "w") as txt_file:
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            txt_file.write(f"input.png {filename}\n")