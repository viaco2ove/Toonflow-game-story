# 角色卡上传指南

## 平台选择

### 推荐：自建 SillyTavern-Card

Chub.ai 和 cards.sillytavern.one 都**没有公开的上传 API**，只能手动网页上传，不支持批量。

**SillyTavern-Card** 是唯一有完整上传 API 的方案：

```bash
# 1. 克隆部署
git clone https://github.com/tolixing/SillyTavern-Card.git
cd SillyTavern-Card
docker compose up -d

# 2. 打开管理界面（首次需要创建管理员账号）
# 访问 http://localhost:3000

# 3. 上传 API（批量脚本用）
curl -X POST http://localhost:3000/api/upload \
  -F "file=@顾泽.png" \
  -F "name=顾泽" \
  -F "version=1.0" \
  -F "description=破局-从冷落走到瞩目 主角"
```

### Chub.ai 手动上传

1. 访问 https://chub.ai
2. 登录账号
3. 点击 Create Character
4. 填写表单：
   - Name（角色名）
   - Description（人设描述）
   - Image（上传 PNG 角色卡）
   - Tags（标签）
5. 发布

> ⚠️ Chub.ai 无 API，不支持批量上传

### cards.sillytavern.one

需要联系运营方收录，无公开上传入口。

---

## 批量上传脚本设计（待实现）

当自建 SillyTavern-Card 后，可使用以下脚本批量上传：

```python
import requests
import os
from pathlib import Path

CHARS_DIR = Path("characters_repo/破局-从冷落走到瞩目")
API_URL = "http://localhost:3000/api/upload"

for png_file in CHARS_DIR.glob("*.png"):
    if png_file.stem == "旁白-叙事者":
        continue  # 叙事者卡暂不上传
    name = png_file.stem
    with open(png_file, "rb") as f:
        files = {"file": (png_file.name, f, "image/png")}
        data = {"name": name, "version": "1.0"}
        resp = requests.post(API_URL, files=files, data=data)
    print(f"{name}: {resp.status_code}")
```

---

## 当前状态

| 项目 | 状态 | 说明 |
|------|------|------|
| 角色卡生成 | ✅ 完成 | 13 个 PNG + 13 个 JSON |
| 叙事者卡 | ✅ 完成 | 旁白-叙事者.png |
| 世界书 | ✅ 完成 | 世界书.json |
| Chub.ai 上传 | ⏳ 待手动 | 无 API，需网页操作 |
| SillyTavern-Card | ⏳ 待部署 | 有 API，推荐自建 |