import json
import os
import random
import re
import subprocess
import tempfile

from loguru import logger

SOURCE_CODE_EXTENSIONS = [
    ".py",
    ".rs",
    ".c",
    ".cpp",
    ".h",
    ".hpp" ".go",
    ".vue",
    ".cs",
    ".ts",
    ".asm",
    ".bat",
    ".cc",
    ".cxx",
    ".h",
    ".h++",
    ".hh",
    ".hpp",
    ".hxx",
    ".inc",
    ".inl",
    ".cmake",
    ".cmake.in",
    ".css",
    ".coffee",
    ".lisp",
    ".cu",
    ".cuh",
    ".d",
    ".dart",
    ".diff",
    ".dockerfile",
    ".djs",
    ".dylan",
    ".emacs",
    ".em",
    ".emberscript",
    ".es",
    ".escript",
    ".html",
    ".php",
    ".java",
    ".js",
    ".sjs",
    ".ssjs",
    ".ipynb",
    ".m",
    ".mm",
    ".swift",
    ".md",
    ".sh",
    ".rb",
]

PROMPT = """
---
已将一个 Git 仓库的所有信息按照概要格式组织，请仔细阅读概要信息，尤其是一定一定要对[Code Snapshot]部分的代码风格、逻辑、规范进行仔细查阅，然后结合具体的例子，给出下面6个维度的0-10分的打分（打分标准见下): 代码质量、文档规范、配置规范、提交规范、大小规范、测试规范，最后完整全面地总结代码的优点和待改进点，给出总结和建议。

### 概要格式
```
[README]:
[LICENSE]:
[.gitignore]:
[Git Commit]:
[Code Snapshot]:
[Test Files]:
[Binary Files]:
[Repo Size]:
[Total Files]:
```

### 评分维度说明

#### 1. 代码质量（0-10）
- **0-3**: 代码不易读，逻辑混乱，缺乏注释, 命名不规范，风格不一致，难以理解，存在多个严重的潜在错误。
- **4-6**: 代码可读性一般，有部分注释，存在一些逻辑问题和不规范命名，风格混合（例如驼峰和下划线命名混用）,偶尔有潜在错误。
- **7-8**: 代码整体清晰，注释较为充分，逻辑严谨通顺，命名统一规范，潜在错误较少。
- **9-10**: 代码结构良好，规范一贯，逻辑清晰，易于理解，命名准确一致，几乎没有潜在错误。
- 如果[Code Snapshot]部分内容为空，说明没有任何源代码，代码质量直接为0分，评分理由是没有任何源代码，

#### 2. 文档规范（0-10）
- **0-3**: 文档缺失(例如没有README)或只包含极少信息(README没有使用说明)，无法帮助用户理解和使用。
- **4-6**: 文档不完整，有部分信息缺失，用户可能需要额外查找信息。
- **7-8**: 文档较为完整，提供了大部分所需信息，少量细节需要完善。
- **9-10**: 文档非常详尽，覆盖所有重要细节，除了README，还有BUILD,CONTRIBUTING，faq，trobuleshooting，docs等专门的文档或目录，用户能够轻松理解和上手。

#### 3. 配置规范（0-10）
- **0-3**: 项目配置混乱，缺少必要的配置文件（如 .gitignore, LICENSE）。
- **4-6**: 项目配置一般，有一些配置文件，但不充分，例如虽然有.gitignore，但是没有忽略.pyc，.DS_Store, .out，.so等中间结果。
- **7-8**: 项目配置良好，包含必要的配置文件，结构清晰，忽略了常见的非源码文件。
- **9-10**: 优化的项目配置，包含所有必要文件(如.gitignore, LICENSE, setup.cfg等)，并遵循最佳实践，忽略了全部的非源码文件，已经不需要的数据目录等。
- 如果[LICENSE]部分或者[.gitignore]部分内容为空，说明没有证书或者忽略规则，配置规范直接为0分，没有证书和gitignore规则是很不专业的开源方式

#### 4. 提交规范（0-10）
- **0-3**: 提交信息极其简单，完全无法理解提交的目的(例如简单的update, upload等)。
- **4-6**: 提交信息有一定描述，但描述不够详细或含糊。
- **7-8**: 提交信息清晰，能够理解修改的内容和目的，同时有固定的格式如angular规范等。
- **9-10**: 提交信息详细且准确，充分解释每次提交的变更和背景，详细内容通过空行再详细说明的形式提交。

#### 5. 大小规范（0-10）
- **0-3**: 计算[Repo Size] / [Total Files]，也就是平均每个文件的大小，超过1M，越小分值越高
- **4-6**: 平均每个文件大小超过500K，越小分值越高
- **7-8**: 平均每个文件大小超过100K，越小分值越高
- **9-10**: 平均每个文件大小小于100K，越小分值越高, 如果小于30K，则为10分
- 如果[Code Snapshot]部分内容为空，但[Size]部分超过10M，大小规范直接为0分，没有源码但size超大说明保存的是二进制文件而不是代码

#### 6. 测试规范（0-10）
- **0-3**: 没有任何的单元测试或者集成测试，也没有任何文档说明 。
- **4-6**: 有默认的mock测试文件，但没有真正代码的测试例子。
- **7-8**: 有一些实际代码的测试例子，但测试覆盖率很低，没有说明怎么进行测试。
- **9-10**: 如果[Test Files]中的测试文件数目/[Total Files] 超过10%，说明测试覆盖率高，这个占比越高分值也越高，同时有详细的说明进行如何测试。
- 如果[Test Files]部分内容为空，说明没有任何的测试，测试规范直接为0分

重要的附加说明：打分一定要有区分度，例如[Test Files]，[LICENSE], [.gitignore] 或 [Code Snapshot] 如果为空，则对应的评分维度就果断打0分，这样最终的结果才有警示意义和区分度，如果做的很好就果断给10分，不要中庸地给8分或者9分.

### 返回格式

请返回以下 JSON 格式的评分结果：

```json
{
    "评分": {
        "代码质量": {
            "分数": [分数],
            "理由": "[ 如果[Code Snapshot]部分为空，则直接给0分，因为仓库没有任何编程代码，只有个README，否则根据 [Code Snapshot] 部分的代码片段进行分析，给出非常详细的理由，用具体的例子进行展开说明，这样对用户才更有帮助，你的回答才更有说服力
            ]"
        },
        "文档规范": {
            "分数": [分数],
            "理由": "[如果[LICENSE]部分或者[.gitignore]部分为空，则直接返回0分，否则再进行详细分析，并给出非常详细的理由，用具体的例子进行展开说明，这样对用户才更有帮助，你的回答才更有说服力]"
        },
        "配置规范": {
            "分数": [分数],
            "理由": "[非常详细的理由，用具体的例子进行展开说明，这样对用户才更有帮助，你的回答才更有说服力]"
        },
        "提交规范": {
            "分数": [分数],
            "理由": "[非常详细的理由，用具体的例子进行展开说明，这样对用户才更有帮助，你的回答才更有说服力]"
        },
        "大小规范": {
            "分数": [分数],
            "理由": "[非常详细的理由，用具体的例子进行展开说明，这样对用户才更有帮助，你的回答才更有说服力]"
        },
        "测试规范": {
            "分数": [分数],
            "理由": "[如果[Test Files]部分为空，则直接返回0分，否则再分析测试代码的覆盖率，并非常详细的理由，用具体的例子进行展开说明，这样对用户才更有帮助，你的回答才更有说服力]"
        }
    },
    "评价与建议": "[详细、实用、全面的评价和建议，用具体的例子进行展开说明，这样对用户才更有帮助，你的回答才更有说服力]"
}
```
一个示例返回结果:
```json
{
    "评分": {
        "代码质量": {
            "分数": 3,
            "理由": "代码格式混乱不统一，比如等号前后空格不一致，使用main.cpp中的第10行使用了未定义行为,代码没有注释说明，代码逻辑混乱不易理清"
        },
        "文档规范": {
            "分数": 10,
            "理由": "有详细的README文档，包含了代码功能说明，如何安装使用，以及常见问题解决方法等"
        },
        "配置规范": {
            "分数": 8,
            "理由": "有.gitignore文件，License文件，代码仓库没有提交临时文件"
        },
        "提交规范": {
            "分数": 6,
            "理由": "git commit 格式统一，但有少量的提交含义不明确，有些提交大量使用update，有些提交提交信息重复了"
        },
        "大小规范": {
            "分数": 0,
            "理由": "仓库太大，超过10G, .git目录包含了大量的历史提交"
        },
        "测试规范": {
            "分数": 10,
            "理由": "包含大量的pytest测试用例，覆盖了所有的代码片段"
        }
    },
    "评价与建议": "代码质量整体一般，在代码规范方面做的很好，但仓库太大，用户下载费劲，建议清理仓库，同时git commit规范性不太高"
}
```

下面是概要信息: """


