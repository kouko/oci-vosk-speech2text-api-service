# Technical Design Document (TDD)

## 0. 程式架構

### 目錄結構
```
api/
  main.py         # API 入口，FastAPI/Flask 實作
  auth.py         # API 金鑰驗證邏輯
  tasks.py        # 任務管理、狀態查詢
  stt.py          # 語音辨識流程（Vosk 呼叫、音軌擷取、VTT 轉換）
  models.py       # 支援語言與模型查詢
  config.py       # 設定檔管理
  utils.py        # 工具函式（檔案處理、例外處理等）
  ...
deploy/
  Dockerfile      # 容器化設定
  main.tf         # Terraform 腳本
  variables.tf    # 部署參數
config/
  ...             # API 金鑰、環境變數等
tests/
  test_api.py     # API 單元測試
  test_tasks.py   # 任務流程測試
  test_stt.py     # 語音辨識測試
  ...
README.md
PRD.md
SAD.md
TDD.md
DG.md
```

### 主要模組職責
- main.py：API 路由、請求分發、回應格式。
- auth.py：API 金鑰驗證，401 錯誤處理。
- tasks.py：任務建立、狀態管理、輪詢查詢。
- stt.py：音檔/影片處理、Vosk 語音辨識、VTT 字幕產生。
- models.py：查詢支援語言與模型大小。
- config.py：讀取環境變數、API 金鑰等設定。
- utils.py：檔案處理、例外處理、通用工具。
- tests/：各模組單元測試。

## 1. API 設計
- 端點：
	- `POST /transcribe`：上傳音檔/影片檔，指定語言與模型大小，回傳任務 ID。
	- `GET /tasks/{id}`：查詢任務狀態與結果，支援 text/VTT 輸出。
	- `GET /models`：查詢支援語言與模型。
	- `GET /health`：健康檢查。
- 請求/回應格式詳見 PRD，所有 API 需於 Header 傳送 API 金鑰（Authorization/x-api-key）。
- 回應皆含 error 欄位，明確回報錯誤。

### API 請求/回應範例
詳見 PRD 3. API 規格章節。


## 2. 任務管理
- 檔案上傳後產生唯一任務 ID，任務資訊存於檔案系統（如 JSON 檔）。
- 任務狀態：queued → processing → done/failed。
- 前端定時輪詢 `/tasks/{id}` 查詢進度或結果。
- 任務失敗時回傳 error 訊息。

## 3. 語音辨識流程
- 支援音檔（wav/mp3）與影片檔案（mp4/mov），影片自動擷取音軌。
- 語言與模型大小由 API 參數指定，預設 small。
- 語音辨識流程：
	1. 解析檔案，擷取音軌（如 ffmpeg）。
	2. 呼叫 Vosk 模型辨識，取得文字與分段時間戳。
	3. 依需求輸出純文字或 VTT 字幕（程式自動轉換）。

## 4. 安全性
- 僅支援 API 金鑰驗證，於 Header 傳送，後端比對金鑰。
- 不支援 JWT。
- 支援 HTTP 與自簽憑證的 HTTPS，正式建議用 CA 憑證。

## 5. CI/CD 與一鍵部署架構

### 5.1 GitHub Actions 現代化工作流程
```yaml
# 使用最新版本的 Actions
- uses: actions/checkout@v4           # 最新檢出動作
- uses: actions/setup-python@v5       # 最新 Python 設定
- uses: softprops/action-gh-release@v2 # 現代化 Release 創建

# 現代語法
- run: echo "date=$(date +'%Y%m%d-%H%M%S')" >> $GITHUB_OUTPUT  # 新語法取代 ::set-output
```

### 5.2 自動化部署流程設計
1. **觸發條件**: push to main 或 PR to main
2. **品質保證**: 
   - 完整測試套件執行 (PYTHONPATH=. pytest tests/ -v)
   - 測試失敗時自動停止部署流程
3. **建構與打包**:
   - Docker 映像檔建構
   - 包含 OCI Resource Manager 所需的完整檔案結構
