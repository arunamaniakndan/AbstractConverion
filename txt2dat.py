import zipfile
import shutil
import re
import os
import sys
import pandas as pd
import html.entities


df=""

def to_named_entities(text):
    result = []
    for char in text:
        codepoint = ord(char)
        # Check if a named entity exists for this character
        entity_name = html.entities.codepoint2name.get(codepoint)
        if entity_name:
            result.append(f"&{entity_name};")
        else:
            # Fallback to the character itself (or html.escape it)
            result.append(char)
    return "".join(result)

def tempfix(temp):
	if temp==[]:
		temp=""
	else:
		temp=temp[0]
	return temp

def getreftx(ref, tag, txt, outtag):
	temp = re.findall(f'<{tag}>(.+?)</{tag}', ref)
	temp = tempfix(temp)
	if temp=="":
		return txt
	if len(outtag)==1:
		if outtag[0]=='_rfaut':
			temp = temp.replace(";", "*")
			temp = temp.replace("* ", "*")
		txt +=f'\n{outtag[0]} {temp}'
	else:
		temp = temp.replace('–', '-')
		temp = temp.replace(" ", '')
		if "-" in temp:
			temp1 = temp.split("-")
			txt +=f'\n{outtag[0]} {temp1[0]}'
			if len(temp1)>1:
				txt +=f'\n{outtag[1]} {temp1[1]}'
		elif not temp.isdigit() and '_rfit' in outtag:
			txt +=f'\n{outtag[2]} {temp}'
		else:
			txt +=f'\n{outtag[0]} {temp}'
	return txt

