# Software Architecture Document (SAD)

## 1. 系統架構概述
本服務為 Vosk STT API，部署於 OCI VM（Free Tier），支援一鍵部署。
架構分為：
- API 層（FastAPI/Flask）：接收 RESTful 請求、驗證 API 金鑰、回傳任務狀態與結果。
- 任務管理層：非同步任務排程、狀態管理，前端輪詢查詢進度。
- 語音辨識層：呼叫 Vosk 模型，支援音檔與影片檔案（自動擷取音軌），分段時間戳轉 VTT 字幕。
- 儲存層：檔案系統儲存上傳檔案、辨識結果。

## 2. 技術棧
- Python (FastAPI/Flask)
- Vosk 語音辨識
- Docker 容器化
- Terraform 腳本
- OCI Resource Manager（Stack zip 部署）

## 3. API 驗證與安全性
- 所有 API 需於 HTTP Header 傳送 API 金鑰（Authorization 或 x-api-key）。
- 僅支援 API 金鑰驗證，不支援 JWT。
- 支援 HTTP 與自簽憑證的 HTTPS 端口，使用者可選擇存取方式。
- 正式公開建議使用受信任 CA 憑證。

## 4. 非同步任務設計
- 檔案上傳後回傳任務 ID，任務狀態存檔案系統。
- 前端定時輪詢 `/tasks/{id}` 查詢進度或結果。
- 任務失敗、格式不支援、API 金鑰錯誤皆有明確回應。

## 5. 部署架構
- 一鍵部署流程：程式碼、Dockerfile、Terraform 腳本打包 zip，上傳 OCI Resource Manager。
- 部署時可自訂 VM CPU/RAM 規格、API 金鑰。
- 支援 HTTP(80) 與 HTTPS(443) 端口，安全組需開放。
- 詳細步驟見 DG.md。

## 6. CI/CD 與自動化
- GitHub Actions：單元測試、格式檢查、Docker 建置、zip 打包。
- zip 檔案結構與內容詳見 DG.md。

## 7. 可擴展性與未來規劃
- 支援多語言、多模型（small/large）。
- 可調整 VM 規格，支援 OCI Free Tier。
- 未來可擴充任務佇列、分布式架構、使用者管理與統計。

---
> 更多細節請依需求補充。
