import cv2

tpl = cv2.imread('13.png')  # 模板
color = cv2.imread('14.png')  # 实拍图
scene = color.copy()

# 1. 模板匹配
res = cv2.matchTemplate(scene, tpl, cv2.TM_CCOEFF_NORMED)
_, maxv, _, maxloc = cv2.minMaxLoc(res)

print('最大匹配得分:', maxv)
if maxv < 0.35:                 # 经验阈值，可自行调
    cv2.putText(color, 'Template not found!', (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow('result', color)
    cv2.waitKey(0)
    exit()

h, w = tpl.shape[:2]
x, y = maxloc
roi = scene[y:y + h, x:x + w]  # 在实拍图里抠出对应区域

# 2. 差异检测（同尺寸了，不用再 resize）
gray1 = cv2.cvtColor(tpl, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
diff = cv2.absdiff(gray1, gray2)
_, thr = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
thr = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel)

cv2.imshow('1.match', cv2.rectangle(color.copy(), (x, y), (x+w, y+h), (0, 0, 255), 2))

cv2.waitKey(0)