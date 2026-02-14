# 为 OpenClaw 添加 OpenCode CLI 支持的 PR 方案

## ✅ 已完成的 PR

### PR #16099: feat: add opencode-cli as CLI backend provider

**链接**: https://github.com/openclaw/openclaw/pull/16099

**状态**: 已提交，等待审核

### PR #16087: docs: enhance OpenCode documentation in coding-agent skill

**链接**: https://github.com/openclaw/openclaw/pull/16087

**状态**: 已提交，等待审核

---

## 📋 调研结果

### OpenClaw 的 Provider 系统架构

OpenClaw 有两种 Provider 系统：

| 类型 | 位置 | 实现方式 | 示例 |
|------|------|----------|------|
| **API Providers** | `models.providers` | SDK/API 调用 | anthropic, openai, google |
| **CLI Backends** | `agents.defaults.cliBackends` | 执行本地 CLI | claude-cli, codex-cli, opencode-cli |

### CLI Backend 工作原理

1. **配置位置**: `src/agents/cli-backends.ts`
2. **路由判断**: `src/agents/model-selection.ts` 中的 `isCliProvider()`
3. **执行逻辑**: `src/agents/cli-runner.ts` 中的 `runCliAgent()`

### CliBackendConfig 接口

```typescript
type CliBackendConfig = {
  command: string;                    // CLI 命令
  args?: string[];                    // 基础参数
  resumeArgs?: string[];              // 恢复会话参数 (支持 {sessionId})
  output?: "json" | "text" | "jsonl"; // 输出格式
  modelArg?: string;                  // 模型参数
  sessionArg?: string;                // 会话参数
  sessionIdFields?: string[];         // 从输出提取 session ID 的字段
  systemPromptArg?: string;           // 系统提示词参数
  imageArg?: string;                  // 图片参数
  clearEnv?: string[];                // 要清除的环境变量
  serialize?: boolean;                // 是否串行化执行
}
```

### OpenCode CLI JSON 输出格式

```json
{"type":"step_start","sessionID":"ses_xxx",...}
{"type":"text","part":{"text":"response text",...}
{"type":"step_finish",...}
```

Session ID 从 `step_start.sessionID` 字段提取。

---

## 🎯 已实现的方案

### 1. 添加 opencode-cli CLI Backend (PR #16099)

**修改文件**:
- `src/agents/cli-backends.ts` - 添加 DEFAULT_OPENCODE_BACKEND 配置
- `src/agents/model-selection.ts` - 添加 opencode-cli 到 isCliProvider()
- `docs/gateway/cli-backends.md` - 添加文档

**配置详情**:
```typescript
const DEFAULT_OPENCODE_BACKEND: CliBackendConfig = {
  command: "opencode",
  args: ["run", "--format", "json"],
  resumeArgs: ["run", "--format", "json", "--session", "{sessionId}"],
  output: "jsonl",
  modelArg: "--model",
  sessionArg: "--session",
  sessionMode: "existing",
  sessionIdFields: ["sessionID"],
  systemPromptArg: "--prompt",
  imageArg: "--file",
  clearEnv: ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", ...],
  serialize: true,
};
```

**使用方式**:
```bash
# 直接使用
openclaw agent --message "hi" --model opencode-cli/anthropic/claude-sonnet-4-5

# 作为 fallback
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["opencode-cli/anthropic/claude-sonnet-4-5"],
      },
    },
  },
}
```

### 2. 增强 coding-agent skill 文档 (PR #16087)

**修改文件**:
- `skills/coding-agent/SKILL.md` - 添加详细的 OpenCode 使用文档

**新增内容**:
- 命令参考表
- Flags 文档
- 会话管理示例
- 多模型支持示例
- GitHub PR 集成
- MCP 集成参考

---

## 📚 原始调研内容（参考）

### OpenClaw 现有支持情况

OpenClaw **已经有 OpenCode 的基础支持**，位于 `skills/coding-agent/SKILL.md`:

