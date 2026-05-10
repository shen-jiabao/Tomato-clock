from PIL import Image, ImageDraw
import os

os.makedirs('assets', exist_ok=True)

img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# 粉红色圆圈
d.ellipse([10, 10, 246, 246], fill=(242, 95, 120, 255))

# 白色内圈
d.ellipse([30, 30, 226, 226], fill=(255, 255, 255, 200))

sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
imgs = [img.resize(s, Image.LANCZOS) for s in sizes]
imgs[0].save('assets/icon.ico', format='ICO', sizes=sizes)
print('Icon created successfully')
