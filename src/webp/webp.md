# webp cli 设计
"""
单个角色的立绘的完整步骤
python -m src.cli webp --living {config} {path_json}
python -m src.cli webp --inanimate {config} {path_json}

config 就是配置文件，如 .workbuddy/config/vedio_to_webp.yml
path_json 就是 生图json 入参。如
npc
{
"input_video":.cache/character/通天传授-收徒系统/墨老/墨老_立绘微动.mp4",
"rolename":"墨老",
"rolenType":"npc",
"story":"通天传授-收徒系统",
"type":"living",
"output_path":".cache/character/通天传授-收徒系统/墨老/webp/"
}

用户
{
"input_video":.cache/character/通天传授-收徒系统/陆川/陆川_立绘微动.mp4",
"rolename":"陆川",
"rolenType":"player",
"story":"通天传授-收徒系统",
"type":"living",
"output_path":".cache/character/通天传授-收徒系统/陆川/webp/"
}

分步操作：视频-》抽帧 -》背景-》首帧-》webp文件-》webp.json
# video.mp4 到 .cache/character/{story}/{rolename}/webp/video.mp4
python -m src.cli webp --living --video.mp4 {config} {path_json}
# 抽帧 到 .cache/character/{story}/{rolename}/webp/_tmp_frames
python -m src.cli webp --living --tmp_frames {config} {path_json}
# 生成背景图片到 到 .cache/character/{story}/{rolename}/webp/background.png
python -m src.cli webp --living --background {config} {path_json}
# 生成首帧图片到 到 .cache/character/{story}/{rolename}/webp/firstFrame.png
python -m src.cli webp --living --firstFrame {config} {path_json}
# 生成抠图后的webp到 .cache/character/{story}/{rolename}/webp/foreground.webp
python -m src.cli webp --living --foreground.webp {config} {path_json}

python -m src.cli webp --living --webp.json {config} {path_json}


"""


def webp_op():
    """webp操作入口（供 cli 调用）"""


### 重影根因分析
重影是合成webp 时导致的，上一帧的图像残留到了下一帧导致了图像拖影。

把 75 个 ANMF header 第 16 字节的 bit0 置 1（disposal: NONE → BACKGROUND），像素数据一字节没动，文件大小完全相同（4918048 bytes）。
文件	BACKGROUND 帧	严格解码	忽略 NO_BLEND	忽略 dispose	三模式一致？
A_current	0/75	1.018	1.147 单调累积	1.018	❌
E_dispose_fix	75/75	1.018	1.018	1.018	✅ 完全一致
C_anim_lossy	17/75	1.018	1.027	1.021	❌
APP_real	36/75	0.996	0.999	0.999	❌
E_dispose_fix 是四个里唯一在三种解码策略下采样序列逐个数字都相同的
（[49690, 49546, 50051, 51210, 50485, 51327, 51328, 49764, 50731]），
也就是不管播放器怎么实现，结果都一样。而且它的严格模式结果
与 A 逐位相同 —— 证明这个改动不改变任何正常视觉效果，纯粹是补上兜底清理。
它比 APP 还稳（APP 三模式有 0.996 / 0.999 / 0.999 的细微飘动）。
残影根因：step_foreground 用全局并集几何把主体位置固定住后，
libwebp_anim 在 -lossless 1 下判断"每帧覆写同一个矩形就够了"，
把 disposal 全部省成 NONE，只留 NO_BLEND 一道防线。
遇到不尊重 NO_BLEND 的播放器就必然残影。app 之所以没这问题，
是它 per-frame normalize 导致主体 bbox 逐帧漂移，反而迫使编码器插入了 36 个 BACKGROUND。
为什么不能靠 ffmpeg 参数解决：
libwebp_anim 只暴露 lossless / preset / cr_threshold / cr_size / quality 五个选项，
没有任何方式指定 disposal。所以修法只能是编码完成后对产物打这个 1 字节位补丁。


## _state.json
_state.json 是谁产出的？
_state.json 由代码中的 write_state() 方法产出，保存在 {output_path}/_tmp_frames/_state.json。它在两个步骤的末尾各写一次：
① step_tmp_frames 末尾（抽帧+抠图完成后）：
python

编辑



t.write_state(frames=len(src_frames), mattingSeconds=matting_seconds,
              model=t.model, fps=fps, gifSide=gif_side, concurrency=concurrency)
写入字段：frames, mattingSeconds, model, fps, gifSide, concurrency
② step_foreground 末尾（WebP 编码完成后）：
python

编辑



t.write_state(normalizeMode=t.normalize_mode, foregroundGeometry=geom,
              frames=len(matte_frames))
写入字段：normalizeMode, foregroundGeometry, frames
write_state 是 read-modify-write：先读已有的 _state.json，合并新字段，再整体写回。所以正常情况下，最终文件应该包含两组字段。
为什么你的 _state_2.json（有问题的）缺字段？
对比两个文件：
表格
字段	_state_1.json（正常的）	_state_2.json（有问题的）
frames	75	48
mattingSeconds	20.32	缺失
model	modnet	缺失
fps	15	缺失
gifSide	512	缺失
concurrency	6	缺失
normalizeMode	global	global
foregroundGeometry	有	有
缺少的 5 个字段（mattingSeconds, model, fps, gifSide, concurrency）恰好就是 step_tmp_frames 写入的那一组。
这说明：step_tmp_frames 的 write_state 调用从未被执行到，只有 step_foreground 的 write_state 被执行了。
是不是进程中断导致的？
是的，几乎可以确定。 推理过程：
step_tmp_frames 的抠图步骤（尤其是 birefnet-portrait + concurrency=2）非常慢，需要几分钟到十几分钟
在这个过程中，进程被中断了（Ctrl+C、超时、崩溃、系统杀进程等）
中断时，matte 帧文件已经写到了 _tmp_frames/matte/ 目录，但 step_tmp_frames 末尾的 write_state 还没执行到
之后你重新运行（用了 --foreground.webp 只跑 foreground 步骤），step_foreground 找到了已有的 matte 帧，正常执行完毕，它的 write_state 写入了 _state.json
但因为 step_tmp_frames 的 write_state 从未执行，所以文件中缺少那 5 个字段
运行日志也佐证了这一点——你第 3 轮运行的命令是 --foreground.webp，日志里只有 geometry / normalize_done / foreground_done，完全没有 frames_extracted / matting_done 这些 step_tmp_frames 的日志，说明 step_tmp_frames 根本没跑。