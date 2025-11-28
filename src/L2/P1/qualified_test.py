import re
from wiki_react import llm, executor

# ====== 1. 题目列表 ======
questions = [
    "Who wrote the novel '1984'?",
    "What is the capital of Canada?",
    ...
]

# ====== 2. 纯 LLM ======
def ask_llm(q):
    return llm.invoke(q).content

# ====== 3. ReAct + Wikipedia ======
def ask_react(q):
    result = executor.invoke({"input": q})
    return result["output"]

# ====== 4. 简单答案匹配（可改进） ======
def normalize(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

def is_correct(pred, gold):
    return normalize(pred) == normalize(gold)

# ====== 5. 评估 ======
def evaluate():
    correct_llm = 0
    correct_react = 0

    for i, (q, gold) in enumerate(questions):
        print(f"\n=== Q{i+1}: {q} ===")

        # 纯 LLM
        ans_llm = ask_llm(q)
        print("LLM:", ans_llm)
        if is_correct(ans_llm, gold):
            correct_llm += 1

        # ReAct + Wiki
        ans_react = ask_react(q)
        print("ReAct:", ans_react)
        if is_correct(ans_react, gold):
            correct_react += 1

    print("\n===== 最终结果 =====")
    print(f"纯 LLM 准确率: {correct_llm}/20 = {correct_llm/20:.2%}")
    print(f"ReAct+Wiki 准确率: {correct_react}/20 = {correct_react/20:.2%}")
