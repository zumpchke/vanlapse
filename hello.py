import numpy as np
import time
import os
import glob
from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/bodhi')
def bodhi(directory):
    img_list = glob.glob(os.path.join(directory, '*.jpg'))
    images = sorted(img_list, key=os.path.getmtime)

    # serve statistics to template
    # seconds to minutes
    intervals = np.diff(np.array(list(map(os.path.getmtime, images)))) / 60
    average_interval = np.mean(intervals)
    largest_interval = np.max(intervals)


    return render_template('base.html', num_images=len(images),
                           first_img_date=time.ctime(os.path.getmtime(images[0])),
                           last_img_date=time.ctime(os.path.getmtime(images[-1])),
                           average_interval=average_interval,
                           largest_interval=largest_interval)
