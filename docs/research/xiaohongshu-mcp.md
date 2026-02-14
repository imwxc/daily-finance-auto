# 小红书 MCP 配置调研

## 项目简介

通过 MCP (Model Context Protocol) 协议，可以让 Claude Code / OpenCode 等 AI 工具直接操作小红书，实现自动化内容浏览和发布。

---

## 推荐项目：xiaohongshu-mcp

| 属性 | 详情 |
|------|------|
| **GitHub** | https://github.com/xpzouying/xiaohongshu-mcp |
| **Stars** | 8.2K+ |
| **技术栈** | Go + Gin + Rod 浏览器自动化 |
| **协议** | MCP (Model Context Protocol) |

### 功能列表

- ✅ 登录和检查登录状态
- ✅ 发布图文内容
- ✅ 发布视频内容
- ✅ 搜索内容
- ✅ 获取推荐列表
- ✅ 获取帖子详情（互动数据、评论）
- ✅ 发表评论
- ✅ 获取用户个人主页

---

## 安装步骤

### 1. 下载预编译二进制

从 [GitHub Releases](https://github.com/xpzouying/xiaohongshu-mcp/releases) 下载对应平台文件：

- macOS: `xiaohongshu-mcp-darwin-arm64`
- Windows: `xiaohongshu-mcp-windows-amd64.exe`
- Linux: `xiaohongshu-mcp-linux-amd64`

### 2. 登录小红书

```bash
chmod +x xiaohongshu-login-darwin-arm64
./xiaohongshu-login-darwin-arm64
```

扫描二维码登录。

### 3. 启动 MCP 服务

```bash
chmod +x xiaohongshu-mcp-darwin-arm64
./xiaohongshu-mcp-darwin-arm64
```

服务地址：`http://localhost:18060/mcp`

---

## Claude Code 配置

```bash
# 添加 HTTP MCP 服务器
claude mcp add --transport http xiaohongshu-mcp http://localhost:18060/mcp

# 验证配置
claude mcp list
```

---

## OpenCode 配置

在项目根目录创建 `.opencode/mcp.json`：

```json
{
  "mcpServers": {
    "xiaohongshu-mcp": {
      "url": "http://localhost:18060/mcp",
      "description": "小红书内容发布服务"
    }
  }
}
```

---

## 可用工具

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `check_login_status` | 检查登录状态 | 无 |
| `publish_content` | 发布图文 | title, content, images |
| `publish_with_video` | 发布视频 | title, content, video |
| `list_feeds` | 获取推荐列表 | 无 |
| `search_feeds` | 搜索内容 | keyword |
| `get_feed_detail` | 获取帖子详情 | feed_id, xsec_token |
| `post_comment_to_feed` | 发表评论 | feed_id, xsec_token, content |
| `user_profile` | 获取用户主页 | user_id, xsec_token |

---

## 使用示例

配置完成后，在 Claude Code / OpenCode 中直接用自然语言：

```
帮我检查小红书登录状态
```

```
搜索小红书上关于"美食"的内容
```

```
帮我发布一篇关于春天的图文到小红书，使用这张图片：/Users/xxx/Pictures/spring.jpg
```

---

## 注意事项

1. **账号安全**：同一账号不要在多个网页端同时登录
2. **发布限制**：小红书每天发帖量约 50 篇
3. **标题限制**：不超过 20 个字
4. **正文限制**：不超过 1000 个字
5. **图片路径**：推荐使用本地绝对路径，避免中文路径
