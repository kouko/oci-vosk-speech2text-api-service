# Vosk STT API Service PRD

本文件將逐步敘述本專案的產品需求（Product Requirements Document, PRD），包含 API 功能、部署需求、OCI 整合等細節。

## 1. 專案目標
- 建立一個可在 OCI 一鍵部署的 Vosk Speech-to-Text API 服務。
- 提供 RESTful API 介面，支援語音檔案上傳與文字轉換。
- 支援多語言模型。
- 具備基本安全性與可擴展性。

### 選擇 Vosk 的理由
- 本專案目標為部署於 OCI Free Tier 可用的機器，資源有限。
- Vosk 支援輕量模型，效能需求低，適合雲端入門方案。
- Whisper 雖辨識率高但資源消耗大，不適合 Free Tier 部署。
- Vosk 支援多語言且易於容器化與自動化部署。

### 長音檔處理需求
- 目標用例包含 YouTube 影片、Podcast 等長時段音檔。
- 需設計非同步任務處理機制，避免阻塞 API。
- 檔案上傳大小限制需放寬，支援大型音檔。

### 非同步處理方案
- 本專案採用「檔案系統 + 前端輪詢」的非同步任務設計：
	- 使用者上傳音檔後，API 回傳任務 ID。
	- 後端將任務加入處理佇列，並將狀態與結果存於檔案系統。
	- 前端定時查詢任務狀態（如 `/tasks/{id}/status`），獲取進度或結果。
- 此方案架構簡單、易於維護，無需額外佇列或推播機制，適合 OCI Free Tier 部署。

## 2. 主要功能
- 語音檔案上傳與即時/批次文字轉換
- 支援多語言模型選擇
- 回傳辨識結果與信心指標

## 3. API 規格
- 端點設計（如 /transcribe, /health, /models）
- 請求/回應格式
- 錯誤處理


### 驗證方式
- 所有 API 需於 HTTP Header 傳送 API 金鑰。
- 範例：
    - `Authorization: Bearer <API_KEY>`
    - 或 `x-api-key: <API_KEY>`
- 請使用 HTTPS 保護金鑰安全。

### 主要端點

#### 1. 上傳音檔並要求語音辨識
- `POST /transcribe`
	- 說明：用於上傳音檔並提交 STT 任務，可指定語言與模型大小。
	   - 請求格式（multipart/form-data）：
		   - `file`: 音檔（必填）
		   - `language`: 語言代碼（如 zh, en, ja，必填，必須指定，API 不支援自動語言偵測）
		- `model_size`: 模型大小（如 small, large，必填，預設為 small）
	- 回應格式（JSON）：
		```json
		{
			"task_id": "abc123",
			"status": "queued"
		}
		```

	- 支援檔案類型：音檔（如 .wav, .mp3）與影片檔案（如 .mp4, .mov）。
	- 若上傳影片檔案，後端將自動擷取音軌進行語音辨識。

#### 2. 查詢任務狀態與結果
- `GET /tasks/{task_id}`
	- 說明：查詢指定任務的狀態與結果。

    - 可選參數：
        - `output_format`: 指定輸出格式，`text`（預設）或 `subtitle`（VTT 格式）。
        - 範例：`GET /tasks/{task_id}?output_format=subtitle`

    - 回應格式（JSON）：

        任務尚未完成（`status` 為 queued 或 processing）：
        ```json
        {
            "task_id": "abc123",
            "status": "processing",
            "result": null,
            "error": null
        }
        ```

        任務失敗（`status` 為 failed）：
        ```json
        {
            "task_id": "abc123",
            "status": "failed",
            "result": null,
            "error": "檔案格式不支援或語音辨識失敗"
        }
        ```

        任務完成且 `output_format=text`：
        ```json
        {
            "task_id": "abc123",
            "status": "done",
            "result": {
                "text": "辨識結果文字",
                "confidence": 0.98
            },
            "error": null
        }
        ```

        任務完成且 `output_format=subtitle`（VTT 格式）：
        ```json
        {
            "task_id": "abc123",
            "status": "done",
            "result": {
                "subtitle": "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n你好，歡迎收聽..."
            },
            "error": null
        }
        ```

#### 3. 查詢支援語言與模型
- `GET /models`
	- 說明：列出目前支援的語言與模型大小。
	- 回應格式（JSON）：
		```json
		{
			"languages": ["zh", "en", "ja"],
			"models": {
				"zh": ["small", "large"],
				"en": ["small", "large"],
				"ja": ["small", "large"]
			}
		}
		```

#### 4. 健康檢查
- `GET /health`
	- 說明：API 健康狀態。
	- 回應格式（JSON）：
		```json
		{ "status": "ok" }
		```

### 錯誤處理
- 所有 API 回應皆包含 `error` 欄位，若有錯誤則回傳錯誤訊息。

## 4. 部署需求

### 4.1 OCI 一鍵部署功能
- **目標**: 提供真正的一鍵部署體驗，使用者點擊 README.md 中的按鈕即可直接跳轉至 OCI Resource Manager 進行部署。

#### 4.1.1 部署流程設計
1. **GitHub Actions 自動化**：
   - 當推送到 main 分支時自動觸發 CI/CD 流程
   - 執行完整測試套件，確保代碼品質
   - 自動建構 Docker 映像檔
   - 打包完整部署檔案為 ZIP 格式
   - 自動發布到 GitHub Releases（基於時間戳記的版本號碼）

