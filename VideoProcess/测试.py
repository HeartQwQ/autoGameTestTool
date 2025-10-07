import cv2
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)
# 自备一张图片在同级目录下
result = ocr.predict("./1.jpg")  # 图片名称要一致
for res in result:
    res.print()
    res.save_to_img("output")
    res.save_to_json("output")
    # 3-1 文字 & 置信度
    texts   = res["rec_texts"]        # List[str]
    scores  = res["rec_scores"]       # List[float]
    # 3-2 矩形框（左上右下）
    boxes   = res["rec_boxes"]        # List[List[int]]

    cv2.polylines(img, [pts], isClosed=True, color=(0, 0, 255), thickness=2)

    # 4. 遍历每条结果
    for text, score, box in zip(texts, scores,boxes):
        print(f"文案：{text}  置信度：{score:.3f}")