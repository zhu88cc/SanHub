"""测试 OpenAI 标准格式 API

测试端点:
- POST /v1/videos - 视频生成
- POST /v1/images/generations - 图片生成
- POST /v1/characters - 角色卡创建
"""
import requests
import base64
import os
import json
from pathlib import Path

API_BASE = "http://50.18.90.121:8000"
API_KEY = "sk-test"

# 测试文件路径
TEST_DIR = Path(__file__).parent
TEST_IMAGE = TEST_DIR / "7b20cc1c-38c2-43c9-9437-8d15e55a0fe9.jpeg"
TEST_VIDEO = TEST_DIR / "user-A6c0Wy3wYoslHaYFXXDAATx8_gen_01kaghqtdte07897b971xcphef_watermarked.mp4"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def load_image_base64() -> str:
    """加载测试图片为 base64"""
    if not TEST_IMAGE.exists():
        print(f"❌ 测试图片不存在: {TEST_IMAGE}")
        return None
    with open(TEST_IMAGE, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def load_video_base64() -> str:
    """加载测试视频为 base64"""
    if not TEST_VIDEO.exists():
        print(f"❌ 测试视频不存在: {TEST_VIDEO}")
        return None
    with open(TEST_VIDEO, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ============================================================
# 视频生成测试
# ============================================================

def test_video_json():
    """测试视频生成 (JSON 请求)"""
    print("\n" + "=" * 60)
    print("测试: POST /v1/videos (JSON)")
    print("=" * 60)
    
    response = requests.post(
        f"{API_BASE}/v1/videos",
        headers=headers,
        json={
            "prompt": "A cute cat walking in a beautiful garden",
            "model": "sora-video-10s",
            "style_id": "anime"
        },
        timeout=600  # 10分钟超时
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200 and "data" in result:
        print(f"✅ 视频生成成功!")
        print(f"   URL: {result['data'][0]['url']}")
    else:
        print(f"❌ 视频生成失败")
    
    return result


def test_video_with_image_json():
    """测试图生视频 (JSON 请求 + 参考图片)"""
    print("\n" + "=" * 60)
    print("测试: POST /v1/videos (JSON + 参考图片)")
    print("=" * 60)
    
    image_b64 = load_image_base64()
    if not image_b64:
        print("⚠️ 跳过测试: 无法加载测试图片")
        return None
    
    response = requests.post(
        f"{API_BASE}/v1/videos",
        headers=headers,
        json={
            "prompt": "Make this image come alive with gentle movement",
            "model": "sora-video-10s",
            "input_image": image_b64
        },
        timeout=600
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200 and "data" in result:
        print(f"✅ 图生视频成功!")
        print(f"   URL: {result['data'][0]['url']}")
    else:
        print(f"❌ 图生视频失败")
    
    return result


def test_video_form_data():
    """测试视频生成 (form-data 请求 + 图片文件)"""
    print("\n" + "=" * 60)
    print("测试: POST /v1/videos (form-data + 图片文件)")
    print("=" * 60)
    
    if not TEST_IMAGE.exists():
        print(f"⚠️ 跳过测试: 测试图片不存在")
        return None
    
    with open(TEST_IMAGE, "rb") as f:
        response = requests.post(
            f"{API_BASE}/v1/videos",
            headers={"Authorization": f"Bearer {API_KEY}"},
            data={
                "prompt": "Make this image come alive",
                "model": "sora-video-10s"
            },
            files={
                "input_reference": ("test.jpg", f, "image/jpeg")
            },
            timeout=600
        )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200 and "data" in result:
        print(f"✅ 视频生成成功!")
        print(f"   URL: {result['data'][0]['url']}")
    else:
        print(f"❌ 视频生成失败")
    
    return result


def test_video_remix(remix_id: str = "s_68e3a06dcd888191b150971da152c1f5"):
    """测试 Remix 模式 (仅支持 prompt/model/seconds/orientation)"""
    print("\n" + "=" * 60)
    print(f"测试: POST /v1/videos (Remix 模式: {remix_id})")
    print("=" * 60)
    
    response = requests.post(
        f"{API_BASE}/v1/videos",
        headers=headers,
        json={
            "prompt": "Change to watercolor painting style",
            "model": "sora-video-10s",
            "seconds": "10",
            "orientation": "landscape",
            "remix_target_id": remix_id
        },
        timeout=600
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200 and "data" in result:
        print(f"✅ Remix 视频生成成功!")
        print(f"   URL: {result['data'][0]['url']}")
    else:
        print(f"❌ Remix 视频生成失败")
    
    return result


# ============================================================
# 图片生成测试
# ============================================================

def test_image_json():
    """测试图片生成 (JSON 请求)"""
    print("\n" + "=" * 60)
    print("测试: POST /v1/images/generations (JSON)")
    print("=" * 60)
    
    response = requests.post(
        f"{API_BASE}/v1/images/generations",
        headers=headers,
        json={
            "prompt": "A beautiful sunset over mountains with orange and purple sky",
            "model": "sora-image-landscape",
            "n": 1,
            "response_format": "url"
        },
        timeout=300  # 5分钟超时
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200 and "data" in result:
        print(f"✅ 图片生成成功!")
        print(f"   URL: {result['data'][0]['url']}")
    else:
        print(f"❌ 图片生成失败")
    
    return result


def test_image_with_reference_json():
    """测试图片生成 (JSON 请求 + 参考图片)"""
    print("\n" + "=" * 60)
    print("测试: POST /v1/images/generations (JSON + 参考图片)")
    print("=" * 60)
    
    image_b64 = load_image_base64()
    if not image_b64:
        print("⚠️ 跳过测试: 无法加载测试图片")
        return None
    
    response = requests.post(
        f"{API_BASE}/v1/images/generations",
        headers=headers,
        json={
            "prompt": "Transform this into a watercolor painting style",
            "model": "sora-image-landscape",
            "input_image": image_b64
        },
        timeout=300
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200 and "data" in result:
        print(f"✅ 图片生成成功!")
        print(f"   URL: {result['data'][0]['url']}")
    else:
        print(f"❌ 图片生成失败")
    
    return result


def test_image_form_data():
    """测试图片生成 (form-data 请求 + 图片文件)"""
    print("\n" + "=" * 60)
    print("测试: POST /v1/images/generations (form-data + 图片文件)")
    print("=" * 60)
    
    if not TEST_IMAGE.exists():
        print(f"⚠️ 跳过测试: 测试图片不存在")
        return None
    
    with open(TEST_IMAGE, "rb") as f:
        response = requests.post(
            f"{API_BASE}/v1/images/generations",
            headers={"Authorization": f"Bearer {API_KEY}"},
            data={
                "prompt": "A beautiful landscape",
                "model": "sora-image-landscape"
            },
            files={
                "input_reference": ("test.jpg", f, "image/jpeg")
            },
            timeout=300
        )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200 and "data" in result:
        print(f"✅ 图片生成成功!")
        print(f"   URL: {result['data'][0]['url']}")
    else:
        print(f"❌ 图片生成失败")
    
    return result


# ============================================================
# 角色卡创建测试
# ============================================================

def test_character_json():
    """测试角色卡创建 (JSON 请求)"""
    print("\n" + "=" * 60)
    print("测试: POST /v1/characters (JSON)")
    print("=" * 60)
    
    video_b64 = load_video_base64()
    if not video_b64:
        print("⚠️ 跳过测试: 无法加载测试视频")
        return None
    
    response = requests.post(
        f"{API_BASE}/v1/characters",
        headers=headers,
        json={
            "model": "sora-video-10s",
            "video": video_b64,
            "timestamps": "0,3",
            "username": "test_character",
            "display_name": "测试角色"
        },
        timeout=600
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200 and "data" in result:
        print(f"✅ 角色卡创建成功!")
        if "cameo_id" in result.get("data", {}):
            print(f"   Cameo ID: {result['data']['cameo_id']}")
    else:
        print(f"❌ 角色卡创建失败")
    
    return result


def test_character_form_data():
    """测试角色卡创建 (form-data 请求 + 视频文件)"""
    print("\n" + "=" * 60)
    print("测试: POST /v1/characters (form-data + 视频文件)")
    print("=" * 60)
    
    if not TEST_VIDEO.exists():
        print(f"⚠️ 跳过测试: 测试视频不存在")
        return None
    
    with open(TEST_VIDEO, "rb") as f:
        response = requests.post(
            f"{API_BASE}/v1/characters",
            headers={"Authorization": f"Bearer {API_KEY}"},
            data={
                "model": "sora-video-10s",
                "timestamps": "0,3",
                "username": "test_char_form",
                "display_name": "测试角色Form"
            },
            files={
                "video": ("test.mp4", f, "video/mp4")
            },
            timeout=600
        )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200 and "data" in result:
        print(f"✅ 角色卡创建成功!")
        if "cameo_id" in result.get("data", {}):
            print(f"   Cameo ID: {result['data']['cameo_id']}")
    else:
        print(f"❌ 角色卡创建失败")
    
    return result


# ============================================================
# 使用角色生成视频测试 (在 prompt 中使用 @username)
# ============================================================

def test_video_with_character(username: str):
    """测试使用角色生成视频 (在 prompt 中使用 @username)"""
    print("\n" + "=" * 60)
    print(f"测试: POST /v1/videos (使用角色: @{username})")
    print("=" * 60)
    
    response = requests.post(
        f"{API_BASE}/v1/videos",
        headers=headers,
        json={
            "prompt": f"@{username} walking happily in a park",
            "model": "sora-video-10s"
        },
        timeout=600
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200 and "data" in result:
        print(f"✅ 角色视频生成成功!")
        print(f"   URL: {result['data'][0]['url']}")
    else:
        print(f"❌ 角色视频生成失败")
    
    return result


# ============================================================
# 主函数
# ============================================================

def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("OpenAI 标准格式 API 测试")
    print("=" * 60)
    print(f"API 地址: {API_BASE}")
    print(f"测试图片: {TEST_IMAGE} (存在: {TEST_IMAGE.exists()})")
    print(f"测试视频: {TEST_VIDEO} (存在: {TEST_VIDEO.exists()})")
    
    # 图片生成测试
    print("\n\n>>> 图片生成测试 <<<")
    test_image_json()
    
    # 视频生成测试
    print("\n\n>>> 视频生成测试 <<<")
    test_video_json()
    
    # 角色卡创建测试
    print("\n\n>>> 角色卡创建测试 <<<")
    result = test_character_json()
    
    # 如果角色卡创建成功，测试使用角色生成视频
    if result and result.get("data", {}).get("username"):
        username = result["data"]["username"]
        print("\n\n>>> 使用角色生成视频测试 <<<")
        test_video_with_character(username)


def run_quick_test():
    """快速测试 (仅测试基本功能)"""
    print("\n" + "=" * 60)
    print("OpenAI 标准格式 API 快速测试")
    print("=" * 60)
    
    # 只测试图片生成
    test_image_json()


if __name__ == "__main__":
    import sys
    
    help_text = """
用法: python test_openai_api.py <测试名称>

可用测试:
  video           - 视频生成 (JSON)
  video-image     - 图生视频 (JSON + 参考图片)
  video-form      - 图生视频 (form-data + 图片文件)
  video-remix     - Remix 模式 (仅 prompt/model/seconds/orientation)
  image           - 图片生成 (JSON)
  image-ref       - 图片生成 (JSON + 参考图片)
  image-form      - 图片生成 (form-data + 图片文件)
  character       - 角色卡创建 (JSON + base64 视频)
  character-form  - 角色卡创建 (form-data + 视频文件)
  quick           - 快速测试 (仅图片生成)
  all             - 运行所有测试

示例:
  python test_openai_api.py image
  python test_openai_api.py video
  python test_openai_api.py all
"""
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        if test_name == "video":
            test_video_json()
        elif test_name == "video-image":
            test_video_with_image_json()
        elif test_name == "video-form":
            test_video_form_data()
        elif test_name == "video-remix":
            remix_id = sys.argv[2] if len(sys.argv) > 2 else "s_68e3a06dcd888191b150971da152c1f5"
            test_video_remix(remix_id)
        elif test_name == "image":
            test_image_json()
        elif test_name == "image-ref":
            test_image_with_reference_json()
        elif test_name == "image-form":
            test_image_form_data()
        elif test_name == "character":
            test_character_json()
        elif test_name == "character-form":
            test_character_form_data()
        elif test_name == "quick":
            run_quick_test()
        elif test_name == "all":
            run_all_tests()
        else:
            print(f"未知测试: {test_name}")
            print(help_text)
    else:
        print(help_text)
