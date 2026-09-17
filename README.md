# 紫团 · Codex 桌宠

[![Release](https://img.shields.io/github/v/release/Sa11os/zituan-codex-pet?display_name=tag&sort=semver)](https://github.com/Sa11os/zituan-codex-pet/releases/latest)
[![Validate](https://github.com/Sa11os/zituan-codex-pet/actions/workflows/validate.yml/badge.svg)](https://github.com/Sa11os/zituan-codex-pet/actions/workflows/validate.yml)
[![Sprite format](https://img.shields.io/badge/sprite-v2-8f72b7)](pet/lilac-chibi/pet.json)

紫团是一只银紫发、金色眼睛、穿宽松紫黑外套的手绘 Q 版 Codex 桌宠。她包含 9 组状态动画、57 个标准动画帧和 16 个顺时针目光方向。

![紫团动作总览](media/contact-sheet.png)

## 功能

- 适配本地桌面端的 v2 桌宠图集：8 列 × 11 行，单格 192 × 208。
- 包含待机、左右移动、挥手、跳跃、失败、等待输入、工作中和审阅中等状态。
- 支持 16 向目光跟随，并保留独立的中心待机参考格。
- 提供浏览器预览页、确定性打包脚本、结构校验脚本和 GitHub Actions。

## 安装

1. 从 [Releases](https://github.com/Sa11os/zituan-codex-pet/releases/latest) 下载 `zituan-codex-pet-v1.0.0.zip`。
2. 解压后，将整个 `lilac-chibi` 文件夹复制到 Codex 配置目录的 `pets` 文件夹中。
3. 在桌面应用的 **Settings → Pets** 中刷新宠物列表，然后选择“紫团”。

Windows 默认路径：

```text
%USERPROFILE%\.codex\pets\lilac-chibi
```

如果设置了 `CODEX_HOME`，请使用 `<CODEX_HOME>/pets/lilac-chibi`。安装后，`pet.json` 与 `spritesheet.webp` 必须位于同一目录。

桌宠的显示入口、状态含义和减少动态效果行为见 [OpenAI 官方 Pets 文档](https://learn.chatgpt.com/docs/pets)。自定义桌宠保存在本机，不会自动同步到 Web 端。

## 兼容性

| 项目 | 值 |
| --- | --- |
| 发布版本 | `v1.0.0` |
| 图集格式 | `spriteVersionNumber: 2` |
| 图集尺寸 | 1536 × 2288 WebP |
| 帧尺寸 | 192 × 208 |
| 标准状态 | 9 组 / 57 帧 |
| 目光方向 | 16 |

当前 OpenAI 官方 Web 上传入口要求 1536 × 1872 的透明 PNG 或 WebP。本项目使用本地桌面端的 1536 × 2288 v2 扩展图集，因此不要把它直接上传到 Web 端的自定义宠物入口。

## 预览

克隆仓库后直接打开 [`preview/index.html`](preview/index.html)，即可查看全部状态、暂停动画、切换背景并测试鼠标方向。

| 待机 | 工作中 | 目光方向 |
| --- | --- | --- |
| ![待机动画](media/previews/idle.gif) | ![工作中动画](media/previews/running.gif) | ![目光方向](media/previews/look-directions.gif) |

## 仓库结构

```text
pet/lilac-chibi/       可直接安装的桌宠目录
preview/               本地浏览器预览页
media/                 README 与人工检查用预览
docs/                  动画触发条件、QA 与安装说明
scripts/               构建和校验发布包
.github/workflows/     持续校验与自动发布
```

## 构建与校验

只需要 Python 3.10 或更高版本，不依赖第三方包：

```powershell
python scripts/validate_release.py
python scripts/build_release.py
python scripts/validate_release.py --archive dist/zituan-codex-pet-v1.0.0.zip
```

构建使用固定文件顺序、时间戳和无损储存方式；相同源码会生成相同 ZIP。发布工作流还会生成 `SHA256SUMS.txt`。

详细质量记录见 [QA 摘要](docs/QA.md)，动画与鼠标触发关系见 [动画触发条件](docs/ANIMATION-TRIGGERS.md)。

## 许可

- `scripts/`、`preview/`、工作流和文字文档使用 [MIT License](LICENSE)。
- `pet/` 与 `media/` 中的角色、美术、图集和动画使用 [CC BY-NC-SA 4.0](ASSET-LICENSE.md)。

© 2026 Sallos