```bash
# 当前支持的命令
bash pty:true workdir:~/project command:"opencode run 'Your task'"
```

### 现有的 Coding Agent 支持

| Agent | 支持状态 | 功能 |
|-------|---------|------|
| Claude Code | ✅ 完整 | `claude 'Your task'` |
| Codex CLI | ✅ 完整 | `codex exec --full-auto 'Your task'` |
| OpenCode | ⚠️ 基础 | `opencode run 'Your task'` |
| Pi Agent | ✅ 完整 | `pi 'Your task'` |

### 需要改进的地方

1. **OpenCode 文档不完整** - 缺少详细的使用说明 ✅ 已修复 (PR #16087)
2. **缺少 OpenCode CLI Backend** - 类似 claude-cli 的 provider 支持 ✅ 已修复 (PR #16099)
3. **缺少 OpenCode provider** - 类似 GitHub Copilot 的认证支持 (未实现)

### Step 1: Fork 并创建分支

```bash
# 1. Fork openclaw/openclaw 到你的 GitHub

# 2. Clone 你的 fork
git clone https://github.com/YOUR_USERNAME/openclaw.git
cd openclaw

# 3. 创建功能分支
git checkout -b feat/enhance-opencode-support

# 4. 安装依赖
pnpm install
```

### Step 2: 修改 coding-agent skill

**文件**: `skills/coding-agent/SKILL.md`

**添加内容** (在 OpenCode 部分):

```markdown
## OpenCode

OpenCode 是一个开源的 AI 编程助手，支持多种模型。

### 基本使用

\`\`\`bash
# 单次执行
bash pty:true workdir:~/project command:"opencode run 'Your task'"

# 后台运行
bash pty:true workdir:~/project background:true command:"opencode run 'Your long task'"

# 使用特定模型
bash pty:true workdir:~/project command:"opencode run -m gemini-2.5-pro 'Your task'"
\`\`\`

### OpenCode 特有功能

#### 1. Session 管理

\`\`\`bash
# 继续上一次会话
bash pty:true workdir:~/project command:"opencode -c"

# 指定 session ID
bash pty:true workdir:~/project command:"opencode -s session_abc123"
\`\`\`

#### 2. MCP 集成

OpenCode 支持 MCP (Model Context Protocol)，可以扩展功能：

\`\`\`bash
# 添加 MCP server
opencode mcp add --transport http xiaohongshu-mcp http://localhost:18060/mcp

# 列出 MCP servers
opencode mcp list
\`\`\`

#### 3. 多模型支持

\`\`\`bash
# 使用 Gemini
bash pty:true command:"opencode run -m gemini-2.5-pro 'Your task'"

# 使用 Claude
bash pty:true command:"opencode run -m claude-opus-4 'Your task'"

# 使用本地模型 (Ollama)
bash pty:true command:"opencode run -m ollama/llama3 'Your task'"
\`\`\`

### OpenCode Flags

| Flag | 说明 |
|------|------|
| `run "prompt"` | 执行单次任务 |
| `-m, --model` | 指定模型 |
| `-c, --continue` | 继续上一次会话 |
| `-s, --session` | 指定 session ID |
| `--fork` | Fork 会话 |
| `--agent` | 指定 agent |
| `mcp add` | 添加 MCP server |
| `mcp list` | 列出 MCP servers |

### 与 Claude Code 的对比

| 功能 | OpenCode | Claude Code |
|------|----------|-------------|
| 开源 | ✅ MIT | ❌ 闭源 |
| 多模型 | ✅ 75+ providers | ❌ 只有 Claude |
| MCP | ✅ 原生支持 | ✅ 原生支持 |
| 本地模型 | ✅ Ollama | ❌ 不支持 |
| 免费使用 | ✅ 可用免费模型 | ❌ 需要订阅 |

### OpenCode 最佳实践

1. **使用 workdir 限制上下文**
   \`\`\`bash
   bash pty:true workdir:~/specific-project command:"opencode run 'Fix the bug'"
   \`\`\`

2. **使用 background 处理长任务**
   \`\`\`bash
   bash pty:true workdir:~/project background:true command:"opencode run 'Refactor entire codebase'"
   process action:log sessionId:XXX
   \`\`\`

3. **完成后通知**
   \`\`\`bash
   bash pty:true workdir:~/project background:true command:"opencode run 'Build feature X. When done, run: openclaw system event --text \"Done: Feature X\" --mode now'"
   \`\`\`
```

### Step 3: 更新 skill.yaml metadata

**文件**: `skills/coding-agent/skill.yaml`

```yaml
name: coding-agent
description: Run Codex CLI, Claude Code, OpenCode, or Pi Coding Agent via background process for programmatic control.
metadata:
  {
    "openclaw": { 
      "emoji": "🧩", 
      "requires": { "anyBins": ["claude", "codex", "opencode", "pi"] }
    },
    "opencode": {
      "features": ["session-management", "mcp-integration", "multi-model"],
      "recommended": "opencode/claude-opus-4-6"
    }
  }
```

### Step 4: 提交 PR

```bash
# 1. 提交更改
git add skills/coding-agent/
git commit -m "feat(skills): enhance OpenCode CLI support

- Add detailed OpenCode usage documentation
- Add session management examples
- Add MCP integration guide
- Add multi-model support examples
- Add comparison with Claude Code
- Add best practices section

Refs: #issue-number"

# 2. Push 到你的 fork
git push origin feat/enhance-opencode-support

# 3. 在 GitHub 上创建 PR
gh pr create --repo openclaw/openclaw \
  --title "feat(skills): enhance OpenCode CLI support" \
  --body "$(cat <<'EOF'
## Summary

Enhance OpenCode CLI support in the coding-agent skill with detailed documentation and examples.

## Changes

- ✅ Add detailed OpenCode usage documentation
- ✅ Add session management examples
- ✅ Add MCP integration guide
- ✅ Add multi-model support examples
- ✅ Add comparison with Claude Code
- ✅ Add best practices section

## Testing

- [x] Tested locally with OpenCode CLI
- [x] Verified commands work as documented
- [x] Checked markdown rendering

## AI-Assisted

- [x] This PR was created with AI assistance (Claude Code)
- [x] I understand what the code does
- [x] Changes have been reviewed

## Related

This addresses the need for better OpenCode documentation as discussed in the community.
EOF
)"
```

---

## 🔄 替代方案

如果核心团队认为这个改动太大，可以考虑：

### 方案 A: 只更新文档

在 `docs/providers/opencode.md` 中添加更详细的使用说明。

### 方案 B: 创建独立的 OpenCode skill

创建一个新的 `skills/opencode/` skill，专门用于 OpenCode 相关功能。

### 方案 C: 提交 GitHub Discussion

先在 [GitHub Discussions](https://github.com/openclaw/openclaw/discussions) 提议，收集社区反馈后再实现。

---

## 📚 参考资源

- [OpenClaw CONTRIBUTING.md](https://github.com/openclaw/openclaw/blob/main/CONTRIBUTING.md)
- [OpenClaw coding-agent skill](https://github.com/openclaw/openclaw/tree/main/skills/coding-agent)
- [OpenCode 官方文档](https://opencode.ai/docs/)
- [OpenCode CLI](https://github.com/anomalyco/opencode)

---

## ✅ 快速开始清单

```bash
# 1. Fork 并 clone
gh repo clone YOUR_USERNAME/openclaw --depth 1

# 2. 创建分支
cd openclaw && git checkout -b feat/enhance-opencode-support

# 3. 安装依赖
pnpm install

# 4. 修改文件
# 编辑 skills/coding-agent/SKILL.md

# 5. 测试
pnpm build && pnpm check

# 6. 提交 PR
git add . && git commit -m "feat: enhance OpenCode support"
git push origin feat/enhance-opencode-support
gh pr create
```
