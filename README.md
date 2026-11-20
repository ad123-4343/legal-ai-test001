# ⚖️ AI 法务对话流自动化测试框架 (Legal-AI-Test)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Pytest](https://img.shields.io/badge/Framework-Pytest-green.svg)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-brightgreen.svg)

## 📖 项目简介

本项目是一个针对 Dify 智能法务助手（对话流 API）构建的**企业级 AI 自动化测试框架**。
针对大语言模型（LLM）输出的“概率性”与“发散性”痛点，本框架不仅涵盖了传统的 API 接口测试，还引入了 **LLM-as-Judge（大模型作为裁判）** 和 **多维度混合断言** 机制，实现了从底层网络连通性到深层语义质量的全方位质量保障。

## ✨ 核心特性

- **数据驱动测试 (DDT)**：使用 YAML 文件管理测试题库与预期标准，实现测试数据与代码逻辑完全解耦，便于业务人员随时扩充题库。
- **多维度混合断言策略**：
  - ⏱️ **性能断言**：监控 API 响应延迟 (Latency)，拦截超时请求。
  - 🛡️ **安全硬断言**：基于 Blacklist（黑名单）机制，强制拦截“包赢”、“保证胜诉”等绝对化违规承诺。
  - 📏 **正则格式校验**：强制校验法条引用格式（如“第X条”），确保回答的专业严谨性。
  - ⚖️ **语义软断言 (LLM-as-Judge)**：接入智谱 GLM 大模型作为第三方裁判，根据预设的合规标准对 AI 回答进行打分评估，解决传统代码无法评估“语义幻觉”的痛点。
- **企业级 Mock 打桩隔离**：通过环境变量自动识别运行环境。在云端运行时，自动启用 Mock 假数据隔离局域网依赖，保障流水线的高可用性并降低 Token 消耗。
- **安全合规**：使用 `python-dotenv` 实现敏感配置（API Keys）与代码库的物理隔离，保障资产安全。

## 🛠️ 技术栈

- **语言**：Python 3
- **测试框架**：Pytest
- **大模型交互**：OpenAI SDK (兼容模式)
- **配置管理**：PyYAML, python-dotenv
- **报告生成**：pytest-html
- **CI 平台**：GitHub Actions

## 🚀 本地运行指南

1. 克隆本仓库到本地：
   ```bash
   git clone https://github.com/你的用户名/legal-ai-test001.git
