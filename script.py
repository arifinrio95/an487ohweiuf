import streamlit as st
import requests
import openai
import re
from datetime import datetime, timedelta

openai.api_key = st.secrets['api_key']
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def check_word_in_url(url, word="Berhasil"):
    try:
        if url == st.secrets['founder_pass']:
            return True
            
        response = requests.get(url, headers = headers)
        response.raise_for_status()

        # Pengecekan kata "Berhasil"
        if word not in response.text:
            return False

        if "DatasansBook" not in response.text:
            return False
            
        # Pengecekan tanggal hari ini
        today_date = datetime.today().strftime('%d-%m-%Y')
        if today_date not in response.text:
            return False
        
        # Pengecekan waktu saat ini sampai 1 jam ke belakang dalam format 12 jam
        current_time = datetime.now()
        one_hour_before = current_time - timedelta(hours=1)
        time_range = [one_hour_before + timedelta(minutes=i) for i in range(61)]
        formatted_times = [time.strftime('%I:%M') for time in time_range]

        # Jika tidak ada waktu yang cocok dalam konten, kembalikan False
        if not any(time in response.text for time in formatted_times):
            return False
            
        return True

    except requests.RequestException as e:
        # st.error("Maaf link bukti pembayaran salah atau status pembayaran tidak sukses.")
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
                 special_topic=' '):
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
    special_topic = st.text_input("Masukkan Topik Khusus (Kosongkan untuk random topik)", value = " ")
    

    if 'button_submit2' not in st.session_state:
        button = st.button("Submit", key='btn_submit')
        if button:
            st.session_state.button_clicked = True
        
    if 'button_clicked' in st.session_state and ml_model and special_topic:
    # if button and ml_model and special_topic:
        prompt_1 = f"Berikan 10 ide judul skripsi tentang {ml_model}, {special_topic}. Beri nomor 1 - 10 pada setiap judul. Jangan berikan kalimat pengantar atau apapun kecuali judul. Langsung mulai dengan '1. (judul no 1)"

        if 'titles' in st.session_state:
            # Menampilkan setiap judul sebagai text yang bisa diklik   
            st.write("Klik pada judul untuk men-generate skripsi sederhana dari Bab 1-4.")
            if ('special_topic' in st.session_state) and ('ml_model' in st.session_state): 
                if (st.session_state.special_topic != special_topic) or (st.session_state.ml_model != ml_model):
                    st.session_state.button_submit2 = True
                    if st.button("Submit", key = 'btn_resubmit'):
                        with st.spinner('Generating title ideas...'):
                            titles = extract_titles(request_title(prompt_1, ml_model, special_topic))
                            st.session_state.titles = titles
                            for title in st.session_state.titles:
                                button2 = st.button(title, key=f'btn_submit_{title}')
                                if button2:
                                    st.button(title, key=f'btn_submit_{title}')
                                    st.session_state.button2_clicked = True
                                    st.session_state.title = title
                else:
                    for title in st.session_state.titles:
                        button2 = st.button(title, key=f'btn_submit_{title}')
                        if button2:
                            # st.button(title, key=f'btn_submit_{title}')
                            st.session_state.button2_clicked = True
                            st.session_state.title = title
                    
        if 'titles' not in st.session_state:
            with st.spinner('Generating title ideas...'):
                titles = extract_titles(request_title(prompt_1, ml_model, special_topic))
                st.session_state.titles = titles
                st.write("Klik pada judul untuk men-generate skripsi sederhana dari Bab 1-4.")
                for i, title in enumerate(st.session_state.titles):
                    button2 = st.button(title, key=f'btn_submit_{title}_{i}')
                    if button2:
                        # st.button(title, key=f'btn_submit_{title}')
                        st.session_state.button2_clicked = True
                        st.session_state.title = title

                        # url = st.text_input("Masukkan link bukti sawer untuk melanjutkan. Masukkan link lengkap mulai dari 'https://'", key=f'btn_textinput1')
                        # st.session_state.url = url
                        # if st.button("Submit", key = "button_url"):
                        #     st.experimental_rerun()
                # if 'url' not in st.session_state:
                #     st.markdown(f"[Sawer seikhlasnya dengan mengeklik link ini.]({'https://saweria.co/DatasansBook'})")
                #     st.markdown("""
                #         <style>
                #         .tooltip {
                #           position: relative;
                #           display: inline-block;
                #           cursor: pointer;
                #           background-color: #f2f2f2; /* Warna abu-abu */
                #           padding: 5px;
                #           border-radius: 6px;
                #         }
                        
                #         .tooltip .tooltiptext {
                #           visibility: hidden;
                #           width: 300px;
                #           background-color: #555;
                #           color: #fff;
                #           text-align: center;
                #           border-radius: 6px;
                #           padding: 5px;
                #           position: absolute;
                #           z-index: 1;
                #           bottom: 125%; 
                #           left: 50%;
                #           margin-left: -150px;
                #           opacity: 0;
                #           transition: opacity 0.3s;
                #         }
                        
                #         .tooltip:hover .tooltiptext {
                #           visibility: visible;
                #           opacity: 1;
                #         }
                #         </style>
                        
                #         <div class="tooltip">Kenapa tidak gratis? (harus nyawer)
                #           <span class="tooltiptext">Proses generate content menggunakan API ChatGPT yang aksesnya berbayar. Sawer seikhlasnya untuk melanjutkan. Link berlaku selama 1 jam setelah sawer berhasil.</span>
                #         </div>
                #         """, unsafe_allow_html=True)
                #     url = st.text_input("Masukkan link bukti sawer untuk melanjutkan. Masukkan link lengkap mulai dari 'https://'", key=f'btn_textinput1')
                #     st.session_state.url = url
                #     st.button("Submit URL", key = 'btn_submiturl_0')
                    

        # if 'url' in st.session_state:
        #     if check_word_in_url(st.session_state.url) == True:
        #         st.success("URL diterima.")
            # for i, title in enumerate(st.session_state.titles):
            #     button2 = st.button(title, key=f'btn_submit_{title}_{i}')
            #     if button2:
            #         # st.button(title, key=f'btn_submit_{title}')
            #         st.session_state.button2_clicked = True
            #         st.session_state.title = title
        # for title in st.session_state.titles:
        #     button2 = st.button(title, key=f'btn_submit_{title}')
        #     if button2:
        #         # st.button(title, key=f'btn_submit_{title}')
        #         st.session_state.button2_clicked = True
        #         st.session_state.title = title
        # if 'title' in st.session_state:
        #     prompt_2 = f"""Tuliskan skripsi dengan judul : {st.session_state.title}
        #                 dengan format:
                        
        #                 Bab I: Pendahuluan
                        
        #                 Bab II: Tinjauan Pustaka dan Kerangka Teori
                        
        #                 Bab III: Metodologi Penelitian
                        
        #                 Bab IV: Modeling dan Pembahasan
                        
        #                 Tuliskan semua bab diatas, untuk Bab IV, buatkan script python lengkap, gunakan dataset yang relevan dari library yang ada atau gunakan data sintetis, dan tulis selengkap mungkin.
        #                 Gunakan format paragraf, ## untuk mengawali bab, ### untuk mengawali subbab.
        #                 Untuk Bab IV, buatkan script python lengkap dengan data sintetis.
        #                 """
        #     st.session_state.prompt2 = prompt_2
        if 'title' in st.session_state:
            prompt_2 = f"""Tuliskan skripsi dengan judul : {st.session_state.title}
                        dengan format:
                        
                        Bab I: Pendahuluan
                        
                        Bab II: Tinjauan Pustaka dan Kerangka Teori
                        
                        Bab III: Metodologi Penelitian
                        
                        Bab IV: Modeling dan Pembahasan
                        
                        Tuliskan semua bab diatas, untuk Bab IV, buatkan script python lengkap, gunakan dataset yang relevan dari library yang ada atau gunakan data sintetis, dan tulis selengkap mungkin.
                        Gunakan format paragraf, ## untuk mengawali bab, ### untuk mengawali subbab.
                        Untuk Bab IV, buatkan script python lengkap dengan data sintetis.
                        """
            st.session_state.prompt2 = prompt_2
            
            # if 'titles' in st.session_state:
            #     # Menampilkan setiap judul sebagai text yang bisa diklik   
            #     # st.write("Klik pada judul untuk men-generate skripsi sederhana dari Bab 1-4.")
            #     if ('special_topic' in st.session_state) and ('ml_model' in st.session_state): 
            #         if (st.session_state.special_topic != special_topic) or (st.session_state.ml_model != ml_model):
            #             st.session_state.button_submit2 = True
            #             if st.button("Submit", key = 'btn_resubmit2'):
            #                 with st.spinner('Generating title ideas...'):
            #                     titles = extract_titles(request_title(prompt_1, ml_model, special_topic))
            #                     st.session_state.titles = titles
            #                     for i, title in enumerate(st.session_state.titles):
            #                         button2 = st.button(title, key=f'btn_submit_{title}_{i}')
            #                         if button2:
            #                             st.button(title, key=f'btn_submit_{title}')
            #                             st.session_state.button2_clicked = True
            #                             st.session_state.title = title
            #         else:
            #              for i, title in enumerate(st.session_state.titles):
            #                 button2 = st.button(title, key=f'btn_submit_{title}_{i}')
            #                 if button2:
            #                     # st.button(title, key=f'btn_submit_{title}')
            #                     st.session_state.button2_clicked = True
            #                     st.session_state.title = title
            # Request ke API ChatGPT
            with st.spinner('Generating content...'):
                simple_thesis = request_content(st.session_state.prompt2)
                
                # Menampilkan skripsi sederhana
                st.subheader(st.session_state.title)
                st.write(str(simple_thesis)) 
                # st.experimental_rerun()

            # if check_word_in_url(st.session_state.url)==False:
            #     st.error("Maaf link bukti pembayaran salah atau status pembayaran tidak sukses/valid.")
            #     url = st.text_input("Masukkan link bukti sawer untuk melanjutkan. Masukkan link lengkap mulai dari 'https://'", key=f'btn_textinput2')
            #     st.session_state.url = url
            #     st.button("Submit URL", key = 'btn_submiturl')
            
        # if st.button(title):
        # if 'button2_clicked' in st.session_state:
        #     if 'url' not in st.session_state:
        #         url = st.text_input("Masukkan link bukti sawer untuk melanjutkan. Masukkan link lengkap mulai dari 'https://'", key=f'btn_textinput1')
        #         st.session_state.url = url
                # if st.button("Submit"):
                #     st.experimental_rerun()
                
            # st.session_state.title = title
            # st.markdown(f"[Sawer seikhlasnya dengan mengeklik link ini.]({'https://saweria.co/DatasansBook'})")
            # st.markdown("""
            #     <style>
            #     .tooltip {
            #       position: relative;
            #       display: inline-block;
            #       cursor: pointer;
            #       background-color: #f2f2f2; /* Warna abu-abu */
            #       padding: 5px;
            #       border-radius: 6px;
            #     }
                
            #     .tooltip .tooltiptext {
            #       visibility: hidden;
            #       width: 300px;
            #       background-color: #555;
            #       color: #fff;
            #       text-align: center;
            #       border-radius: 6px;
            #       padding: 5px;
            #       position: absolute;
            #       z-index: 1;
            #       bottom: 125%; 
            #       left: 50%;
            #       margin-left: -150px;
            #       opacity: 0;
            #       transition: opacity 0.3s;
            #     }
                
            #     .tooltip:hover .tooltiptext {
            #       visibility: visible;
            #       opacity: 1;
            #     }
            #     </style>
                
            #     <div class="tooltip">Kenapa tidak gratis? (harus nyawer)
            #       <span class="tooltiptext">Proses generate content menggunakan API ChatGPT yang aksesnya berbayar. Sawer seikhlasnya untuk melanjutkan. Link berlaku selama 1 jam setelah sawer berhasil.</span>
            #     </div>
            #     """, unsafe_allow_html=True)
            
        
        st.session_state.special_topic = special_topic 
        st.session_state.ml_model = ml_model 
        
                
if __name__ == "__main__":
    main()
