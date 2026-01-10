import streamlit as st
import zipfile
from datetime import datetime
from pathlib import Path
import text_extract
import smtplib
from email.message import EmailMessage

def send_email_with_attachments(receiver_email, job_name, folder_path):
    # மின்னஞ்சல் விவரங்கள்
    sender_email = "arunamanikandan.2025@gmail.com"  # உங்கள் மின்னஞ்சல்
    app_password = "jpwl hewf jsdl bynr"   # கூகுள் ஆப் பாஸ்வேர்டு

    msg = EmailMessage()
    msg['Subject'] = f"Job Completed: {job_name}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"வணக்கம்,\n\n{job_name} வேலையின் முடிவுகள் இணைக்கப்பட்டுள்ளன.")

    # அவுட்புட் ஃபோல்டரில் உள்ள பைல்களை இணைத்தல்
    for file_path in Path(folder_path).glob("*.*"):
        if file_path.is_file():
            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_name = file_path.name
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    # சர்வர் மூலம் மின்னஞ்சல் அனுப்புதல்
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)


# அவுட்புட் சேமிக்க வேண்டிய இடம்
OUTPUT_ROOT = Path("output")
OUTPUT_ROOT.mkdir(exist_ok=True)

st.set_page_config(page_title="PDF Extraction Web", page_icon="📦")

st.title("📦 ZIP பைல் ப்ராசஸர்")
st.write("உங்கள் ZIP பைலை கீழே பதிவேற்றவும் (Upload).")

# 1. பைல் பதிவேற்றும் வசதி (File Uploader)
uploaded_file = st.file_uploader("ZIP பைலை தேர்ந்தெடுக்கவும்", type="zip")

if uploaded_file is not None:
    job_name = Path(uploaded_file.name).stem
    today = datetime.now().strftime("%Y%m%d")
    
    # ஃபோல்டர் அமைப்பு
    job_output = OUTPUT_ROOT / today / job_name
    extract_dir = job_output / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    # ப்ராசஸ் நிலையை காட்ட (Progress Status)
    with st.status(f"வேலை நடக்கிறது: {job_name}...", expanded=True) as status:
        try:
            # 2. ZIP-ஐ எக்ஸ்ட்ராக்ட் செய்தல்
            st.write("பைல்களை பிரிக்கிறது...")
            with zipfile.ZipFile(uploaded_file, 'r') as z:
                z.extractall(extract_dir)
            
            # 3. PDF மற்றும் Excel-ஐ கண்டறிதல்
            pdf = next(extract_dir.rglob("*.pdf"), None)
            excel = next(extract_dir.rglob("*.xlsx"), None)
            
            if not pdf or not excel:
                st.error("❌ ZIP-க்குள் PDF அல்லது Excel பைல் இல்லை!")
            else:
                # 4. உங்கள் பழைய Main Logic-ஐ இயக்குதல்
                st.write("தகவல்களை பிரித்தெடுக்கிறது (Processing)...")
                text_extract.main(
                    pdf_path=str(pdf),
                    excel_path=str(excel),
                    output_dir=str(job_output)
                )
                
                # ... பழைய கோட் ...
                st.success(f"✅ {job_name} வெற்றிகரமாக முடிக்கப்பட்டது!")

                # மின்னஞ்சல் அனுப்பும் பகுதி
                with st.spinner("மின்னஞ்சல் அனுப்பப்படுகிறது..."):
                    try:
                        # நீங்கள் அனுப்ப வேண்டிய மெயில் ஐடியை இங்கே கொடுக்கவும்
                        send_email_with_attachments("manikandan.sowmesh@gmail.com", job_name, job_output)
                        st.info("📩 முடிவுகள் மின்னஞ்சல் மூலம் அனுப்பப்பட்டது!")
                    except Exception as e:
                        st.error(f"மின்னஞ்சல் அனுப்புவதில் பிழை: {e}")                
                
                # 5. ரிசல்ட் பைல்களை டவுன்லோட் செய்ய
                st.subheader("முடிவுகளை பதிவிறக்கம் செய்க:")
                for result_file in job_output.glob("*.*"):
                    if result_file.is_file():
                        with open(result_file, "rb") as f:
                            st.download_button(
                                label=f"Download {result_file.name}",
                                data=f,
                                file_name=result_file.name
                            )
                            
        except Exception as e:
            st.error(f"பிழை ஏற்பட்டுள்ளது: {e}")
        

        status.update(label="வேலை முடிந்தது!", state="complete")


