---
date: '2026-03-17T15:38:58+08:00'
draft: true
title: '编译llamaCpp 并使用大模型'
---
2026-03-18 11:56:45

## 一、 环境准备 (核心依赖)

在开始之前，确保你的系统已安装以下组件，这是调用 4060 显卡的前提：

* **CUDA Toolkit**: 建议安装 12.x 或 13.1 版本（你当前为 13.1）。
* **Visual Studio 2022**: 必须安装“使用 C++ 的桌面开发”工作负载。
* **CMake**: 建议版本 3.20 或更高。

### 二、 性能最大化编译步骤

针对你的 Ada Lovelace 架构 (RTX 4060)，请在 **Developer PowerShell for VS 2022** 中执行以下命令：

1. **创建构建目录**：

    ```powershell
    cd D:\AI\llama_2
    mkdir build
    cd build
    ```

2. **配置 CMake (针对 4060 优化)**：
    使用 `-DGGML_CUDA=ON` 开启 GPU 加速，并指定 `8.9` 计算架构以获得最佳指令集优化：

    ```powershell
    cmake .. -G "Visual Studio 17 2022" -A x64 -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89
    ```

3. **执行高并发编译**：
    使用 `Release` 模式（性能最高）并开启多线程编译：

    ```powershell
    cmake --build . --config Release --parallel 16
    ```

### 三、 常见编译报错修复 (No CUDA toolset found)

如果你遇到该错误，通常是 VS 找不到 CUDA 路径。

* **手动修复**：将 `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1\extras\visual_studio_integration\MSBuildExtensions` 下的所有文件，复制到 Visual Studio 的构建自定义目录中（例如 `...\MSBuild\Microsoft\VC\v170\BuildCustomizations`）。

### 四、 运行时的“榨干性能”参数

编译完成后，或者使用预编译的 `.dll` 库文件（如 `cublas64_13.dll`, `cudart64_13.dll` 等）时，请务必使用以下参数启动：

* **`-ngl 99` (或 `--n-gpu-layers 99`)**：
    将模型所有层强制加载到显存。4060 的 8G 显存足以完整运行量化后的 7B/8B 模型。
* **`-fa on` (或 `--flash-attn on`)**：
    **必须开启**。它能大幅提升推理速度并减少显存占用，是现代 NVIDIA 显卡的性能核心。
* **`-c 8192` (Context Size)**：
    合理设置上下文长度。开启 Flash Attention 后，你可以尝试更大的上下文而不会导致显存溢出。
* **`-t 16` (Threads)**：
    设置线程数与你 CPU 的逻辑核心数一致，加速 Prompt 的预处理阶段。

### 五、 快速验证清单

1. **检查设备识别**：运行 `./llama-cli.exe --list-devices`，确认输出中有 `RTX 4060`。
2. **检查库文件**：确保 `llama-cli.exe` 与那三个 CUDA 核心 `.dll` 文件（cublas, cublasLt, cudart）位于同一文件夹下。
3. **开启 Fallback**：在 Windows NVIDIA 控制面板中确保开启了 `System Memory Fallback`，以防显存偶尔不足时程序崩溃。
