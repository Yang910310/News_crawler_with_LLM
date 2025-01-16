# News_crawler_with_LLM
# README

## 項目概述

此項目是一個基於 Streamlit 的互動式應用程序，用於抓取特定網站的新聞數據並進行分析，借助大型語言模型（LLM）生成有意義的報告。主要特性包括：

- **新聞數據抓取**：自動爬取 MoneyDJ 網站的新聞內容。
- **數據分析**：通過 CSV 文件的數據進行語義分析，並依據內容分類及摘要。
- **即時互動**：允許用戶通過聊天界面與模型互動。

### 使用技術

- **語言**：Python
- **框架**：Streamlit
- **模型庫**：Llama Index（結合 Ollama 模型進行處理）
- **其他依賴**：pandas、BeautifulSoup、requests

此應用適用於需要自動抓取並分析文本數據的使用場景，例如媒體數據分析、內容分類及摘要。

## 安裝要求

在安裝本應用之前，請確保您的系統滿足以下要求：

1. **Python 版本**：Python 3.8 或更高版本
2. **必要依賴項**：可以通過 `requirements.txt` 文件安裝以下依賴項：
   - `streamlit`
   - `llama-index`
   - `pandas`
   - `requests`
   - `beautifulsoup4`
   - `lxml`
   - `ollama`（請確保已安裝支持 Ollama 的庫）

## 安裝步驟

1. 克隆此存儲庫或下載源代碼：

   ```bash
   git clone https://github.com/Yang910310/News_crawler_with_LLM.git
   cd News_crawler_with_LLM
   ```

2. 安裝必要的 Python 庫：

   ```bash
   pip install -r requirements.txt
   ```

3. 下載所需的模型：

   在執行應用程序之前，請執行以下指令下載模型：

   ```bash
   ollama pull llama3.1:8b-instruct-q4_K_M
   ```

4. 運行應用程序：

   ```bash
   streamlit run app.py
   ```

## 使用概述

1. 啟動應用後，您將進入一個網頁界面。
2. 在側邊欄中，選擇以下操作：
   - **抓取新聞數據**：點擊 "抓取新聞並生成 CSV" 按鈕，自動爬取新聞數據並生成可下載的 CSV 文件。
   - **上傳 CSV 文件**：如果已有新聞數據文件，您可以直接上傳進行分析。
   - **選擇模型**：支持多種 LLM 模型（如 llama3.1:8b-instruct-q4\_K\_M）。
3. 如果需要進一步互動，您可以在聊天輸入框中輸入問題，模型將生成相關回應。

## 資源連結

- [Streamlit 官方文檔](https://docs.streamlit.io/)
- [Llama Index 文檔](https://gpt-index.readthedocs.io/)
- [BeautifulSoup 文檔](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Ollama 官方文檔](https://ollama.ai/)

如有疑問或需要進一步支持，請聯繫項目作者或提交問題到此存儲庫的 Issues 區。

