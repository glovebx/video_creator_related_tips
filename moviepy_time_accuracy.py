#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This script checks the time accuracy of MoviePy.

First, a one-hour video is generated, where the frame
at time t displays t (in seconds, e.g. '1200.50') in white
on a black baground.

Then we ask MoviePy to open this video file, fetch
different times (1200.5, 850.2, 2000.3, 150.25, 150.25),
extract the corresponding frame as a JPEG image file, and
check that the time indicated in the frame corresponds to
the time requested (up to 0.04 seconds, because the video
is 25 fps).

Status:
Works perfectly with these formats: .mp4, .ogv, .webm.
Other formats not tested but should work perfectly too.
"""

import numpy as np
import PIL.Image as plim
from PIL import ImageFont, ImageDraw
import moviepy.editor as mpy
from moviepy.video.io.bindings import PIL_to_npimage
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.editor import TextClip

import gizeh as gz

# For speed we will use PIL/Pillow to draw the texts
# instead of the simpler/slower TextClip() option

fontname = "PingFang.ttc"
font = ImageFont.truetype(fontname, 24)

duration = 30

# 10分钟之内显示这个台词
text = '1. VantageAI - 一个基于人工智能的企业智能平台，帮助中小企业利用数据分析和机器学习来优化其业务流程，提高生产效率并实现可持续发展，作为一名技术工作者，你是不是希望下一代仍旧沿袭老路？就我本身来讲是完全没有这个想法的。绝大多数技术人一直跟电脑等机器打交道，一天天几乎坐着不动，也缺乏人与人的交流，相对来说，身心健康得不到全方位平衡发展。我希望下一代可以非技术类型的职业事业来支撑她的,同时，也掌握一部分程序、技术，并能懂有关软件工程的知识，这样的话，也许人生会更加丰富，可能也更理性一点。另外，我的设定是，这份事业和主业务不能有太大的冲突，只需要每天抽取一定的时间，我们把成就托付给时间的力量--有的人3年就能大成功，那我笨一点，试试花30年看一下能否有所成就。'

"""
0 A
0 A long
0 A long,
0 A long, long
0 A long, long,
1 a
   A long, long, a 
1 a wee
1 a wee lad

