import os
from PIL import Image
import re
from collections import defaultdict

# 设置文件夹路径
folder_path = 'new_dataset'  # 替换为你的图片文件夹路径
output_folder = 'train'     # 拼接后的图片保存路径

# 创建输出文件夹
os.makedirs(output_folder, exist_ok=True)

# 正则表达式匹配文件名：patient_<id>_<num>.png
pattern = re.compile(r'patient_(\d+)_(\d+)\.png')

# 按 id 分组文件
images_dict = defaultdict(list)

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    match = pattern.match(filename)
    if match:
        patient_id = match.group(1)
        img_num = int(match.group(2))
        if 1 <= img_num <= 3:  # 只处理 _1, _2, _3
            images_dict[patient_id].append((img_num, filename))

# 处理每一个 patient_id
for patient_id, files in images_dict.items():
    # 按序号排序，确保 1, 2, 3 顺序
    files.sort(key=lambda x: x[0])
    nums = [f[0] for f in files]

    # 必须有 1, 2, 3 三张图
    if nums != [1, 2, 3]:
        print(f"Warning: patient_{patient_id} 缺少完整的 1/2/3 图片，跳过。")
        continue

    # 准备拼接图像
    images = []
    size = (256, 256)

    # 定义每张图的转换模式
    convert_modes = {
        1: 'L',      # 第1张：灰度
        2: 'RGB',    # 第2张：彩色
        3: 'L'       # 第3张：灰度
    }

    success = True
    for img_num, filename in files:
        filepath = os.path.join(folder_path, filename)
        # print(f"正在处理: {filepath}")
        try:
            img = Image.open(filepath).convert(convert_modes[img_num])  # 按要求转换
            img = img.resize(size, Image.Resampling.LANCZOS)

            # 如果是 'L' 模式（灰度），转换为 RGB 以便拼接（避免粘贴时模式不匹配）
            if img.mode == 'L':
                img = img.convert('RGB')

            images.append(img)
        except Exception as e:
            print(f"无法打开或处理 {filename}: {e}")
            success = False
            break

    if success and len(images) == 3:
        # 创建拼接图像 (768 x 256)
        combined = Image.new('RGB', (size[0] * 3, size[1]))

        # 从左到右粘贴
        for i, img in enumerate(images):
            combined.paste(img, (i * size[0], 0))

        # 保存为 patient_<id>.png
        output_path = os.path.join(output_folder, f'patient_{patient_id}.png')
        combined.save(output_path)
        print(f"已生成: {output_path}")