import argparse
import glob
import shutil
import sys
import tempfile
import os.path
import ffmpeg
from joblib import Parallel, delayed
from tqdm import tqdm
import os
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import gc
import dateutil.parser
from datetime import datetime, timedelta, timezone

NUM_DAYS = 30
FRAMERATE = 24
VIDEO_WIDTH = 600

def file_in_range(file_obj, num_hours):
    file_date = dateutil.parser.parse(file_obj['modifiedDate'])
    now = datetime.now(timezone.utc)
    if (now - file_date) < timedelta(hours=num_hours):
        return True

    return False

def get_file(directory, file_obj):
    file_path = os.path.join(directory, file_obj['title'])
    if os.path.isfile(file_path):
        return file_path

    file_obj.GetContentFile(file_path)
    del file_obj
    gc.collect()
    return file_path

def get_folder_id(file_list, folder_name):
    for file1 in file_list:
        if file1['title'] == folder_name:
            folder_id = file1['id']
            return folder_id
    return None

def get_files_in_folder(drive, folder_id):
    '''Get list of files in GDrive folder'''
    file_list = drive.ListFile({'q': "'{0}' in parents and trashed=false".
                               format(folder_id)}).GetList()
    return file_list

def main(directory, output_file_name):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    folder_id = get_folder_id(file_list, directory)
    
    timelapse_files = get_files_in_folder(drive, folder_id)
    timelapse_files = [f for f in timelapse_files if file_in_range(f, 24*NUM_DAYS)]
    output = Parallel(n_jobs=4, prefer='threads')(delayed(get_file)(directory, i)
                                                  for i in tqdm(timelapse_files))
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        for f in output:
            shutil.copy(f, os.path.join(tmp_dir, os.path.basename(f)))
        stream = ffmpeg.input('%s/*.jpg' % (tmp_dir), pattern_type='glob', framerate=FRAMERATE)
        stream = ffmpeg.filter(stream, 'transpose', 1)
        stream = ffmpeg.filter(stream, 'scale', VIDEO_WIDTH, -2)
        stream = ffmpeg.vflip(stream)
        stream = ffmpeg.output(stream, output_file_name, crf=23)
        ffmpeg.run(stream, overwrite_output=True)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    sys.exit(main(args.directory, args.output))


