import edge_tts
import playsound
from playsound import playsound

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

# main loop
if __name__ == "__main__":
    text_to_speech(text="已完成！")