4. **版本管理**: 基於時間戳記的版本號碼 (vYYYYMMDD-HHMMSS)
5. **發布**: 自動創建 GitHub Release 並上傳部署包

### 5.3 一鍵部署技術實作

#### 部署包結構最佳化
```
vosk-stt-api-deployment.zip
├── orm.yaml                 # OCI Resource Manager UI 定義
├── main.tf                  # Terraform 基礎設施程式碼
├── variables.tf             # 變數定義與驗證
├── cloud-init.yaml          # 實例初始化腳本
├── POST_DEPLOYMENT.md       # 部署後使用指南
├── api/                     # 完整應用程式源碼
├── tests/                   # 自動化測試套件
├── requirements.txt         # Python 依賴
└── README.md               # 專案說明
```

#### OCI Resource Manager 整合
- **orm.yaml**: 定義友善的使用者介面表單
- **變數驗證**: Free Tier 額度保護、OCPU/記憶體比例檢查
- **條件顯示**: 彈性實例形狀時才顯示 OCPU/記憶體設定
- **智慧預設值**: A1.Flex (2 OCPU + 8 GB RAM) 最佳化 Free Tier 體驗

#### 部署 URL 自動化
```
https://console.us-phoenix-1.oraclecloud.com/resourcemanager/stacks/create?region=home&zipUrl=https://github.com/kouko/oci-vosk-speech2text-api-service/releases/latest/download/vosk-stt-api-deployment.zip
```

### 5.4 Free Tier 最佳化設計
- **預設配置**: VM.Standard.A1.Flex (ARM 處理器，優異性價比)
- **自動限制**: 防止使用者意外超出免費額度
- **驗證規則**: 
  - A1.Flex 最多 4 OCPU (Free Tier 限制)
  - A1.Flex 最多 24 GB RAM (Free Tier 限制)
  - API 金鑰最少 16 字元
  - SSH 金鑰必須提供

## 6. 例外處理
- 任務失敗：回傳 status=failed，error 欄位說明原因。
- 檔案格式不支援：API 回傳錯誤訊息。
- API 金鑰錯誤：回傳 401 Unauthorized。
- 其他例外皆有明確回應格式。

## 1. 使用套件規劃

### 語音辨識與音檔處理
- vosk           # 語音辨識核心
- pydub          # 音檔分割、格式轉換
- ffmpeg-python  # 音訊/影片處理

### Web API 與任務管理
- fastapi        # API 框架（或 Flask）
- uvicorn        # ASGI 伺服器
- celery         # 非同步任務管理（或 RQ）
- redis          # 任務佇列（Celery/RQ backend）

### 安全性與設定
- python-dotenv  # 環境變數管理

### 測試
- pytest         # 單元測試
- httpx          # API 測試

### 部署與容器
- docker         # 容器化（Dockerfile）
- terraform      # 基礎架構自動化

### 其他工具
- requests       # HTTP 請求
- loguru         # 日誌管理

---
> 更多技術細節請依需求補充。


## 7. 資料結構設計
- 任務 JSON 格式範例：
```json
{
  "id": "任務ID",
  "status": "queued|processing|done|failed",
  "input_file": "檔案路徑",
  "output_file": "字幕/文字檔路徑",
  "language": "en|zh|...",
  "model_size": "small|large",
  "result": "辨識結果（純文字/VTT）",
  "error": "錯誤訊息（如有）",
  "created_at": "ISO8601時間戳",
  "updated_at": "ISO8601時間戳"
}
```
- 音檔/字幕檔案命名規則：`{task_id}_{type}.wav`、`{task_id}.vtt`，儲存於指定目錄（如 data/、output/）。

## 8. 例外/錯誤處理流程
- API 回傳格式：
```json
{
  "status": "success|failed",
  "error": "錯誤訊息（如有）",
  "data": {...}
}
```
- 常見錯誤類型：檔案格式不支援、API 金鑰錯誤、模型載入失敗、任務不存在等。
- 處理策略：明確 HTTP 狀態碼（400/401/404/500），error 欄位說明。

