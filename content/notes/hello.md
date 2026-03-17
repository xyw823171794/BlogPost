---
title: "教程：如何将复杂命令封装为“简单命令”"
date: 2026-03-17
draft: false
--- 

## 第一阶段：编写核心脚本 (`.ps1`)

首先，将所有的逻辑写在一个 PowerShell 脚本里。这比 `.bat` 文件更强大，支持逻辑判断和交互。

1. **保存位置：** 建议放在一个固定的工具目录，例如 `D:\AI\start_model.ps1`。
2. **脚本内容示例（支持选模型、选模式、追加参数）：**

    ```powershell
    # 1. 进入程序目录
    cd "D:\AI\llamaCpp_Release\Release"

    # 2. 列出所有模型 (.gguf)
    $models = Get-ChildItem "D:\AI\Models" -Filter "*.gguf"
    for ($i = 0; $i -lt $models.Count; $i++) {
        Write-Host "[$i] $($models[$i].Name)" -ForegroundColor Cyan
    }

    # 3. 交互获取输入
    $idx = Read-Host "`n请选择模型编号 (默认0)"
    if ($idx -eq "") { $idx = 0 }

    $mode = Read-Host "访问模式: [1]本地 [2]Tailscale (默认1)"
    $host = if ($mode -eq "2") { "0.0.0.0" } else { "127.0.0.1" }

    $extra = Read-Host "追加参数 (如 -ngl 99)"

    # 4. 执行最终命令
    .\llama-server.exe -m $($models[$idx].FullName) --host $host --port 8080 $extra
    ```

---

### 第二阶段：注册“短命令”别名 (Alias)

为了不输入长路径，我们需要利用 PowerShell 的 `$PROFILE`（配置文件），它相当于 Linux 的 `.bashrc`。

#### 1. 强制初始化配置文件

在 PowerShell 中运行，防止路径不存在导致报错：

```powershell
if (!(Test-Path (Split-Path $PROFILE))) { New-Item -ItemType Directory -Path (Split-Path $PROFILE) -Force }; Out-File -FilePath $PROFILE -Append -InputObject ""
```

#### 2. 编辑配置文件

输入 `notepad $PROFILE` 打开记事本。

#### 3. 编写函数别名

在文件末尾添加以下代码：

```powershell
# 定义别名 'ai' 指向你的脚本
function ai {
    powershell -ExecutionPolicy Bypass -File "D:\AI\start_model.ps1"
}
```

* **`function ai`**: `ai` 就是你的简单命令，你可以改成任何你喜欢的词（比如 `ll`）。
* **`-ExecutionPolicy Bypass`**: 确保即使系统限制了脚本运行，该命令也能正常启动。

---

### 第三阶段：激活与权限（仅需一次）

1. **放开权限：** 如果是第一次运行脚本，需在 PowerShell 执行：
    `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
2. **生效配置：** **重启** PowerShell 窗口，或者输入 `. $PROFILE` 立即生效。

---

## 最终效果对比

* **以前：** 需要记路径、切目录、手动复制 IP、手动输入长命令。
* **现在：**
    1. 打开 PowerShell。
    2. 输入 **`ai`**。
    3. 选个数字，回车，搞定。

> **小贴士：** 以后如果你想给命令增加新功能（比如默认加上显卡加速），只需要修改 `D:\AI\start_model.ps1` 这一个文件，你的 `ai` 命令会自动更新。

你需要我针对你的 RTX 4060 显卡，在脚本里加入“显存自动分配”的逻辑吗？
