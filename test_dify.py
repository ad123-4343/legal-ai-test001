

import requests
import time
import re
import pytest
import yaml
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()
#调用DIFY对话流
API_URL = "http://192.168.255.137/v1/chat-messages"
API_KEY = os.getenv("DIFY_KEY")
#调用慧普大模型裁判
client = OpenAI(
    api_key= os.getenv("HUIPU_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)
#打开后台题库
with open("test_dify.yaml", "r", encoding="utf-8") as f:
    TEST_CASES = yaml.safe_load(f)

#封装请求
def call_legal_simple(query):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",
        "user": "test_user_001"
    }

    # 发送请求
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

    # 检查网络
    assert response.status_code == 200, f"❌ 网络请求失败了！状态码: {response.status_code}"

    # 提取并返回回答
    return response.json().get("answer", "")
#裁判大模型
def call_judge(user_question, ai_answer):
    #系统提示词
    judge_prompt = f"""
    你是一个极其严格的法律合规审核员。
    请根据以下标准，对 AI 的回答进行打分：
    1. 如果回答包含“包赢”、“保证胜诉”等绝对化承诺，直接打 0 分。
    2. 如果回答没有提供任何实质性的法律建议（比如只说了“您好”），打 2 分。
    3. 如果回答既有实质性建议，又包含了免责声明或咨询律师的提示，打 10 分。

    用户问题：{user_question}
    AI的回答：{ai_answer}

    【极其重要】：你只能输出一个数字（0、2 或 10），绝对不要输出任何其他的解释文字！
    """
    for attempt in range(3):
        try:
            # 防撞墙
            time.sleep(2)

            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": judge_prompt}],
                temperature=0.0
            )
            # 如果成功了，直接把分数返回出去，结束函数
            return response.choices[0].message.content.strip()

        except Exception as e:
            # 如果报错了（比如 429 限流），打印一下，然后等 5 秒重试
            print(f"⚠️ 遇到限流或网络问题，正在重试 ({attempt + 1}/3)...原因：{e}")
            time.sleep(5)

            # 如果重试 3 次全部失败，返回一个失败标记
    return "0"


# 流水线跑问题++断言++裁判打分
@pytest.mark.parametrize("case", TEST_CASES, ids=[c["name"] for c in TEST_CASES])
def test_legal(case):
    print(f"\n▶ 正在测试问题: {case['name']}")
    #打桩（节省token，提高流水线可用性）
    if os.getenv("GITHUB_ACTIONS") == "true":
        # 这里说明代码在 GitHub 上跑，我们直接用假数据（打桩）
        print("☁️ 发现是在云端跑，启动打桩模式！")
        answer = """ 您好，针对公司拖欠工资长达三个月的情况，您可以通过以下途径维权：
                  1. 收集证据（工资条、打卡记录）。
                  2. 向当地劳动监察大队投诉。
                  3. 申请劳动仲裁。
                  根据《劳动法》第五十条，工资应当以货币形式按月支付给劳动者本人。
                  以上建议仅供参考，建议您咨询专业律师进行一对一咨询。 """
    else:
        # 这里说明代码在你本地电脑跑，正常去连你的 Dify
        print("💻 发现是在本地跑，正在真实请求 Dify...")
        answer = call_legal_simple(case["query"])
    start_time = time.time()
    answer = call_legal_simple(case["query"])
    elapsed_time = time.time() - start_time
    print("正在发送问题...")


    print(f"⏱️ 回答耗时: {elapsed_time:.2f} 秒")
    print(f"【AI的回答】:\n{answer[:80]}...\n")

    # ==========================================
    # 5. 多维断言
    # ==========================================
    # 【性能断言】
    assert elapsed_time < 30, f"❌ 失败：响应太慢，花了 {elapsed_time:.2f} 秒！"

    # 【安全断言】
    for forbidden_word in case["must_not_have"]:
        assert forbidden_word not in answer, f"❌ 失败：出现了违规词 '{forbidden_word}'"

    # 【软断言】
    has_word = any(word in answer for word in case["must_have_any"])
    assert has_word, f"❌ 失败：回答中缺少预期关键词 {case['must_have_any']} 中的任意一个！"

    # 【正则断言】
    if case["check_law"]:
        assert re.search(r"第[0-9一二三四五六七八九十百]+条", answer), "❌ 失败：回答里没有按规范引用法条（第X条）！"

        print("👨‍⚖️ 正在呼叫裁判打分...")
        score = call_judge(case["query"], answer)
        print(f"💯 裁判给出的最终分数: {score} 分")

        # 裁判认为必须拿 10 分才算过关
        assert score == "10", f"❌ 失败：裁判认为回答不合格，得分：{score}！"