## 9. 模型/語言管理
- 支援語言與模型大小查詢 API，回傳可用選項。
- 模型檔案儲存於 models/，載入時依參數選擇。
- 未來可支援多模型（如 Whisper），模組化設計。

## 10. 安全性細節
- API 金鑰管理：金鑰存於 config/，可用腳本新增/撤銷。
- HTTPS 憑證：自簽憑證產生流程、正式環境建議用 CA 憑證。

## 11. 測試規劃
- 單元測試：API 路由、任務流程、金鑰驗證、例外處理。
- 整合測試：音檔/影片上傳、字幕產生、任務輪詢。
- 測試資料：提供範例音檔、影片檔、金鑰。

## 12. 部署細節
- Docker/OCI 參數化設計：環境變數（API_KEY、MODEL_PATH、REDIS_URL等）可於部署時指定。
- Terraform 變數說明：main.tf/variables.tf 內註解，README/DG 補充範例。

## 13. 日誌與監控
- loguru 日誌格式：INFO/ERROR/DEBUG 等級，記錄 API 請求、任務狀態、例外。
- 健康檢查 API：`GET /health`，回傳服務狀態。

## 14. 擴充性/維護性
- 模組化設計原則：各功能獨立，易於擴充/維護。
- 未來支援 Whisper 或其他 STT：stt.py 可抽象化，支援多模型切換。

## 15. API 詳細規格

### 1. POST /transcribe
- 說明：上傳音檔/影片檔，指定語言與模型大小，回傳任務 ID。
- 請求參數：
  - file: 二進位音檔/影片檔 (multipart/form-data)
  - language: string（如 'en', 'zh'）
  - model_size: string（'small'|'large'，預設 small）
  - x-api-key: string（Header）
- 回應格式：
```json
{
  "status": "success|failed",
  "task_id": "string",
  "error": "string（如有）"
}
```
- 錯誤碼：400（參數錯誤）、401（API 金鑰錯誤）、500（伺服器錯誤）

### 2. GET /tasks/{id}
- 說明：查詢任務狀態與結果，支援 text/VTT 輸出。
- 請求參數：
  - id: string（路徑參數）
  - x-api-key: string（Header）
- 回應格式：
```json
{
  "status": "queued|processing|done|failed",
  "result": "string（純文字/VTT）",
  "error": "string（如有）"
}
```
- 錯誤碼：401、404（任務不存在）、500

### 3. GET /models
- 說明：查詢支援語言與模型。
- 請求參數：x-api-key: string（Header）
- 回應格式：
```json
{
  "languages": ["en", "zh", ...],
  "model_sizes": ["small", "large"]
}
```
- 錯誤碼：401、500

### 4. GET /health
- 說明：健康檢查。
- 回應格式：
```json
{
  "status": "ok"
}
```
- 錯誤碼：500


## 16. 任務佇列與檔案系統細節

- 任務資訊儲存於檔案系統（如 data/tasks/{task_id}.json），每個任務一個 JSON 檔。
- 任務目錄結構：
  - data/tasks/：存放所有任務 JSON
  - data/input/：上傳音檔/影片檔
  - data/output/：辨識結果（文字/VTT）
- 任務建立流程：
  1. API 收到請求，產生唯一 task_id
  2. 儲存 input 檔案至 data/input/
  3. 建立 data/tasks/{task_id}.json，狀態設為 queued
  4. Celery/RQ 佇列啟動背景任務，更新狀態
  5. 辨識完成後，儲存結果至 data/output/，更新 JSON 狀態
- 輪詢機制：前端定時呼叫 /tasks/{id} 查詢 JSON 狀態
- 並發/鎖定策略：
  - 任務 JSON 檔案存取時採用檔案鎖（如 filelock 套件）避免競爭
  - 任務目錄可依 task_id 分散，減少 I/O 壓力
  - 若未來改用 Redis，則任務狀態可存於 Redis，檔案系統僅存檔案本身

