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
        

# (Lainnya sama seperti kode Anda)

def main():
    st.title("Generator Skripsi Machine Learning by Datasans")

    ml_model = st.selectbox("Pilih Jenis Model Machine Learning", ["Klasifikasi", "Regresi", "Clustering"])
    special_topic = st.text_input("Masukkan Topik Khusus")

    if st.button("Submit"):
        st.session_state.button_clicked = True

    if 'button_clicked' in st.session_state and ml_model and special_topic:
        # (Lainnya sama seperti kode Anda)

        if 'titles' in st.session_state:
            st.write("Klik pada judul untuk men-generate skripsi sederhana dari Bab 1-4.")
            for title in st.session_state.titles:
                if st.button(title):
                    st.session_state.title = title
                    st.session_state.button2_clicked = True

                    if 'button2_clicked' in st.session_state:
                        # (Lainnya sama seperti kode Anda)

                        if 'url' in st.session_state:
                            is_valid = check_word_in_url(st.session_state.url)
                            if is_valid:
                                # (Lainnya sama seperti kode Anda)
                            else:
                                st.error("Maaf link bukti pembayaran salah atau status pembayaran tidak sukses/valid.")

if __name__ == "__main__":
    main()
