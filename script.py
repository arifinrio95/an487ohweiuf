import streamlit as st
import requests
import openai
import re

openai.api_key = st.secrets['api_key']

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
                           
# Fungsi simulasi untuk menggantikan panggilan API ke ChatGPT
# def simulated_chatGPT_request(prompt):
#     if "Berikan 50 ide judul skripsi" in prompt:
#         return [f"{i+1}. Judul Skripsi Ide {i+1}" for i in range(50)]
#     else:
#         return "Ini adalah skripsi sederhana berdasarkan judul yang Anda pilih."

# Streamlit app
def main():
    st.title("Generator Skripsi Machine Learning by Datasans")

    # User memilih satu jenis model machine learning
    ml_model = st.selectbox("Pilih Jenis Model Machine Learning", ["Klasifikasi", "Regresi", "Clustering"])
    
    # User meng-input free text topik khusus
    special_topic = st.text_input("Masukkan Topik Khusus")
    
    button = st.button("Submit", key='btn_submit')
    if button:
        st.session_state.button_clicked = True

    if 'button_clicked' in st.session_state and ml_model and special_topic:
        prompt_1 = f"Berikan 10 ide judul skripsi tentang {ml_model}, fokus pada {special_topic}. Beri nomor 1 - 10 pada setiap judul. Jangan berikan kalimat pengantar atau apapun kecuali judul. Langsung mulai dengan '1. (judul no 1)"
        
        # Request ke API ChatGPT (dalam hal ini, kita gunakan fungsi simulasi)
        # titles = simulated_chatGPT_request(prompt_1)
        
        with st.spinner('Generating title ideas...'):
            titles = extract_titles(request_title(prompt_1, ml_model, special_topic))
        
        # Menampilkan setiap judul sebagai text yang bisa diklik
        st.write("Klik pada judul untuk men-generate skripsi sederhana dari Bab 1-4.")
        for title in titles:
            # button2 = st.button(title, key=f'btn_submit_{title}')
            # if button2:
            #     st.session_state.button2_clicked = True
                
            if st.button(title):
            # if 'button2_clicked' in st.session_state:
                st.session_state.title = title
                prompt_2 = f"""Tuliskan skripsi dengan judul : {st.session_state.title}
                            dengan format:
                            
                            Bab I: Pendahuluan
                            
                            Bab II: Tinjauan Pustaka dan Kerangka Teori
                            
                            Bab III: Metodologi Penelitian
                            
                            Bab IV: Modeling dan Pembahasan
                            
                            Untuk Bab IV, buatkan script python lengkap, gunakan dataset yang relevan dari library yang ada atau gunakan data sintetis, dan tulis selengkap mungkin.
                            Gunakan format paragraf, ## untuk mengawali bab, ### untuk mengawali subbab.
                            """
                
                # Request ke API ChatGPT (dalam hal ini, kita gunakan fungsi simulasi)
                with st.spinner('Generating content...'):
                    simple_thesis = request_content(prompt_2)
                    
                    # Menampilkan skripsi sederhana
                    st.subheader(title)
                    st.write(str(simple_thesis))
                
if __name__ == "__main__":
    main()
