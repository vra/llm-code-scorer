<template>
  <div id="app" class="app">
    <h1 class="title">代码评分工具</h1>
    <p class="description">输入您的 GitHub 仓库 URL，快速获取代码质量评分！</p>
    <input
      v-model="repoUrl"
      type="text"
      placeholder="输入 GitHub 仓库 URL"
      class="input"
      @keyup.enter="getScore"
    />
    <button @click="getScore" class="btn" :disabled="loading">
      获取评分
    </button>
    <div v-if="loading" class="loader"></div>

    <div v-if="score !== null && !loading" ref="resultArea" class="result">
      <h2 class="score">评分: <span>{{ score.toFixed(2) }}</span> / 10</h2>
      <p class="suggestion">{{ comment }}</p>
      <div class="image-container">
        <img
          v-if="imageUrl"
          :src="imageUrl"
          alt="评分结果图片"
          class="result-image"
          :style="{ width: '512px', height: '512px' }"
        />
      </div>
      <p class="suggestion">{{ detail }}</p>
      <p class="suggestion">{{ description }}</p>
    </div>

    <footer class="footer">
      <p>
        <a href="https://github.com/your-repo" target="_blank" class="link">GitHub Repo</a> |
        <a href="https://yourhomepage.com" target="_blank" class="link">作者主页</a>
      </p>
      <p>支持我们:</p>
      <div class="donate-links">
        <a href="https://donate-link-1.com" target="_blank">
          <img src="https://example.com/donate1.png" alt="Donate Link 1" class="donate-image" />
        </a>
        <a href="https://donate-link-2.com" target="_blank">
          <img src="https://example.com/donate2.png" alt="Donate Link 2" class="donate-image" />
        </a>
      </div>
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
      detail: '',
      description: '',
      imageUrl: '',
      loading: false,
    };
  },
  methods: {
    async getScore() {
      this.loading = true;
      this.score = null; 
      this.comment= ''; 
      this.detail= ''; 
      this.description = ''; 
      this.imageUrl = ''; 

      try {
        const response = await axios.post('http://localhost:5000/get-score', {
          url: this.repoUrl
        });
        
        this.score = response.data.score; 
        this.comment = response.data.comment; 
        this.detail = response.data.detail; 
        this.description = response.data.description; 
        this.imageUrl = response.data.imageUrl; 
      } catch (error) {
        console.error('Error fetching score data:', error);
      } finally {
        this.loading = false;
      }
    },
  }
}
</script>

<style scoped>
@keyframes gradient {
  0% { background-color: #5a67d8; }
  100% { background-color: #b83280; }
}

.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-family: 'Arial', sans-serif;
  background: linear-gradient(-45deg, #5a67d8, #b83280); /* Gradient background */
  text-align: center;
  margin: 0; /* Remove margin */
  padding: 0 2rem; /* Add padding to sides */
}

.title {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.description {
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
}

.input {
  padding: 1rem;
  font-size: 1rem;
  border: none;
  border-radius: 20px;
  margin-bottom: 1rem;
  width: 100%;
  max-width: 400px; /* Limit input width */
  box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.input:focus {
  outline: none;
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
}

.btn {
  background: #ff4081; /* Button color */
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

.score {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 5px rgba(255, 255, 255, 0.3);
}

.image-container {
  position: relative;
  overflow: hidden;
  border-radius: 15px;
  margin-bottom: 1rem;
}

.result-image {
  max-width: 100%;
  transition: transform 0.3s ease;
}

.result-image:hover {
  transform: scale(1.1); /* Hover effect */
}

.suggestion {
  font-size: 1.2rem;
  color: #f0e68c; /* Light color for contrast */
  animation: fadeIn 1s ease-in;
}

/* Loader styles */
.loader {
  border: 8px solid rgba(255, 255, 255, 0.3);
  border-top: 8px solid #ff4081;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
  margin: 1.5rem auto; /* Center the loader */
}

/* Spin animation */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Fade-in animation */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Footer styles */
.footer {
  text-align: center;
  margin-top: auto; /* Align footer at the bottom */
  padding: 1rem;
}

.link {
  color: #ff80ab; /* Link color */
  text-decoration: none;
}

.link:hover {
  text-decoration: underline; /* Underline on hover */
}

.donate-links {
  display: flex;
  justify-content: center;
  gap: 1rem; /* Space between images */
  margin-top: 0.5rem;
}

.donate-image {
  max-width: 100px; /* Set a max-width for donate images */
}

/* Responsive styles */
@media (max-width: 600px) {
  .title {
    font-size: 2rem; /* Smaller title font size for mobile */
  }
  .input {
    font-size: 0.9rem; /* Smaller input font size */
  }
  .btn {
    padding: 0.5rem 1rem; /* Smaller button padding */
  }
}

.share-btn {
  margin-top: 20px; /* 合适的间隔 */
}

.result-image {
  max-width: 100%; /* 确保图片不会超出容器宽度 */
}
</style>

