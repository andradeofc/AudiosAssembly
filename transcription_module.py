from pytube import YouTube
from moviepy.editor import AudioFileClip
import requests
import os

def baixar_audio_youtube_como_mp3(url_video):
    yt = YouTube(url_video)
    video = yt.streams.filter(only_audio=True).first()
    caminho_arquivo_mp4 = video.download()
    caminho_arquivo_mp3 = caminho_arquivo_mp4.replace("mp4", "mp3")
    
    videoclip = AudioFileClip(caminho_arquivo_mp4)
    videoclip.write_audiofile(caminho_arquivo_mp3)
    
    os.remove(caminho_arquivo_mp4)
    
    return caminho_arquivo_mp3

def transcrever_audio_assemblyai(caminho_arquivo, language_code="en"):
    headers = {
        "authorization": "7b928535263d4f80b130462a80a16000",
        "content-type": "application/json"
    }
    response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files={'file': open(caminho_arquivo, 'rb')})
    audio_url = response.json()['upload_url']

    json = {
        "audio_url": audio_url,
        "language_code": language_code
    }
    response_transcricao = requests.post('https://api.assemblyai.com/v2/transcript', json=json, headers=headers)
    transcript_id = response_transcricao.json()['id']

    while True:
        check_response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
        if check_response.json()['status'] == 'completed':
            return check_response.json()['text']
        elif check_response.json()['status'] == 'failed':
            return "A transcrição falhou."

def transcrever_video_youtube(url_video, language_code="en"):
    # Supondo que baixar_audio_youtube_como_mp3 retorne o caminho completo do arquivo MP3
    caminho_audio_mp3 = baixar_audio_youtube_como_mp3(url_video)
    texto_transcrito = transcrever_audio_assemblyai(caminho_audio_mp3, language_code)
    # Retorne tanto o texto transcrito quanto o nome do arquivo MP3
    return texto_transcrito, os.path.basename(caminho_audio_mp3)
