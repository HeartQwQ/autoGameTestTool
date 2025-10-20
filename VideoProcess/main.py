from utils.VideoProcess import VideoProcess
from stages.仓库到账前 import exchange_shop_before
from stages.兑换前碎片 import exchange_shop_exchange_before
from stages.兑换中弹窗 import exchange_shop_exchange_middle
from stages.恭喜获得 import exchange_shop_congratulation
from stages.兑换后碎片 import exchange_shop_exchange_after
from stages.仓库到账后 import exchange_shop_after


if __name__ == "__main__":
    config = {
        "video_path": "1.mp4",      # 视频文件名，放在项目根目录下
        "data_path": "data.json",   # 数据文件名，放在项目根目录下
        "redeem_shards": 10000,     # 初始兑换碎片数量
        "target_fps": 3,            # 每秒识别3张
        "hamming_threshold": 120,   # 汉明距离，值越大，判断的差异越大，太大可能误判
        "hash_size": 32,            # pHash 精度（8/16/32，越大越准但慢）
        "ocr": {
            "use_doc_orientation_classify": False,                  # 不使用文档方向分类
            "use_doc_unwarping": False,                             # 不使用文档扭曲矫正
            "use_textline_orientation": False,                      # 不使用文本行方向分类
            "text_recognition_batch_size": 64,                      # OCR识别批次大小, 越大越快但显存占用越高
            # 文本检测模型, 推荐 v5_mobile 速度更快，精度损失不大
            "text_detection_model_name": "PP-OCRv5_mobile_det",
            # OCR识别模型, 推荐 v5_server 速度损失不多，但精度更高
            "text_recognition_model_name": "PP-OCRv5_server_rec",
            "text_rec_score_thresh": 0.9,                           # OCR最小分数
        },
        "stages": [
            {
                "name": "仓库到账前",
                "fun": exchange_shop_before,
            },
            {
                "name": "兑换前碎片",
                "fun": exchange_shop_exchange_before,
            },
            {
                "name": "兑换中弹窗",
                "fun": exchange_shop_exchange_middle,
            },
            {
                "name": "恭喜获得",
                "fun": exchange_shop_congratulation,
            },
            {
                "name": "兑换后碎片",
                "fun": exchange_shop_exchange_after,
            },
            {
                "name": "仓库到账后",
                "fun": exchange_shop_after,
            }
        ]
    }

    VideoProcess(config).video_ocr()
