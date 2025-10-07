from utool import process
from datetime import datetime
log_dir_name = datetime.now().strftime(f"%Y.%m.%d_%H.%M.%S") + ".log"

# ----------------- 主逻辑 -----------------
start_sec = 3 * 60 + 43
end_sec = 6 * 60

# 附加条件
ifs = [
    {
        "文案": "恭喜获得",
        "识别范围": (1776, 75, 138, 684)
    },
]

process(
    start_sec=start_sec,
    end_sec=end_sec,
    interval=8,
    # scope=True,
    # roi=(93, 498, 305, 330),
    log_name="仓库到账后",
    log_dir_name=log_dir_name,
    # ifs=ifs,
)
