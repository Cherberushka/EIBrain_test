import asyncio

import speech_recognition as sr


class FFmpeg():
    PROGRAM = "ffmpeg"
    FLAG1 = '-i'
    FILE_IN = 'voice.ogg'
    FILE_OUT = 'voice.wav'
    FLAG2 = '-y'


async def audio_convert() -> None:
    """Конвертирование формата файла"""
    process = await asyncio.create_subprocess_exec(
        FFmpeg.PROGRAM, FFmpeg.FLAG1,
        FFmpeg.FILE_IN, FFmpeg.FILE_OUT, FFmpeg.FLAG2
    )
    await process.wait()


async def audio_recognition(file: str = FFmpeg.FILE_OUT) -> str:
    """Процесс распознавания речи из аудиофайла"""
    r = sr.Recognizer()
    user_audio_file = sr.AudioFile(file)
    with user_audio_file as source:
        user_audio = r.record(source)
    try:
        message_text = r.recognize_google(user_audio, language='ru-RU')
        return str(message_text)
    except sr.UnknownValueError:
        return "РРРРррр!\nЧто-то невнятное! Еще разок ..."
