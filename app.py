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

logging.basicConfig(level=logging.INFO)

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'stop_flag' not in st.session_state:
    st.session_state.stop_flag = False

def stream_chat(model, messages):
    try:
        llm = Ollama(model=model, request_timeout=300)
        resp = llm.stream_chat(messages)
        response = ""
        response_placeholder = st.empty()
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

def analyze_csv_with_llm(csv_file, model):
    try:
        # # 確保檔案指標已經準備好
        # csv_file.seek(0)
        # 讀取 CSV 檔案
        df = pd.read_csv(csv_file)
        st.sidebar.write("CSV 檔案內容：", df)

        # 檢查是否存在 'article' 欄位
        if 'article' not in df.columns:
            st.error("CSV 文件中沒有找到 'article' 欄位！")
            return

        with st.spinner("生成中..."):
        # 逐段處理，步長為 3
            for i in range(0, 3, 2):  # 每次處理 3 筆資料
                # 提取 'article' 欄位的部分內容
                chunk = "\n\n".join(
                    df.iloc[i:i+2]['article'].fillna("無內容").astype(str)
                )  # 合併 3 筆資料，用換行分隔
                prompt = f"以下是 CSV 數據的 article 部分：\n{chunk}\n請分析並依國家分類，最後用以下格式回應:1. 分析摘要：- 用一兩句話概述該國家的主要內容。 2. 重點：- 條列出該國家文章的 2~3 個最重要觀點。3. 結論：- 根據該國家的相關文章做簡單結論。"

                # 儲存 prompt 作為用戶訊息
                st.session_state.messages.append({"role": "user", "content": prompt})

                # 傳遞訊息到模型並獲取回應
                response_message = stream_chat(model, [
                    ChatMessage(role=msg["role"], content=msg["content"])
                    for msg in st.session_state.messages
                ])
                # st.write(f"第 {i//3 + 1} 部分分析結果：", response_message)

    except Exception as e:
        st.error(f"無法分析 CSV 檔案：{e}")


# 爬取數據的函數
def crawl_news():
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
        page_title="全球經濟新聞分析",  # 頁面標題
        page_icon="📍"         # 分頁圖標 (可以是 Emoji 或圖標 URL)
    )
    
    st.title("Chat with LLMs Models")
    logging.info("App started")
    
    #選擇模型
    model = st.sidebar.selectbox("選擇模型", ["llama3.1:8b-instruct-q4_K_M", "llama3.2:3b"])
    logging.info(f"Model selected: {model}")
    
    # 初始化 session_state 用於模擬文件上傳
    if 'uploaded_csv' not in st.session_state:
        st.session_state.uploaded_csv = None

    # 按鈕觸發爬蟲並生成 CSV
    if st.sidebar.button("抓取新聞並生成 CSV"):
        with st.spinner("正在抓取新聞數據..."):
            try:
                # 執行爬蟲
                news_df = crawl_news()
                
                # 顯示抓取的數據
                st.write("抓取到的新聞數據：", news_df)

                # 將 DataFrame 轉為 CSV 並存入 session_state
                csv_buffer = BytesIO()
                news_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                csv_buffer.seek(0)

                # 儲存生成的 CSV 到 session_state
                st.session_state.uploaded_csv = csv_buffer
                st.success("新聞數據已成功抓取並生成 CSV！")

                # 提供下載按鈕
                st.download_button(
                    label="下載新聞 CSV",
                    data=csv_buffer,
                    file_name="moneydj_news.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"抓取過程中發生錯誤：{e}")

    # # 顯示模擬的 "file_uploader" 行為
    # st.header("模擬文件上傳")
    # if st.session_state.uploaded_csv:
    #     # 如果已生成 CSV 文件，直接將其顯示作為已「上傳」的內容
    #     st.write("已生成並模擬上傳的 CSV 文件：")
    #     uploaded_df = pd.read_csv(st.session_state.uploaded_csv)
    #     st.write(uploaded_df)

        # # 第二個按鈕：觸發分析
        # if st.button("分析上傳的 CSV 文件"):
        #     uploaded_csv = pd.read_csv(st.session_state.uploaded_csv)
        #     st.write("以下為uploaded_csv")
        #     st.write(uploaded_csv)            
        #     st.info("開始分析上傳的 CSV 文件...")
        #     # 確保指標復位到文件起始位置
        #     st.session_state.uploaded_csv.seek(0)

        #     analyze_csv_with_llm(uploaded_csv, model)

    else:
        st.sidebar.write("若要生成 CSV 文件。按下「抓取新聞並生成 CSV」按鈕。")
            
    #手動上傳csv檔
    csv_file = st.sidebar.file_uploader("上傳 CSV 檔案", type=["csv"])
    if csv_file and st.sidebar.button("開始分析"):
        analyze_csv_with_llm(csv_file, model)

    #LLM基本互動
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
