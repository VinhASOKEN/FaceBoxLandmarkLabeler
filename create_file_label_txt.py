import os

folder_path = R"C:\Users\vietl\OneDrive\Desktop\Gannhan\data_faces"

for filename in os.listdir(folder_path):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(folder_path, filename)
        
        txt_filename = os.path.splitext(filename)[0] + '.txt'
        txt_path = os.path.join(folder_path, txt_filename)
        
        with open(txt_path, 'w') as txt_file:
            continue