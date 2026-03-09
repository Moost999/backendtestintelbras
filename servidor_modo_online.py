# server.py
from flask import Flask, request, jsonify
import json
import ast
import time
import os
from pathlib import Path

app = Flask(__name__)

# Configuração de diretórios
BASE_DIR = Path(__file__).parent
SAVE_DIR = BASE_DIR / "s_files"
SAVE_RAW_DIR = BASE_DIR / "s_raw_files"

# Cria os diretórios se não existirem
SAVE_DIR.mkdir(exist_ok=True)
SAVE_RAW_DIR.mkdir(exist_ok=True)

@app.route('/notification', methods=['POST'])
def event_receiver():
    if request.method == 'POST':
        try:
            raw_data = request.data
            # Salva o raw data
            raw_name = f"raw_data_{time.strftime('%Y-%m-%d_%H_%M_%S')}.txt"
            with open(SAVE_RAW_DIR / raw_name, "ab") as fp:
                fp.write(raw_data)

            data_list = raw_data.split(b"--myboundary\r\n")
            
            if data_list:
                for a_info in data_list:
                    if b"Content-Type" in a_info:
                        lines = a_info.split(b"\r\n")
                        a_type = lines[0].split(b": ")[1]

                        if a_type == b"image/jpeg":
                            a_name = f"image_{time.strftime('%Y-%m-%d_%H_%M_%S')}.jpg"
                            with open(SAVE_DIR / a_name, "wb") as fp:
                                data = b"\r\n".join(lines[3:-3])
                                fp.write(data)
                        else:
                            a_name = f"event_{time.strftime('%Y-%m-%d_%H_%M_%S')}.txt"
                            with open(SAVE_DIR / a_name, "wb") as fp:
                                data = b"\r\n".join(lines[3:-1])
                                fp.write(data)
                            
                            # Processa o evento
                            evento_str = data.decode("utf-8")
                            evento_dict = ast.literal_eval(evento_str.replace("--myboundary--", " "))
                            resp_dict = json.loads(json.dumps(evento_dict, indent=4))
                            
                            print(resp_dict)
                            event_code = resp_dict.get("Events", [{}])[0].get('Code', '')
                            print(f"################## {event_code} ##################")

                            if event_code == "AccessControl":
                                event_data = resp_dict["Events"][0].get('Data', {})
                                print(f"UserID: {event_data.get('UserID')}")
                                print(f"CardNo: {event_data.get('CardNo')}")
                                
                                # Sua lógica de autorização aqui
                                if event_data.get('UserID') == 6:
                                    return jsonify({"message": "Pagamento não realizado!", "code": "200", "auth": "false"})
                                elif event_data.get('CardNo') in ["EC56D271", "09201802"]:
                                    return jsonify({"message": "Bem vindo!", "code": "200", "auth": "true"})
                                elif event_data.get('DynPWD') == "222333":
                                    return jsonify({"message": "Acesso Liberado", "code": "200", "auth": "true"})

            return jsonify({"message": "", "code": "200", "auth": "false"})

        except Exception as e:
            print(f"Error processing request: {str(e)}")
            return jsonify({"error": str(e)}), 500

@app.route('/keepalive', methods=['GET'])
def keep_alive():
    return "OK"

@app.route('/cgi-bin/<path:subpath>', methods=['GET', 'POST'])
def cgi_mock(subpath):
    """Mock para endpoints CGI do dispositivo Intelbras"""
    print(f"Mocking CGI call: {subpath}")
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)