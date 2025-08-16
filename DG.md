# Deployment Guide (DG)

## 1. 部署前準備
- 取得 OCI 帳號與 Free Tier 資源
- 設定 API 金鑰
- 準備 zip 檔案（程式碼、Dockerfile、Terraform 腳本）

## 2. 一鍵部署流程
- 於 OCI Resource Manager 上傳 zip 檔
- 設定 VM CPU/RAM 規格、API 金鑰等參數
- 啟動部署，等待資源建立

## 3. 網路與安全組
- 開放 HTTP (80) 與 HTTPS (443) 端口
- 安裝自簽憑證（nginx/Apache）
- 說明自簽憑證安全性與用戶端存取方式

## 4. 部署後驗證
- 取得公開 IP，測試 API 端點
- 驗證 API 金鑰
- 測試 HTTP/HTTPS 連線

## 5. 常見問題
- 部署失敗排查
- 憑證安裝與安全警告處理
- zip 檔案結構與內容限制

---
> 詳細操作與除錯請依實際需求補充。
