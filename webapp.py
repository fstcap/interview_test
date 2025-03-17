import json
import re
import requests
from datetime import datetime

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)


prompt = """Determine whether the user's intent is casual chat or meeting scheduling:

Current date and time is {}
1、If it's casual chat: Respond politely in compliance with laws and regulations, and cannot fabricate information. Emphasize at the end that you are a meeting scheduling assistant, and inform users they can schedule meetings.
2、If it's meeting scheduling: Extract time range, meeting type, and participants. If any information is missing (time range/meeting type/participants), prompt the user to provide the missing details. If complete, output only in this format:
{{"time_range": the_value, "meeting_type": the_value, "participants": the_value}}
3、The value of the_value must be a string;
4、Responses must be concise;
5、The time format is like this example: 2025-03-24 13:14:18;
6、The fields for which the user did not mention any information are represented by a carriage return (newline).
7、The output JSON section must strictly adhere to the JSON format.
"""




# 模拟后台信息数据
info_data = [
    {"title": "Meeting Type:", "content": ""},
    {"title": "Time Range:", "content": ""},
    {"title": "Participants:", "content": ""},
]


def get_llm_answer(messages):
    obj = {
        "model": "llama3.1",
        "messages": messages,
        "stream": False,
        "options": {"num_ctx": 512}
    }

    response = requests.post(
        "http://localhost:11434/api/chat",
        json=obj
    )
    with open("./test_res.json", "w") as file:
        file.write(response.text)
    return json.loads(response.text)


@app.route('/')
def index():
    return render_template('chat.html')


@app.route('/get_info')
def get_info():
    return jsonify(info_data)


def clean_string(s):
    s = re.sub(r"\n", "", s)
    # 去除开头所有非字母字符
    s = re.sub(r'^[^a-zA-Z]*', '', s)
    # 去除结尾所有非字母字符
    s = re.sub(r'[^a-zA-Z]*$', '', s)
    s = '"' + s + '"'
    return s


def check_result(messages):
    content = messages['content']
    ex_msg_0 = content.split("{")

    if len(ex_msg_0) < 2:
        return {"type": 0, "content": content}

    ex_msg_1 = ex_msg_0[-1]
    ex_msg_2 = ex_msg_1.split("}")[0]

    ex_msg_2 = clean_string(str(ex_msg_2).strip())

    ex_msg = "{" + ex_msg_2 + "}"

    print(ex_msg)
    msg = json.loads(ex_msg)
    print(msg)
    if not ("time_range" in msg and "meeting_type" in msg and "participants" in msg):
        return {"type": 0, "content": ex_msg_1.split("}")[-1]}

    for key in msg.keys():
        if str(msg[key]).strip() == "":
            return {"type": 0, "content": ex_msg_1.split("}")[-1]}

    info_datas = []
    for key in msg.keys():
        if key == "meeting_type":
            info_datas.append({"title": "Meeting Type:", "content": msg['meeting_type']})
        elif key == "time_range":
            info_datas.append({"title": "Time Range:", "content": msg['time_range']})
        elif key == "participants":
            info_datas.append({"title": "Participants:", "content": msg['participants']})

    return {"type": 1, "content": info_datas}


@socketio.on('user_message')
def handle_message(data):
    # 获取当前日期和时间
    now = datetime.now()
    # 格式化日期和时间为字符串
    current_datetime_str = now.strftime("%Y%m%d%H%M%S")
    prompt_str = prompt.format(current_datetime_str)

    system_messages = [{"role": "assistant", "content": prompt_str}]
    data = [item for item in data if item["role"] == "user"]
    if len(data) > 3:
        data = data[-3:]
    messages = system_messages + data
    res = get_llm_answer(messages)
    res_msg = res["message"]
    result = check_result(res_msg)
    if result["type"] == 0:
        # 处理多轮对话逻辑
        emit('chat_update', {'role': 'system', 'content': result["content"]}, broadcast=True)
    else:
        emit('msg_update', {'role': 'system', 'content': result["content"]}, broadcast=True)
        # 处理多轮对话逻辑
        emit('chat_update', {'role': 'system', 'content': "The meeting information is already displayed on the right. Please confirm."}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
    # msg = "Here is the information for the meeting:\n\nTime Range: 13:00 - 14:00\nMeeting Type: Interview\nParticipants:\n1. Ross\n2. Jack"