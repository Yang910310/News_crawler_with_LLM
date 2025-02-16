import streamlit as st
import requests
from llama_index.core.llms import ChatMessage
import logging
import time
import pandas as pd
from llama_index.llms.ollama import Ollama
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import threading
import torch  # 新增：引入 torch 判斷 GPU

logging.basicConfig(level=logging.INFO)

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'stop_flag' not in st.session_state:
    st.session_state.stop_flag = False

def stream_chat(model, messages):
    try:
        # 根據 torch.cuda 判斷是否可用 GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Using device: {device}")  # 新增：記錄使用的 GPU 或 CPU
        # 傳入 device 參數以利用 GPU 加速（假設 Ollama 支援該參數）
        llm = Ollama(model=model, request_timeout=300, device=device)
        response = ""
        response_placeholder = st.empty()
        resp = llm.stream_chat(messages)
        for r in resp:
            if st.session_state.stop_flag:
                break
            response += r.delta
            response_placeholder.write(response)
        logging.info(f"Model: {model}, Messages: {messages}, Response: {response}")
        return response
    except Exception as e:
        logging.error(f"Error during streaming: {str(e)}")
        raise e

# ...existing code...
def analyze_csv_with_llm(csv_file, model):
    try:
        # ...existing code...
        df = pd.read_csv(csv_file)
        st.sidebar.write("CSV 檔案內容：", df)
        if 'article' not in df.columns:
            st.error("CSV 文件中沒有找到 'article' 欄位！")
            return
        with st.spinner("生成中..."):
            for i in range(0, 3, 2):
                chunk = "\n\n".join(
                    df.iloc[i:i+2]['article'].fillna("無內容").astype(str)
                )
                prompt = f"以下是 CSV 數據的 article 部分：\n{chunk}\n請分析並依國家分類，最後用以下格式回應:1. 分析摘要：- 用一兩句話概述該國家的主要內容。 2. 重點：- 條列出該國家文章的 2~3 個最重要觀點。3. 結論：- 根據該國家的相關文章做簡單結論。"
                st.session_state.messages.append({"role": "user", "content": prompt})
                response_message = stream_chat(model, [
                    ChatMessage(role=msg["role"], content=msg["content"])
                    for msg in st.session_state.messages
                ])
    except Exception as e:
        st.error(f"無法分析 CSV 檔案：{e}")

def crawl_news():
    # ...existing code...
    domain = 'https://www.moneydj.com/'
    res = requests.get('https://www.moneydj.com/kmdj/news/newsreallist.aspx?a=mb020000')
    soup = BeautifulSoup(res.text, 'lxml')
    def get_content(url):
        dic = {}
        res2 = requests.get(url)
        soup2 = BeautifulSoup(res2.text, 'lxml')
        dic['title'] = soup2.select_one('h1').text if soup2.select_one('h1') else "No title"
        dic['article'] = soup2.select_one('article').text if soup2.select_one('article') else "No content"
        return dic
    news = []
    for url in soup.select('.forumgrid tr a'):
        news.append(get_content(domain + url.get('href')))
    df = pd.DataFrame(news)
    return df

def main():
    st.set_page_config(
        page_title="全球經濟新聞分析",
        page_icon="📍"
    )
    st.title("Chat with LLMs Models")
    logging.info("App started")
    model = st.sidebar.selectbox("選擇模型", ["llama3.1:8b-instruct-q4_K_M", "llama3.2:3b"])
    logging.info(f"Model selected: {model}")
    if 'uploaded_csv' not in st.session_state:
        st.session_state.uploaded_csv = None

    if st.sidebar.button("抓取新聞並生成 CSV"):
        with st.spinner("正在抓取新聞數據..."):
            try:
                news_df = crawl_news()
                st.write("抓取到的新聞數據：", news_df)
                csv_buffer = BytesIO()
                news_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                csv_buffer.seek(0)
                st.session_state.uploaded_csv = csv_buffer
                st.success("新聞數據已成功抓取並生成 CSV！")
                st.download_button(
                    label="下載新聞 CSV",
                    data=csv_buffer,
                    file_name="moneydj_news.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"抓取過程中發生錯誤：{e}")
    else:
        st.sidebar.write("若要生成 CSV 文件。按下「抓取新聞並生成 CSV」按鈕。")
            
    csv_file = st.sidebar.file_uploader("上傳 CSV 檔案", type=["csv"])
    if csv_file and st.sidebar.button("開始分析"):
        analyze_csv_with_llm(csv_file, model)

    if prompt := st.chat_input("輸入問題"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        logging.info(f"User input: {prompt}")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                st.session_state.stop_flag = False
                start_time = time.time()
                logging.info("Generating response")
                with st.spinner("生成中..."):
                    try:
                        messages = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in st.session_state.messages]
                        response_message = stream_chat(model, messages)
                        duration = time.time() - start_time
                        response_message_with_duration = f"{response_message}\n\nDuration: {duration:.2f} seconds"
                        st.session_state.messages.append({"role": "assistant", "content": response_message_with_duration})
                        st.write(f"Duration: {duration:.2f} seconds")
                        logging.info(f"Response: {response_message}, Duration: {duration:.2f} s")
                    except Exception as e:
                        st.session_state.messages.append({"role": "assistant", "content": str(e)})
                        st.error("An error occurred while generating the response.")
                        logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
