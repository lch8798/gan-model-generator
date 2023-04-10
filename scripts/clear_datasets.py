import os

def remove_all_files(folder_path) -> int:
    file_len = 0
    for root, dirs, files in os.walk(folder_path):
        file_len = len(files)
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                print(f"[{file_path}] removed")
            except Exception as e:
                print(f"[{file_path}] ERROR: {e}")
    
    return file_len

def main():
    path_img = './datasets/image/'
    len_img = remove_all_files(path_img)

    path_text = './datasets/text/'
    len_text = remove_all_files(path_text)
    
    print(f"{path_img} removed: {len_img}")
    print(f"{path_text} removed: {len_text}")

main()