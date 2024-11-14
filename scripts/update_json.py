import os
import json
import base64
from pydub import AudioSegment

audio_dir = "audio"
json_file_path = "docs/pitch_indices.json"


def get_audio_duration(audio_path):
    audio = AudioSegment.from_mp3(audio_path)
    return len(audio) / 1000


def load_json(json_file):
    with open(json_file, "r") as f:
        return json.load(f)


def save_json(json_file, data):
    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)


def get_audio_base64(audio_path):
    with open(audio_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode("utf-8")


def update_json_with_audio_times():
    data = load_json(json_file_path)

    audio_files = [
        "1.mp3",
        "2.mp3",
        "3.mp3",
        "4.mp3",
        "5.mp3",
        "6.mp3",
        "7.mp3",
        "8.mp3",
        "9.mp3",
        "10.mp3",
        "11.mp3",
        "12.mp3",
        "13.mp3",
        "14.mp3",
        "15.mp3",
        "16.mp3",
        "17.mp3",
        "18.mp3",
        "19.mp3",
        "20.mp3",
        "21.mp3",
        "22.mp3",
        "23.mp3",
        "24.mp3",
        "25.mp3",
        "26.mp3",
        "27.mp3",
        "28.mp3",
        "29.mp3",
        "30.mp3",
    ]
    current_time = 0
    for audio_file in audio_files:
        audio_id = os.path.splitext(audio_file)[0]

        if audio_id in data:
            audio_path = os.path.join(audio_dir, audio_file)
            audio_duration = get_audio_duration(audio_path)
            audio_base64 = get_audio_base64(audio_path)

            data[audio_id]["time_start"] = current_time
            data[audio_id]["time_end"] = current_time + audio_duration
            data[audio_id]["audio_base64"] = audio_base64

            current_time += audio_duration

    save_json(json_file_path, data)
    print("JSON file updated successfully!")


if __name__ == "__main__":
    update_json_with_audio_times()
