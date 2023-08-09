from collections import Counter
import colorsys
import math
from PIL import Image, ImageDraw, ImageFont



# 定义一个函数，输入一个十六进制的颜色值，返回它的十进制数值或原值
def getRGB(c):
  try:
    return int(c, 16)
  except ValueError:
    return c

# 定义一个函数，输入一个十六进制的颜色值，返回它的sRGB值
def getsRGB(c):
  return getRGB(c) / 255 / 12.92 if getRGB(c) / 255 <= 0.03928 else ((getRGB(c) / 255 + 0.055) / 1.055) ** 2.4

# 定义一个函数，输入一个十六进制的颜色值，返回它的亮度值
def get_luminance(hexColor):
  return (
    0.2126 * getsRGB(hexColor[1:3]) +
    0.7152 * getsRGB(hexColor[3:5]) +
    0.0722 * getsRGB(hexColor[-2:])
  )

# 定义一个函数，输入两个十六进制的颜色值，返回它们的对比度
def get_contrast(f, b):
  L1 = get_luminance(f)
  L2 = get_luminance(b)
  return (max(L1, L2) + 0.05) / (min(L1, L2) + 0.05)

# 定义一个函数，输入一个十六进制的背景颜色值，返回一个合适的文本颜色值
def getTextColor(bgColor):
  white_contrast = get_contrast(bgColor, '#ffffff')
  black_contrast = get_contrast(bgColor, '#000000')

  return (255, 255, 255) if white_contrast > black_contrast else (0, 0, 0)


def get_main_color(img):
    # 将图片转换为RGB模式
    # 获取图片的像素数据
    pixels = img.convert("RGB").getdata()
    # 统计每种颜色出现的次数
    counts = Counter(pixels)
    # 按照出现次数降序排序
    counts = counts.most_common()
    # 获取最主要的颜色和第二主要的颜色
    main_color = counts[0][0]
    sencond_color = counts[1][0]

    return main_color, sencond_color


