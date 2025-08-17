# 🎉 部署完成！Vosk STT API 服務已成功部署

## 📋 部署資訊

您的 Vosk Speech-to-Text API 服務已成功部署到 OCI！

### 🔗 服務端點

- **API 基礎 URL**: `http://YOUR_INSTANCE_IP:8000`
- **API 文檔**: `http://YOUR_INSTANCE_IP:8000/docs`
- **健康檢查**: `http://YOUR_INSTANCE_IP:8000/health`

### 🔑 API 使用方式

#### 1. 健康檢查
```bash
curl http://YOUR_INSTANCE_IP:8000/health
```

#### 2. 獲取支援的語言和模型
```bash
curl -H "x-api-key: YOUR_API_KEY" \
     http://YOUR_INSTANCE_IP:8000/models
```

#### 3. 語音轉文字（同步）
```bash
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -F "file=@your_audio.wav" \
     -F "language=en" \
     -F "model_size=small" \
     http://YOUR_INSTANCE_IP:8000/transcribe
```

#### 4. 語音轉文字（異步）
```bash
# 提交任務
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -F "file=@your_audio.wav" \
     -F "language=en" \
     -F "model_size=small" \
     http://YOUR_INSTANCE_IP:8000/transcribe-async

# 檢查任務狀態
curl -H "x-api-key: YOUR_API_KEY" \
     http://YOUR_INSTANCE_IP:8000/tasks/TASK_ID
```

### 🎯 支援的功能

- ✅ **多語言支援**: 中文、英文、日文
- ✅ **模型大小**: small (快速) / large (精確)
- ✅ **同步/異步處理**: 適應不同使用場景
- ✅ **多種輸出格式**: JSON、字幕格式 (VTT)
- ✅ **檔案格式支援**: WAV, MP3, MP4, FLAC, AAC

### 🔧 管理和監控

#### SSH 連接到實例
```bash
ssh opc@YOUR_INSTANCE_IP
```

#### 查看服務日誌
```bash
# 部署日誌
sudo tail -f /var/log/vosk-stt-deployment.log

# 服務日誌
docker logs vosk-stt-api

# 即時日誌
docker logs -f vosk-stt-api
```

#### 重啟服務
```bash
sudo docker restart vosk-stt-api
```

#### 檢查服務狀態
```bash
sudo docker ps
sudo docker stats vosk-stt-api
```

### 📊 性能調優建議

1. **模型選擇**:
   - `small` 模型：更快的處理速度，適合即時應用
   - `large` 模型：更高的準確度，適合批量處理

2. **實例規格**:
   - 最小配置：1 OCPU, 6GB RAM (適合輕量使用)
   - 推薦配置：2+ OCPU, 8GB+ RAM (適合生產環境)

3. **檔案大小限制**:
   - 預設最大檔案大小：100MB
   - 可透過環境變數 `MAX_FILE_SIZE` 調整

### 🛡️ 安全性注意事項

1. **API 金鑰管理**:
   - 請妥善保管您的 API 金鑰
   - 定期更新 API 金鑰
   - 不要在客戶端代碼中硬編碼 API 金鑰

2. **網路安全**:
   - 考慮使用 HTTPS (需要額外配置 Load Balancer)
   - 限制來源 IP 範圍（如需要）

### 🆘 常見問題

#### Q: 為什麼 API 回應很慢？
A: 首次使用時，系統需要下載模型檔案（約 100-500MB），請耐心等待。

#### Q: 如何更改 API 金鑰？
A: 重新部署時設定新的 API 金鑰，或透過 Docker 環境變數更新。

#### Q: 支援哪些音頻格式？
A: WAV, MP3, MP4, FLAC, AAC 等常見格式。

#### Q: 如何提高轉錄準確度？
A: 使用 large 模型、確保音質清晰、選擇正確的語言設定。

### 📞 技術支援

如果遇到問題，請檢查：
1. [GitHub Issues](https://github.com/kouko/oci-vosk-speech2text-api-service/issues)
2. 服務日誌檔案
3. OCI 控制台中的實例狀態

---

**🎊 恭喜！您的 Vosk STT API 服務已準備就緒！**