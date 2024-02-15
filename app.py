from flask import Flask, request, render_template, jsonify, send_file, session, after_this_request

from transcription_module import transcrever_video_youtube
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.secret_key = 'teste'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcricao', methods=['POST'])
def transcricao():
    url_video = request.form['url_video']
    language_code = request.form['language_code']
    try:
        # Agora a função retorna dois valores
        texto_transcrito, nome_arquivo_mp3 = transcrever_video_youtube(url_video, language_code)
        # Armazene o nome do arquivo na sessão
        session['nome_arquivo_mp3'] = nome_arquivo_mp3

        # Salvamos a transcrição temporariamente para permitir o download
        temp_filename = "transcricao_temp.txt"
        with open(temp_filename, 'w', encoding='utf-8') as f:
            f.write(texto_transcrito)

        return jsonify({"texto": texto_transcrito})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/download', methods=['GET'])
def download():
    # Nome do arquivo que você deseja enviar para o usuário
    filename = 'transcricao_temp.txt'
    
    # Construindo o caminho absoluto para o arquivo dentro da pasta do projeto
    path_to_file = os.path.join(app.root_path, filename)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(path_to_file)
            print(f"Arquivo {filename} excluído com sucesso.")
        except Exception as e:
            print(f"Erro ao excluir o arquivo {filename}: {e}")
        return response

    try:
        return send_file(path_to_file, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
