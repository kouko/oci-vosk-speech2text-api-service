#!/usr/bin/env python3
"""
Vosk 模型下載腳本
用於本地開發環境下載 Vosk 語音辨識模型
"""

import os
import requests
import zipfile
import shutil
from pathlib import Path
import sys

# 模型配置
MODELS_CONFIG = {
    "zh": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip",
            "archive_name": "vosk-model-small-cn-0.22",
            "size": "42M"
        },
        "large": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip",
            "archive_name": "vosk-model-cn-0.22",
            "size": "1.3G"
        }
    },
    "en": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip", 
            "archive_name": "vosk-model-small-en-us-0.15",
            "size": "40M"
        },
        "large": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
            "archive_name": "vosk-model-en-us-0.22",
            "size": "1.8G"
        }
    },
    "ja": {
        "small": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip",
            "archive_name": "vosk-model-small-ja-0.22", 
            "size": "48M"
        },
        "large": {
            "url": "https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip",
            "archive_name": "vosk-model-ja-0.22",
            "size": "1G"
        }
    }
}

def download_file(url: str, dest_path: str, description: str = "") -> bool:
    """
    下載檔案並顯示進度
    """
    print(f"正在下載 {description}...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"\r進度: {progress:.1f}% ({downloaded_size // (1024*1024)}MB/{total_size // (1024*1024)}MB)", end="")
        
        print("\n下載完成!")
        return True
        
    except Exception as e:
        print(f"\n下載失敗: {e}")
        return False

def extract_model(zip_path: str, extract_to: str, archive_name: str) -> bool:
    """
    解壓縮模型檔案
    """
    print(f"正在解壓縮模型到 {extract_to}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # 移動檔案到正確位置
        extracted_dir = os.path.join(extract_to, archive_name)
        if os.path.exists(extracted_dir):
            for item in os.listdir(extracted_dir):
                src = os.path.join(extracted_dir, item)
                dst = os.path.join(extract_to, item)
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.move(src, dst)
                else:
                    if os.path.exists(dst):
                        os.remove(dst)
                    shutil.move(src, dst)
            
            # 清理空目錄
            os.rmdir(extracted_dir)
        
        # 清理 zip 檔案
        os.remove(zip_path)
        print("解壓縮完成!")
        return True
        
    except Exception as e:
        print(f"解壓縮失敗: {e}")
        return False

def check_model_exists(model_dir: str) -> bool:
    """
    檢查模型是否已存在
    """
    mfcc_conf = os.path.join(model_dir, "mfcc.conf")
    return os.path.exists(mfcc_conf)

def download_model(language: str, model_size: str = "small", models_root: str = None) -> bool:
    """
    下載指定語言和大小的模型
    """
    if language not in MODELS_CONFIG:
        print(f"不支援的語言: {language}")
        print(f"支援的語言: {', '.join(MODELS_CONFIG.keys())}")
        return False
    
    if model_size not in MODELS_CONFIG[language]:
        print(f"不支援的模型大小: {model_size}")
        print(f"支援的大小: {', '.join(MODELS_CONFIG[language].keys())}")
        return False
    
    # 設定模型目錄
    if models_root is None:
        script_dir = Path(__file__).parent.parent
        models_root = script_dir / "models"
    else:
        models_root = Path(models_root)
    
    model_dir = models_root / language / model_size
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # 檢查模型是否已存在
    if check_model_exists(str(model_dir)):
        print(f"模型已存在: {language}/{model_size}")
        return True
    
    config = MODELS_CONFIG[language][model_size]
    
    print(f"準備下載 {language} {model_size} 模型 (大小: {config['size']})")
    
    # 下載模型
    zip_path = model_dir / f"{config['archive_name']}.zip"
    
    if not download_file(config['url'], str(zip_path), f"{language} {model_size} 模型"):
        return False
    
    # 解壓縮模型
    if not extract_model(str(zip_path), str(model_dir), config['archive_name']):
        return False
    
    # 驗證模型
    if check_model_exists(str(model_dir)):
        print(f"✅ {language} {model_size} 模型下載並安裝成功!")
        return True
    else:
        print(f"❌ 模型安裝驗證失敗")
        return False

def download_all_models(models_root: str = None):
    """
    下載所有預設模型
    """
    print("開始下載所有 Vosk 模型...")
    
    success_count = 0
    total_count = 0
    
    for language in MODELS_CONFIG:
        for model_size in MODELS_CONFIG[language]:
            total_count += 1
            if download_model(language, model_size, models_root):
                success_count += 1
            print("-" * 50)
    
    print(f"\n下載完成! 成功: {success_count}/{total_count}")

def main():
    """
    主函數
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="下載 Vosk 語音辨識模型")
    parser.add_argument("--language", "-l", choices=list(MODELS_CONFIG.keys()), 
                       help="要下載的語言 (zh, en, ja)")
    parser.add_argument("--size", "-s", default="small", choices=["small", "large"],
                       help="模型大小 (small 或 large)")
    parser.add_argument("--models-dir", "-d", help="模型儲存目錄")
    parser.add_argument("--all", "-a", action="store_true", help="下載所有模型")
    
    args = parser.parse_args()
    
    if args.all:
        download_all_models(args.models_dir)
    elif args.language:
        download_model(args.language, args.size, args.models_dir)
    else:
        print("請指定要下載的語言或使用 --all 下載所有模型")
        print("範例:")
        print("  python download_models.py --language ja")
        print("  python download_models.py --all")
        parser.print_help()

if __name__ == "__main__":
    main()