"""
text_list = text.split()


words = []


# 使用for循环遍历字符串中的每个字符
for tttt in text_list:
    # 定义一个空的字符串，用来存储当前的字符或单词
    word = []

    for char in tttt:
        # 如果字符是中文
        if '\u4e00' <= char <= '\u9fff':
            # 如果word不为空，说明之前有非中文的单词，将其添加到数组中
            if word:
                words.append(''.join(word))
                # 清空word
                word = []
            # 将中文字符添加到数组中
            words.append(char)
        # 如果字符是其他非中文字符
        else:
            # 将字符追加到word中
            word.append(char)

    # 如果word不为空，说明最后还有非中文的单词，将其添加到数组中
    if word:
        words.append(''.join(word))

# print(words)

# 定义一个空的数组，长度为60
array = [None] * duration

# 定义一个变量，表示每个单词显示的时间间隔，单位是秒
word_interval = (duration - 1) / len(words)

# 定义一个变量，表示当前单词显示的时间点，初始为0
time = 0

for i, word in enumerate(words):
    # 将时间点四舍五入到最近的整数
    index = round(time)

    # # 将单词赋值给数组对应的位置
    if array[index]:
        array[index] = f"{array[index]} {word}"
    else:
        array[index] = word

    if index > 0:
        # 当前索引
        pre_i = i
        while pre_i > 0:
            sentence = array[index]
            # 当前文字的宽度
            bbox = font.getbbox(sentence)
            # print(f"{index} - {bbox}")
            if bbox[2] - bbox[0] > 500:
                # # 已经满足宽度
                # if index_changed:
                #     array[index] = word
                # print('break.......')
                break

            pre_i -= 1
            # 计算宽度，不够则向前拿值
            # 如果前值已经包含在当前字幕，则需要继续往前拿值
            if words[pre_i] not in array[index]:
                array[index] = f"{words[pre_i]} {array[index]}"
                # print(f"{index}--{array[index]}")

    # 更新时间点，增加时间间隔
    time += word_interval

# # print(array)

def makeframe(t):
    # 透明必须是RGBA模式
    im = plim.new('RGBA', (720,80))
    draw = ImageDraw.Draw(im)

    idx = int("%d" % (t,))
    # draw.text((50, 25), "%.02f"%(t), font=font)
    # print(array[idx])
    text = array[idx]
    if not text:
        while True:
            idx -= 1
            if idx < 0:
                break
            text = array[idx]
            if text:
                break
    # text 可能会太长，需要分行            
    draw.text((0, 25), text, font=font,
              stroke_width=2,
              stroke_fill=COLOR)
    output = PIL_to_npimage(im)
    # output = output[:, :, 0]/255 #I have no idea what this does, but it seemed to work?
    return output    

COLOR = (1, 1, 0)
# def render_text(t):
#     idx = int("%d" % (t,))
#     # draw.text((50, 25), "%.02f"%(t), font=font)
#     # print(array[idx])
#     text = array[idx]
#     if not text:
#         while True:
#             idx -= 1
#             if idx < 0:
#                 break
#             text = array[idx]
#             if text:
#                 break

#     surface = gz.Surface(640, 80, bg_color=(0, 1, 0, 0.1))
#     text = gz.text(text, fontfamily="苹方-简-常规体",
#                    fontsize=50, fontweight='bold', fill=COLOR, xy=(0, 25))
#     text.draw(surface)
#     return surface.get_npimage(transparent=True)

# 字幕背景透明，参考这里
# https://rk.edu.pl/en/programmatically-creating-video-clips-and-animated-gifs-in-python/
def set_transparency(drawable):
    clip_mask = mpy.VideoClip(lambda t: drawable(t)[:, :, 3] / 255.0, duration=duration, ismask=True)
    return mpy.VideoClip(lambda t: drawable(t)[:, :, :3], duration=duration).set_mask(clip_mask)

subtitles_clips = []
for idx, text in enumerate(array):
    if not text:
        while True:
            idx -= 1
            if idx < 0:
                break
            text = array[idx]
            if text:
                break    
    subtitles_clips.append(TextClip(text, 
                                    font=fontname, 
                                    fontsize=32, 
                                    stroke_width=2,
                                    stroke_color="white",
                                    color="black")
                                    .set_pos('center')
                                    .set_duration(1))

subtitles_clip = set_transparency(makeframe) # mpy.VideoClip(makeframe, duration=duration)


# mask_filename = "mask.webm" # Or .ogv, .webm

# subtitles_clip.write_videofile(mask_filename, fps=25, threads=8)

def prepare_background(W: int, H: int) -> VideoFileClip:
    clip = (
        VideoFileClip("test.mp4")
        .without_audio()
        .resize(height=H)
    )

    # calculate the center of the background clip
    c = clip.w // 2

    # calculate the coordinates where to crop
    half_w = W // 2
    x1 = c - half_w
    x2 = c + half_w

    return clip.crop(x1=x1, y1=0, x2=x2, y2=H)

# Write the 1h-long clip to a file (takes 2 minutes)
# You can change the extension to test other formats


# clip.write_videofile(one_hour_filename, fps=25)

background_clip = prepare_background(W=720, H=720)
# background_clip.set_mask(subtitles_clip.mask)

subtitles_concat = concatenate_videoclips([subtitles_clip]).set_position(
    'bottom'
)

one_hour_filename = "temp.mp4" # Or .ogv, .webm

final = CompositeVideoClip([background_clip, subtitles_concat])
final.write_videofile(one_hour_filename, fps=25, threads=8)

# # We now read the file produced and extract frames at several
# # times. Check that the frame content matches the time.

# new_clip = mpy.VideoFileClip(one_hour_filename)
# for t in [0,1200.5, 850.2, 2000.3, 150.25, 150.25]:
#     new_clip.save_frame('%d.jpeg'%(int(100*t)),t)

