import streamlit as st
import requests
import openai
import re
from datetime import datetime, timedelta  # Tambahan

openai.api_key = st.secrets['api_key']
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def check_word_in_url(url, word="Berhasil"):
    try:
        if url == st.secrets['founder_pass']:
            return True

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        if word not in response.text:
            return False

        if "DatasansBook" not in response.text:
            return False

        today_date = datetime.today().strftime('%d-%m-%Y')
        if today_date not in response.text:
            return False

        current_time = datetime.now()
        one_hour_before = current_time - timedelta(hours=1)
        time_range = [one_hour_before + timedelta(minutes=i) for i in range(61)]
        formatted_times = [time.strftime('%I:%M') for time in time_range]

        if not any(time in response.text for time in formatted_times):
            return False
            
        return True

    except requests.RequestException as e:
        st.error("Maaf link bukti pembayaran salah atau status pembayaran tidak sukses.")
        return False
        

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

def extract_titles(text):
    # Menggunakan regex untuk menemukan semua judul yang diawali oleh angka dan titik
    matches = re.findall(r'\d+\.\s*(.*)', text)
    return matches

def request_title(prompt,
                 ml_model,
                 special_topic):
    messages = [{
        "role":
        "system",
        "content":
        f"Aku akan memberikan 10 ide judul skripsi tentang {ml_model} dengan fokus ke {special_topic}."
    }, {
        "role":
        "user",
        "content": prompt
    }]

    response = openai.ChatCompletion.create(
        # model="gpt-4",
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=3000,
        temperature=0)
    script = response.choices[0].message['content']
    return script

def request_content(prompt):
    messages = [{
        "role":
        "system",
        "content":
        f"Aku akan membantumu menulis skripsi dengan bahasa Indonesia."
    }, {
        "role":
        "user",
        "content": prompt
    }]

    response = openai.ChatCompletion.create(
        # model="gpt-4",
        model="gpt-3.5-turbo-16k",
        messages=messages,
        max_tokens=13000,
        temperature=0)
    script = response.choices[0].message['content']
    return script

def main():
    st.title("Generator Skripsi Machine Learning by Datasans")

    ml_model = st.selectbox("Pilih Jenis Model Machine Learning", ["Klasifikasi", "Regresi", "Clustering"])
    special_topic = st.text_input("Masukkan Topik Khusus")

    if st.button("Submit"):
        st.session_state.button_clicked = True

    if 'button_clicked' in st.session_state and ml_model and special_topic:
        prompt_1 = f"Berikan 10 ide judul skripsi tentang {ml_model}, fokus pada {special_topic}. Beri nomor 1 - 10 pada setiap judul. Jangan berikan kalimat pengantar atau apapun kecuali judul. Langsung mulai dengan '1. (judul no 1)"

        if 'titles' not in st.session_state:
            with st.spinner('Generating title ideas...'):
                titles = extract_titles(request_title(prompt_1, ml_model, special_topic))
                st.session_state.titles = titles

        if 'titles' in st.session_state:
            st.write("Klik pada judul untuk men-generate skripsi sederhana dari Bab 1-4.")
            for title in st.session_state.titles:
                if st.button(title):
                    st.session_state.title = title
                    st.session_state.button2_clicked = True

                    if 'button2_clicked' in st.session_state:
                        # st.session_state.title = title
                        st.markdown(f"[Sawer seikhlasnya dengan mengeklik link ini.]({'https://saweria.co/DatasansBook'})")
                        st.markdown("""
                            <style>
                            .tooltip {
                              position: relative;
                              display: inline-block;
                              cursor: pointer;
                              background-color: #f2f2f2; /* Warna abu-abu */
                              padding: 5px;
                              border-radius: 6px;
                            }
                            
                            .tooltip .tooltiptext {
                              visibility: hidden;
                              width: 300px;
                              background-color: #555;
                              color: #fff;
                              text-align: center;
                              border-radius: 6px;
                              padding: 5px;
                              position: absolute;
                              z-index: 1;
                              bottom: 125%; 
                              left: 50%;
                              margin-left: -150px;
                              opacity: 0;
                              transition: opacity 0.3s;
                            }
                            
                            .tooltip:hover .tooltiptext {
                              visibility: visible;
                              opacity: 1;
                            }
                            </style>
                            
                            <div class="tooltip">Kenapa tidak gratis? (harus nyawer)
                              <span class="tooltiptext">Proses generate content menggunakan API ChatGPT yang aksesnya berbayar. Sawer seikhlasnya untuk melanjutkan. Link berlaku selama 1 jam setelah sawer berhasil.</span>
                            </div>
                            """, unsafe_allow_html=True)
                                
                        if 'url' in st.session_state:
                            is_valid = check_word_in_url(st.session_state.url)
                            if is_valid:
                                # st.session_state.title = title
                                prompt_2 = f"""Tuliskan skripsi dengan judul : {st.session_state.title}
                                            dengan format:
                                            
                                            Bab I: Pendahuluan
                                            
                                            Bab II: Tinjauan Pustaka dan Kerangka Teori
                                            
                                            Bab III: Metodologi Penelitian
                                            
                                            Bab IV: Modeling dan Pembahasan
                                            
                                            Untuk Bab IV, buatkan script python lengkap, gunakan dataset yang relevan dari library yang ada atau gunakan data sintetis, dan tulis selengkap mungkin.
                                            Gunakan format paragraf, ## untuk mengawali bab, ### untuk mengawali subbab.
                                            Untuk Bab IV, buatkan script python lengkap dengan data sintetis.
                                            """
                                st.session_state.prompt2 = prompt_2
                                if 'title' in st.session_state and 'prompt2' in st.session_state:            
                                    # Request ke API ChatGPT
                                    with st.spinner('Generating content...'):
                                        simple_thesis = request_content(st.session_state.prompt2)
                                        
                                        # Menampilkan skripsi sederhana
                                        st.subheader(st.session_state.title)
                                        st.write(str(simple_thesis)) 
                            else:
                                st.error("Maaf link bukti pembayaran salah atau status pembayaran tidak sukses/valid.")

if __name__ == "__main__":
    main()
