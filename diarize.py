import sys
import os
from pyannote.audio import Pipeline
from pyannote_whisper.utils import diarize_text
from pywhispercpp.model import Model
import json

# https://gist.github.com/hbredin/049f2b629700bcea71324d2c1e7f8337
# https://vas3k.club/post/18916/

# Open the JSON file for reading
with open("settings.json", "r") as json_file:
    # Load the JSON data from the file
    settings = json.load(json_file)

# Extract the tokens from the JSON data
token = settings["token"]

# Указываем путь до файла с конфигом, он должен быть в той же директории, как сказано на шаге 3.
# in case of `OSError: [WinError 1314]` see windows_symbolic_links.md
#speaker_diarization = Pipeline.from_pretrained("config.yaml")
speaker_diarization = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token=token)

# Указываем название модели large и путь до директории с whisper-моделями из шага 1.
path_to_store_model = '/Users/guschin/whisper.cpp/models' #'./models' # '/Users/guschin/whisper.cpp/models'
model = Model('large', path_to_store_model, n_threads=6)


# speakers_Nr = sys.argv[1] # None

output_file_1 = None
output_file_2 = None

for audio_file_name in sys.argv[1:]:
    try:
        print("-----------------")
        print("analyze file: " + audio_file_name)
        
        transcription_extension = ".txt"
        root, _ = os.path.splitext(audio_file_name)

        # Указываем путь до аудио-файл, который будем расшифровывать в текст. Путь обязательно абсолютный.
        print("transcribe...")
        asr_result = model.transcribe(audio_file_name, language="ru")

        # Конвертация результата в формат, который понимает pyannote-whisper.
        result = {'segments': list()}

        transcription_path_1 = root + "_wh" + transcription_extension
        print(transcription_path_1)
        output_file_1 = open(transcription_path_1, "w")
        for item in asr_result:
            result['segments'].append({
                'start': item.t0 / 100,
                'end': item.t1 / 100,
                'text': item.text
                }
            )
            line = f'{item.t0:.2f} --> ' + f'{item.t1:.2f} : ' + item.text
            output_file_1.write(line + '\n')

        # Сегментация аудио-файла на реплики спикеров. Путь обязательно абсолютный.
        print("diarize...")
        diarization_result = speaker_diarization(audio_file_name)
        ''' num_speakers=speakers_Nr,  # these values can be
        min_speakers=speakers_Nr,  # provided by the user
        max_speakers=speakers_Nr)  # when they are known'''

        # Пересечение расшифровки и сегментаци.
        print("combine...")
        final_result = diarize_text(result, diarization_result)


        # Сохранить результат в файл
        transcription_path_2 = root + "_pa" + transcription_extension
        print(transcription_path_2)
        output_file_2 = open(transcription_path_2, "w") # "output.txt"
        for seg, spk, sent in final_result:
            int_seg_start = int(seg.start)
            start_hours = int_seg_start // 3600
            start_minutes = (int_seg_start % 3600) // 60
            start_seconds = int_seg_start % 60
            int_seg_end = int(seg.end)
            end_hours = int_seg_end // 3600
            end_minutes = (int_seg_end % 3600) // 60
            end_seconds = int_seg_end % 60

            line = f'{start_hours:02d}:{start_minutes:02d}:{start_seconds:02d} --> ' + f'{end_hours:02d}:{end_minutes:02d}:{end_seconds:02d} {spk} : ' + sent   # f'{seg.start:.2f} {seg.end:.2f} {spk} {sent}'
            output_file_2.write(line + '\n')
        print("finshed!")
    except Exception as e:
        print("Error! " + str(e))
    finally:
        if (output_file_1):
            output_file_1.close()
        if (output_file_2):
            output_file_2.close()