# Panacea AI 编码工具链

本食谱解释了 Panacea 的 AI 编码体验是如何通过 CLI、SDK 和 VS Code 提供的。

## 您将学习到的内容

- Panacea 中不同的 AI 编码入口点
- CLI、SDK 和 VS Code 扩展与共享后端的关系
- 私有代码辅助的关键产品功能
- 在代码库中查找实现细节的位置

## 为什么这很重要

Panacea 被构建为一个统一的产品，具有多个接口：

- 一个 **CLI**，支持 `anote chat`、代码搜索和代码库审查
- 一个 **VS Code 扩展**，用于编辑器内的 AI 辅助
- 一个 **SDK**，用于将 Panacea 嵌入其他应用程序

这些接口共享一个后端和基于代理的推理层，使产品在桌面、Web 和代码工作流程中保持一致。

## 关键的 Panacea 文件

| 文件 | 重要性 |
|---|---|
| `Panacea/packages/cli` | 开发者工作流程的 TypeScript CLI 实现 |
| `Panacea/packages/vscode` | VS Code 扩展和聊天集成 |
| `Panacea/packages/sdk` | 用于编程访问的 TypeScript SDK |
| `Panacea/packages/backend` | 支持所有 UI 和 CLI 交互的共享后端服务 |

## 工作原理

- 编码用户操作从 CLI、SDK 或 VS Code 扩展开始。
- 请求被发送到 Panacea 的后端 API。
- 后端使用代理编排和模型提供者生成代码感知的答案。
- 响应在同一接口中返回，包含代码建议、解释或修复。

## 有用的产品功能

- **CLI**：`anote chat`、代码库搜索、代码审查、代码生成和基于嵌入的辅助。
- **VS Code**：内联聊天、差异预览、代码操作和流式响应。
- **SDK**：Panacea API 的客户端包装器，支持自定义集成。

## 本地运行

从工作区根目录 (`anote/panacea`)：

```bash
cd Panacea
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

这将启动共享的后端和前端服务。

在另一个终端中，运行 CLI 包：

```bash
cd Panacea/packages/cli
npm install
npm run dev
```

然后您可以在本地使用 CLI 或使用 `npm run build` 构建它。

对于 VS Code 开发，请在 VS Code 中打开 `Panacea/packages/vscode` 并使用调试器启动扩展。

## 食谱说明

本食谱对需要高层次了解 Panacea 多接口 AI 编码产品的团队成员非常有用。它还可以指引读者查找可以修改或扩展的实现文件。
