# Software Architecture Document (SAD)

## 1. 系統架構概述
本服務為 Vosk STT API，部署於 OCI 計算實例，支援 Free Tier，提供完整的一鍵部署體驗。

### 1.1 整體架構分層
```
┌─────────────────────────────────────────────────────────────┐
│                     使用者介面層                              │
│  README.md "Deploy to Oracle Cloud" 按鈕 → OCI Console      │
└─────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────┐
│                    部署自動化層                               │
│  GitHub Actions → CI/CD → Release → OCI Resource Manager    │
└─────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────┐
│                   基礎設施層                                  │
│  Terraform → OCI Compute → VCN → Security Lists            │
└─────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────┐
│                    應用程式層                                 │
│       FastAPI → 任務管理 → Vosk STT → 檔案系統              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 核心組件架構
- **API 層（FastAPI）**：RESTful API 接收請求、驗證 API 金鑰、任務管理、結果回傳
- **任務管理層**：非同步任務處理、狀態追蹤、檔案系統為基礎的持久化
- **語音辨識層**：Vosk 模型整合、多語言支援、音檔/影片處理、VTT 字幕生成
- **儲存層**：檔案系統儲存（上傳檔案、辨識結果、任務狀態）
- **部署層**：Docker 容器化、Terraform 基礎設施即程式碼、OCI Resource Manager 整合

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

### 5.1 一鍵部署流程架構
```
GitHub Repository
       ↓ (push to main)
GitHub Actions CI/CD
       ↓ (自動建構)
GitHub Releases (ZIP 檔案)
       ↓ (Deploy to Oracle Cloud 按鈕)
OCI Resource Manager
       ↓ (使用者設定參數)
Terraform 部署
       ↓ (基礎設施建置)
OCI 計算實例 + Docker 容器
       ↓ (服務啟動)
Vosk STT API 服務運行
```

### 5.2 OCI Resource Manager 整合架構
- **orm.yaml**: 定義使用者介面表單和參數驗證
- **main.tf**: 基礎設施資源定義（VCN、子網路、安全規則、計算實例）
- **variables.tf**: 變數定義與限制（Free Tier 保護、OCPU/記憶體比例驗證）
- **cloud-init.yaml**: 實例初始化腳本（Docker 安裝、容器啟動）

### 5.3 基礎設施組件
- **網路架構**: 自動建立 VCN、子網路、網際網路閘道、路由表
- **安全組規則**: 自動配置防火牆（SSH 22、HTTP 80、HTTPS 443、API 8000）
- **計算實例**: 支援多種形狀（E2.1.Micro、A1.Flex、E3.Flex、E4.Flex）
- **儲存**: 本地檔案系統（/app/data、/app/models）

### 5.4 容器化架構
- **多階段建構**: 基礎映像檔 → 依賴安裝 → 應用程式複製 → 啟動腳本
- **自動模型管理**: 首次啟動時自動下載 Vosk 模型檔案
- **健康檢查**: 容器層級和應用程式層級的健康監控
- **日誌管理**: 標準輸出/錯誤、檔案日誌、部署日誌

### 5.5 Free Tier 最佳化架構
- **預設配置**: VM.Standard.A1.Flex (2 OCPU + 8 GB RAM)
- **自動限制**: 防止超出免費額度的驗證機制
- **效能調優**: ARM 處理器最佳化、記憶體使用優化
- **彈性升級**: 支援升級到完整免費規格或付費方案

## 6. CI/CD 與自動化架構

### 6.1 GitHub Actions 工作流程
```
觸發條件: push to main 或 PR to main
    ↓
程式碼檢出 (actions/checkout@v4)
    ↓
Python 環境設定 (actions/setup-python@v5)
    ↓
依賴安裝 (pip install -r requirements.txt)
    ↓
測試執行 (PYTHONPATH=. pytest tests/ -v)
    ↓ (測試通過)
Docker 映像檔建構
    ↓
部署包打包 (包含 orm.yaml, Terraform 檔案, 源碼)
    ↓
版本號碼生成 (基於時間戳記: vYYYYMMDD-HHMMSS)
    ↓
GitHub Release 建立 + ZIP 檔案上傳
```

### 6.2 自動化品質保證
- **測試失敗保護**: 測試失敗時自動停止部署流程
- **版本管理**: 基於時間戳記的唯一版本號碼
- **語法現代化**: 使用最新版本的 GitHub Actions
- **安全性驗證**: 自動檢查 API 金鑰和 SSH 金鑰設定

### 6.3 部署包自動化
- **完整性檢查**: 自動包含所有必要檔案
- **結構標準化**: 符合 OCI Resource Manager 要求
- **文檔整合**: 自動包含部署後使用指南

## 7. 可擴展性與未來規劃
- 支援多語言、多模型（small/large）。
- 可調整 VM 規格，支援 OCI Free Tier。
- 未來可擴充任務佇列、分布式架構、使用者管理與統計。

---
> 更多細節請依需求補充。
