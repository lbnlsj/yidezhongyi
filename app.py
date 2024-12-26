from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import random
import uuid

app = Flask(__name__)

# 模拟数据 - 医生列表
DOCTORS = {
    1: {"id": 1, "name": "张医生", "department": "内科", "title": "主任医师"},
    2: {"id": 2, "name": "李医生", "department": "外科", "title": "副主任医师"},
    3: {"id": 3, "name": "王医生", "department": "儿科", "title": "主治医师"},
    4: {"id": 4, "name": "刘医生", "department": "内科", "title": "主治医师"},
    5: {"id": 5, "name": "陈医生", "department": "神经科", "title": "主任医师"}
}


# 生成时间段数据
def generate_time_slots():
    time_slots = []
    base_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

    for day in range(7):
        current_date = base_date + timedelta(days=day)
        for hour in range(8, 17):
            for minute in [0, 30]:
                slot_time = current_date.replace(hour=hour, minute=minute)
                time_slots.append({
                    "id": len(time_slots) + 1,
                    "start_time": slot_time.strftime("%Y-%m-%d %H:%M"),
                    "available": random.choice([True, False])
                })
    return time_slots


TIME_SLOTS = generate_time_slots()

# 存储正在运行的任务
RUNNING_TASKS = {}


@app.route('/')
def index():
    """渲染主页（任务列表页面）"""
    return render_template('index.html', tasks=RUNNING_TASKS)


@app.route('/select')
def select():
    """渲染选择页面"""
    return render_template('select.html',
                           doctors=DOCTORS.values(),
                           time_slots=TIME_SLOTS)


@app.route('/api/doctors')
def search_doctors():
    """搜索医生API"""
    keyword = request.args.get('keyword', '').lower()
    if not keyword:
        return jsonify(list(DOCTORS.values()))

    filtered_doctors = [
        doctor for doctor in DOCTORS.values()
        if keyword in doctor['name'].lower() or
           keyword in doctor['department'].lower() or
           keyword in doctor['title'].lower()
    ]
    return jsonify(filtered_doctors)


@app.route('/api/add_task', methods=['POST'])
def add_task():
    """添加新任务"""
    data = request.json
    doctor_id = data.get('doctor_id')
    time_slot_id = data.get('time_slot_id')

    if not doctor_id or not time_slot_id:
        return jsonify({"success": False, "message": "请选择医生和时间段"})

    # 创建新任务
    task_id = str(uuid.uuid4())
    doctor = DOCTORS.get(int(doctor_id))
    time_slot = next((slot for slot in TIME_SLOTS if slot["id"] == int(time_slot_id)), None)

    if not doctor or not time_slot:
        return jsonify({"success": False, "message": "无效的医生或时间段"})

    RUNNING_TASKS[task_id] = {
        "id": task_id,
        "doctor": doctor,
        "time_slot": time_slot,
        "status": "running",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return jsonify({
        "success": True,
        "message": "任务已添加",
        "task": RUNNING_TASKS[task_id]
    })


@app.route('/api/delete_task/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    if task_id in RUNNING_TASKS:
        del RUNNING_TASKS[task_id]
        return jsonify({"success": True, "message": "任务已删除"})
    return jsonify({"success": False, "message": "任务不存在"})


@app.route('/api/tasks')
def get_tasks():
    """获取所有任务"""
    return jsonify(list(RUNNING_TASKS.values()))


if __name__ == '__main__':
    app.run(debug=True)