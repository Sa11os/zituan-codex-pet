# 安装紫团桌宠

## Windows

1. 关闭正在占用旧版紫团文件的桌面应用。
2. 将发布包中的 `lilac-chibi` 文件夹复制到 `%USERPROFILE%\.codex\pets\`。
3. 确认目录中同时存在 `pet.json` 和 `spritesheet.webp`。
4. 打开桌面应用，在 **Settings → Pets** 中刷新并选择“紫团”。

最终目录应为：

```text
%USERPROFILE%\.codex\pets\lilac-chibi\pet.json
%USERPROFILE%\.codex\pets\lilac-chibi\spritesheet.webp
```

设置了 `CODEX_HOME` 时，将 `%USERPROFILE%\.codex` 替换为对应目录。

## 验证下载

发布页同时提供 `SHA256SUMS.txt`。在 PowerShell 中运行：

```powershell
Get-FileHash .\zituan-codex-pet-v1.0.0.zip -Algorithm SHA256
```

将输出与 `SHA256SUMS.txt` 中的值对比。

## 预览

双击发布包中的 `preview.html`，可以在浏览器中查看 9 组动画和 16 个目光方向。预览通过只证明图集加载和切帧正常，不能替代具体桌面应用版本的悬浮层运行测试。

桌宠功能入口与平台差异见 [OpenAI 官方 Pets 文档](https://learn.chatgpt.com/docs/pets)。
