<template>
  <div id="app" class="app">
    <div class="header">
      <h1 class="title">LLM Code Scorer</h1>
      <p class="description">Get AI's Comments and Suggestions on Your Code.</p>
      <div class="input-container">
        <input v-model="repoUrl" type="text" placeholder="输入 GitHub 仓库 URL" class="input" @keyup.enter="getScore" />
        <button @click="getScore" class="btn" :disabled="loading">获取评分</button>
      </div>
      <div v-if="loading" class="loader"></div>
      <p v-if="loading" class="loading-text">LLM 打分中，请耐心等待...</p>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </div>

    <div v-if="score !== null && !loading" ref="resultArea" class="result">
      <div class="score-container">
        <h2 class="score">评分: <span>{{ score.toFixed(2) }}</span> / 10</h2>
        <button @click="shareResults" class="save-btn" ref="saveButton">保存</button>
      </div>
      <p class="comment">{{ comment }}</p>
      <h3 class="details-title">评分细节</h3>
      <div class="details">
        <div v-for="(item, key) in detail" :key="key" class="detail-item">
          <h4>{{ key }}:{{ item.分数 }}</h4>
          <p>{{ item.理由 }}</p>
        </div>
      </div>
    <h3 class="summary-title">总评与建议</h3>
    <p class="suggestion">{{ description }}</p>
    </div>

    <footer class="footer">
      <p>
        <a href="https://github.com/vra/llm-code-scorer" target="_blank" class="link">GitHub</a>|
        <a href="https://github.com/vra/llm-code-scorer/issues" target="_blank" class="link">Feedback</a>|
        <a href="https://www.zhihu.com/people/yunfeng-87" target="_blank" class="link">Yunfeng Wang</a>
      </p>
    </footer>
  </div>
</template>

<script>
import axios from 'axios';
import { toPng } from 'html-to-image';
export default {
  data() {
    return {
      repoUrl: '',
      score: null,
      comment: '',
      detail: {},
      description: '',
      imageUrl: '',
      loading: false,
      errorMessage: '',  // 新增错误信息状态

    };
  },
  methods: {
    validateUrl(url) {
      const regex = /^(https:\/\/github\.com\/[^/]+\/[^/]+(\.git)?)$/;
      return regex.test(url);
    },
    async getRepoData(user, repo) {
      try {
        const response = await axios.get(`https://api.github.com/repos/${user}/${repo}`);
        return response.data; // 返回仓库数据
      } catch (error) {
        if (error.response && error.response.status === 404) {
          throw new Error("仓库不存在"); // 抛出错误以在调用处处理
        } else {
          console.error("获取仓库数据时出错:", error);
          throw error; // 处理其他错误
        }
      }
    },
    async getScore() {
      if (!this.validateUrl(this.repoUrl)) {
        alert("请输入有效的 GitHub 仓库 URL:\n https://github.com/user/repo 或 https://github.com/user/repo.git");
        return; // 如果 URL 无效，结束方法
      }

      this.loading = true;

      // 提取用户和仓库名称
      const regex = /https:\/\/github\.com\/([^/]+)\/([^/]+)(\.git)?/;
      const match = this.repoUrl.match(regex);
      if (match) {
        const user = match[1];
        const repo = match[2].replace(/\.git$/, '');

        // 获取仓库数据，检查是否存在及大小
        try {
          const repoData = await this.getRepoData(user, repo);
          const sizeInKB = repoData.size; // 获取仓库大小（单位：KB）

          // 判断是否超过 100MB
          if (sizeInKB > 1024 * 1024) { // 100MB = 100 * 1024 KB
            this.errorMessage = "仓库大小超过100M，暂不支持(仓库这么大是否合理？)";
            this.loading = false; // 结束加载
            return; // 不评分，直接返回
          }
        } catch (error) {
          alert(error.message); // 处理仓库不存在的情况
          this.loading = false; // 结束加载
          return;
        }
      } else {
        alert("无效的仓库格式，请确认URL是否正确");
        this.loading = false;
        return;
      }

      this.score = null;
      this.comment = '';
      this.detail = {};
      this.description = '';
      this.imageUrl = '';
      this.errorMessage = '';
      const apiUrl = '/api';
      try {
        const response = await axios.post(`${apiUrl}/get-score`, {
          url: this.repoUrl
        });

        this.score = response.data.score;
        this.comment = response.data.comment;
        this.detail = response.data.detail;
        this.description = response.data.description;
      } catch (error) {
        console.error('Error fetching score data:', error);
        this.errorMessage = "打分出错，请稍后重试"; // 设置错误信息
      } finally {
        this.loading = false;
      }
    },
    shareResults() {
      const originalResult = this.$refs.resultArea;
      if (originalResult) {
        // 容器元素
        const container = document.createElement('div');
        container.style.width = '720px';
        container.style.background = 'linear-gradient(-45deg, #5a67d8, #b83280)';
        container.style.padding = '20px'
        container.style.color = '#fff';
        // 创建显示仓库 URL 的元素并添加到容器顶部
        const repoUrlDiv = document.createElement('div');
        repoUrlDiv.textContent = `代码仓库: ${this.repoUrl}`;
        repoUrlDiv.style.marginBottom = '20px';
        repoUrlDiv.style.wordWrap = 'break-word';
        repoUrlDiv.style.fontSize = '16px';
        repoUrlDiv.style.fontWeight = 'bold';
        container.appendChild(repoUrlDiv);
        // 克隆 result 元素并更改样式
        const saveBtn = this.$refs.saveButton;
        saveBtn.style.visibility="hidden";
        const resultClone = originalResult.cloneNode(true);
        resultClone.style.maxHeight = 'none';
        resultClone.style.overflow = 'visible';
        resultClone.style.width = '100%';
        container.appendChild(resultClone);
        saveBtn.style.visibility="visible";

        document.body.appendChild(container);

        const now = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
        const fileName = `LLM_Code_Scorer_${now}.png`;
        toPng(container)
          .then((dataUrl) => {
            document.body.removeChild(container);
            const link = document.createElement('a');
            link.download = fileName;
            link.href = dataUrl;
            link.click();
          })
          .catch((error) => {
            console.error('Error generating image:', error);
          });
      }
    }
  }
}
</script>

