import sys
import cv2
import io
from pathlib import Path
from paddleocr import PaddleOCR

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = sys.argv[1]

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)
img = cv2.imread(file_path)

result = ocr.predict(file_path)

for res in result:
    for text, score, box in zip(res["rec_texts"], res["rec_scores"], res["rec_boxes"]):
        x1, y1, x2, y2 = box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

out_path = Path(file_path).with_name(Path(file_path).stem + '_boxed.jpg')
cv2.imwrite(out_path, img)
sys.stdout.write(str(out_path) + '\n')
sys.stdout.flush()