def is_source_code_file(filename):
    return any(filename.endswith(ext) for ext in SOURCE_CODE_EXTENSIONS)


def is_binary_file(filename):
    with open(filename, "rb") as f:
        # Read the first 1024 bytes of the file
        data = f.read(1024)
        # Check for null bytes
        return b"\0" in data


def get_repo_size(repo_path):
    result = subprocess.run(["du", "-sh", repo_path], capture_output=True, text=True)
    repo_size = result.stdout.split()[0]
    return repo_size
    # 也可以单独计算.git目录的大小并加入总和
    git_dir_size_result = subprocess.run(
        ["du", "-sh", os.path.join(repo_path, ".git")], capture_output=True, text=True
    )
    git_dir_size = git_dir_size_result.stdout.split()[0]
    return git_dir_size


def generate_repo_summary(repo_path):
    # 获取仓库的README文件内容
    readme_content = ""
    readme_path = os.path.join(repo_path, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()

    # 获取仓库的LICENSE文件内容
    license_content = ""
    license_path = os.path.join(repo_path, "LICENSE")
    if os.path.exists(license_path):
        with open(license_path, "r", encoding="utf-8") as f:
            license_content = f.read()

    # 获取仓库的.gitignore文件内容
    gitignore_content = ""
    gitignore_path = os.path.join(repo_path, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gitignore_content = f.read()

    # 获取仓库的所有git commit信息
    commit_log = subprocess.check_output(
        [
            "git",
            "log",
            "--pretty=format:%s",
        ],
        cwd=repo_path,
    ).decode("utf-8")
    print("==> commit_log:", commit_log)

    # 获取仓库的所有源代码文件内容
    code_content = ""
    source_file_list = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file == "README.md":
                continue
            if is_source_code_file(file):
                source_file_list.append(os.path.join(root, file))

    actual_samples = min(len(source_file_list), 10)
    selected_file_paths = random.sample(source_file_list, actual_samples)
    for path in selected_file_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                code_content += (
                    f"--- File: {path} ---\n{''.join(line for line in (f.readline() for _ in range(100)) if line)}\n"

                )
        except UnicodeDecodeError:
            pass

    # 获取仓库的所有测试文件
    test_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_whole_path = os.path.join(root, file)
            if "test" in file_whole_path:
                if not is_binary_file(file_whole_path):
                    test_files.append(os.path.join(root, file))


    # 获取仓库的所有二进制文件路径（这里仅列出路径，不包含内容）
    binary_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_whole_path = os.path.join(root, file)
            if ".git" in file_whole_path:
                continue

            if is_binary_file(file_whole_path):
                binary_files.append(os.path.join(root, file))

    # 获取仓库的所有文件
    total_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_whole_path = os.path.join(root, file)
            if ".git" in file_whole_path:
                continue
            total_files.append(os.path.join(root, file))
    num_total_files = len(total_files)

    size = get_repo_size(repo_path)

    output = f"[README]:\n{readme_content}\n[LICENSE]:\n{license_content}\n[.gitignore]:\n{gitignore_content}\n[Git Commit]:\n{commit_log}\n[Code Snapshot]:\n{code_content}\n[Test Files]:\n"
    output += "\n".join(test_files)
    output += "\n[Binary Files]:\n"
    output += "\n".join(binary_files)
    output += f"\n[Repo Size]:\n{size}"
    output += f"\n[Total Files]:\n{num_total_files}"
    return output


class AICodeScorer:
    def __init__(self, api_key, llm_api_type="zhipu"):
        self.llm_api_type = llm_api_type

        self.client = eval(f"self.init_llm_client_{self.llm_api_type}")(api_key)

    def is_valid_github_repo(self, repo_url):
        # GitHub 仓库的正则表达式模式
        #pattern = r"^https://github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)$"
        pattern = r"^https://github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)(\.git)?$"


        # 使用正则表达式进行匹配
        match = re.match(pattern, repo_url)

        return match is not None

    def run(self, repo_url):
        # check repo_url is valid GitHub url
        assert self.is_valid_github_repo(repo_url)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone to temp folder
            fast_repo_url = repo_url.replace(
                "https://github.com/", "https://gitclone.com/github.com/"
            )
            print(fast_repo_url)
            try:
                subprocess.run(["git", "clone", fast_repo_url, temp_dir])
            except subprocess.CalledProcessError:
                logger.error("Git clone 失败，commit 信息为空")

            logger.info(f"已成功克隆{repo_url} to：{temp_dir}")

            # Generate content summary
            logger.info("Generating repo summary...")
            repo_summary = generate_repo_summary(temp_dir)
            logger.info("repo_summary:")
            logger.info(repo_summary)

            # Aad prompt to construct llm input
            llm_input = PROMPT + "\n" + repo_summary

            # Run LLM to get evaluation results
            logger.info("Scoring...")
            results_str = eval(f"self.evaluate_{self.llm_api_type}")(
                self.client, llm_input
            )
            logger.info("Raw results:" + results_str)

            # Convert raw results to python's dict
            results_dict = json.loads(results_str.strip("```").strip("json"))
            logger.info("Results dict:")
            logger.info(results_dict)

            return results_dict

    def init_llm_client_zhipu(self, api_key):
        from zhipuai import ZhipuAI

        client = ZhipuAI(api_key=api_key)
        return client

    def evaluate_zhipu(self, client, llm_input):

        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。",
                },
                {"role": "user", "content": llm_input},
            ],
            top_p=1,
            temperature=0,
        )
        results = response.choices[0].message.content
        return results


if __name__ == "__main__":
    api_key = os.environ["API_KEY"]
    scorer = AICodeScorer(api_key, llm_api_type="zhipu")

    scorer.run("https://github.com/vra/flopth")
