# scripts/generate_fake_data.py

"""
InferOps - 伪数据生成器

这个脚本用于为 InferOps 的数据集处理功能生成一个模拟的 JSON 数据集文件。
生成的数据可以用于测试文件上传和批处理流程。
"""

import json
import random
import os

# --- 配置 ---
OUTPUT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILENAME = "sample_dataset.json"
NUM_RECORDS = 100  # 要生成的记录数量

# --- 模拟数据源 ---
SUBJECTS = ["科学", "历史", "艺术", "技术", "体育", "文学"]
ACTIONS = ["总结", "翻译成英文", "提取关键词", "写一首关于它的诗", "解释给一个五岁的孩子听"]
OBJECTS = [
    "黑洞的形成", "文艺复兴时期的艺术特点", "金字塔的建造之谜", "量子计算的基本原理",
    "第一次世界大战的起因", "莎士比亚的戏剧风格", "CRISPR基因编辑技术", "奥林匹克运动会的历史"
]

def generate_record(record_id):
    """生成一条单独的数据记录。"""
    subject = random.choice(SUBJECTS)
    action = random.choice(ACTIONS)
    obj = random.choice(OBJECTS)
    
    # 随机组合成一个指令
    instruction = f"关于 {subject} 领域的 '{obj}'，请为我 {action}。"
    
    return {
        "id": f"task_{record_id:04d}",
        "instruction": instruction,
        "metadata": {
            "category": subject,
            "complexity": random.randint(1, 10)
        }
    }

def main():
    """主函数，生成并保存数据集。"""
    print("="*50)
    print("  InferOps - 开始生成伪数据集...")
    print("="*50)

    dataset = []
    for i in range(NUM_RECORDS):
        dataset.append(generate_record(i + 1))
        # 打印进度
        progress = (i + 1) / NUM_RECORDS
        print(f"  > 生成记录: {i+1}/{NUM_RECORDS} [{'#' * int(progress * 20):<20}] {int(progress * 100)}%", end='\r')

    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=4)
        
        print("\n" + "-"*50)
        print(f"✅ 成功生成数据集!")
        print(f"  - 记录数量: {NUM_RECORDS}")
        print(f"  - 文件已保存至: {output_path}")
        print("="*50)

    except IOError as e:
        print(f"\n❌ 错误: 无法写入文件 {output_path}。")
        print(f"  - 原因: {e}")
        print("="*50)

if __name__ == "__main__":
    main()
