import os
import re
from pathlib import Path
from datetime import datetime
from google import genai
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from colorama import Fore, Style, init
import time
import streamlit as st
client = genai.Client(api_key=st.secrets["API_KEY"])

user_prompt1='<a>--author and splitted by semi colon and remove comma and author format Surname With initial short format and retain or add dot and remove space within initial, <e>--other title means book or article,  <s>--source or Chapter or article title, <y>--Year1,  <v>--Volume 1, <is>--Issue, <pg>--page range, <txt>--Other text and month annd except tag text is taken <txt>, <url>--URL, <doi>--DOI, <coll>--Collabration author (Company), collab is not a within author Author replace is company, <rawtext>--retain original format reference, <ref>--each reference tag within <ref> do not validate reference and just only add short tag if any tag content is not available or matching in input ignore tag retain [[ch####]] Example tagging Structure: <ref><rawtext></rawtext><au></au><s></s><e></e><v></v><is></is><pg></pg><txt></txt></ref>'
# user_prompt1='NLM DTD XML Structure Reference Part only and add additional tag for <rawtx> plain reference'
# user_prompt2 = "I need Title with colon Subtitle apply short tag in <title>, Author split by semicolorn <au>, <org1>, <country>, abstract text <abstext>, <doi>, <copyright> other text ignored and retain [[ch####]]"
# user_prompt2='NLM DTD XML Structure and Front matter only'
user_prompt2='''read and analysis apply xml short tag, apply for <title>, <subtitle>, <au#><name>Lussier:M.</name><givenname>Mark</givenname><orchid></orchid><aff><org></org><inst></inst><city></city><st></st><country></country></aff><email></email></au#>, <abstract>, <doi>, <url>, <copy> any author info missing getting from [[con]] and retain [[ch###]] getting tag file each <ch###><title><subtitle><au#><name><organization><instituation><city><state><country></au#><abstract><doi><url><copy></ch##> no need search city and state other than out of text but country is must
<name>--Surname colon with Initial, Initial insert dot and remove space
<givenname>--Expand Initials only dont take surname
<aff>--if emirates/has/has been found in text ignore <aff>
<org>--Department, Center,
<inst>--University, Organisation 
<abstract><doi><url><copy>--Missing content ignore it
'''

def process_single_file(text_file):
    try:
        init(autoreset=True)
        print(f"\n{Fore.RED}✔ Process: {text_file.name}{Fore.RESET}")
        
        with open(text_file, 'r', encoding="utf-8") as f:
            content = f.read()

        prompt = user_prompt1 if "_ref" in text_file.name else user_prompt2
        full_content = f"Context:\n{content}\n\nTask: {prompt}"

        # Gemini API அழைப்பு
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=[full_content]
        )
        
        rtext = response.text
        rtext = rtext.replace('```xml', '')
        rtext = rtext.replace('```', '')
        
        # Text cleaning logic
        if "_ref" in text_file.name:
            rtext = re.sub('\n<', '<', rtext)
            rtext = re.sub('\n+', '\n', rtext)
            rtext = rtext.strip()
            rtext = re.sub('\n', ' ', rtext)
            rtext = re.sub('</ref>', '</ref>\n', rtext)
        else:
            rtext = re.sub('\n +', '\n', rtext)
            rtext = re.sub('\n+', '\n', rtext)
            rtext = re.sub('\n', '', rtext)
            rtext = re.sub('<ch', '\n<ch', rtext)
            
        new_file_path = text_file.with_name(f"{text_file.stem}_tagged.txt")
        with open(new_file_path, 'w', encoding="utf-8") as f:
            f.write(rtext)
            
        print(f"\n{Fore.GREEN}✔ Done: {text_file.name}{Fore.RESET}")
        print(f"Prompt Tokens: {response.usage_metadata.prompt_token_count}") 
        print(f"Candidates Tokens: {response.usage_metadata.candidates_token_count}") 
        print(f"Total Tokens: {response.usage_metadata.total_token_count}")
    except Exception as e:
        print(f"{Fore.RED}✘ Permanent Error {text_file.name}: {e}{Fore.RESET}")
    return False

def m1(folder_path,st):
    # Ensure we only pick files that need tagging
    text_files = [f for f in folder_path.glob('*.txt') if "_tagged" not in f.name]
    files = [f.name for f in text_files]
    st.write(f"Processing: {",".join(files)})
    if not text_files:
        return

    print(f"Batch Processing {len(text_files)} files...")

    # The 'with' statement handles the shutdown and wait automatically
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_single_file, f) for f in text_files]
        # REINFORCEMENT: Explicitly wait for all futures in this batch to finish
        wait(futures, return_when=ALL_COMPLETED)
    st.success(f"Processing: {",".join(files)})
    print("Batch threads finished.")


if __name__ == "__main__":
    myFolder = r'D:\JOB\Arul-S1\Sample1\9798369331774\E2\WIP'
    folder_path = Path(myFolder)
    m1(folder_path)
    print("completed")

    # List all .txt files, excluding those already processed (files containing '_tagged')



