"""
.. module: basics_methods
.. moduleauthor: Marcel Kennert
"""
from datetime import datetime
from logging import DEBUG, basicConfig, Formatter, FileHandler, getLogger
from os import listdir, remove, makedirs, unlink
from os.path import join, basename, isfile, isdir
from shutil import rmtree

from cv2 import imread, imwrite, resize, addWeighted

from application.configuration import \
    resized_images_dir, roi_file, images_dir, corr_properties_dir, \
    result_normal_dir, image_file, result_resized_dir, temp_dir, \
    experiment_dir, storage_temp_dir, backup_dir, recorder_dir, \
    evaluation_dir, displacement_dir, displacement_u_dir,\
    displacement_v_dir, dirs, log_dir, result_dir, travel_sensor_dir,\
    travel_sensor_images_dir, travel_sensor_draw_images_dir,\
    travel_sensor_sensors_dir, strain_dir, strain_exx_dir, strain_exy_dir,\
    strain_eyy_dir
from basic_modules.basic_dialogs import ProcessDialog
import matplotlib.pyplot as plt
import numpy as np


def resize_image(fpath, draw_roi=False, after_experiment=False):
    """Resizes the images and save them in the temp-folder

    :param fpath: Path to the image
    :type fpath: string
    :param draw_roi: Overdraw the ROI about the image (optional)
    :type draw_roi: Bool
    :param after_experiment: Necessary if the project was loaded (optional)
    :type after_experiment: Bool
    """
    fname = basename(fpath)
    if draw_roi and after_experiment:
        img = imread(join(images_dir, fname))
        roi = imread(join(corr_properties_dir, roi_file))
        img = addWeighted(img, 0.6, roi, 0.4, 0)
        resized_img = resize(img, (300, 225))
    elif draw_roi:
        img = imread(join(resized_images_dir, fname))
        roi = imread(join(resized_images_dir, roi_file))
        img = resize(img, (300, 225))
        resized_img = addWeighted(img, 0.6, roi, 0.4, 0)
    else:
        img = imread(join(images_dir, fname))
        resized_img = resize(img, (300, 225))
    imwrite(join(resized_images_dir, fname), resized_img)


def resize_strain_images():
    """Resizes all strain-images in the folder: /evaluation/results/normal"""
    files = get_all_files(result_normal_dir)
    n=len(files)
    if n>0:
        progress = ProcessDialog(title="Resize strain_images", max_n=len(files))
        for i in range(len(files)):
            f = files[i]
            progress.update(n=i, msg="Resize image: {0}".format(f))
            src = join(result_normal_dir, f)
            dst = join(result_resized_dir, f)
            img = imread(src)
            img = resize(img, (300, 225))
            imwrite(dst, img)
        progress.close()


def create_strain_images(folder, fcsv, fimg):
    """
    Creates a strain image with the given image and the given csv-file

    :param folder: Folder where be located the csv-file
    :type folder: string
    :param fcsv: csv-file
    :type fcsv: string
    :param fimg: Name of the result image-file 
    :type fimg: string
    """
    files = get_all_files(folder)
    n = len(files)
    if n>0:
        progress = ProcessDialog(title="Generate files", max_n=len(files))
        cur_n = convert_number(n)
        fpath = join(folder, fcsv.format(cur_n))
        image = join(images_dir, image_file.format(cur_n, '.JPG'))
        progress.update(1, 'Generate file: {0}'.format(basename(fpath)))
        m = create_max_strain_image(fpath, image, fimg.format(cur_n))
        for i in range(1, n):
            cur_n = convert_number(i)
            fpath = join(folder, fcsv.format(cur_n))
            image = join(images_dir, image_file.format(cur_n, '.JPG'))
            arr = np.loadtxt(fpath, dtype=np.float, delimiter=',')
            img = imread(image)
            progress.update(i, 'Generate file: {0}'.format(basename(fpath)))
            create_strain_image(m, arr, img, fimg.format(cur_n))
        progress.close()


def create_max_strain_image(fpath, image_path, dst_img):
    """
    Creates the max-strain image

    :param fpath: Path to the csv-file
    :type fpath: string
    :param image_path: Path to the image
    :type image_path: string
    :param dst_img:  
    :type dst_img: 
    :returns: average value
    :rtype: float
    """
    arr = np.loadtxt(fpath, dtype=np.float, delimiter=',')
    img = imread(image_path)
    min_x, min_y = np.unravel_index(arr.argmin(), arr.shape)
    max_x, max_y = np.unravel_index(arr.argmax(), arr.shape)
    m = (arr[max_x, max_y] + arr[min_x, min_y]) / 2.
    create_strain_image(m, arr, img, dst_img)
    return m


