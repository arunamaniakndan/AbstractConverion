import os
import shutil
import text2xml
# import test_mis
from pathlib import Path
from datetime import datetime
from google import genai
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
import time

# ... (keep your other imports like text2xml, genai, etc.)

source_folder = ''
wip_folder = ''
out_folder = ''

def batch_process_files():
    global source_folder, wip_folder, out_folder
    batch_size = 5
    
    # Get only files from source (exclude WIP/Out folders)
    all_files = [f for f in os.listdir(source_folder) 
                 if os.path.isfile(os.path.join(source_folder, f))]

    if not all_files:
        return False

    for i in range(0, len(all_files), batch_size):
        batch = all_files[i:i+batch_size]
        
        # Step 1: Move batch to WIP
        for file_name in batch:
            shutil.move(os.path.join(source_folder, file_name), 
                        os.path.join(wip_folder, file_name))
        
        # Step 2: Run Process
        folder_path = Path(wip_folder)
        text2xml.m1(Path(folder_path))

        # Step 3: Check for _Tagged.txt and Move/Reject
        for file_name in batch:
            # We assume the original file name is used to generate the tagged name
            base_name = os.path.splitext(file_name)[0]
            tagged_file_name = f"{base_name}_Tagged.txt"
            
            wip_original = os.path.join(wip_folder, file_name)
            wip_tagged = os.path.join(wip_folder, tagged_file_name)
            
            if os.path.exists(wip_tagged):
                # SUCCESS: Move both or just the tagged file to Out
                shutil.move(wip_tagged, os.path.join(out_folder, tagged_file_name))
                shutil.move(wip_original, os.path.join(out_folder, file_name))
                print(f"{Fore.GREEN}Success:{Style.RESET_ALL} {tagged_file_name} moved to Out.")
            else:
                # FAILURE: Move original back to Source to retry in next loop
                if os.path.exists(wip_original):
                    shutil.move(wip_original, os.path.join(source_folder, file_name))
                    i-=1
                print(f"{Fore.RED}Rejected:{Style.RESET_ALL} {file_name} (No tagged file found).")
        
        time.sleep(2)
    return True

def main(source):
    global source_folder, wip_folder, out_folder
    source_folder = source
    wip_folder = os.path.join(source_folder, 'WIP')
    out_folder = os.path.join(source_folder, 'Out')

    for folder in [wip_folder, out_folder]:
        os.makedirs(folder, exist_ok=True)

    # input("manikandan")
    # --- THE LOOP ---
    try:
        chk = True
        while chk == True:
            chk = batch_process_files()
            if chk==True:
                time.sleep(10) # Wait 10 seconds before checking source again
    except KeyboardInterrupt:
        print("\nProcess stopped by user.")

if __name__ == "__main__":
    # Ensure 'source' is defined or passed as an argument
    target_path = r'C:\Your\Path\Here' 
    main(target_path)