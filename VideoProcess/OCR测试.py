
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    text_detection_model_name="PP-OCRv5_mobile_det",
    device="gpu",
)

result = ocr.predict("./1.png")

for res in result:
    res.save_to_img("output")
    res.save_to_json("output")
    for text, score, box in zip(res['rec_texts'], res['rec_scores'], res['rec_boxes']):
        print(text, score)