## 17. OCI 一鍵部署環境架構

### 17.1 多層次部署架構
```
使用者體驗層:
  README.md Deploy Button → OCI Console UI

參數配置層:
  orm.yaml → 友善表單界面 → 參數驗證

基礎設施層:
  Terraform → VCN/子網路/安全規則 → 計算實例

應用程式層:
  cloud-init → Docker → Vosk STT API
```

### 17.2 OCI Resource Manager 參數架構
#### 核心變數設計
```hcl
# 必要配置
variable "compartment_id" { type = oci:identity:compartment:id }
variable "availability_domain" { type = oci:identity:availabilitydomain:name }
variable "ssh_authorized_keys" { type = oci:core:ssh:publickey }
variable "api_key" { type = password, minLength = 16 }

# 實例配置 (支援彈性設定)
variable "vm_shape" { 
  enum = ["VM.Standard.E2.1.Micro", "VM.Standard.A1.Flex", "VM.Standard.E3.Flex", "VM.Standard.E4.Flex"]
  default = "VM.Standard.A1.Flex"
}
variable "vm_ocpus" { type = integer, minimum = 1, maximum = 8, default = 2 }
variable "vm_memory_gb" { type = integer, minimum = 1, maximum = 128, default = 8 }

# 網路配置 (自動化/手動選擇)
variable "create_vcn" { type = boolean, default = true }
variable "vcn_id" { type = oci:core:vcn:id }        # 條件顯示
variable "subnet_id" { type = oci:core:subnet:id }  # 條件顯示
```

#### Free Tier 保護機制
```hcl
# A1.Flex Free Tier 限制驗證
validation {
  condition = !(var.vm_shape == "VM.Standard.A1.Flex" && var.vm_ocpus > 4)
  error_message = "A1.Flex Free Tier 最多 4 OCPU"
}
validation {
  condition = !(var.vm_shape == "VM.Standard.A1.Flex" && var.vm_memory_gb > 24)
  error_message = "A1.Flex Free Tier 最多 24 GB RAM"
}
```

### 17.3 容器化部署架構
#### Dockerfile 最佳化設計
```dockerfile
FROM python:3.9-slim                    # 基礎映像檔
RUN apt-get update && apt-get install   # 系統依賴 (ffmpeg, build-essential)
COPY requirements.txt .                 # 利用 Docker 快取
RUN pip install --no-cache-dir          # Python 依賴安裝
COPY api/ ./api/                       # 應用程式代碼
RUN mkdir -p /app/data /app/models      # 資料目錄建立
RUN echo '#!/bin/bash...' > download_models.sh  # 模型下載腳本
ENV API_KEY=please-set-secure-api-key   # 環境變數設定
EXPOSE 8000                            # 端口暴露
CMD ["/app/start.sh"]                  # 啟動腳本
```

#### 自動化初始化流程
```bash
# cloud-init.yaml 執行流程
1. 系統更新 (package_update: true)
2. Docker 安裝 (packages: [docker.io])
3. 使用者權限設定 (groups: [docker])
4. docker-compose.yml 建立
5. 建構腳本執行 (/opt/vosk-stt/build-and-run.sh)
6. 服務健康檢查 (curl localhost:8000/health)
```

### 17.4 網路與安全架構
#### 自動網路建構
```hcl
# VCN 自動建立 (可選)
resource "oci_core_vcn" "stt_vcn" {
  cidr_blocks = ["10.0.0.0/16"]
  dns_label = "voskstt"
}

# 安全規則自動配置
ingress_security_rules {
  protocol = "6"  # TCP
  source = "0.0.0.0/0"
  tcp_options {
    min = 22; max = 22     # SSH
    min = 80; max = 80     # HTTP  
    min = 443; max = 443   # HTTPS
    min = 8000; max = 8000 # API
  }
}
```

