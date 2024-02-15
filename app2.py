from pytube import YouTube
import requests
from moviepy.editor import *
import os

# Função para baixar o áudio de um vídeo do YouTube e converter para MP3
def baixar_audio_youtube_como_mp3(url_video):
    yt = YouTube(url_video)
    video = yt.streams.filter(only_audio=True).first()
    caminho_arquivo_mp4 = video.download()
    caminho_arquivo_mp3 = caminho_arquivo_mp4.replace("mp4", "mp3")
    
    # Converte de MP4 para MP3
    videoclip = AudioFileClip(caminho_arquivo_mp4)
    videoclip.write_audiofile(caminho_arquivo_mp3)
    
    # Apaga o arquivo MP4 original para liberar espaço
    os.remove(caminho_arquivo_mp4)
    
    return caminho_arquivo_mp3

# Função para enviar o áudio para o AssemblyAI e obter a transcrição
def transcrever_audio_assemblyai(caminho_arquivo, language_code="en"):
    headers = {
        "authorization": "7b928535263d4f80b130462a80a16000",
        "content-type": "application/json"
    }
    response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files={'file': open(caminho_arquivo, 'rb')})
    audio_url = response.json()['upload_url']

    json = {
        "audio_url": audio_url,
        "language_code": language_code  # Adiciona o código do idioma à solicitação
    }
    response_transcricao = requests.post('https://api.assemblyai.com/v2/transcript', json=json, headers=headers)
    transcript_id = response_transcricao.json()['id']

    while True:
        check_response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
        if check_response.json()['status'] == 'completed':
            return check_response.json()['text']
        elif check_response.json()['status'] == 'failed':
            return "A transcrição falhou."

# Combinação dos dois processos em um único script
def transcrever_video_youtube(url_video, language_code="en"):
    print("Baixando e convertendo áudio do vídeo para MP3...")
    caminho_audio_mp3 = baixar_audio_youtube_como_mp3(url_video)
    print("Áudio convertido para MP3. Iniciando transcrição...")
    texto_transcrito = transcrever_audio_assemblyai(caminho_audio_mp3, language_code)
    return texto_transcrito

# Exemplo de uso
url = "https://youtu.be/iB2QZLVESv0"  # Substitua pela URL do vídeo do YouTube
language_code = "pt"  # Substitua pelo código do idioma desejado
texto_transcrito = transcrever_video_youtube(url, language_code)
print("Texto transcrito:", texto_transcrito)
