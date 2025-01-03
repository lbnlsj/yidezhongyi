import requests
import time
from typing import Dict, Optional


def get_doctor_schedule(config, is_am: int = 0) -> Dict:
    """
    获取医生排班时间信息的函数

    参数:
        is_am: 是否上午班次 (0: 下午, 1: 上午)

    返回:
        Dict: 接口返回的JSON数据
    """
    base_url = f"https://yy.baiyikeyi.top/stj_api/doctor/schedule_time?&department_id={config['department_id']}&doctor_id={config['doctor_id']}&date={time.strftime('%Y-%m-%d', time.localtime(time.time() + 24 * 3600))}&is_am={is_am}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/6.8.0(0x16080000) MacWechat/3.8.8(0x13080813) XWEB/1227 Flue',
        'Accept': '*/*',
        'from': 'h5',
        'insid': 'Mg==',
        'branchid': '2',
        'x-token': config['x_token'],
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty'
    }

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {str(e)}")
        return None


def make_appointment(config, schedule_date_id: str, card_id: int, info_text: str = "") -> Dict:
    """
    预约医生门诊的函数

    参数:
        schedule_date_id: 排班时间ID
        card_id: 就诊卡ID
        info_text: 附加信息文本，可选

    返回:
        Dict: 接口返回的JSON数据
    """
    url = "https://yy.baiyikeyi.top/stj_api/doctor/appointment"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/6.8.0(0x16080000) MacWechat/3.8.8(0x13080813) XWEB/1227 Flue',
        'Accept': '*/*',
        'from': 'h5',
        'insid': 'Mg==',
        'branchid': '2',
        'x-token': config['x_token'],
        'Content-Type': 'application/json',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty'
    }

    data = {
        "schedule_date_id": schedule_date_id,
        "card_id": card_id,
        "info_text": info_text
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"预约请求发生错误: {str(e)}")
        return None


if __name__ == "__main__":
    # 查询排班示例
    schedule_result = get_doctor_schedule()
    if schedule_result:
        print("排班查询成功!")
        print(schedule_result)

    # 预约示例
    appointment_result = make_appointment(
        schedule_date_id="45009",
        card_id=35511
    )
    if appointment_result:
        print("预约请求成功!")
        print(appointment_result)