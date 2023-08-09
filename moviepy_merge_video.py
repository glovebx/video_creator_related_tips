from moviepy.editor import *
from moviepy.video.tools.drawing import circle

background_clip = VideoFileClip("test.mp4", audio=False).\
           subclip(10,15)

# w,h = background_clip.size

# clip = VideoFileClip("temp.mp4", audio=False).\
#            subclip(26,31).\
#            add_mask()
clip = VideoFileClip("avatar.mp4").subclip(0,5).add_mask()

# 画面尺寸缩小一半，指定height，moviepy会自动计算width以保持比例
clip = clip.resize(height=int(clip.h/2))

w1,h1 = clip.size

radius = int(min(w1/2, h1/2))
# 需要修改moviepy的源码，否则有bug，参考 https://github.com/Zulko/moviepy/issues/1256
# The mask is a circle with vanishing radius r(t) = 800-200*t               
clip.mask.get_frame = lambda t: circle(screensize=(clip.w,clip.h),
                                       center=(clip.w/2,clip.h/2),
                                       # radius=max(0,int(600-200*t)),
                                       radius=radius,
                                       col1=1, col2=0, blur=4)




the_end = TextClip("The End", font="Amiri-bold", color="white",
                   fontsize=70).set_duration(clip.duration)

# final = CompositeVideoClip([the_end.set_pos('center'),clip],
#                            size =clip.size)
final = CompositeVideoClip([background_clip, clip], size =background_clip.size)
                           
final.write_videofile("theEnd.mp4")