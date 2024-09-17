import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random

from ai_code_scorer import AICodeScorer

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

scorer = AICodeScorer(api_key=os.environ["API_KEY"])


@app.route("/health", methods=["GET"])
def health_check():
        return jsonify({"status": "healthy"}), 200


@app.route("/get-score", methods=["POST"])
def get_score():
    try:
        data = request.json
        repo_url = data.get("url")
        if not repo_url:
            return jsonify({"error": "Missing URL parameter"}), 400

        comments = {
            10: [
                "李拉斯脱袜子见了您都得叫声哥",
                "您的代码，龟叔都觉得优雅",
                "准确无误，完美无缺，给人深刻印象！",
                "作为典范，毫无疑问地值得满分。",
            ],
            9: [
                "您写代码比雷军还优雅",
                "想学啊？我教你啊",
                "优雅，真TMD优雅",
            ],
            8: [
                "AI都得向您学习",
                "呐，这个就叫专业",
            ],
            7: [
                "程序员如果没有梦想，那跟咸鱼有什么分别?",
                "不错，值得一看，但仍有提升空间。",
                "整体表现良好，但还有一些小瑕疵。",
            ],
            6: [
                "60分万岁，多一份浪费??",
                "能跑就行了，要啥自行车??",
                "细节上有点东拼西凑，可以更精致一些。",
                "有潜力，但需要更多打磨和优化。",
            ],
            5: [
                "求您了，做个真正的coder吧",
                "半途而废，虽然有点进步，但距离优秀还有很大差距。",
                "中规中矩，但完全没有超出预期的地方。",
            ],
            4: [
                "您的代码是不体育老师教的?",
                "有一些亮点，但整体上依然不够好。",
                "还是很差，基本上没什么值得称道的地方。",
            ],
            3: [
                "您的代码看得我脑壳疼",
                "只是勉强过了底线，根本无法令人满意。",
                "大多数地方都需要重做，这样的质量无法容忍。",
            ],
            2: [
                "您这代码是不是凌晨两点写的？！",
                "您的代码，就是bug本哥",
                "只有两分，足以证明缺乏努力。",
                "这仅比一分好一点，但依然糟糕透顶。",
            ],
            1: [
                "GPT3写的代码都比这好",
                "您的代码进步空间挺大的🙂",
                "这完全不及格，简直是令人失望的作品。",
                "这就像是失败的实验，毫无价值。",
            ],
            0: [
                "这真是一坨狗屎，完全无法接受。",
                "臭，真臭，臭不可闻！",
                "依托答辩",
                "一坨狗屎!",
                "💩💩💩",
                "负分滚粗，真是浪费时间！",
            ],
        }

        eval_results = scorer.run(repo_url)

        detail = eval_results["评分"]
        print("==> detail:", type(detail), detail)

        score_list = [e["分数"] for e in detail.values()]
        print("==> score_list:", score_list)
        mean_score = sum(score_list) / len(score_list)
        comment = random.choice(comments[int(round(mean_score))])

        description = eval_results["评价与建议"]

        # 生成图像 URL
        # image_filename = '1x1_一个小伙子在笔记本电脑面前专心地写代码.png'  # 替换为您的图片名称
        # image_url = f"http://localhost:5000/images/{image_filename}"

        return jsonify(
            {
                "score": mean_score,
                "comment": comment,
                "detail": detail,
                "description": description,
            }
        )
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# 提供静态文件
@app.route("/images/<path:filename>", methods=["GET"])
def send_image(filename):
    return send_from_directory(os.path.join(app.root_path, "images"), filename)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=False)
