# 🔐 MiniMax TTS 激活验证服务

这是一个基于 Vercel + Serverless 的在线激活码验证系统，为 MiniMax TTS 桌面应用提供激活码验证服务。

## 🚀 功能特性

- ✅ **在线激活验证** - 支持15位激活码验证
- ✅ **状态查询** - 查询激活码详细状态信息  
- ✅ **设备绑定** - 支持单设备激活限制
- ✅ **安全加密** - 采用加密算法保护激活码
- ✅ **Web界面** - 提供可视化测试界面
- ✅ **API接口** - RESTful API支持

## 📋 API 文档

### 验证激活码
```
POST /api/validate
Content-Type: application/json

{
  "activation_code": "A23456789BCDEFG"
}
```

**响应示例：**
```json
{
  "success": true,
  "valid": true,
  "data": {
    "activation_id": "376d46c9-9a38-4b62-9cec-6e6623777390",
    "expire_date": "2025-06-10T14:21:00",
    "days_valid": 365,
    "version": "3.0"
  },
  "message": "激活码验证成功"
}
```

### 查询激活状态
```
POST /api/status
Content-Type: application/json

{
  "activation_code": "A23456789BCDEFG"
}
```

## 🧪 测试激活码

以下是预设的测试激活码，您可以在Web界面中测试：

| 激活码 | 状态 | 说明 |
|--------|------|------|
| `23456789ABCDEFG` | 已激活 | 测试已激活状态 |
| `A23456789BCDEFG` | 有效未激活 | 测试有效但未激活 |
| `B23456789CDEFGH` | 已过期 | 测试过期状态 |
| `35X3M278XQNFLEQ` | 真实激活码 | 由系统生成的真实激活码 |

## 🛠️ 部署到 Vercel

### 方法1：GitHub 连接 (推荐)

1. **推送代码到 GitHub**：
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **连接 Vercel**：
   - 访问 [vercel.com](https://vercel.com)
   - 点击 "New Project"
   - 导入您的 GitHub 仓库
   - 点击 "Deploy"

### 方法2：Vercel CLI

1. **安装 Vercel CLI**：
   ```bash
   npm install -g vercel
   ```

2. **部署**：
   ```bash
   vercel
   ```

## 🔧 本地开发

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **生成测试激活码**：
   ```bash
   python generate_activation_codes.py
   ```

3. **本地测试验证**：
   ```bash
   python -c "from license_manager import LicenseManager; lm = LicenseManager(); print(lm.validate_activation_code('35X3M278XQNFLEQ'))"
   ```

## 📱 桌面应用集成

在您的桌面应用中添加在线验证功能：

```python
import requests

def verify_activation_online(activation_code, base_url="https://your-vercel-app.vercel.app"):
    """在线验证激活码"""
    try:
        response = requests.post(
            f"{base_url}/api/validate",
            json={"activation_code": activation_code},
            timeout=10
        )
        result = response.json()
        return result.get("success", False) and result.get("valid", False)
    except:
        # 网络错误时回退到本地验证
        return verify_activation_local(activation_code)
```

## 🌐 访问地址

部署成功后，您将获得类似这样的访问地址：
- **主页**: `https://your-app-name.vercel.app`
- **验证API**: `https://your-app-name.vercel.app/api/validate`
- **状态API**: `https://your-app-name.vercel.app/api/status`

## 📂 项目结构

```
TTS-迭代主版本/
├── index.html              # Web界面首页
├── api/                    # Vercel Serverless 函数
│   ├── validate.py         # 激活码验证API
│   └── status.py           # 状态查询API
├── vercel.json             # Vercel配置文件
├── requirements.txt        # Python依赖
├── license_manager.py      # 激活码管理核心
├── generate_activation_codes.py  # 激活码生成工具
└── README.md               # 项目说明
```

## ✅ 下一步

1. **部署到 Vercel** - 按照上述步骤部署
2. **测试API** - 使用测试激活码验证功能
3. **集成到桌面应用** - 在TTS应用中添加在线验证
4. **生成正式激活码** - 为用户生成正式的激活码

现在您的激活验证服务已经准备就绪！🎉 