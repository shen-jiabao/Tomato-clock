# 🍅 番茄钟 (Tomato Clock)

一个基于 Python + Tkinter 的桌面端番茄工作法计时器，支持 Windows 系统。

##  功能特点

- **三种模式**：专注 (25分钟)、短休息 (5分钟)、长休息 (15分钟)
- **可视化进度条**：圆形进度条实时显示剩余时间
- **系统托盘支持**：最小化到托盘，后台运行
- **桌面通知**：番茄完成时弹出系统通知 + 提示音
- **自定义设置**：可调整各模式时长、自动开始、提示音开关
- **番茄计数**：自动记录完成的番茄数量
- **快捷键支持**：`空格键` 开始/暂停，`Ctrl+R` 重置
- **配置持久化**：设置自动保存到本地

## ️ 界面预览

![番茄钟界面](https://github.com/shen-jiabao/Tomato-clock/raw/main/assets/screenshot.png)

## 📦 安装方式

### 方法一：直接运行（便携版）

下载 `dist/番茄钟.exe`，双击即可运行，无需安装。

### 方法二：完整安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/shen-jiabao/Tomato-clock.git
   cd Tomato-clock
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 运行安装脚本：
   ```bash
   python installer/installer.py
   ```

   或双击 `dist/番茄钟_安装包/运行.bat`

### 方法三：从源码运行

```bash
git clone https://github.com/shen-jiabao/Tomato-clock.git
cd Tomato-clock
pip install tkinter Pillow pystray pywin32
python main.py
```

##  使用说明

| 操作 | 说明 |
|------|------|
| **专注** | 默认 25 分钟，时间结束自动进入休息模式 |
| **短休息** | 默认 5 分钟，适合每 4 个番茄后使用 |
| **长休息** | 默认 15 分钟，每完成 4 个番茄后自动触发 |
| **开始/暂停** | 点击按钮或按 `空格键` |
| **重置** | 重置当前模式计时 |
| **跳过** | 跳过当前阶段，进入下一阶段 |
| **设置** | 自定义时间、提示音、自动开始等选项 |

## ⚙️ 自定义设置

点击主界面底部的 **⚙️ 设置** 按钮，可调整：

| 设置项 | 说明 | 默认值 |
|--------|------|--------|
| 专注时长 | 工作模式时长 (分钟) | 25 |
| 短休息 | 短休息时长 (分钟) | 5 |
| 长休息 | 长休息时长 (分钟) | 15 |
| 长休息前的番茄数 | 多少个番茄后进入长休息 | 4 |
| 自动开始休息 | 番茄完成后自动开始休息 | 开启 |
| 启用提示音 | 完成时播放提示音 | 开启 |

## 📁 项目结构

```
Tomato-clock/
├── main.py                 # 桌面应用主程序
├── app.js                  # 网页版逻辑 (可选)
├── style.css               # 网页版样式 (可选)
├── index.html              # 网页版主页面 (可选)
├── run.py                  # 运行入口
├── pomodoro.spec           # PyInstaller 打包配置
├── .gitignore              # Git 忽略规则
├── requirements.txt        # Python 依赖
├── assets/
│   └── icon.ico            # 应用图标
├── installer/
│   ├── installer.py        # 安装脚本
│   ├── build_installer.py  # 安装程序构建脚本
│   └── pomodoro_setup.iss  # Inno Setup 配置 (可选)
└── dist/
    ├── 番茄钟.exe           # 便携版可执行文件
    └── 番茄钟_安装包/       # 完整安装程序包
```

##  开发指南

### 环境要求

- Windows 10 或更高版本
- Python 3.12 或更高版本

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行项目

```bash
python main.py
```

### 打包为 .exe

```bash
pyinstaller pomodoro.spec
```

打包后的文件位于 `dist/` 目录。

## 📝 配置文件

用户设置保存在：
- Windows: `%USERPROFILE%\.pomodoro_settings.json`

##  配色方案

| 元素 | 颜色 |
|------|------|
| 背景色 | `#1E1E24` (深灰黑) |
| 工作模式主色 | `#F25F78` (玫瑰粉) |
| 休息模式主色 | `#4ECDC4` (薄荷绿) |
| 文字色 | `#FFFFFF` (纯白) |
| 次要文字 | `#A0A0B0` (浅灰) |

## 📄 许可证

MIT License

## 🙏 致谢

感谢使用番茄钟！如有问题或建议，欢迎提交 Issue 或 Pull Request。
