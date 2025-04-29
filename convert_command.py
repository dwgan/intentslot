# -*- coding: utf-8 -*-

# 配置区
ROOM_ALIAS = {
    '一楼': ['楼下'],
    '二楼': ['楼上'],
    '厨房': ['后厨'],
    '车库': ['车房']
}

DEVICE_MAPPING = {
    # 格式: (标准房间, 设备) : (设备类型, 设备ID)
    ('一楼', '灯'): (0x05, 0x03),
    ('二楼', '灯'): (0x05, 0x08),
    ('车库', '灯'): (0x05, 0x09),
    ('餐厅', '灯'): (0x05, 0x02),
    ('客厅', '灯'): (0x05, 0x03),
    ('卧室', '灯'): (0x05, 0x08),
    ('书房', '灯'): (0x05, 0x07),
    ('一楼', '大灯'): (0x05, 0x03),
    ('二楼', '大灯'): (0x05, 0x08),
    ('客厅', '大灯'): (0x05, 0x03),
    ('一楼', '射灯'): (0x05, 0x03),
    ('二楼', '射灯'): (0x05, 0x08),
    ('客厅', '灯带'): (0x05, 0x04),
    ('客厅', '彩灯'): (0x05, 0x04),
    ('二楼', '圆灯'): (0x05, 0x08),
    ('客厅', '空调'): (0x05, 0x06),
    ('卧室', '空调'): (0x05, 0x08),
    ('二楼', '空调'): (0x05, 0x06),
    ('车库', '充电桩'): (0x05, 0x09),
    ('客厅', '窗帘'): (0x0A, 0x07),
    ('卧室', '窗帘'): (0x0A, 0x07),
    ('', '总开关'): (0x05, 0x00),
    ('', '门'): (0x05, 0x01),
    ('', '大门'): (0x05, 0x01)
}

INTENT_MAPPING = {
    'OPEN': 0x01,
    'CLOSE': 0x00
}


def normalize_room(raw_room):
    """标准化房间名称"""
    for std_room, aliases in ROOM_ALIAS.items():
        if raw_room in aliases + [std_room]:
            return std_room
    return raw_room


def find_device(device, room=None):
    """查找设备信息"""
    candidates = []

    for (r, d), info in DEVICE_MAPPING.items():
        if d == device:
            if not room or r == room:
                candidates.append(info)

    if not candidates:
        raise ValueError(f"设备 {device} 不存在{'于 ' + room if room else ''}")

    return candidates


def generate_command(device_type, device_id, intent):
    """生成串口指令"""
    return bytes([0x7E, device_type, device_id, INTENT_MAPPING[intent], 0x7F])


# def _build_packet(device_info: tuple, intent: str) -> bytes:
#     dev_type, dev_id = device_info
#     action = INTENT_MAPPING.get(intent)
#     if action is None:
#         raise ValueError(f"未知操作类型: {intent}")
#     return bytes([0x7E, dev_type, dev_id, action, 0x7F])

def convert_command(intent, slots):
    """
    新版指令转换函数
    :param intent: 意图字符串，如 'OPEN'
    :param slots: 槽位字典，如 {'room': ['楼上'], 'device': ['大灯']}
    :return: 十六进制指令字符串 或 错误信息
    """
    try:
        # 参数校验
        if not intent or intent not in INTENT_MAPPING:
            raise ValueError(f"无效指令类型: {intent}")
        
        # 获取设备名称
        device_list = slots.get('device', [])
        if not device_list:
            raise ValueError("未指定控制设备")
        device = device_list[0]

        # 标准化房间名称
        raw_rooms = slots.get('room', [])
        rooms = [normalize_room(r) for r in raw_rooms]

        # 获取候选设备
        candidates = []
        if rooms:
            for r in rooms:
                try:
                    candidates.extend(find_device(device, r))
                except ValueError as e:
                    print(f"⚠️ {str(e)}")
        else:
            candidates = find_device(device)

        if not candidates:
            raise ValueError(f"没有找到可控制的 {device} 设备")
        # else:
        #     print(f"{intent} {r} {device}")

        # # 生成指令集
        # commands = []
        # for dev_type, dev_id in candidates:
        #     cmd_bytes = bytes([0x7E, dev_type, dev_id, INTENT_MAPPING[intent], 0x7F])
        #     commands.append(cmd_bytes.hex(' '))
        #
        # return '; '.join(commands) if len(commands) > 1 else commands[0]

        # 生成指令集（保持字节格式）
        commands = []
        for dev_type, dev_id in candidates:
            commands.append(generate_command(dev_type, dev_id, intent))

        return commands  # 返回字节数组列表

    except (KeyError, IndexError) as e:
        # print("参数解析错误: {str(e)}")
        return None
    except ValueError as e:
        # print(f"控制失败: {str(e)}")
        return None
# 新版测试用例
if __name__ == "__main__":
    # 有效指令测试
    print(convert_command(
        intent="OPEN",
        slots={"room": ["上层"], "device": ["大灯"]}
    ))  # 7e 01 01 01 7f

    # 广播控制测试
    print(convert_command(
        intent="CLOSE",
        slots={"device": ["射灯"]}
    ))  # 7e 01 02 00 7f; 7e 01 03 00 7f

    # 错误指令测试
    print(convert_command(
        intent="OPEN",
        slots={"room": ["车库"], "device": ["空调"]}
    ))  # 控制失败: 没有找到可控制的 空调 设备
