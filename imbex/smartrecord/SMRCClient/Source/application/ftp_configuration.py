"""
.. module: ftp_configuration
.. moduleauthor: Marcel Kennert
"""
#=========================================================================
# Important folders for the experiments (server)
#=========================================================================

# first level
correlation_folder = "correlation"

experiment_folder = "experiment"

recordings_folder = "recordings"

first_level_dirs = [correlation_folder,
                    experiment_folder,
                    recordings_folder]

# second level
evaluation_folder = correlation_folder + "/evaluation"

properties_folder = correlation_folder + "/properties"

images_folder = recordings_folder + "/images"

recorder_folder = recordings_folder + "/recorder"

second_level_dirs = [evaluation_folder,
                     properties_folder,
                     images_folder,
                     recorder_folder]

# third level
displacement_folder = evaluation_folder + "/displacements"

strain_folder = evaluation_folder + "/strains"

third_level_dirs = [strain_folder, displacement_folder]

# 4. level

udisplacement_folder = displacement_folder + '/u_displacement'

vdisplacement_folder = displacement_folder + '/v_displacement'

strain_exx_folder = strain_folder + '/strain_exx'

strain_eyy_folder = strain_folder + '/strain_eyy'

strain_exy_folder = strain_folder + '/strain_exy'

travel_sensor_folder = displacement_folder + '/travel_sensor'

fourth_level_dirs = [udisplacement_folder,
                     vdisplacement_folder,
                     travel_sensor_folder,
                     strain_exx_folder,
                     strain_exy_folder,
                     strain_eyy_folder]



all_server_folders = first_level_dirs + second_level_dirs + \
    third_level_dirs + fourth_level_dirs 

download_folders = [properties_folder, experiment_folder,
                    images_folder, recorder_folder,
                    udisplacement_folder, vdisplacement_folder,
                    travel_sensor_folder, strain_exx_folder,
                    strain_exy_folder, strain_eyy_folder]
