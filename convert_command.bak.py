# 配置区
ROOM_ALIAS = {
    '一楼': ['楼下', '底层'],
    '二楼': ['楼上', '上层'],
    '厨房': ['后厨'],
    '车库': ['车房']
}

DEVICE_MAPPING = {
    # 格式: (标准房间, 设备) : (设备类型, 设备ID)
    ('一楼', '大灯'): (0x01, 0x00),
    ('二楼', '大灯'): (0x01, 0x01),
    ('一楼', '射灯'): (0x01, 0x02),
    ('二楼', '射灯'): (0x01, 0x03),
    ('厨房', '冰箱'): (0x02, 0x04),
    ('车库', '充电桩'): (0x03, 0x05),
    ('客厅', '空调'): (0x04, 0x06),
    ('卧室', '空调'): (0x04, 0x07)
}

INTENT_MAPPING = {
    'OPEN': 0x01,
    'CLOSE': 0x00,
    'ADJUST': 0x02,
    'QUERY': 0x03
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

def convert_command(data):
    try:
        # 参数解析
        device = data['slots']['device'][0]
        raw_rooms = data['slots'].get('room', [])
        intent = data['intent']
        
        # 标准化房间
        rooms = [normalize_room(r) for r in raw_rooms]
        
        # 获取候选设备
        if rooms:
            candidates = []
            for r in rooms:
                candidates.extend(find_device(device, r))
        else:
            candidates = find_device(device)
        
        # 生成指令集
        commands = []
        for dev_type, dev_id in candidates:
            commands.append(generate_command(dev_type, dev_id, intent).hex(' '))
        
        return '; '.join(commands) if len(commands) > 1 else commands[0]
    
    except (KeyError, IndexError) as e:
        return f"参数错误: {str(e)}"
    except ValueError as e:
        return f"指令错误: {str(e)}"

# 测试样例
test_case1 = {
    'text': '打开一楼大灯',
    'intent': 'OPEN',
    'slots': {'room': ['一楼'], 'device': ['大灯']}
}
print("测试1:", convert_command(test_case1))  # 7e 01 00 01 7f

test_case2 = {
    'text': '关闭所有射灯',
    'intent': 'CLOSE',
    'slots': {'device': ['射灯']}
}
print("测试2:", convert_command(test_case2))  # 7e 01 02 00 7f; 7e 01 03 00 7f

test_case3 = {
    'text': '开启二楼空调',
    'intent': 'OPEN',
    'slots': {'room': ['上层'], 'device': ['空调']}
}
print("测试3:", convert_command(test_case3))  # 指令错误: 设备 空调 不存在于 二楼
