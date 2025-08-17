# 沒有 VCN 的新用戶部署指南

## 😊 針對全新 OCI 帳戶的部署方案

如果您的 OCI 帳戶中沒有任何 VCN，這裡提供完整的解決方案：

### 🎯 推薦方案："Create Minimal VCN and Subnet"

我們特別為新用戶設計了 **"Create Minimal VCN and Subnet"** 選項：

#### ✅ 優點
- **自動創建最小必要的網路資源**
- **專為 Free Tier 設計**
- **使用不同的 CIDR 範圍避免衝突**
- **添加 Free Tier 標籤便於管理**
- **最小權限要求**

#### 📋 這個選項會創建
- VCN: `10.1.0.0/16` (避免與常見範圍衝突)
- Subnet: `10.1.1.0/24`
- Internet Gateway
- Route Table
- Security List (只開放必要端口)

### 🔧 部署步驟

1. **點擊一鍵部署連結**
2. **選擇 "Create Minimal VCN and Subnet"** (預設選項)
3. **選擇合適的 Compartment**
4. **確認其他設定**
5. **執行部署**

### 🚨 如果仍遇到權限問題

#### 方案 A: 請求管理員權限
聯繫您的 OCI 管理員，請求以下最小權限：

```
Allow group <YourGroup> to manage virtual-network-family in compartment <CompartmentName>
Allow group <YourGroup> to manage instances in compartment <CompartmentName>
```

#### 方案 B: 創建基本 VCN 後使用
如果您可以通過 OCI Console 手動創建 VCN：

1. **手動創建 VCN**：
   - 在 OCI Console → Networking → Virtual Cloud Networks
   - 創建 VCN with Internet Connectivity
   - CIDR: `10.0.0.0/16`

2. **然後使用 "Use Existing VCN and Subnet"**：
   - 選擇您剛創建的 VCN
   - 選擇 Public Subnet

#### 方案 C: 使用 Root Compartment
如果您是帳戶擁有者：

1. **確認您在 Root Compartment 有權限**
2. **選擇 Root Compartment 進行部署**
3. **使用 "Create Minimal VCN and Subnet"**

### 🎓 理解權限層級

| 操作 | 所需權限級別 | 說明 |
|------|-------------|------|
| 使用現有 VCN | `use virtual-network-family` | 最低權限 |
| 創建 Minimal VCN | `manage virtual-network-family` | 中等權限 |
| 創建完整 VCN | `manage virtual-network-family` + 其他 | 較高權限 |

### 🆓 Free Tier 考量

**"Create Minimal VCN and Subnet"** 專門考慮了 Free Tier 限制：

- **VCN**: Free Tier 允許每個 tenancy 最多 2 個 VCN
- **資源標籤**: 自動添加 `FreeTier=true` 標籤
- **命名規範**: 使用 `minimal` 前綴便於識別
- **CIDR 選擇**: 使用 `10.1.x.x` 避免與預設範圍衝突

### 🔍 故障排除

#### 如果部署失敗
1. **檢查 Compartment 權限**
2. **確認 Free Tier 配額**
3. **查看 Resource Manager 日誌**
4. **嘗試不同的 Region**

#### 常見錯誤解決
- `404-NotAuthorizedOrNotFound`: 權限不足
- `LimitExceeded`: Free Tier 配額已滿
- `InvalidParameter`: CIDR 範圍衝突

### 📞 獲得幫助

1. **查看詳細故障排除指南**: `docs/DEPLOYMENT_TROUBLESHOOTING.md`
2. **檢查項目 Issues**: GitHub Issues 頁面
3. **OCI 文檔**: [Free Tier 資源](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm)

### 🚀 成功部署後

部署成功後，您將獲得：
- ✅ 可用的 Vosk STT API 服務
- ✅ 公共 IP 位址訪問
- ✅ API 文檔端點
- ✅ 完整的網路基礎設施

記住：這個 VCN 可以重複使用於其他項目！
