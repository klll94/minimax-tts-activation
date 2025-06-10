import re
from typing import List, Dict

def parse_text_to_tasks(text: str) -> List[Dict]:
    """
    解析带标记或普通文本为结构化任务列表。
    支持：
    - W: 女声英文 (必须在行首)
    - M: 男声英文 (必须在行首)
    - (叮咚打点)/(叮咚打点)：dingdong音效（支持句中、行中、全角/半角括号）
    - 停顿 00′03″: 静音
    - 普通文本：自动识别中英文，中文用Chinese_Male_Announcer，英文用English_Graceful_Lady
    """
    tasks = []
    lines = text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 停顿标记 - 支持多种格式
        if line.startswith('停顿'):
            duration = 0
            
            # 方案1: 简化中文格式 (优先匹配)
            # 停顿3秒、停顿2分钟、停顿1分20秒
            if '分钟' in line and '秒' in line:
                # 如：停顿1分20秒
                match = re.search(r'停顿\s*(\d+)分(\d+)秒', line)
                if match:
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    duration = minutes * 60 + seconds
            elif '分钟' in line:
                # 如：停顿2分钟
                match = re.search(r'停顿\s*(\d+)分钟?', line)
                if match:
                    minutes = int(match.group(1))
                    duration = minutes * 60
            elif '秒' in line:
                # 如：停顿3秒
                match = re.search(r'停顿\s*(\d+)秒', line)
                if match:
                    seconds = int(match.group(1))
                    duration = seconds
            
            # 方案2: 传统格式兼容 (作为备用)
            # 支持各种引号：′″、'＂、'″、＇″等
            if duration == 0:
                match = re.search(r'停顿\s*(\d{1,2})[′＇\'](\d{1,2})[″＂"]', line)
                if match:
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    duration = minutes * 60 + seconds
            
            # 方案3: 纯数字格式 (如：停顿 3)
            if duration == 0:
                match = re.search(r'停顿\s*(\d+)$', line)
                if match:
                    duration = int(match.group(1))  # 默认为秒
            
            if duration > 0:
                tasks.append({"type": "silence", "duration": duration})
            continue
        
        # 对话标记 - 严格匹配行首的W:或M:
        if re.match(r'^W:\s*', line):
            content = re.sub(r'^W:\s*', '', line).strip()
            # 根据内容判断是中文女声还是英文女声
            if re.search(r'[\u4e00-\u9fff]', content):
                voice = "Chinese_Female_Announcer"  # 中文女声
            else:
                voice = "English_Graceful_Lady"  # 英文女声
        elif re.match(r'^M:\s*', line):
            content = re.sub(r'^M:\s*', '', line).strip()
            # 根据内容判断是中文男声还是英文男声
            if re.search(r'[\u4e00-\u9fff]', content):
                voice = "Chinese_Male_Announcer"  # 中文男声
            else:
                voice = "English_Trustworthy_Man"  # 英文男声
        else:
            content = line
            # 简单判断中英文，但不指定性别
            if re.search(r'[\u4e00-\u9fff]', content):
                voice = "Chinese_Auto"  # 让主程序根据用户选择决定
            elif re.search(r'[a-zA-Z]', content):
                voice = "English_Auto"  # 让主程序根据用户选择决定
            else:
                voice = "Chinese_Auto"  # 让主程序根据用户选择决定
        
        # 如果content为空，跳过
        if not content.strip():
            continue
            
        # 拆分所有括号形式的叮咚打点
        # 支持 (叮咚打点)、（叮咚打点）、( 叮咚打点 )、（ 叮咚打点 ）等
        parts = re.split(r'[（(]\s*叮咚打点\s*[)）]', content)
        # 查找音效出现次数
        effect_count = len(re.findall(r'[（(]\s*叮咚打点\s*[)）]', content))
        for i, part in enumerate(parts):
            if part.strip():
                tasks.append({"type": "tts", "text": part.strip(), "voice": voice})
            if i < effect_count:
                tasks.append({"type": "effect", "effect": "dingdong.mp3"})
    return tasks

# 示例用法
if __name__ == "__main__":
    sample = '''
W: Hello, how are you?
M: I'm fine, thank you!
(叮咚打点)
请听录音(叮咚打点)开始。
请听录音（叮咚打点）开始。
请听录音 ( 叮咚打点 ) 开始。
请听录音（ 叮咚打点 ）开始。
停顿 00′03″
你好，这是一段中文。
This is a long English paragraph without any mark.
'''
    for task in parse_text_to_tasks(sample):
        print(task) 