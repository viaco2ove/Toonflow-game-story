import sys, time
RVM_SRC = r"D:/Users/viaco/tools/Toonflow-game/toonflow-game-app/Toonflow-game/tools/avatar-matting/birefnet/rvm-src"
PTH = r"D:/Users/viaco/tools/Toonflow-game/toonflow-game-app/Toonflow-game/tools/avatar-matting/birefnet/model-cache/rvm_mobilenetv3.pth"
sys.path.insert(0, RVM_SRC)
import torch
from model import MattingNetwork

model = MattingNetwork('mobilenetv3').eval()
sd = torch.load(PTH, map_location='cpu', weights_only=True)
model.load_state_dict(sd)
print("pth loaded ok")

rec = [None]*4
t0 = time.time()
src = torch.rand(1, 3, 512, 512)
with torch.no_grad():
    for i in range(5):
        fgr, pha, *rec = model(src, *rec, downsample_ratio=0.25)
        print(f"frame {i+1}: pha={tuple(pha.shape)} mean={float(pha.mean()):.4f} dt={time.time()-t0:.2f}s")
