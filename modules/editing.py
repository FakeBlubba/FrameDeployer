from moviepy.editor import AudioFileClip, CompositeVideoClip, ImageClip, TextClip, CompositeAudioClip
from moviepy.video.tools.subtitles import SubtitlesClip
import os
from PIL import Image, ImageFilter
import numpy as np

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


# TODO: Update create_video_with_data with the next func


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
        blurred_img = resized_img.filter(ImageFilter.GaussianBlur(radius=6))
        blurred_img_np = np.array(blurred_img)
        return blurred_img_np, new_width, new_height

def make_textclip(txt):
    ''' 
    Create a TextClip with the specified text, formatted in uppercase, centered, and styled with Arial-Bold font.
    
    Parameters:
    - txt (str): Text to display in the TextClip.
    
    Returns:
    - TextClip: Generated TextClip object.
    '''
    txt = txt.upper()
    max_text_width = 1000  # Adatta questo valore alle tue necessità
    

    return TextClip(txt, font='Arial-Bold', fontsize=80, color='white', size=(max_text_width, None), align='center').set_position('center')


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

    composite_clip = CompositeVideoClip([stroke_clip.set_position("center"), txt_clip.set_position("center")], size=(max_width, 1880))
    
    return composite_clip

def create_video_with_data(data):
    ''' 
    Create a video using provided data, combining images, audio, subtitles, and music.
    
    Parameters:
    - data (dict): Dictionary containing paths to audio, music, subtitles, images, and other metadata.
    '''
    audio_path = data['Audio']
    music_path = data["MusicPath"]["path"]
    srt_path = data['subs']
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
    
    subs = SubtitlesClip(srt_path, make_textclip).set_position(('center', 'center'))
    
    final_clip = CompositeVideoClip([video_clip, subs], size=video_size)
    
    final_clip.write_videofile(output_video_path, fps=24)


# Carica i dati come prima e chiama la funzione

#data = {'Trend': 'Apollo', 'TextScript': 'The god was most commonly identified by either a bow or a musical instrument (usually a lyre, but sometimes a more specialized stringed instrument called a cithara). In addition to the bow, lyre, and cithara, Apollo was also represented by the tripod, a tall, three-footed structure (sometimes elaborately decorated) used for sacrifices and religious rituals.\nThis license lets others remix, tweak, and build upon this content non-commercially, as long as they credit the author and license their new creations under the identical terms. One second later the descent rocket engine was cut off, as the astronauts gazed down onto a sheet of lunar soil blown radially in all directions.\nApollo 8 carried out the first step of crewed lunar exploration: from Earth orbit it was injected into a lunar trajectory, completed lunar orbit, and returned safely to Earth. In the method ultimately employed, lunar orbit rendezvous, a powerful launch vehicle (Saturn V rocket) placed a 50-ton spacecraft in a lunar trajectory.', 'Audio': 'media\\Apollo12-02-2024\\speech.wav', 'subs': 'media\\Apollo12-02-2024\\sub.srt', 'Description': '\nThe god was most commonly identified by either a bow or a musical instrument (usually a lyre, but sometimes a more specialized stringed instrument called a cithara).\n', 'Tags': '#Toward #end #th #lunar #orbit #Apollo #spacecraft #became #two #separate #Columbia #piloted #Collins #Eagle #occupied', 'Images': ['media\\Apollo12-02-2024\\image_1.jpg', 'media\\Apollo12-02-2024\\image_2.jpg', 'media\\Apollo12-02-2024\\image_3.jpg', 'media\\Apollo12-02-2024\\image_4.jpg', 'media\\Apollo12-02-2024\\image_5.jpg', 'media\\Apollo12-02-2024\\image_6.jpg', 'media\\Apollo12-02-2024\\image_7.jpg', 'media\\Apollo12-02-2024\\image_8.jpg', 'media\\Apollo12-02-2024\\image_9.jpg', 'media\\Apollo12-02-2024\\image_10.jpg', 'media\\Apollo12-02-2024\\image_11.jpg', 'media\\Apollo12-02-2024\\image_12.jpg', 'media\\Apollo12-02-2024\\image_13.jpg', 'media\\Apollo12-02-2024\\image_14.jpg', 'media\\Apollo12-02-2024\\image_15.jpg', 'media\\Apollo12-02-2024\\image_16.jpg'], 'MusicPath': {'path': 'media/music/1\\Rameses B - Keep You [NCS Release].mp3', 'cc': 'Song: Rameses B - Keep You [NCS Release]\nMusic provided by NoCopyrightSounds\nFree Download/Stream: http://ncs.io/RB_KeepYou\nWatch: http://ncs.lnk.to/RB_KeepYouAT/youtube'}}
#create_video_with_data(data)