def create_strain_image(m, arr, img, dst_img):
    """Creates the strain images and save it

    :param m: Average value of the strain-value
    :type m: float
    :param arr: Strain-values 
    :type arr: ndarray
    :param img: Image 
    :type img: ndarray
    :param dst_img: Destination path
    :type dst_img: string
    """
    fpath = join(result_normal_dir, dst_img)
    dx, dy = arr.shape[:2]
    img = resize(img, (dy, dx))
    arr[arr == 0] = np.nan
    plt.title(dst_img)
    plt.imshow(img)
    plt.imshow(arr, cmap='jet', vmin=m * 0.1, vmax=m * 0.9) 
    plt.colorbar()
    plt.axis('off')
    plt.savefig(fpath, bbox_inches='tight', pad_inches=0)
    plt.close()

#=========================================================================
# Basic methods to log the processes and handling the folders
#=========================================================================


def get_all_files(directory):
    """
    Returns all files of the directory

    :param directory: Path to the directory
    :type directory: string
    :returns: Paths of all files
    :rtype: List
    """
    files = [f for f in listdir(directory) if isfile(join(directory, f))]
    return sorted(files)


def number_of_files(directory):
    """
    Returns the number of files

    :param directory: Path to the directory
    :type directory: string
    :returns: Number of files
    :rtype: int
    """
    return len(get_all_files(directory))


def clear_folder(directory):
    """
    Deletes all files of the directory

    :param directory: Path to the directory
    :type directory: string
    """
    files = get_all_files(directory)
    for f in files:
        try:
            remove(join(directory, f))
        except Exception, e:
            print e


def clear_temp_folder():
    """Clears the whole temp-folder"""
    temp_dirs = [
        temp_dir,
        experiment_dir,
        storage_temp_dir,
        backup_dir, images_dir, resized_images_dir, recorder_dir,
        evaluation_dir,
        corr_properties_dir,
        result_dir, result_normal_dir, result_resized_dir,
        displacement_dir,
        displacement_u_dir, displacement_v_dir,
        travel_sensor_dir, travel_sensor_images_dir,
        travel_sensor_draw_images_dir, travel_sensor_sensors_dir,
        strain_dir, strain_exx_dir, strain_exy_dir, strain_eyy_dir
        ]
    for d in temp_dirs:
        clear_folder(d)


def clear_storage_temp():
    """Clears the whole storage-temp-folder"""
    folder = storage_temp_dir
    for the_file in listdir(folder):
        file_path = join(folder, the_file)
        try:
            if isfile(file_path):
                unlink(file_path)
            elif isdir(file_path):
                rmtree(file_path)
        except Exception as e:
            print(e)


def create_folder(d):
    """Creates all directories of the application."""
    if not isdir(d):
        makedirs(d)


def create_dir():
    """
    Creates all directories. If the directory exists the
    method will do nothing.
    """
    for d in dirs:
        create_folder(d)


def create_logger(name):
    """
    Creates a logger to log all actions.

    :param name: Name of the logger
    :type name: string
    :returns: Logger
    """
    basicConfig(level=DEBUG)
    log_file = join(log_dir, "{0}.log".format(name))
    with open(log_file, "w") as f:
        f.write("#Log all operations of the application\n")
        f.close()
    fmtr = Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s",
                     datefmt="%Y-%m-%d %H:%M:%S")
    handler = FileHandler(log_file, mode="a")
    handler.setFormatter(fmtr)
    logger = getLogger(name)
    logger.addHandler(handler)
    return logger


def file_exist_in_dir(fdir, fname):
    """Checks whether the given file exist in the given directory

    :returns: True if the file is in the directory, False otherwise.
    :rtype: bool
    """
    files = get_all_files(fdir)
    return fname in files

#=========================================================================
# Convert methods
#=========================================================================


def secs_to_time(seconds):
    """Converts the given seconds to a time-format

    :param seconds: Seconds
    :param seconds: int
    :returns: Time-format
    :rtype: string
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return "%02d:%02d:%02d:%02d" % (d, h, m, s)


def time_to_secs(tfmt):
    """Converts the given time-format to seconds.

    :param tfmt: Time-format
    :type tfmt: string
    :returns: seconds
    :rtype: int
    """
    splt = np.array(tfmt.split(":"), int)
    t = splt[0] * 24 * 60 * 60 + splt[1] * \
        60 * 60 + splt[2] * 60 + splt[3]
    return t


def convert_date_to_string(date):
    """Converts the given date to a string.

    :param date: Date which should convert
    :type date: Datetime
    :returns: Converted string
    :rtype: string
    """
    if date.month < 10:
        month = "0" + str(date.month)
    else:
        month = str(date.month)
    if date.day < 10:
        day = "0" + str(date.day)
    else:
        day = str(date.day)
    return "{0}-{1}-{2}".format(date.year, month, day)


def convert_string_to_date(date):
    """Converts the given string to a date

    :param date: Date in the format YYYY-mm-dd
    :type date: string
    :returns: The date
    :rtype: datetime
    """
    return datetime.strptime(date, '%Y-%m-%d')


def convert_number(n):
    """Converts the given number to a string

    :param n: Number
    :type n: int
    :returns: The converted number
    :rtype: string
    """
    if n < 10:
        return "00" + str(n)
    elif n < 100:
        return "0" + str(n)
    else:
        return str(n)
