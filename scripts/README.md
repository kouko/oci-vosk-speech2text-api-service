# 模型下載腳本

這個目錄包含用於下載 Vosk 語音辨識模型的腳本。

## download_models.py

Python 腳本，用於在本地開發環境下載 Vosk 模型。

### 使用方法

#### 下載單一語言模型
```bash
# 下載日文模型
python scripts/download_models.py --language ja

# 下載英文模型  
python scripts/download_models.py --language en

# 下載中文模型
python scripts/download_models.py --language zh
```

#### 下載所有模型
```bash
python scripts/download_models.py --all
```

#### 指定模型儲存目錄
```bash
python scripts/download_models.py --language ja --models-dir /custom/path/models
```

### 支援的模型

| 語言 | 語言代碼 | 模型大小 | 檔案大小 | 來源 |
|------|----------|----------|----------|------|
| 中文 | zh | small | 42M | vosk-model-small-cn-0.22 |
| 中文 | zh | large | 1.3G | vosk-model-cn-0.22 |
| 英文 | en | small | 40M | vosk-model-small-en-us-0.15 |
| 英文 | en | large | 1.8G | vosk-model-en-us-0.22 |
| 日文 | ja | small | 48M | vosk-model-small-ja-0.22 |
| 日文 | ja | large | 1G | vosk-model-ja-0.22 |

### 模型目錄結構

下載後的模型會儲存在以下結構：

```
models/
├── zh/
│   └── small/
│       ├── mfcc.conf
│       ├── final.mdl
│       └── ...
├── en/
│   └── small/
│       ├── mfcc.conf
│       ├── final.mdl
│       └── ...
└── ja/
    └── small/
        ├── mfcc.conf
        ├── final.mdl
        └── ...
```

### 腳本功能

- ✅ 自動檢查模型是否已存在，避免重複下載
- ✅ 顯示下載進度
- ✅ 自動解壓縮和安裝
- ✅ 模型完整性驗證
- ✅ 支援自定義模型目錄
- ✅ 清理暫存檔案

### 依賴套件

腳本需要以下 Python 套件：
- `requests` (用於下載檔案)
- `zipfile` (用於解壓縮)
- `pathlib` (用於路徑處理)

這些套件都是 Python 標準庫的一部分，無需額外安裝。