def main(df, output_dir, fm_file):
	final_path = os.path.join(output_dir, "final")
	outout_out = os.path.join(output_dir, "out")
	fm_file_tagged = fm_file.replace(".txt", "_Tagged.txt")
	os.makedirs(final_path, exist_ok=True)
	mytemp='_spaid 898\n_spuid 123456789\n_grid1 199\n_par1 199\n\n'
	url = ""
	if os.path.exists(os.path.join(output_dir, "out", fm_file_tagged))==False:
		return False

	with open(os.path.join(output_dir, "out", fm_file_tagged), 'r', encoding="utf-8") as file:
		fm_text = file.read()
	fm_text = fm_text.replace("<subtitle></subtitle>", "")
	fm_text = fm_text.replace("</subtitle>", "</title>")
	fm_text = fm_text.replace("</title><subtitle>", ": ")
	fm_text = fm_text.replace("<chcon>", "<con>")
	fm_text = fm_text.replace("</chcon>", "</con>")
	fm_text = re.sub('ch([0-9])>', 'ch0\\1>', fm_text)

	for index, row in df.iterrows():
		if row['name'] == "url":
			if not pd.isna(row['start']):
				url = row['start']

	for index, row in df.iterrows():
		txt = mytemp + f"_ity {row['type']}"
		if not pd.isna(row['doi']):
			txt +=f'\n_doi {row["doi"]}'
		if url!="":
			txt +=f'\n_url {url}'

		txt += f'\n_pag {row["start"]}-{row["end"]}'
		cno = row['name']
		if cno in ['con', 'prelims', 'url']:
			continue
		chaptx = re.findall(f'<{cno}>.+?</{cno}>', fm_text)
		chaptx = tempfix(chaptx)
		temp = re.findall('<title>(.+?)</title>', chaptx)
		temp = tempfix(temp)
		txt += f'\n_eti {temp}'
		txt += f'\n_lit ENGL\n_lab ENGL\n'
		temp = re.findall('<abstract>(.+?)</abstract>', chaptx)
		temp = tempfix(temp)
		if temp!="":
			txt += f'\n_abs {temp}\n'

		# input(f'{cno}--{txt}\n\n')
		auths = re.findall(r'<(au[0-9]+)>(.+?)<\/\1>', chaptx)
		for x, auth in enumerate(auths):
			auth = auth[1]
			auth = auth.replace('</givenname>', '</name>')
			auth = auth.replace('</name><givenname>', '*')
			name = re.findall(f'<name>(.+?)</name>', auth)
			name = tempfix(name)
			name = name.replace(":", "*")
			txt += f'\n_auth {x+1}*{name}'
			orchid = re.findall('<orch.+?</orchid>', auths[x][1])
			orchid = tempfix(orchid)
			orchid = orchid.replace("<orchid>", "")
			orchid = orchid.replace("</orchid>", "")
			if orchid!="":
				txt += f'\norchid {orchid}'

		txt += f'\n'
		for x, auth in enumerate(auths):
			auth = auth[1]
			txt += f'\n_adseq {x+1}'
			temp = re.findall('<org.+</org>', auth)
			temp = tempfix(temp)
			temp = temp.replace("<org>", "")
			temp = temp.replace("</org>", "")
			if temp!="":
				txt +=f'\n_aor1 {temp}'
			temp = re.findall('<in.+</inst>', auth)
			temp = tempfix(temp)
			temp = temp.replace("<inst>", "")
			temp = temp.replace("</inst>", "")
			if temp!="":
				txt +=f'\n_aor2 {temp}'
			temp = re.findall('<ci.+</city>', auth)
			temp = tempfix(temp)
			temp = temp.replace("<city>", "")
			temp = temp.replace("</city>", "")
			if temp!="":
				txt +=f'\n_acty {temp}'
			temp = re.findall('<s.+</st>', auth)
			temp = tempfix(temp)
			temp = temp.replace("<st>", "")
			temp = temp.replace("</st>", "")
			if temp!="":
				txt +=f'\n_asat {temp}'
			temp = re.findall('<count.+</country>', auth)
			temp = tempfix(temp)
			temp = temp.replace("<country>", "")
			temp = temp.replace("</country>", "")
			if temp!="":
				txt +=f'\n_acny {temp}'
			txt += f'\n'

		if os.path.exists(os.path.join(output_dir, 'out', f'{cno}_ref_tagged.txt')):
			# input("REF")
			txt +=f'\n'
			with open(os.path.join(output_dir, 'out', f'{cno}_ref_tagged.txt'), 'r', encoding="utf-8") as file:
				reftx = file.read()
			refs = re.findall('<ref>.+</ref>', reftx)
			txt += f'\n_ref {len(refs)}\n'
			for x, ref in enumerate(refs):
				rtxt = f'\n_rfseq {x+1}'
				rtxt = getreftx(ref, "rawtext", rtxt, ['_rffrt'])
				rtxt = getreftx(ref, "au", rtxt, ['_rfaut'])
				rtxt = getreftx(ref, "s", rtxt, ['_rfeti'])
				rtxt = getreftx(ref, "e", rtxt, ['_rfsti'])
				if "_rfeti " in rtxt and "_rfsti " not in rtxt:
					rtxt = rtxt.replace('_rfeti ', '_rfsti ')
				rtxt = getreftx(ref, "y", rtxt, ['_rfpy1', '_rfpy2'])
				rtxt = getreftx(ref, "v", rtxt, ['_rfvn1', '_rfvn2'])
				rtxt = getreftx(ref, "is", rtxt, ['_rfis1', '_rfis2', '_rfit'])
				rtxt = getreftx(ref, "pg", rtxt, ['_rfpag'])
				rtxt = getreftx(ref, "coll", rtxt, ['_rfcollab'])
				rtxt = getreftx(ref, "txt", rtxt, ['_rftxt'])
				rtxt = getreftx(ref, "url", rtxt, ['_rfurl'])
				rtxt = getreftx(ref, "doi", rtxt, ['_rfdoi'])
				rtxt += f'\n'
				txt += rtxt
		else:
			txt +='\n\n_ref 0'

		txt = re.sub('\n\n+', '\n\n', txt)
		try:
			corrected_txt = txt.encode('cp1252').decode('utf-8')
		except:
			corrected_txt = txt.replace('â€“', '–')
		corrected_txt = to_named_entities(corrected_txt)

		with open(os.path.join(final_path, f'{cno}.dat'), 'w', encoding="utf-8-sig") as file:
			file.write(corrected_txt)
		txt=""

	# ===============================
	# ZIP ALL FINAL FILES & OUT FOLDER
	# ===============================
	zip_name = os.path.splitext(fm_file)[0] + ".zip"
	zip_path = os.path.join(output_dir, zip_name)
	
	out_folder_path = os.path.join(output_dir, "out")

	with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
		# 1. 'final' கோப்புறையில் உள்ள கோப்புகளை மட்டும் சேர்க்கிறது (நேரடியாக ZIP-க்குள்)
		for root, _, files in os.walk(final_path):
			for file in files:
				file_path = os.path.join(root, file)
				arcname = os.path.relpath(file_path, final_path)
				zipf.write(file_path, arcname)

		# 2. 'out' கோப்புறையை அதன் பெயருடனேயே ZIP-க்குள் சேர்க்கிறது
		if os.path.exists(out_folder_path):
			# out_folder_path-க்கு ஒரு படி மேலே உள்ள பாதையை எடுக்கிறோம்
			base_dir = os.path.dirname(out_folder_path) 
			for root, _, files in os.walk(out_folder_path):
				for file in files:
					file_path = os.path.join(root, file)
					# இது ZIP-க்குள் 'out/file.txt' என அமையும்
					arcname = os.path.relpath(file_path, base_dir)
					zipf.write(file_path, arcname)

	print(f"✅ Final ZIP created with 'final' files and 'out' folder: {zip_path}")
if __name__ == "__main__":
	excel_path = r"D:\Python\final\output\20260110\9798369331774\extracted\9798369331774.xlsx"
	output_dir = r'D:\Python\final\output\20260110\9798369331774'
	fm_file=r'9798369331774.txt'
	df = pd.read_excel(excel_path)
	main(df, output_dir, fm_file)