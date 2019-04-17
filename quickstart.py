import glob
import os.path
import ffmpeg
from joblib import Parallel, delayed
from tqdm import tqdm
import os
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

def get_file(file_obj):
    file_path = os.path.join('bodhi4', file_obj['title'])
    if os.path.isfile(file_path):
        return
    file_obj.GetContentFile(file_path)

def get_folder_id(file_list, folder_name):
    for file1 in file_list:
        if file1['title'] == folder_name:
            folder_id = file1['id']
            return folder_id
    return None

def get_files_in_folder(folder_id):
    file_list = drive.ListFile({'q': "'{0}' in parents and trashed=false".format(folder_id)}).GetList()
    return file_list

# Auto-iterate through all files that matches this query

file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
folder_id = get_folder_id(file_list, 'bodhi4')
bodhi_files = get_files_in_folder(folder_id)
#
Parallel(n_jobs=16, prefer='threads')(delayed(get_file)(i) for i in tqdm(bodhi_files))
stream = ffmpeg.input('bodhi4/*.jpg', pattern_type='glob', framerate=18)
stream = ffmpeg.filter(stream, 'transpose', 1)
stream = ffmpeg.vflip(stream)
stream = ffmpeg.drawtext(stream, text="%{frame_num}", start_number='0', fontfile='OCRB Medium.ttf', fontcolor='white', borderw='1', fontsize='100', x=500, y=700, escape_text=False)
stream = ffmpeg.output(stream, 'movie.mp4', crf=20)
ffmpeg.run(stream, overwrite_output=True)
