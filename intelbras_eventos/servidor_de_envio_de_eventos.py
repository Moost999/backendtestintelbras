
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json

def enviar_requisicao():
    host = entry_host.get()
    metodo = combo_metodo.get()
    endpoint = combo_endpoints.get()
    url = f"{host}{endpoint}"
    corpo_raw = text_json.get("1.0", tk.END).strip()

    parametros = endpoints_config.get(endpoint, {}).get("params", {})
    body_default = endpoints_config.get(endpoint, {}).get("body", {})

    headers = {"Content-Type": "application/json"}

    try:
        if metodo == "GET":
            response = requests.get(url, params=parametros)
        elif metodo == "POST":
            body = json.loads(corpo_raw) if corpo_raw else body_default
            response = requests.post(url, params=parametros, json=body, headers=headers)
        else:
            messagebox.showerror("Erro", "Método HTTP não suportado.")
            return

        text_resposta.delete("1.0", tk.END)
        text_resposta.insert(tk.END, f"Status: {response.status_code}\n")
        text_resposta.insert(tk.END, response.text)

    except Exception as e:
        messagebox.showerror("Erro", str(e))

def atualizar_campos(event=None):
    endpoint = combo_endpoints.get()
    config = endpoints_config.get(endpoint, {})
    params = config.get("params", {})
    body = config.get("body", {})
    combo_metodo.set(config.get("method", "GET"))
    entry_parametros.config(state="normal")
    entry_parametros.delete(0, tk.END)
    entry_parametros.insert(0, "&".join([f"{k}={v}" for k, v in params.items()]))
    entry_parametros.config(state="disabled")
    text_json.delete("1.0", tk.END)
    if body:
        text_json.insert(tk.END, json.dumps(body, indent=2))

janela = tk.Tk()
janela.title("Cliente API Intelbras - Mock")
janela.geometry("800x700")

tk.Label(janela, text="Host/IP do dispositivo ou mock:").pack()
entry_host = tk.Entry(janela, width=90)
entry_host.insert(0, "https://intelbras-caco-api.intelbras.com.br")
entry_host.pack(pady=2)

tk.Label(janela, text="Método HTTP:").pack()
combo_metodo = ttk.Combobox(janela, values=["GET", "POST"], state="readonly")
combo_metodo.set("GET")
combo_metodo.pack(pady=2)

tk.Label(janela, text="Endpoint da API:").pack()
combo_endpoints = ttk.Combobox(janela, values=[], state="readonly", width=80)
combo_endpoints.pack(pady=2)
combo_endpoints.bind("<<ComboboxSelected>>", atualizar_campos)

tk.Label(janela, text="Parâmetros:").pack()
entry_parametros = tk.Entry(janela, width=90, state="disabled")
entry_parametros.pack(pady=2)

tk.Label(janela, text="Corpo JSON (POST):").pack()
text_json = scrolledtext.ScrolledText(janela, height=10, width=90)
text_json.pack(pady=5)

btn_enviar = tk.Button(janela, text="Enviar Requisição", command=enviar_requisicao, bg="green", fg="white")
btn_enviar.pack(pady=10)

tk.Label(janela, text="Resposta:").pack()
text_resposta = scrolledtext.ScrolledText(janela, height=20, width=90)
text_resposta.pack()

# Endpoints e parâmetros mockados para testes
endpoints_config = {
    "/cgi-bin/accessControl.cgi": {
        "method": "GET",
        "params": {"action": "openDoor", "channel": "1"}
    },
    "/notification": {
        "method": "POST",
        "params": {},
        "body": {
            "Events": [{
                "Code": "AccessControl",
                "Data": {
                    "DynPWD": "222333",
                    "UserID": 12,
                    "Door": "1"
                }
            }]
        }
    },
    "/cgi-bin/user.cgi": {
        "method": "GET",
        "params": {"action": "getAllUserInfo"}
    },
    "/cgi-bin/configManager.cgi": {
        "method": "GET",
        "params": {"action": "getConfig", "name": "AccessControl"}
    }
}

combo_endpoints["values"] = list(endpoints_config.keys())
combo_endpoints.set("/cgi-bin/accessControl.cgi")
atualizar_campos()

janela.mainloop()
