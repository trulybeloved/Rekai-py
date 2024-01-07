from google.cloud import texttospeech
import concurrent.futures
from datetime import datetime
from loguru import logger
from Rekai.nlp_modules.basic_nlp import TextSplitter
from Rekai.appconfig import AppConfig
from Rekai.db_management import TextToSpeechDBM
# To do
# input validation

# @staticmethod

lines = """　彼の人生は十七年、その全てを語り尽くすにはそれこそ十七年の時間を必要とする。

　それらを割愛し、彼の現在の立場を簡単に説明するのならば『高校三年生にしてひきこもり』となる。

　詳細に説明するなら、『受験を間近に控えた時期なのに、親の期待もなにもかもうっちゃって自分の殻に閉じこもったどうしようもないクズ』といったところだ。



　ひきこもった理由は特にない。

　普通の平日、たまたま「今日は起きるのが面倒だ」となんとなく思い、サボりを実行に移したことが切っ掛けではあった。

　そのままずるずると自主休校が増え、気付けば立派に親を泣かせるひきこもり。

　日がな一日怠惰をむさぼり、コミュニケーション皆無のネットに沈み続け――、



「その結果が異世界召喚か……もはや自分で言ってて意味わかんねぇな」



　改めて状況を再確認して、スバルはもう何度目になるかわからないため息をついた。



　先ほどまで好奇の視線を浴びていた通りから場所を移し、今は少し薄暗い路地裏に腰を下ろしている。

　地面は舗装されていて、現代日本と比較すれば雑な仕事だが悪くはない。
"""
list_of_lines = TextSplitter.splitlines_to_list(lines)


def tts_string_with_google_api(line: str) -> list:

    """DOCSTRING PENDING"""

    now = datetime.now()
    timestamp = now.strftime('%Y_%m_%d_%H_%M_%S')

    # Get configration on run
    language_code: str = AppConfig.GoogleTTSConfig.language_code
    ssml_gender = AppConfig.GoogleTTSConfig.ssml_gender
    voice_name: str = AppConfig.GoogleTTSConfig.voice_name
    audio_encoding = AppConfig.GoogleTTSConfig.audio_encoding
    speaking_rate: float = AppConfig.GoogleTTSConfig.speaking_rate
    pitch: float = AppConfig.GoogleTTSConfig.pitch
    volume_gain_db: float = AppConfig.GoogleTTSConfig.volume_gain_db


    tts_client = texttospeech.TextToSpeechClient()
    input_for_synthesis = texttospeech.SynthesisInput({"text": f"{line}"})
    voice_settings = texttospeech.VoiceSelectionParams(
        {
            "language_code": language_code,
            "ssml_gender": ssml_gender,
            "name": voice_name
        }
    )
    audio_configuration = texttospeech.AudioConfig(
        {
            "audio_encoding": audio_encoding,
            "speaking_rate": speaking_rate,
            "pitch": pitch,
            "volume_gain_db": volume_gain_db,
        }
    )
    logger.info(f'TTS_API_CALL: Line: {line}')

    api_response = tts_client.synthesize_speech(
        input=input_for_synthesis,
        voice=voice_settings,
        audio_config=audio_configuration)

    logger.info(f'TTS_API_CALL for {line} was sucessful')
    output = [line, api_response.audio_content]
    # with open(
    #         f"C:\\Users\\prav9\\OneDrive\\Desktop\\Coding\\MTL\Rekai\\tts_outputs\\google_tts_api_output_{timestamp}.opus",
    #         "wb") as out:
    #     # Write the response to the output file.
    #     out.write(output[1])
    return output


# tts_string_with_google_api('「マジで勘弁してくれよ。俺にどうしろっつーんだよ」')


def tts_list_with_google_api(list_of_lines: list) -> list[list[str | bytes]]:

    if isinstance(list_of_lines, list):
        with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
            output_list = list(executor.map(tts_string_with_google_api, list_of_lines))
    return output_list

if __name__ == '__main__':
    # tts_db_interface = TextToSpeechDBM()
    #
    # now = datetime.now()
    # timestamp = now.strftime('%Y_%m_%d_%H_%M_%S')
    # # output = tts_list_with_google_api(list_of_lines)
    # # for raw_line, tts_bytes in output:
    # #     tts_db_interface.insert(raw_line=raw_line, tts_bytes=tts_bytes)
    # # tts_db_interface.close_connection()
    # for index, raw_line in enumerate(list_of_lines):
    #     tss_bytes = tts_db_interface.query(raw_line=raw_line)
    #     with open(
    #         f"C:\\Users\\prav9\\OneDrive\\Desktop\\Coding\\MTL\Rekai\\tts_outputs\\google_tts_api_output_{timestamp}_{index}.opus",
    #         "wb") as out:
    #         out.write(tss_bytes)
    pass