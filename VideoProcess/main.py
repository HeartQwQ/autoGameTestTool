from datetime import datetime
from utool import process
log_dir_name = datetime.now().strftime(f"%Y.%m.%d_%H.%M.%S") + ".log"

# ----------------- 主逻辑 -----------------
start_sec = 3 * 60 + 43
end_sec = 6 * 60

process(
    start_sec=start_sec,        # 识别开始时间
    end_sec=end_sec,            # 识别结束时间
    interval=8,                 # 识别间隔
    scope=False,                 # 是否启用识别区域辅助工具
    roi=(93, 498, 305, 330),    # 识别区域
    min_score=0.9,              # 识别阈值
    log_name="仓库到账后",
    log_dir_name=log_dir_name
)
