import os

# === [CORE NODE DEFINITIONS] ===
# 1. memory/  : 知能の永続記憶（SQLite, JSONL）
# 2. logic/   : 推論プロトコル、カスタム命令
# 3. logs/    : 行動記録、エラー追跡（Prometheus/Loki連携用）
# 4. config/  : 主権の定義、接続鍵

CORE_NODES = [
    "memory",
    "logic",
    "logs",
    "config",
    "temp"
]

def build_sovereign_nodes():
    print("🛠️ Initializing Core Nodes for Sovereign Engine...")
    
    base_dir = os.getcwd()
    
    for node in CORE_NODES:
        node_path = os.path.join(base_dir, node)
        if not os.path.exists(node_path):
            os.makedirs(node_path)
            # 各ノードに .gitkeep を作成（空ディレクトリをGitで追跡可能にするため）
            with open(os.path.join(node_path, ".gitkeep"), "w") as f:
                f.write("")
            print(f"✅ Node created: {node}/")
        else:
            print(f"⚠️ Node already exists: {node}/")

    print("\n🚀 Core Nodes successfully established.")
    print("Next step: Define your identity in config/sovereign.env")

if __name__ == "__main__":
    build_sovereign_nodes()