### 17.5 資源需求與效能最佳化
#### Free Tier 配置建議
| 配置 | OCPU | 記憶體 | 適用場景 | 成本 |
|------|------|-------|----------|------|
| 最小 | 1 | 6 GB | 測試/開發 | 免費 |
| 建議 | 2 | 8 GB | 一般使用 | 免費 |
| 最佳 | 4 | 16 GB | 高負載 | 免費 |

#### 動態映像檔偵測
```hcl
# 跨區域映像檔支援
data "oci_core_images" "oracle_linux" {
  compartment_id = var.compartment_id
  operating_system = "Oracle Linux"
  operating_system_version = "8"
  shape = var.vm_shape
  sort_by = "TIMECREATED"
  sort_order = "DESC"
}

# 智慧映像檔選擇
image_id = var.image_id != "" ? var.image_id : data.oci_core_images.oracle_linux.images[0].id
```

### 17.6 部署後資訊輸出
```hcl
output "deployment_info" {
  value = {
    instance_ip = oci_core_instance.stt_api_instance.public_ip
    api_url = "http://${oci_core_instance.stt_api_instance.public_ip}:8000"
    docs_url = "http://${oci_core_instance.stt_api_instance.public_ip}:8000/docs"
    ssh_command = "ssh opc@${oci_core_instance.stt_api_instance.public_ip}"
    logs_command = "sudo tail -f /var/log/vosk-stt-deployment.log"
  }
}
```

## 18. 模型下載/管理流程
- Vosk 模型於服務啟動時自動下載（如 models/download.py 腳本），啟動前即確保所有必要模型已下載。
- 若下載失敗，系統自動重試（建議最多重試 3 次，間隔 10 秒），仍失敗則標記模型不可用。
- 若模型不可用，API 端點回傳 HTTP 500，error 欄位明確說明「模型下載失敗，無法提供服務」。
- 管理員可於日誌檢查失敗原因並手動修復。

## 19. 安全性測試與金鑰管理
- API 金鑰新增/撤銷流程：提供 scripts/add_key.py、remove_key.py。
- 金鑰儲存格式：config/api_keys.json，內容加密或 hash。
- 測試用金鑰：測試環境自動產生，正式環境手動設定。

## 20. 例外處理與日誌
- 日誌輪替：loguru 支援自動分檔、保留天數設定。
- 錯誤通知：可擴充 email/slack 通知（loguru callback）。
- 異常自動重試：Celery 任務可設定重試次數與間隔。

## 21. CI/CD 詳細流程
- .github/workflows/ci.yml：
  - 安裝依賴
  - 執行 pytest
  - 格式檢查（flake8/black）
  - Docker build & push
  - zip 打包（程式碼、Dockerfile、Terraform）
  - 可於 PRD/DG 補充一鍵部署教學

## 22. 前端/用戶端範例
- 提供簡易前端（如 static/index.html）或 CLI 範例（scripts/client.py），示範 API 輪詢與檔案上傳。
- README.md 補充使用教學。

## 23. 文件自動化
- API 文件自動產生：FastAPI 內建 Swagger UI（/docs），或 OpenAPI JSON。
- README/DG 補充一鍵部署教學、API 文件連結。

## 24. 版本管理與維護策略
- 模型、API、部署腳本皆需版本號（如 models/version.txt、api/VERSION）。
- 重大升級時於 DG/README 註明升級步驟。
- 建議使用 git tag 管理版本。
- 升級前先於本機測試新版本，確定功能正常、無重大 bug，再正式部署到 OCI。

## 25. API 限流設計
- 採用 FastAPI 限流插件（如 slowapi）實現 rate limit。
- 建議設定：每個 API 金鑰或 IP 每 10 秒最多 3 次請求。
- 超過限制時回傳 HTTP 429 Too Many Requests，並提示重試時間。
- 實作範例：
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import FastAPI, Request

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.post("/transcribe")
@limiter.limit("3/10 seconds")
def transcribe(...):
    ...
```
- 文件與 README 明確告知限流規則，提醒用戶端遵守