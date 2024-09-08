<template>
  <div id="app" class="app">
    <h1 class="title">LLM Code Scorer</h1>
    <p class="description">输入 GitHub Repo URL，立即获取评分！</p>
    <input v-model="repoUrl" type="text" placeholder="输入 GitHub 仓库 URL" class="input" @keyup.enter="getScore" />
    <button @click="getScore" class="btn" :disabled="loading">获取评分</button>
    <div v-if="loading" class="loader"></div>
    <p v-if="loading" class="loading-text">LLM 打分中，请耐心等待...</p>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

    <div v-if="score !== null && !loading" ref="resultArea" class="result">
      <div class="score-container">
        <h2 class="score">评分: <span>{{ score.toFixed(2) }}</span> / 10</h2>
        <p class="comment">{{ comment }}</p>
      </div>

      <h3 class="details-title">评分细节(上下滑动查看)</h3>
      <div class="details">
        <div v-for="(item, key) in detail" :key="key" class="detail-item">
          <h4>{{ key }}</h4>
          <p>分数: <strong>{{ item.分数 }}</strong></p>
          <p>理由: {{ item.理由 }}</p>
        </div>
      </div>

      <h3 class="summary-title">总评与建议</h3>
      <p class="suggestion">{{ description }}</p>
      <p class="url-display">URL: <strong>{{ repoUrl }}</strong></p>
    </div>

    <footer class="footer">
      <p>
        <a href="https://github.com/vra/llm-code-scorer" target="_blank" class="link">GitHub</a> |
        <a href="https://github.com/vra/llm-code-scorer" target="_blank" class="link">Feedback</a> |
        <a href="https://vra.github.io/about" target="_blank" class="link">Yunfeng Wang</a>
      </p>

    </footer>
  </div>
</template>

<script>
import axios from 'axios';
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
    async checkRepoExists(user, repo) {
      try {
        const response = await axios.get(`https://api.github.com/repos/${user}/${repo}`);
        return response.status === 200; // 返回 true 表示仓库存在
      } catch (error) {
        if (error.response && error.response.status === 404) {
          return false; // 返回 false 表示仓库不存在
        } else {
          console.error("检查仓库存在性时出错:", error);
          throw error; // 处理其他错误
        }
      }
    },
    async getScore() {
      if (!this.validateUrl(this.repoUrl)) {
        alert("请输入有效的 GitHub 仓库 URL:\n https://github.com/user/repo 或 https://github.com/user/repo.git");
        return; // 如果 URL 无效，结束方法
      }

      // 提取用户和仓库名称
      const regex = /https:\/\/github\.com\/([^/]+)\/([^/]+)(\.git)?/;
      const match = this.repoUrl.match(regex);
      if (match) {
        const user = match[1];
        const repo = match[2].replace(/\.git$/, '');

        // 检查仓库是否存在
        const exists = await this.checkRepoExists(user, repo);
        if (!exists) {
          alert("仓库不存在，请确认URL是否正确:" + user + " " + repo);
          return;
        }
      } else {
        alert("无效的仓库格式，请确认URL是否正确");
        return;
      }

      this.loading = true;
      this.score = null;
      this.comment = '';
      this.detail = {};
      this.description = '';
      this.imageUrl = '';
      this.errorMessage = '';
      try {
        const response = await axios.post('http://47.99.139.135:5000/get-score', {
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
  }
}
</script>

<style scoped>
.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #fff;
  /* 统一为白色字体 */
  font-family: 'Arial', sans-serif;
  background: linear-gradient(-45deg, #5a67d8, #b83280);
  text-align: center;
  margin: 0;
  padding: 0 2rem;
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

.input {
  padding: 1rem;
  font-size: 1rem;
  border: none;
  border-radius: 20px;
  margin-bottom: 1rem;
  width: 100%;
  max-width: 400px;
  box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.input:focus {
  outline: none;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
}

.btn {
  background: #ff4081;
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 0.8rem 1.5rem;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.2s ease;
}

.btn:hover {
  background: #ff80ab;
  transform: scale(1.05);
}

.result {
  margin-top: 1.5rem;
  width: 100%;
}

.score-container {
  display: flex;
  flex-direction: column;
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

.comment {
  font-style: italic;
  color: #fff;
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
  max-height: 200px;
  overflow-y: auto;
}

.detail-item {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1rem;
  transition: background 0.3s;
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

.footer {
  text-align: center;
  margin-top: auto;
  padding: 1rem;
}

.link {
  color: #ff4081;
  /* 使用偏粉色 */
  text-decoration: none;
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
