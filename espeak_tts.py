import os

def tts(text, speed=250, volume=100):
    os.system(f'espeak -v zh -s {speed} -a {volume} "{text}"')

if __name__ == "__main__":
    # 控制音量为 150
    tts("有什么可以帮您", volume=20)
