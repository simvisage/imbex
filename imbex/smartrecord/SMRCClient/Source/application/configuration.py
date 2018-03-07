"""
.. module: configuration
.. moduleauthor: Marcel Kennert
"""
from os.path import join, abspath

from application.ftp_configuration import recordings_folder, experiment_folder,\
    correlation_folder, properties_folder, evaluation_folder, recorder_folder,\
    images_folder, \
    displacement_folder, udisplacement_folder, vdisplacement_folder,\
    travel_sensor_folder, strain_folder, strain_exx_folder, strain_eyy_folder,\
    strain_exy_folder

#=========================================================================
# Directories of the configuration folder
#=========================================================================
result_folder = evaluation_folder + '/results'

travel_sensor_images = travel_sensor_folder + '/images'

travel_sensor_draw_images = travel_sensor_folder + '/drawed_images'

travel_sensor_sensors = travel_sensor_folder + '/sensors'

result_resized_folder = result_folder + '/resized'

result_normal_folder = result_folder + '/normal'


confdir = abspath("../configuration")

cameras_dir = abspath(join(confdir, "cameras"))

storage_temp_dir = abspath(join(confdir, "storage_temp"))

server_dir = abspath(join(confdir, "server"))

log_dir = abspath(join(confdir, "logs"))

backup_dir = abspath(join(confdir, "backup"))

temp_dir = abspath(join(confdir, "temp"))

recordings_dir = abspath(join(temp_dir, recordings_folder))

experiment_dir = abspath(join(temp_dir, experiment_folder))

correlation_dir = abspath(join(temp_dir, correlation_folder))

corr_properties_dir = abspath(join(temp_dir, properties_folder))

evaluation_dir = abspath(join(temp_dir, evaluation_folder))

recorder_dir = abspath(join(temp_dir, recorder_folder))

images_dir = abspath(join(temp_dir, images_folder))

resized_images_dir = abspath(join(recordings_dir, "resized_images"))

result_dir = abspath(join(temp_dir, result_folder))

result_resized_dir = abspath(join(temp_dir, result_resized_folder))

result_normal_dir = abspath(join(temp_dir, result_normal_folder))

displacement_dir = abspath(join(temp_dir, displacement_folder))

displacement_u_dir = abspath(join(temp_dir, udisplacement_folder))

displacement_v_dir = abspath(join(temp_dir, vdisplacement_folder))

travel_sensor_dir = abspath(join(temp_dir, travel_sensor_folder))

strain_dir = abspath(join(temp_dir, strain_folder))

strain_exx_dir = abspath(join(temp_dir, strain_exx_folder))

strain_eyy_dir = abspath(join(temp_dir, strain_eyy_folder))

strain_exy_dir = abspath(join(temp_dir, strain_exy_folder))

correlation_temp_folder = join(storage_temp_dir, "temp{0}")

travel_sensor_images_dir = join(temp_dir, travel_sensor_images)

travel_sensor_draw_images_dir = join(temp_dir, travel_sensor_draw_images)

travel_sensor_sensors_dir = join(temp_dir, travel_sensor_sensors)

dirs = [confdir,
        cameras_dir,
        server_dir,
        log_dir,
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

#=========================================================================
# Important filenames of the application
#=========================================================================

ldap_file = "ldap_config.json"

experiment_recorder_file = "recorder.json"

experiment_type_file = "type.json"

recording_file = "recordings.npy"

sensor_evaluation_file = "sensor_evaluation.npy"

sensor_file = "Sensor-{0}.npy"

force_file = "force.npy"

recorder_file = "recorded_images.json"

correlation_properties_file = "correlation_properties.json"

roi_file = "roi.png"

image_file = "image_{0}{1}"

phases_file = "phases.json"

measuring_card_file = "measuring_card.json"

smrc_server = "smrc_server.json"

udisplacement_file="U_disp_{0}.csv"

vdisplacement_file="V_disp_{0}.csv"

strain_exx_file = "Exx_{0}.csv"

strain_exy_file = "Exy_{0}.csv"

strain_eyy_file = "Eyy_{0}.csv"

strain_exx_img_file = "strain_exx_img{0}.png"

strain_exy_img_file = "strain_exy_img{0}.png"

strain_eyy_img_file = "strain_eyy_img{0}.png"

travel_sensor_name = "Sensor-{0}"

sensor_json = "{0}.json"
#=========================================================================
# Extensions
#=========================================================================

experiment_ext = "smrcexp"

project_ext = "smrcprj"

exp_ext = "_exp"

img_ext = '_img'

resized_img_ext = '_rimg'

corr_prop_ext = '_corr'

recorder_ext = '_rec'

travel_sensor_ext = '_trse'

udisplacement_ext = '_udsp'

vdisplacement_ext = '_vdsp'

strain_exx_ext = '_sexx'

strain_exy_ext = '_sexy'

strain_eyy_ext = '_seyy'

result_ext = '_res'

result_normal_ext = '_resn'

result_resized_ext = '_ress'

ext_pairs = [(experiment_dir, exp_ext),
             (corr_properties_dir, corr_prop_ext),
             (images_dir, img_ext),
             (resized_images_dir, resized_img_ext),
             (recorder_dir, recorder_ext),
             (travel_sensor_dir, travel_sensor_ext),
             (displacement_u_dir, udisplacement_ext),
             (displacement_v_dir, vdisplacement_ext),
             (strain_exx_dir, strain_exx_ext),
             (strain_exy_dir, strain_exy_ext),
             (strain_eyy_dir, strain_eyy_ext),
             (result_dir, result_ext),
             (result_normal_dir, result_normal_ext),
             (result_resized_dir, result_resized_ext)]

#=========================================================================
# Important folders for the server
#=========================================================================

ftp_experiments = "/experiments"

ftp_series = ftp_experiments + "/series"

#=========================================================================
# Stylesheets
#=========================================================================

toolbar_background = "#2de5ab"

stylesheet_qtoolbutton = 'QToolButton{background-color: transparent}\
                        QToolButton:hover{background-color: white}'

stylesheet_qmenu = 'QMenu::item:selected{background-color: None}\
                    QMenu{background-color: None}'

stylesheet_application = 'QWidget{background-color: white}\
                        QToolBar{background: ' + toolbar_background + '}\
                        QPushButton{background-color:None}'

stylesheet_smrc = stylesheet_application + \
    stylesheet_qmenu + stylesheet_qtoolbutton
