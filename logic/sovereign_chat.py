import os
import sqlite3
import requests
import json
import sys

# === [GENERIC INTERFACE] ===
def get_config(var_name):
    """環境変数を取得。未設定時は『設定して下さい。』と出力し停止する"""
    value = os.getenv(var_name)
    if not value:
        print("設定して下さい。")
        sys.exit(1)
    return value

# 知能の構成要素（名前、接続先、記憶、モデル）を完全に外部化
AGENT_NAME   = os.getenv("SOVEREIGN_NAME", "Sovereign")
DB_PATH      = get_config("SOVEREIGN_DB_PATH")
API_ENDPOINT = get_config("SOVEREIGN_API_ENDPOINT")
MODEL_NAME   = get_config("SOVEREIGN_MODEL")

def retrieve_context():
    """DBから直近の記録を抽出し、推論の文脈を構成する"""
    if not os.path.exists(DB_PATH):
        return "Initial Node"
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        # id降順で最新の履歴を参照
        cur.execute("SELECT path FROM records ORDER BY id DESC LIMIT 7")
        rows = cur.fetchall()
        conn.close()
        return ", ".join([os.path.basename(r[0]) for r in rows])
    except:
        return "Safe Mode"

def build_prompt(user_input, context):
    """Gemma 2B チャットテンプレートに準拠したプロンプト構成"""
    return f"""<start_of_turn>user
あなたは自律型AI「{AGENT_NAME}」です。
抽出された記憶断片（{context}）を保持する専門家として、
マスターの指示に対し、簡潔かつ鋭く応答してください。

{user_input}<end_of_turn>
<start_of_turn>model
"""

def main():
    print(f"🚀 {AGENT_NAME} Engine Initializing...")
    context = retrieve_context()
    
    while True:
        try:
            user_input = input("\nMaster > ")
            if user_input.lower() in ["exit", "quit"]: break
            if not user_input.strip(): continue

            payload = {
                "model": MODEL_NAME,
                "prompt": build_prompt(user_input, context),
                "stream": True,
                "options": {
                    "num_thread": int(os.getenv("SOVEREIGN_THREADS", "4")),
                    "temperature": float(os.getenv("SOVEREIGN_TEMP", "0.7")),
                    "stop": ["<start_of_turn>", "<end_of_turn>"]
                }
            }

            response = requests.post(API_ENDPOINT, json=payload, stream=True, timeout=120)
            
            if response.status_code != 200:
                print(f"❌ Error: {response.status_code}")
                continue

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    print(chunk.get("response", ""), end="", flush=True)
                    if chunk.get("done"): print("")
                        
        except Exception as e:
            print(f"\n❌ Halt: {e}")

if __name__ == "__main__":
    main()
