import os
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route('/get-score', methods=['POST'])
def get_score():
    data = request.json
    repo_url = data.get('url')

    # 模拟生成一个 0-10 的浮点分数
    score = round(random.uniform(0, 10), 2)
    comments = {
        10: [
            "准确无误，完美无缺，给人深刻印象！",
            "作为典范，毫无疑问地值得满分。"
        ],
        9: [
            "非常接近完美，只差一点点就能满分。",
            "轻微的不足之处，整体表现令人印象深刻。"
        ],
        8: [
            "很出色，但缺乏一些创新元素。",
            "质量优秀，但小细节会让它更完美。"
        ],
        7: [
            "不错，值得一看，但仍有提升空间。",
            "整体表现良好，但还有一些小瑕疵。"
        ],
        6: [
            "细节上有点东拼西凑，可以更精致一些。",
            "有潜力，但需要更多打磨和优化。"
        ],
        5: [
            "半途而废，虽然有点进步，但距离优秀还有很大差距。",
            "中规中矩，但完全没有超出预期的地方。"
        ],
        4: [
            "有一些亮点，但整体上依然不够好。",
            "还是很差，基本上没什么值得称道的地方。"
        ],
        3: [
            "只是勉强过了底线，根本无法令人满意。",
            "大多数地方都需要重做，这样的质量无法容忍。"
        ],
        2: [
            "只有两分，足以证明缺乏努力。",
            "这仅比一分好一点，但依然糟糕透顶。"
        ],
        1: [
            "这完全不及格，简直是令人失望的作品。",
            "这就像是失败的实验，毫无价值。"
        ],
        0: [
            "这真是一坨狗屎，完全无法接受。",
            "负分滚粗，真是浪费时间！"
        ]
    }


    # 模拟生成一段描述
    descriptions = [
        "代码结构良好，但有一些小问题需要修正。",
        "总体不错，建议优化算法性能。",
        "代码质量一般，建议进行重构。",
        "有几个语法错误，需要修复。",
        "很好的代码实现，建议加入文档注释。"
    ]
    description = random.choice(descriptions)
    detail = """
"代码质量": {
            "分数": 7,
            "理由": "代码整体清晰，逻辑严谨，命名规范，但存在一些潜在错误和改进空间，例如，部分配置文件可能存在冗余或不必要的配置项。"
        },
        "文档完整性": {
            "分数": 6,
            "理由": "README文件提供了基本的项目描述，但缺少详细的使用说明和配置指导，对于用户理解和使用项目有一定的障碍。"
        },
        "项目配置": {
            "分数": 5,
            "理由": "项目缺少.gitignore文件，可能会将不必要的文件包含在版本控制中，如日志文件、编译生成的文件等，这可能会影响仓库的整洁性。"
        },
        "提交规范": {
            "分数": 8,
            "理由": "提交信息较为清晰，能够理解修改的内容和目的，但部分提交信息可以更加详细，以便于更好地理解代码变更的背景和原因。"
        },
        "二进制文件管理": {
            "分数": 4,
            "理由": "项目中存在二进制文件，但未使用Git LFS进行管理，这可能会导致仓库过大，影响克隆和下载速度。"
        },
        "大小/性能": {
            "分数": 7,
            "理由": "项目大小为140K，相对较小，但考虑到项目类型为配置文件集合，大小合理。性能方面没有明显问题，但可以通过优化配置文件来进一步提升。"
        },
        "代码规范": {
            "分数": 8,
            "理由": "代码风格一致，有充分的注释，易于理解。但部分文件如vim配置文件中注释较少，对于不熟悉vim的用户来说可能不够友好。"
        }
    """

    # 生成图像 URL
    time.sleep(0.2)  # 模拟延迟，例如进行复杂计算
    image_filename = '1x1_一个小伙子在笔记本电脑面前专心地写代码.png'  # 替换为您的图片名称
    image_url = f"http://localhost:5000/images/{image_filename}"

    return jsonify({
        "score": score,
        "comment": random.choice(comments[int(score)]),
        "detail": detail,
        "description": description,
        "imageUrl": image_url
    })

# 提供静态文件
@app.route('/images/<path:filename>', methods=['GET'])
def send_image(filename):
    return send_from_directory(os.path.join(app.root_path, 'images'), filename)

if __name__ == '__main__':
    app.run(debug=True)