# 定义一个函数，输入一个RGB颜色，返回它的反差色
def get_complementary_color(color):
  # 将RGB颜色转换为HSL颜色
  h, s, l = colorsys.rgb_to_hls(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
  # 计算反差色的色相值，即在色轮上旋转180度
  h_complementary = (h + 0.5) % 1
  # 将HSL颜色转换为RGB颜色
  r, g, b = colorsys.hls_to_rgb(h_complementary, l, s)
  # 将RGB颜色乘以255并取整数
  r = int(r * 255.0)
  g = int(g * 255.0)
  b = int(b * 255.0)
  # 返回反差色
  return (r, g, b)

# 定义一个函数，用于将文字分割成多行
def split_text(text, font, W):
    lines = []
    line = ""
    for word in text:
        bbox = font.getbbox(line + word)
        # if font.getsize(line + word)[0] > W:
        if bbox[2] - bbox[0] > W:
            lines.append(line)
            line = ""
        line += word
    if line:
        lines.append(line)
    return lines


# 创建缩略图，返回文件名（不包含路径）
def thumbnail(fullpath: str, W: int, H: int):
    # 打开一张图片
    img = Image.open(fullpath)
    width, height = img.size
    # 如果图片宽高大于1440x1920，则resize到这个尺寸
    if width > W or height > H:
        asked_width = (width * H) // height
        asked_height = (height * W) // width

        # thumbnail 会保持住宽高比
        # resize方法不会保持，需要自己手动计算
        img.thumbnail((asked_width, asked_height), Image.ANTIALIAS)

        name = '.'.join(fullpath.split('.')[:-1])
        # 文件名后缀
        ext = fullpath.split('.')[-1]
        new_fullpath = f"{name}_thumbnail.{ext}"
        # 保存合并后的图片
        img.save(new_fullpath)

        return True, new_fullpath.split('/')[-1]
    
    return False, fullpath.split('/')[-1]

# 图片默认的最大宽高
MAX_WIDTH = 1440
MAX_HEIGHT = 1920

def get_font_list(mode):
    fontname = "PingFang.ttc"
    if mode == 'title':
        # title_fontname = "OPPOSans-H.ttf"
        title_fontname = "PingFang.ttc"
        main_font = ImageFont.truetype(title_fontname, 128) # 用苹果的中文字体
        guluart_font = ImageFont.truetype(fontname, 24) # 用苹果的中文字体
        suffix_font = ImageFont.truetype(fontname, 20) # 用苹果的中文字体
    else:
        main_font = ImageFont.truetype(fontname, 32) # 用苹果的中文字体
        guluart_font = ImageFont.truetype(fontname, 24) # 用苹果的中文字体
        suffix_font = ImageFont.truetype(fontname, 20) # 用苹果的中文字体

    return main_font, guluart_font, suffix_font

# caption 有5个方向
# 居中、上方、下方、左边、右边
# mode 有水印、标题
def compose_image_with_watermark(filename, caption, 
                                 mode='watermark', 
                                 position='bottom', 
                                 W=MAX_WIDTH, 
                                 H=MAX_HEIGHT):
    name = '.'.join(filename.split('.')[:-1])
    # 文件名后缀
    ext = filename.split('.')[-1]

    # 打开一张图片
    img = Image.open(filename)

    main_color, sencond_color = get_main_color(img)
    # complementary_color = get_complementary_color(main_color)
    # print(main_color)
    # print(complementary_color)

    # 获取图片的宽高
    width, height = img.size

    # 如果图片宽高大于1440x1920，则resize到这个尺寸
    if width > W or height > H:
        asked_width = (width * H) // height
        asked_height = (height * W) // width

        # thumbnail 会保持住宽高比
        # resize方法不会保持，需要自己手动计算
        img.thumbnail((asked_width, asked_height), Image.ANTIALIAS)

        # 重新获取图片的宽高
        width, height = img.size

    # 定义水印的文字，字体，大小，颜色和透明度
    text = caption
    # font = ImageFont.truetype("PingFang.ttc", 32) # 用苹果的中文字体
    # guluart_font = ImageFont.truetype("PingFang.ttc", 24) # 用苹果的中文字体
    # guluart_suffix_font = ImageFont.truetype("PingFang.ttc", 20) # 用苹果的中文字体

    font, guluart_font, guluart_suffix_font = get_font_list(mode)
    # color = (255, 255, 255, 230) # 白色，透明度为0.9
    # opacity = 0.9

    # 将文字分割成多行，以适应图片的宽度
    # 两边留白
    text_padding = 32
    lines = split_text(text, font, img.width - text_padding * 2)

    offset = 6 # 行间距
    # 计算每行文字的高度和总高度
    # line_height = font.getsize(" ")[1]
    bbox = font.getbbox(lines[0])
    line_height = bbox[3] - bbox[1] + offset
    total_height = line_height * (len(lines) + 1) # 最底部固定输出 "古鹿珠宝"

    watermark_height = total_height + 32

    # 计算水印的位置，使其居中于图片底部
    # x = (img.width - font.getsize(lines[0])[0]) // 2 # 水平居中
    # bbox = font.getbbox(lines[0])
    if position == 'right_center':
        # 右边，垂直居中
        x = img.width - (bbox[2] - bbox[0]) # 水平居右
        y = (img.height - watermark_height) // 2 # 垂直居中
    else:
        x = (img.width - (bbox[2] - bbox[0])) // 2 # 水平居中
        y = img.height - watermark_height # 距离底部12像素

    # watermark_height = total_height + 12
    # 在水印图片上逐行绘制文字
    # 创建一个新的图片，用于存放水印
    watermark = Image.new("RGBA", (width, watermark_height))

    # 创建一个绘图对象，用于在水印图片上绘制文字
    draw = ImageDraw.Draw(watermark)

    # 图片主色调、半透明的背景
    watermark_bg = Image.new("RGBA", (width, watermark_height), main_color + (128,))
    # layer和原始图片大小一致
    layer = Image.new('RGBA', (width, height))
    layer.paste(watermark_bg, (0, y))
    # 将水印图片和原图片合并，这里是为了获取水印文字的背景颜色
    img_temp = Image.alpha_composite(img.convert("RGBA"), layer)
    img_crop = img_temp.crop((0, y, width, y + watermark_height))

    # img_crop.convert("RGB").save(f"{name}_crop.{ext}")

    watermark_bg_color, _ = get_main_color(img_crop)
    # print(watermark_bg_color)

    # main_color后面要加半透明，这里的text_color可能不准确
    text_color = getTextColor('#%02x%02x%02x' % (watermark_bg_color[0], watermark_bg_color[1], watermark_bg_color[2]))
    # print(text_color)

    watermark_y = 2
    # complementary_color = get_complementary_color(main_color)
    for line in lines:
        if mode == 'title':
            draw.text((x, watermark_y), line, fill=text_color, font=font, stroke_width=8, stroke_fill=main_color)
        else:
            draw.text((x, watermark_y), line, fill=text_color, font=font)
        watermark_y += line_height

    # 底部居中 guluart 文字    
    guluart = '古鹿™️珠宝'
    guluart_suffix = '整理'

    bbox = guluart_font.getbbox(guluart)
    guluart_x = (img.width - (bbox[2] - bbox[0])) // 2 # 水平居中
    guluart_suffix_x = guluart_x + (bbox[2] - bbox[0]) + 8
    watermark_y += 16
    draw.text((guluart_x, watermark_y), guluart, fill=text_color, font=guluart_font)
    draw.text((guluart_suffix_x, watermark_y + 4), guluart_suffix, fill=text_color + (156,), font=guluart_suffix_font)

    # # 图片主色调、半透明的背景
    # watermark_bg = Image.new("RGBA", (width, watermark_height), main_color + (128,))
    # 文字叠加到半透明背景上
    watermark = Image.alpha_composite(watermark_bg, watermark)

    layer = Image.new('RGBA', (width, height))
    layer.paste(watermark, (0, y))

    # 将水印图片和原图片合并
    img = Image.alpha_composite(img.convert("RGBA"), layer)
    # img.paste(watermark, (0, y))

    # # 如果图片是RGBA或P模式，就转换为RGB模式
    if ext.lower() != 'png' and img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # 保存合并后的图片
    img.save(f"{name}_wm.{ext}")


compose_image_with_watermark('test.jpg', '项链 WG×钻石×蛋项链 WG×钻石×蛋白石', mode='title', position='right_center')    
