from snowboy.examples.Python3 import snowboydecoder
import sys
import signal
import wenet
from record import record
from auto_record import auto_record
from detector import JointIntentSlotDetector
import serial
from send_command import send_command
from convert_command import convert_command
import edge_tts
import playsound
import edge_tts
from playsound import playsound
from espeak_tts import tts

def text_to_speech(
    text: str,
    voice: str = "zh-CN-XiaoxiaoNeural",  # 默认使用晓晓语音
    rate: str = "+0%",                    # 语速调整（±百分比）
    volume: str = "-90%",                 # 音量调整（±百分比）
    pitch: str = "+0Hz",                  # 音调调整（±赫兹）
    output_file: str = "temp.wav"         # 临时音频文件路径
) -> None:
    """
    将文本转换为语音并播放
    
    Args:
        text: 输入文本内容
        voice: 语音角色（支持zh-CN-YunyangNeural等中文语音）
        rate: 语速调节（如'+50%'加速）
        volume: 音量调节（如'+20%'提高）
        pitch: 音调调节（如'+100Hz'升调）
        output_file: 临时音频保存路径
    """
    # 生成语音文件（同步保存）
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch
    )
    communicate.save_sync(output_file)
    
    # 播放音频
    playsound(output_file)


def keyword_detected():
    print('keyword detected')
    try:
        # 响应请求
        print("识别到关键词，正在播放声音")
        # text_to_speech(text="您好，有什么可以帮您！")
        # tts("您好，有什么可以帮您？", volume=20)
        playsound("./audio/what_can_i_do_for_you.wav")

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
        print("done\n")
        playsound("./audio/done.wav")
        # text_to_speech(text="已完成")
        # tts("已完成", volume=20)
        print(command_list)

    except KeyboardInterrupt:
        print("\n程序已终止")
    finally:
        keyword_detetor.start()  # 处理完成后重新启动监听


# auto_record(output_filename="record.wav", min_record_time=2, silence_timeout=1)
# print('\n正在转文字...\n')
# result = model_wenet.transcribe('record.wav')
# print(result['text'])

# main loop
if __name__ == "__main__":
    print('正在加载模型...')

    # 一次性初始化（只需加载一次）
    model_wenet = wenet.load_model('chinese')
    model_bert = JointIntentSlotDetector.from_pretrained(
        model_path='result/model/model_epoch4',
        tokenizer_path='result/tokenizer/',
        intent_label_path='data/intent_labels.txt',
        slot_label_path="data/slot_labels.txt"
    )
    keyword_detetor = snowboydecoder.HotwordDetector('xiaoyi.pmdl', sensitivity=0.4, detected_callback=keyword_detected)
    serial_port = serial.Serial('/dev/ttyAMA1', baudrate=115200, timeout=1)

    # tts("欢迎使用智能语音助手", volume=20)
    # text_to_speech(text="欢迎使用智能语音助手")
    playsound("./audio/wellcome.wav")
    print("请说话，或按 Ctrl+C 退出...")
    keyword_detetor.start(sleep_time=0.03)
    keyword_detetor.terminate()
    serial_port.close()
