from moviepy.editor import AudioFileClip, CompositeVideoClip, ImageClip, TextClip, CompositeAudioClip, VideoFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx.all import resize
from PIL import Image
import PIL.ImageFilter as ImageFilter
import numpy as np
import os
import moviepy.config as mpy_config

import conf

mpy_config.change_settings({"IMAGEMAGICK_BINARY": conf.IMAGEMAGICK_BINARY})

def convert_to_rgb_resize_and_blur(image_path):
    ''' 
    Convert the image to RGB format, resize while maintaining aspect ratio, and apply Gaussian blur.
    
    Parameters:
    - image_path (str): Path of the image to process.
    
    Returns:
    - blurred_img_np (np.ndarray): Numpy array of the processed image.
    - new_width (int): Width of the resized image.
    - new_height (int): Height of the resized image.
    '''
    with Image.open(image_path) as img:
        original_width, original_height = img.size
        new_height = 1920
        aspect_ratio = original_width / original_height
        new_width = int(new_height * aspect_ratio)
        resized_img = img.convert('RGB').resize((new_width, new_height), Image.LANCZOS)
        blurred_img = resized_img.filter(ImageFilter.GaussianBlur(radius=10))  
        blurred_img_np = np.array(blurred_img)
        return blurred_img_np, new_width, new_height

def edit_caption(txt):
    ''' 
    Create a TextClip with the specified text, formatted in uppercase, centered, and styled with Arial-Bold font.
    
    Parameters:
    - txt (str): Text to display in the TextClip.
    
    Returns:
    - TextClip: Generated TextClip object.
    '''
    txt = txt.upper()
    max_text_width = 980
    font_path = 'media\\props\\Comfortaa.ttf'
    
    return TextClip(
        txt,
        font="Impact",
        fontsize=120,
        color='white',
        stroke_color='black',
        stroke_width=2.5,
        size=(max_text_width, None),
        align='North'
    ).set_position('center', 'center')

def adjust_text_lines(text, words_per_line=4):
    ''' 
    Adjust the text to fit within specified words per line, splitting into multiple lines if necessary.
    
    Parameters:
    - text (str): Original text to adjust.
    - words_per_line (int): Maximum number of words per line.
    
    Returns:
    - str: Adjusted text with line breaks.
    '''
    words = text.split()  
    lines = [' '.join(words[i:i+words_per_line]) for i in range(0, len(words), words_per_line)]
    return '\n'.join(lines)

def make_textclip_with_stroke(sub):
    ''' 
    Create a TextClip with stroke effect, adjusting font size to fit within specified dimensions.
    
    Parameters:
    - sub (SubtitlesClip): SubtitlesClip object containing text to display.
    
    Returns:
    - CompositeVideoClip: Composite video clip containing the text with stroke effect.
    '''
    font_size = 100  
    max_width = 1000
    max_height = 1880
    
    clip_fits = False

    while not clip_fits:
        sub.text = sub.text.upper()
        sub.text = adjust_text_lines(sub.text, words_per_line=3)  

        txt_clip = TextClip(sub.text, fontsize=font_size, color='white', font='Arial-Bold', size=(max_width, 1880), method='caption')
        
        stroke_clip = TextClip(sub.text, fontsize=font_size + 4, color='black', font='Arial-Bold', stroke_width=8, size=(max_width, 1880), method='caption')
        
        if txt_clip.size[1] > max_height:
            font_size -= 1  
        else:
            clip_fits = True  

    composite_clip = CompositeVideoClip([stroke_clip.set_position("North"), txt_clip.set_position("North")], size=(max_width, 1880))
    
    return composite_clip

def add_title_with_background(title_text, duration):
    ''' 
    Create a title with background rectangle that shrinks and disappears after the specified duration.
    
    Parameters:
    - title_text (str): The text to display as the title.
    - duration (int): Duration in seconds before the text shrinks and disappears.
    
    Returns:
    - CompositeVideoClip: The final video clip with the title.
    '''
    # Create the text clip
    txt_clip = TextClip(title_text, fontsize=70, font='media/props/ubuntu-mono.ttf', color='white')
    
    # Create a black background rectangle
    txt_w, txt_h = txt_clip.size
    rect_clip = TextClip(' ', fontsize=70, font='Arial-Bold', color='black', size=(txt_w, txt_h)).set_duration(duration)
    
    # Composite the text and the background
    text_with_bg = CompositeVideoClip([rect_clip, txt_clip.set_position("center")])

    # Function to shrink the text and background
    def shrink(get_frame, t):
        factor = max(0, 1 - t / duration) 
        return resize(get_frame(t), newsize=(txt_w * factor, txt_h * factor))

    # Apply the shrink effect after the specified duration
    final_clip = text_with_bg.set_duration(duration).fl(shrink, apply_to='mask')

    return final_clip

def create_video_with_data(data):
    ''' 
    Create a video using provided data, combining images, audio, subtitles, and music.
    
    Parameters:
    - data (dict): Dictionary containing paths to audio, music, subtitles, images, and other metadata.
    '''
    title_text = data["Trend_name"]
    audio_path = data['Audio']
    music_path = data["MusicPath"]["path"]
    srt_path = data['Subs']
    images = data['Images']
    images_folder = os.path.dirname(images[0])
    output_video_path = os.path.join(images_folder, "video.mp4")
    
    main_audio = AudioFileClip(audio_path)
    background_music = AudioFileClip(music_path).volumex(0.08)
    final_audio = CompositeAudioClip([main_audio, background_music.set_duration(main_audio.duration)])
    
    audio_duration = main_audio.duration
    total_video_duration = audio_duration + 4
    base_image_duration = (total_video_duration - 4) / len(images)
    
    video_size = (1080, 1920)
    frame_path = 'media/props/frame.png'
    frame_clip = ImageClip(frame_path).set_duration(total_video_duration).resize(video_size)
    
    image_clips = []
    for index, image_path in enumerate(images):
        image_duration = base_image_duration
        if index == 0 or index == len(images) - 1:
            image_duration += 2
        
        resized_img, new_width, new_height = convert_to_rgb_resize_and_blur(image_path)
        img_clip = ImageClip(resized_img).set_position(('center', 'center')).set_duration(image_duration)
        image_clips.append(img_clip.set_start((index * base_image_duration) if index != 0 else 0))
    
    video_clip = CompositeVideoClip(image_clips, size=video_size)
    video_clip = video_clip.set_duration(total_video_duration)
    video_clip = video_clip.set_audio(final_audio)
    
    subs = SubtitlesClip(srt_path, edit_caption).set_position(('center', 580))
    title_clip = add_title_with_background(title_text, duration=10).set_position("center").set_duration(10)

    final_clip = CompositeVideoClip([video_clip, frame_clip, subs, title_clip], size=video_size)
    
    final_clip.write_videofile(output_video_path, fps=24)
