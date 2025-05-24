import cv2
import numpy as np
import os

def Iswhite(image, y1, y2, x1, x2):
    """判断指定区域是否为白色（亮）"""
    # 边界检查
    if len(image.shape) == 0 or image.shape[0] == 0 or image.shape[1] == 0:
        return False, 0.0
    
    # 确保索引在有效范围内
    y1 = max(0, min(int(y1), image.shape[0] - 1))
    y2 = max(0, min(int(y2), image.shape[0] - 1))
    x1 = max(0, min(int(x1), image.shape[1] - 1))
    x2 = max(0, min(int(x2), image.shape[1] - 1))
    
    if y1 >= y2 or x1 >= x2:
        return False, 0.0
    
    roi = image[y1:y2, x1:x2]
    if roi.size == 0:
        return False, 0.0
    
    # 使用像素值为255的像素计数来判断
    white_pixels = np.sum(roi > 180)
    total_pixels = roi.size
    
    # 计算白色像素比例
    white_ratio = white_pixels / total_pixels if total_pixels > 0 else 0
    is_white = white_ratio > 0.3
    
    return is_white, white_ratio

def TubeIdentification(num, image):
    """七段数码管识别函数"""
    tube = 0
    height, width = image.shape[:2]
    
    # 如果是灰度图，转换为彩色图以便显示彩色标注
    if len(image.shape) == 2:
        image_annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        image_annotated = image.copy()
    
    # 改进的七段数码管ROI定义
    # 横段：只取中间50%的横坐标范围
    # 竖段：只取中间50%的纵坐标范围
    tubo_roi = [
        # 段 a (顶部横段) - 横段，纵坐标保持，横坐标取中间50%
        [height * 0.05, height * 0.25, width * 0.25, width * 0.75],
        # 段 b (右上竖段) - 竖段，横坐标保持，纵坐标取中间50%
        [height * 0.125, height * 0.375, width * 0.7, width * 0.95],
        # 段 c (右下竖段) - 竖段，横坐标保持，纵坐标取中间50%
        [height * 0.625, height * 0.875, width * 0.7, width * 0.95],
        # 段 d (底部横段) - 横段，纵坐标保持，横坐标取中间50%
        [height * 0.75, height * 0.95, width * 0.25, width * 0.75],
        # 段 e (左下竖段) - 竖段，横坐标保持，纵坐标取中间50%
        [height * 0.625, height * 0.875, width * 0.05, width * 0.3],
        # 段 f (左上竖段) - 竖段，横坐标保持，纵坐标取中间50%
        [height * 0.125, height * 0.375, width * 0.05, width * 0.3],
        # 段 g (中间横段) - 横段，纵坐标保持，横坐标取中间50%
        [height * 0.4, height * 0.6, width * 0.25, width * 0.75],
    ]
    
    segment_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    
    print(f"\n数字 {num+1} 的段检测结果:")
    
    # 检测每个段是否亮起
    for i in range(7):
        # 使用原始灰度图进行检测
        original_image = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        is_white, white_ratio = Iswhite(original_image, tubo_roi[i][0], tubo_roi[i][1], tubo_roi[i][2], tubo_roi[i][3])
        
        print(f"  段 {segment_names[i]}: 白色像素比例 {white_ratio:.3f}, 状态: {'亮' if is_white else '暗'}")
        
        if is_white:
            tube = tube + pow(2, i)
        
        # 在彩色图上用黑色框标出每段的检测区域
        cv2.rectangle(
            image_annotated,
            (int(tubo_roi[i][2]), int(tubo_roi[i][0])),
            (int(tubo_roi[i][3]), int(tubo_roi[i][1])),
            (0, 0, 0),  # 黑色框 (BGR格式)
            2,
        )
        
        # 在矩形中心添加段名称标签（白色文字）
        center_x = int((tubo_roi[i][2] + tubo_roi[i][3]) / 2)
        center_y = int((tubo_roi[i][0] + tubo_roi[i][1]) / 2)
        cv2.putText(image_annotated, segment_names[i], (center_x-5, center_y+5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # 数字识别 (0-9)
    digit_patterns = {
        63: 0,   # 1111110 (a,b,c,d,e,f)
        6: 1,    # 0000110 (b,c)
        91: 2,   # 1011011 (a,b,d,e,g)
        79: 3,   # 1001111 (a,b,c,d,g)
        102: 4,  # 1100110 (b,c,f,g)
        110: 4,  # 带干扰的4
        109: 5,  # 1101101 (a,c,d,f,g)
        125: 6,  # 1111101 (a,c,d,e,f,g)
        7: 7,    # 0000111 (a,b,c)
        127: 8,  # 1111111 (a,b,c,d,e,f,g)
        111: 8,  # 带干扰的8
        103: 9,  # 1100111 (a,b,c,d,f,g)
    }
    
    # 字母识别 (a-z)
    letter_patterns = {
        119: "a", # 1110111 (a,b,c,e,f,g)
        124: "b", # 1111100 (c,d,e,f,g)
        57: "c",  # 0111001 (a,d,e,f)
        94: "d",  # 1011110 (b,c,d,e,g)
        121: "e", # 1111001 (a,d,e,f,g)
        113: "f", # 1110001 (a,e,f,g)
        61: "g",  # 0111101 (a,c,d,e,f)
        116: "h", # 1110100 (b,c,e,f,g)
        118: "h", # 备选h
        4: "i",   # 0000100 (c)
        14: "j",  # 0001110 (b,c,d,e)
        30: "j",  # 备选j
        56: "l",  # 0111000 (d,e,f)
        84: "n",  # 1010100 (c,e,g)
        92: "o",  # 1011100 (c,d,e,g)
        115: "p", # 1110011 (a,b,e,f,g)
        67: "q",  # 1000011 (a,b,f,g)
        80: "r",  # 1010000 (e,g)
        109: "s", # 同5
        120: "t", # 1111000 (d,e,f,g)
        28: "u",  # 0011100 (c,d,e)
        62: "u",  # 备选u
        28: "v",  # 0011100 (c,d,e)
        42: "w",  # 0101010 (近似)
        118: "x", # 1110110 (b,c,e,f,g)
        110: "y", # 1101110 (b,c,d,f,g)
        91: "z",  # 同2
    }
    print(f"识别的数码管段值: {tube:07b} (十进制: {tube})")
    
    # 首先尝试数字识别
    if tube in digit_patterns:
        onenumber = digit_patterns[tube]
    # 然后尝试字母识别
    elif tube in letter_patterns:
        onenumber = letter_patterns[tube]
    else:
        onenumber = -1

    return onenumber, image_annotated

def parse_data_labels(data_labels_text):
    """解析数据标识文本，返回每个数字的四个角点坐标"""
    lines = data_labels_text.strip().split('\n')
    digit_coords = []
    
    for line in lines:
        coords = list(map(int, line.split()))
        if len(coords) >= 9:
            # 提取x1,y1,x2,y2,x3,y3,x4,y4 (忽略第一个数字)
            points = []
            for i in range(1, 9, 2):
                points.append([coords[i], coords[i+1]])
            digit_coords.append(np.array(points, dtype=np.float32))
    
    return digit_coords

def perspective_transform(image, src_points, width=100, height=150):
    """透视变换校正数字区域"""
    # 目标矩形的四个角点（标准正视图）
    dst_points = np.array([
        [0, 0],
        [width-1, 0],
        [width-1, height-1],
        [0, height-1]
    ], dtype=np.float32)
    
    # 计算透视变换矩阵
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    
    # 应用透视变换
    corrected = cv2.warpPerspective(image, matrix, (width, height))
    
    return corrected

def format_result(digits, data_type):
    """根据数据类型格式化识别结果"""
    # 过滤掉值为-1的数字
    valid_digits = [d for d in digits if d != -1]
    
    if not valid_digits:
        return "识别失败"
    
    if data_type == "字母":
        return ''.join(str(d) for d in valid_digits)
    elif data_type == "数字一位小数":
        if len(valid_digits) >= 2:
            integer_part = ''.join(str(d) for d in valid_digits[:-1] if isinstance(d, int))
            decimal_part = str(valid_digits[-1]) if isinstance(valid_digits[-1], int) else '0'
            return f"{integer_part}.{decimal_part}"
        elif len(valid_digits) == 1:
            return f"0.{valid_digits[0]}" if isinstance(valid_digits[0], int) else "0.0"
        else:
            return "0.0"
    elif data_type == "数字两位小数":
        if len(valid_digits) >= 3:
            integer_part = ''.join(str(d) for d in valid_digits[:-2] if isinstance(d, int))
            decimal_part = ''.join(str(d) for d in valid_digits[-2:] if isinstance(d, int))
            return f"{integer_part}.{decimal_part}"
        elif len(valid_digits) == 2:
            decimal_part = ''.join(str(d) for d in valid_digits if isinstance(d, int))
            return f"0.{decimal_part}"
        elif len(valid_digits) == 1:
            return f"0.0{valid_digits[0]}" if isinstance(valid_digits[0], int) else "0.00"
        else:
            return "0.00"
    else:
        return ''.join(str(d) for d in valid_digits)

def read_data_labels_from_file(file_path):
    """从txt文件读取数据标识"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"数据标识文件不存在: {file_path}")
    except Exception as e:
        raise ValueError(f"读取数据标识文件失败: {e}")

def seven_segment_recognition(image_path, data_labels_input, data_type):
    """主函数：七段数码管识别"""
    # 1. 加载图片并灰度化
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"无法加载图片: {image_path}")
    
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. 解析数据标识（支持文件路径或直接文本）
    if os.path.isfile(data_labels_input):
        data_labels_text = read_data_labels_from_file(data_labels_input)
        print(f"从文件读取数据标识: {data_labels_input}")
    else:
        data_labels_text = data_labels_input
        print("使用直接提供的数据标识文本")
    
    digit_coords = parse_data_labels(data_labels_text)
    
    if not digit_coords:
        raise ValueError("数据标识解析失败")
    
    # 3. 识别每个数字
    results = []
    corrected_images = []
    
    for i, coords in enumerate(digit_coords):
        # 透视变换校正
        corrected = perspective_transform(gray_image, coords)
        corrected_images.append(corrected)
        
        # 识别数字（这里会打印段检测信息）并获取带标注的图像
        digit, annotated_image = TubeIdentification(i, corrected.copy())
        results.append(digit)
        
        # 保存带有段标注的校正图片（黑色框标注）
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        corrected_path = f"/home/zyy/yyc/test_led/{base_name}_corrected_{i}_segments.png"
        cv2.imwrite(corrected_path, annotated_image)
        print(f"已保存带段标注的图片: {corrected_path}")
        
        if digit == -1:
            print(f"数字 {i+1}: 识别失败 (跳过)")
        else:
            print(f"数字 {i+1}: {digit}")
    
    # 4. 格式化结果
    final_result = format_result(results, data_type)
    
    # 显示有效数字信息
    valid_digits = [d for d in results if d != -1]
    print(f"\n有效识别数字: {valid_digits}")
    print(f"跳过的数字个数: {len(results) - len(valid_digits)}")
    
    return final_result, results, corrected_images

# 测试代码
def test_recognition():
    """测试函数"""
    # 示例数据
    image_path = "172.22.5.55.jpg"
    
    # 使用txt文件作为数据标识
    data_labels_file = "gauge.txt"
    
    data_type = "数字一位小数"
    
    try:
        # 执行识别
        result, individual_results, corrected_images = seven_segment_recognition(
            image_path, data_labels_file, data_type
        )
        
        print(f"识别结果: {result}")
        print(f"各位数字: {individual_results}")
        print(f"数据类型: {data_type}")
        
        return result
        
    except Exception as e:
        print(f"识别失败: {e}")
        return None

# def create_sample_data_labels():
#     """创建示例数据标识文件"""
#     sample_content = """1 100 50 200 50 200 200 100 200
# 2 250 50 350 50 350 200 250 200"""
    
#     sample_file_path = "/home/zyy/yyc/test_led/data_labels.txt"
    
#     with open(sample_file_path, 'w', encoding='utf-8') as f:
#         f.write(sample_content)
    
#     print(f"示例数据标识文件已创建: {sample_file_path}")
#     return sample_file_path

if __name__ == "__main__":
    # 创建示例数据标识文件
    # create_sample_data_labels()
    
    # 运行测试
    test_recognition()
    
    # 使用示例
    print("\n=== 使用示例 ===")
    print("1. 准备jpg格式的图片")
    print("2. 准备数据标识txt文件（每行9个数字，空格分隔）")
    print("3. 指定数据类型：'字母'、'数字一位小数'、'数字两位小数'")
    print("4. 调用 seven_segment_recognition(image_path, data_labels_file_path, data_type)")
    print("   或 seven_segment_recognition(image_path, data_labels_text_string, data_type)")
