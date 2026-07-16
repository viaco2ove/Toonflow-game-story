"""
PNG tEXt chunk 工具：嵌入和验证角色卡数据

PNG tEXt chunk 标准格式:
    keyword\x00compression_method\x00text
其中 compression_method=0 表示不压缩

SillyTavern 角色卡使用 keyword="chara"，text=base64(UTF-8 JSON)
"""
import base64
import json
import struct
import zlib
from pathlib import Path


PNG_SIGNATURE = bytes([137, 80, 78, 71, 13, 10, 26, 10])


def embed_card_to_png(card_json: dict, avatar_path: str, output_path: str,
                      keyword: str = "chara") -> bool:
    """
    将角色卡 JSON 嵌入 PNG 的 tEXt chunk

    如果输入文件是 JPEG，先转换为 PNG。

    Args:
        card_json: 角色卡 JSON 字典
        avatar_path: 源头像文件路径（PNG 或 JPEG）
        output_path: 输出 PNG 文件路径
        keyword: tEXt chunk 关键字（"chara" 或 "ccv3"）

    Returns:
        True 成功，False 失败
    """
    # 读取源文件
    with open(avatar_path, "rb") as f:
        original_data = f.read()

    # 如果不是 PNG，用 PIL 转换
    if original_data[:8] != PNG_SIGNATURE:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(original_data))
        img = img.convert("RGBA")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        original_data = buf.getvalue()
        print(f"    (JPEG -> PNG 转换完成)")

    # 编码 JSON 为 base64
    json_str = json.dumps(card_json, ensure_ascii=False)
    b64_data = base64.b64encode(json_str.encode("utf-8"))

    # 构建 tEXt chunk data: keyword\x00\x00<base64>
    keyword_bytes = keyword.encode("latin-1")
    chunk_data = keyword_bytes + b"\x00" + b"\x00" + b64_data

    # 计算 CRC32
    chunk_type = b"tEXt"
    crc = zlib.crc32(chunk_type + chunk_data) & 0xffffffff
    chunk = struct.pack(">I", len(chunk_data)) + chunk_type + chunk_data + struct.pack(">I", crc)

    # 解析所有 chunks，在 IEND 之前插入新的 tEXt
    new_png = PNG_SIGNATURE
    pos = 8
    keyword_bytes_set = {b"chara", b"ccv3"}  # 跳过所有已存在的角色卡 chunk

    while pos < len(original_data):
        length = struct.unpack(">I", original_data[pos:pos + 4])[0]
        ct = original_data[pos + 4:pos + 8]
        cd = original_data[pos + 8:pos + 8 + length]

        if ct == b"IEND":
            # 在 IEND 之前插入新的 tEXt
            new_png += chunk
            # 重新计算 IEND 的 CRC
            iend_crc = zlib.crc32(b"IEND") & 0xffffffff
            new_png += struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)
            break
        elif ct == b"tEXt" and any(cd.startswith(kw + b"\x00") for kw in keyword_bytes_set):
            # 跳过已有的角色卡 tEXt chunk
            pass
        else:
            # 保留原始 chunk，重新计算 CRC
            crc = zlib.crc32(ct + cd) & 0xffffffff
            new_png += struct.pack(">I", length) + ct + cd + struct.pack(">I", crc)

        pos += 12 + length

    with open(output_path, "wb") as f:
        f.write(new_png)

    return True


def verify_chara_chunk(png_path: str) -> tuple:
    """
    验证 PNG 文件的 tEXt chunk

    Returns:
        (valid: bool, spec: str or None)
    """
    with open(png_path, "rb") as f:
        data = f.read()

    pos = 8
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        chunk_type = data[pos + 4:pos + 8].decode("ascii", errors="replace")
        chunk_data = data[pos + 8:pos + 8 + length]

        if chunk_type == "tEXt":
            try:
                null1 = chunk_data.index(0x00)
                keyword = chunk_data[:null1].decode()
                rest = chunk_data[null1 + 1:]
                if 0x00 in rest:
                    null2 = rest.index(0x00)
                    text = rest[null2 + 1:]

                    if keyword == "chara":
                        decoded = base64.b64decode(text)
                        card = json.loads(decoded)
                        return True, card.get("spec")
            except Exception:
                pass

        pos += 12 + length

    return False, None