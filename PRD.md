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
 - OCI Resource Manager/Terraform 一鍵部署
     - 部署流程可讓使用者於 OCI 介面自訂以下參數：
         - 機器 CPU/RAM 規格（如 OCPU 數量、記憶體大小）
         - API 金鑰（於部署時設定，作為 API 驗證用）
     - 詳細部署步驟、zip 檔案結構、參數設定等技術細節將於技術設計文件或部署說明書中補充。
 - Docker 容器化
 - 環境變數與設定檔管理
 - API 服務同時支援 HTTP 與自簽憑證的 HTTPS 端口：
     - 使用者可自行選擇存取方式。
     - HTTP 為明文傳輸，安全性較低。
     - HTTPS 為加密傳輸，但自簽憑證會有安全警告，適合內部或測試用途。

## 5. 安全性
 - API 金鑰驗證（不支援 JWT 驗證）
 - 基本存取控制
 - API 服務同時支援 HTTP 與自簽憑證的 HTTPS 端口：
     - HTTP 為明文傳輸，API 金鑰與資料易被攔截，僅建議內部或測試用途。
     - HTTPS 為加密傳輸，但自簽憑證不被瀏覽器或客戶端信任，存取時會有安全警告。
     - 用戶端可選擇跳過憑證驗證（如 Python requests `verify=False`），但安全性較低。
     - 正式公開服務建議使用受信任的 CA 憑證與 HTTPS。

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
