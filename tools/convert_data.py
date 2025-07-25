import os
from PIL import Image
import re
from collections import defaultdict

# 设置文件夹路径
folder_path = 'new_dataset'  # 替换为你的图片文件夹路径
output_folder = 'output'           # 拼接后的图片保存路径

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
    size = (286, 286)
    for _, filename in files:
        filepath = os.path.join(folder_path, filename)
        try:
            img = Image.open(filepath)
            img = img.resize(size, Image.Resampling.LANCZOS)  # 高质量 resize
            images.append(img)
        except Exception as e:
            print(f"无法打开或处理 {filename}: {e}")
            break
    else:  # 成功加载三张图
        # 创建拼接图像 (286*3 = 858 宽，286 高)
        combined = Image.new('RGB', (size[0] * 3, size[1]))

        # 从左到右粘贴
        for i, img in enumerate(images):
            combined.paste(img, (i * size[0], 0))

        # 保存为 patient_<id>.png
        output_path = os.path.join(output_folder, f'patient_{patient_id}.png')
        combined.save(output_path)
        print(f"已生成: {output_path}")