2. **一鍵部署按鈕**：
   - README.md 包含官方 "Deploy to Oracle Cloud" 按鈕
   - 直接導引到 OCI Resource Manager 建立堆疊頁面
   - 自動載入最新版本的部署包

3. **使用者體驗流程**：
   - 點擊部署按鈕 → 自動開啟 OCI Console
   - 友善的 UI 表單進行參數設定
   - 一鍵執行部署，約 5-10 分鐘完成
   - 取得完整的 API 端點和使用說明

#### 4.1.2 部署參數設定介面
使用者可於 OCI Resource Manager 界面設定以下參數：

**必要配置**：
- **Compartment**: 目標區間選擇（下拉選單）
- **Availability Domain**: 可用性網域選擇（下拉選單）
- **SSH 公鑰**: 實例安全存取金鑰（文字區域，支援多組金鑰）
- **API 金鑰**: STT 服務驗證金鑰（密碼欄位，最少 16 字元）

**實例配置**：
- **Instance Shape**: 計算實例規格選擇
  - 固定規格：E2.1.Micro (免費)、E2.2 (付費)
  - 彈性規格：E3.Flex、E4.Flex、A1.Flex
- **OCPU 數量**: 彈性規格專用，1-8 顆（A1.Flex 免費額度：最多 4 顆）
- **記憶體大小**: 彈性規格專用，1-128 GB（A1.Flex 免費額度：最多 24 GB）

**網路配置**：
- **建立新 VCN**: 是否自動建立虛擬雲端網路（預設：是）
- **現有 VCN**: 使用現有網路時的 VCN 選擇
- **現有子網路**: 使用現有網路時的子網路選擇

**進階設定**（可摺疊）：
- **區域**: OCI 部署區域
- **自訂映像檔 ID**: 指定作業系統映像檔（預設自動偵測）
- **Docker 映像檔名稱**: 容器映像檔名稱
- **GitHub 倉庫 URL**: 原始碼倉庫位置

#### 4.1.3 Free Tier 支援
- **完整免費層級支援**：專案預設配置為 VM.Standard.A1.Flex (2 OCPU + 8 GB RAM)
- **自動限制保護**：防止使用者超出免費額度
- **效能最佳化**：A1.Flex ARM 處理器提供優異的性價比
- **彈性升級**：支援升級至完整免費規格 (4 OCPU + 24 GB RAM)

#### 4.1.4 部署包結構
自動化產生的 ZIP 檔案包含：
- **schema.yaml**: OCI Resource Manager UI 定義檔案
- **main.tf**: Terraform 基礎設施程式碼
- **variables.tf**: 變數定義與驗證規則
- **cloud-init.yaml**: 實例初始化腳本
- **Dockerfile**: 容器建構檔案
- **api/**: 完整應用程式原始碼
- **tests/**: 自動化測試套件
- **POST_DEPLOYMENT.md**: 部署後使用指南

### 4.2 技術實作需求
- **Docker 容器化**: 完整的容器化應用程式
- **環境變數管理**: 透過 OCI Resource Manager 設定
- **自動模型下載**: 首次啟動時自動下載 Vosk 模型檔案
- **健康檢查**: 內建容器健康檢查機制
- **日誌管理**: 完整的部署和運行日誌

### 4.3 安全性設計
- **API 金鑰驗證**: 強制 16+ 字元安全金鑰
- **SSH 金鑰驗證**: 必須提供有效的 SSH 公鑰
- **網路安全**: 自動配置防火牆規則（僅開放必要端口）
- **HTTPS 準備**: 支援 Load Balancer 整合（進階配置）

## 5. 安全性設計

### 5.1 個人使用安全模式
本專案針對個人使用場景設計，採用簡化但有效的安全措施：

#### 核心安全機制
- **API 金鑰驗證**：16+ 字元強制要求，支援 `x-api-key` 或 `Authorization: Bearer` 標頭
- **請求限流**：每 10 秒最多 3 次請求，防止濫用
- **SSH 金鑰存取**：實例管理採用金鑰認證，無密碼登入
- **網路防火牆**：OCI Security Lists 自動配置，僅開放必要端口

#### 傳輸安全
- **HTTP API** (port 8000)：適合個人使用的簡化方案
- **明文傳輸**：API 金鑰和資料為明文，適合內部或個人用途
- **建議使用**：在可信網路環境中使用（家庭網路、VPN、內網）

#### 安全性限制說明
- ⚠️ **不適合公開服務**：API 金鑰和資料為明文傳輸
- ⚠️ **不支援 HTTPS**：避免複雜的憑證管理，降低部署門檻
- ✅ **個人使用足夠**：對於個人開發、學習、測試用途已提供適當保護

### 5.2 安全性升級路徑
當專案需要更高安全性時：
- **網域 + HTTPS**：購買網域名稱，配置 SSL 憑證
- **OCI Load Balancer**：使用付費服務提供企業級 HTTPS
- **API 閘道**：整合 OCI API Gateway 進行進階驗證

## 6. CI/CD 與自動化
 - GitHub Actions 工作流
 - 單元測試與自動部署
 - 自動打包程式碼、Dockerfile、設定檔與 Terraform 腳本為 zip 檔，供 OCI Resource Manager 一鍵部署使用

## 7. 未來規劃
- 支援更多語音模型
- 增加使用者管理與統計

## 8. 討論區
- 請於此文件逐步補充與討論各項需求。

---

> 請於下方補充/討論 API 功能、架構、OCI 部署細節等。
