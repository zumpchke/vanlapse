import numpy as np
import time
import os
import glob
from flask import Flask
from flask import render_template

GENFILE = '.gen'

app = Flask(__name__)

def load_app(dir_name):
    app.dir_name = dir_name
    return app

@app.route('/bodhi')
def bodhi():
    img_list = glob.glob(os.path.join(app.dir_name, '*.jpg'))
    images = sorted(img_list, key=os.path.getmtime)

    # serve statistics to template
    # seconds to minutes
    intervals = np.diff(np.array(list(map(os.path.getmtime, images)))) / 60
    average_interval = np.mean(intervals)
    largest_interval = np.max(intervals)

    # is the file currently being generated?
    inprog = os.path.isfile(os.path.join('.', GENFILE))

    return render_template('base.html', num_images=len(images),
                           first_img_date=time.ctime(os.path.getmtime(images[0])),
                           last_img_date=time.ctime(os.path.getmtime(images[-1])),
                           average_interval=average_interval,
                           largest_interval=largest_interval,
                           inprog=inprog)
