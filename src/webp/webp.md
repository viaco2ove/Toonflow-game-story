# webp cli 设计
"""
单个角色的立绘的完整步骤
python -m src.cli webp --living {config} {path_json}
python -m src.cli webp --inanimate {config} {path_json}

config 就是配置文件，如 .workbuddy/config/vedio_to_webp.yml
path_json 就是 生图json 入参。如
{
"input_video":.cache/character/通天传授-收徒系统/墨老/墨老_立绘微动.mp4",
"rolename":"墨老",
"story":"通天传授-收徒系统",
"type":"living",
"output_path":".cache/character/通天传授-收徒系统/墨老/webp/"
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