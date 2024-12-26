from flask import Flask, render_template, request, jsonify
import json
import threading
import time
from utils import get_doctor_schedule, make_appointment

app = Flask(__name__)

# Global variables for controlling the scanning thread
scanning_thread = None
is_scanning = False
config = {
    "department_id": "",
    "doctor_id": "",
    "card_id": "",
    "x_token": "",
    "is_running": False
}


def load_config():
    try:
        with open('config.json', 'r') as f:
            global config
            config = json.load(f)
    except FileNotFoundError:
        save_config()


def save_config():
    with open('config.json', 'w') as f:
        json.dump(config, f)


def scanning_task():
    global is_scanning
    while is_scanning:
        try:
            # Check morning schedule
            morning_schedule = get_doctor_schedule(config, is_am=1)
            if morning_schedule and morning_schedule.get('data'):
                schedule_date_id = morning_schedule['data'][0].get('schedule_date_id')
                if schedule_date_id:
                    result = make_appointment(
                        config,
                        schedule_date_id=str(schedule_date_id),
                        card_id=int(config['card_id'])
                    )
                    print(f"Morning appointment result: {result}")
                    is_scanning = False
                    config['is_running'] = False
                    save_config()
                    return

            # Check afternoon schedule
            afternoon_schedule = get_doctor_schedule(config, is_am=0)
            if afternoon_schedule and afternoon_schedule.get('data'):
                schedule_date_id = afternoon_schedule['data'][0].get('schedule_date_id')
                if schedule_date_id:
                    result = make_appointment(
                        config,
                        schedule_date_id=str(schedule_date_id),
                        card_id=int(config['card_id'])
                    )
                    print(f"Afternoon appointment result: {result}")

                    is_scanning = False
                    config['is_running'] = False
                    save_config()
                    return

        except Exception as e:
            print(f"Error during scanning: {str(e)}")

        time.sleep(0.5)  # Wait for 5 seconds before next scan


# Replace before_first_request with alternative approach
with app.app_context():
    load_config()


@app.route('/')
def index():
    return render_template('index.html', config=config)


@app.route('/api/config', methods=['POST'])
def update_config():
    global config
    data = request.json
    config.update(data)
    save_config()
    return jsonify({"status": "success"})


@app.route('/api/start', methods=['POST'])
def start_scanning():
    global scanning_thread, is_scanning, config

    if not is_scanning:
        is_scanning = True
        config['is_running'] = True
        save_config()
        scanning_thread = threading.Thread(target=scanning_task)
        scanning_thread.daemon = True
        scanning_thread.start()

    return jsonify({"status": "success", "message": "Scanning started"})


@app.route('/api/stop', methods=['POST'])
def stop_scanning():
    global is_scanning, config
    is_scanning = False
    config['is_running'] = False
    save_config()
    return jsonify({"status": "success", "message": "Scanning stopped"})


@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "is_running": config['is_running'],
        "config": config
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)