<style>
body {
  margin: 0;
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  border-radius: 2px;
  background-color: #e2e8f0;
}

::-webkit-scrollbar-thumb:hover {
  background-color: #cbd5e0;
}

.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  /* 确保内容均匀分布 */
  align-items: center;
  color: #fff;
  font-family: 'Arial', sans-serif;
  background: linear-gradient(-45deg, #5a67d8, #b83280);
  text-align: center;
  margin: 0;
  padding: 0 2rem;
}

.header {
  flex: 0 0 auto;
  /* Header 固定高度 */
}

.title {
  font-size: 2.2rem;
  color: #fff;
}

.description {
  font-size: 1.0rem;
  color: #fff;
  /* 设置为白色 */
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.input {
  padding: 1rem;
  font-size: 1rem;
  border: none;
  border-radius: 20px;
  margin-bottom: 0.6rem;
  width: 100%;
  max-width: 400px;
  box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.btn {
  background: #ff4081;
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 1rem;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

@media (min-width: 768px) {
  .input-container {
    flex-direction: row;
    justify-content: center;
    align-items: center;
  }

  .input {
    flex: 1;
    margin-right: 0.5rem;
    margin-bottom: 0rem;
    height: 100%;
  }

  .btn {
    flex-shrink: 0;
    height: auto;
    padding: 1.15rem 1.5rem;
    display: flex;
    align-items: center;
  }
}

.input:focus {
  outline: none;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
}

.btn:disabled {
  background: #ccc;
  /* 灰色背景 */
  cursor: not-allowed;
  /* 鼠标指针样式 */
}

.btn:hover {
  background: #ff80ab;
  transform: scale(1.05);
}

/* .result {
  margin-top: 1.5rem;
  width: 100%;
} */

.result {
  flex: 1;
  /* 结果区域占据剩余空间 */
  margin: 1.5rem 0;
  /* 上下间距 */
  max-height: 60%;
  /* 限制最大高度 */
  overflow-y: auto;
  /* 允许内容滚动 */
  width: 100%;
  /* 占满宽度 */
}

.score-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}

.score {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #fff;
  /* 设置为白色 */
}

.save-btn {
  background-color: #efeaf1;
  color: black;
  border: none;
  border-radius: 5px;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-left: 1rem;
}

.save-btn:hover {
  background-color: #929094;
}

.comment {
  font-style: italic;
  color: #FFD700;
  /* 设置为白色 */
}

.details-title,
.summary-title {
  font-size: 1.5rem;
  margin-top: 1rem;
  color: #fff;
  /* 设置为白色 */
}

.details {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .details {
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  }
}

.detail-item {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1rem;
  transition: ease-in 0.3s;
}

.detail-item h4 {
  color: #fff;
  /* 设置为白色 */
}

.detail-item p {
  font-size: 0.9rem;
  line-height: 1.4;
  color: #fff;
  /* 设置为白色 */
}

.detail-item:hover {
  background: rgba(255, 255, 255, 0.2);
}

.url-display {
  font-size: 1rem;
  margin-top: 1rem;
  color: #fff;
  /* 设置为白色 */
}

/* Loader styles */
.loader {
  border: 8px solid rgba(255, 255, 255, 0.3);
  border-top: 8px solid #ff4081;
  /* 使用偏粉色 */
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
  margin: 1.5rem auto;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* .footer {
  text-align: center;
  margin-top: auto;
  padding: 1rem;
} */

.footer {
  text-align: center;
  padding: 1rem;
  /* background: linear-gradient(-45deg, #5a67d8, #b83280); */
  /* background: rgba(91, 103, 216, 0.8); 使用 rgba 设置透明度 */
  width: 100%;
  /* 确保全宽 */
}


.link {
  color: #ff4081;
  /* 使用偏粉色 */
  text-decoration: none;
  margin: 0 1rem;
  /* 链接间距 */
}

.link:hover {
  text-decoration: underline;
}

.donate-links {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.donate-image {
  max-width: 100px;
}

.loading-text {
  color: #fff;
  /* 根据您的需要设置颜色 */
  font-size: 1.0rem;
  /* 字体大小 */
  margin-top: 10px;
  /* 上边距 */
}

.error-message {
  color: #fff;
  /* 设置为红色以突出显示 */
  margin-top: 10px;
  /* 上边距 */
}
</style>
