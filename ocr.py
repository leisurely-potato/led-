import cv2
import pytesseract

image = cv2.imread('/home/zyy/yyc/test_led/172.22.5.55_region_0_corrected.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# 可选：增强对比度或二值化
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# 指定只识别数字
custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
result = pytesseract.image_to_string(thresh, config=custom_config)
print(result)
