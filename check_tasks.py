# check_tasks.py - 检查所有 taskId 的状态
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from src.config import load_global_config
from src.toonflow.client import ToonflowClient

cfg = load_global_config()
cli = ToonflowClient(cfg)

for tid in range(21, 34):
    try:
        st = cli.api_call("/game/convertAvatarVideoToGif/status", {"taskId": tid}, timeout=15)
        d = st.get("data", {})
        print(f"taskId={tid}: status={d.get('status')} progress={d.get('progress')}% "
              f"msg={d.get('message','')} err={d.get('errorMessage','')}", flush=True)
    except Exception as e:
        print(f"taskId={tid}: 查询失败 {e}", flush=True)
