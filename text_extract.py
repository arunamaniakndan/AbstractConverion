import fitz  # PyMuPDF
import pandas as pd
import os
import re
import txt2xml_main
import txt2dat

df=""
# --- Configuration ---
pdf_path = r"D:\JOB\Arul-S1\Sample1\9798369331774\9798369331774.pdf"
excel_path = r"D:\JOB\Arul-S1\Sample1\9798369331774\9798369331774.xlsx"
output_dir = r"D:\JOB\Arul-S1\000000"
# prelims_offset = 26 

file_text = os.path.join(os.path.dirname(pdf_path), os.path.basename(pdf_path))
file_text = file_text.replace(".pdf", ".txt")
file_ref = file_text.replace(".txt", "_ref.txt")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def roman_to_int(s):
    if not isinstance(s, str): return int(s)
    s = s.lower()
    roman_map = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100, 'd': 500, 'm': 1000}
    res = 0
    for i in range(len(s)):
        if i + 1 < len(s) and roman_map[s[i]] < roman_map[s[i+1]]:
            res -= roman_map[s[i]]
        else: res += roman_map[s[i]]
    return res

def extract_pdf_text(pdf, start_pg, end_pg, offset=0):
    text = ""
    
    # Helper to convert or cast page inputs
    def get_val(pg):
        if isinstance(pg, str) and not pg.isdigit():
            return roman_to_int(pg)
        return int(pg)

    try:
        start_val = get_val(start_pg)
        end_val = get_val(end_pg)
        
        # Logic: Offsets usually apply to the "printed" Arabic page numbers
        # to match the PDF's internal zero-based index.
        # If the input is Roman, we assume offset is 0 or handled separately.
        current_offset = 0 if not str(start_pg).isdigit() else offset
        
        start_index = (start_val + current_offset) - 1
        end_index = (end_val + current_offset)

        for page_num in range(start_index, end_index):
            if 0 <= page_num < len(pdf):
                page = pdf[page_num] # Standard PyMuPDF access
                text += page.get_text("text")
                
    except Exception as e:
        print(f"Error processing pages: {e}")
        
    return text

def main(pdf_path, excel_path, output_dir):
    process_job(pdf_path, excel_path, output_dir)
    txt2xml_main.main(output_dir)
    fm_file = os.path.basename(pdf_path).replace(".pdf", ".txt")
    txt2dat.main(df, output_dir, fm_file)

def process_job(pdf_path, excel_path, output_dir):
    global df
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    doc = fitz.open(pdf_path)
    df = pd.read_excel(excel_path)
    name_list=["prelims", "url"]
    df = pd.read_excel(excel_path)
    for index, r in df.iterrows():
        if r["name"]=="prelims":
            current_offset= int(r["start"])

    doc = fitz.open(pdf_path)
    
    text_fm=""
    text_ref=""
    for index, row in df.iterrows():
        name = str(row['name'])
        if name in name_list:
            continue
        try:
            print(f"Processing {name}...")
            s1 = str(row['start'])
            full_text = extract_pdf_text(doc, s1, s1, current_offset)
            text_fm += f'[[{name}]]\n{full_text}\n'            
            # with open(os.path.join(output_dir, f"{name}.txt"), "w", encoding="utf-8") as f:
            #     f.write(full_text)

            # Extract and Merge References Text
            if pd.notna(row['Ref Start']) and pd.notna(row['Ref End']):
                ref_text = extract_pdf_text(doc, row['Ref Start'], row['Ref End'], current_offset)
                text_ref += f'[[{name}]]\n{ref_text}\n'
                with open(os.path.join(output_dir, f"{name}_ref.txt"), "w", encoding="utf-8") as f:
                    f.write(ref_text)
        
        except Exception as e:
            print(f"Error processing {name}: {e}")
    # input(file_text)

    with open(os.path.join(output_dir, os.path.basename(pdf_path).replace(".pdf", ".txt")), "w", encoding="utf-8") as f:
        f.write(text_fm)
    # with open(file_ref, "w", encoding="utf-8") as f:
    #     f.write(text_ref)

    doc.close()
    print(f"\nSuccess! Merged text saved to: {output_dir}")

# if __name__ == "__main__":
    # process_chapters()
    # tx2xml_main.main(output_dir)
    # fm_file = os.path.basename(pdf_path).replace(".pdf", ".txt")
    # txt2dat.main(df, output_dir, fm_file)
