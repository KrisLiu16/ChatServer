### ChatServer

ChatServer 是一个简单而美观的留言聊天应用，适合部署在云服务器上作为留言板使用。它还包含一个 `/file` 端点，方便跨平台传输文件而无需额外安装软件。

#### 主要特点：
- **留言板功能：** 用户可以发布消息并实时查看更新。
- **文件传输：** 跨平台分享文件变得更加容易。
- **可扩展性：** 可以作为毕业设计项目或个人项目二次开发。
- **集成性：** 可以通过 POST 方法轻松集成到现有应用中。
- **简易部署：** 只需下载文件到服务器并运行 `server.py` 即可。

#### 环境要求：
- Python 3.9+
- Flask

#### 安装步骤：
1. 克隆仓库：
   ```bash
   git clone <repository_url>
   cd ChatServer
   ```
2. 安装 Flask（如果尚未安装）：
   ```bash
   pip install Flask
   ```

#### 使用方法：
1. 启动服务器：
   ```bash
   python server.py
   ```
2. 在浏览器中访问 `http://localhost` 即可使用应用，默认端口80。

#### 文件结构：
- `server.py`：启动 Flask 服务器的主要脚本。
- `templates/`：包含用于渲染网页界面的 HTML 文件。
- `static/`：包含用于样式和功能的 CSS 和 JavaScript 文件。

#### 示例应用：
- 可作为毕业设计项目或个人使用。
- 情侣之间分享日常.

---

欢迎根据个人需求自由定制和扩展 ChatServer。祝您编码愉快！
