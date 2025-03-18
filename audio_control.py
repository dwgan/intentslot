import wenet
from record import record
from auto_record import auto_record
from detector import JointIntentSlotDetector
import serial
from send_command import send_command
from convert_command import convert_command

print('正在加载模型...')

# 一次性初始化（只需加载一次）
model_wenet = wenet.load_model('chinese')
model_bert = JointIntentSlotDetector.from_pretrained(
    model_path='result/model/model_epoch4',
    tokenizer_path='result/tokenizer/',
    intent_label_path='data/intent_labels.txt',
    slot_label_path="data/slot_labels.txt"
)
serial_port = serial.Serial('/dev/ttyAMA1', baudrate=115200, timeout=1)

try:
    while True:
        # 等待用户输入触发新循环
        input("\n按回车键开始检测声音，或按 Ctrl+C 退出...")
        
        # 录音流程
        auto_record(output_filename="record.wav", min_record_time=2, silence_timeout=1)
        print('\n正在转文字...\n')
        
        # 语音识别
        result = model_wenet.transcribe('record.wav')
        print(result['text'])
        
        # 意图识别
        text = [result['text']]
        bert_output = model_bert.detect(text)[0]
        print(bert_output)

        # 转换指令

        command_list = convert_command(bert_output["intent"], bert_output["slots"])

#        cmd = convert_command(bert_output["intent"], bert_output["slots"])
#         cmd = convert_command(bert_output)
        if command_list != None:
            for cmd in command_list:
                if cmd:
                    print(f"📤 发送指令: {cmd}")
                    serial_port.write(cmd)
                else:
                    print("⛔ 未执行任何操作")

except KeyboardInterrupt:
    print("\n程序已终止")
finally:
    serial_port.close()
