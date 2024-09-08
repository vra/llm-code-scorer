# llm-code-scorer
用 LLM 给 GitHub 代码仓库进行打分

体验地址: <https://llm-code-scorer.simpleai.site>

## 项目概述
1. LLM：采用免费的智谱`glm-4-flash`模型
2. 网页后端：flask + gunicorn
3. 网页前端：Vue

## 一些限制
1. 采用大模型打分，目前没找到固定回复的方法，每次返回的分值和理由会有变化
2. 超过100M的仓库国内机器下载很慢，因此暂不支持

## 环境搭建
1. 使用nvm安装nodejs和npm
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install 22
node -v
npm -v
```
2. 用npm安装vue
```bash
npm install -g @vue/cli 
```
3. 安装python包
```bash
pip install flask gunicorn flask-cors zhipuai
```

## 运行代码
```bash
npm install
npm run serve
cd src
API_KEY=<zhipuai_api_key> gunicorn -w 4 -b 0.0.0.0:5000 flask_app:app --timeout 600
```

## 项目细节
1. PROMPT设计对结果影响很大，具体参考<ai_coder_scorer.py>
2. 国内服务器 github clone很慢，此仓库使用的是gitclone.com镜像
