import os
import sys
import configparser
import argparse

from datetime import datetime
from netCDF4 import Dataset

# Add a bulk set of attributes to a NetCDF file. The purpose on this script is to more efficently
# add a group of attrubtes to a NetCDF. Because attributes live in the header of a NetCDF file,
# adding an attribute requires the data below the header (the rest of the header and all the data)
# to be rewritten (to fit the attrbute between the data and header).
#
# The python NetCDF4 provides a function, setnatts, which allows for a bulk set of attrbutes to be
# set with one call, and thus will only call netcdf enddef once, which will then only rewrite the
# data once.

def get_linux_creation_date(file_path):
    # Determine and return the Linux creation date from the filesystem
    mod_time_s = os.stat(file_path).st_mtime
    # Convert to human readable datetime ... Thu Jun 25 hh:mm:ss MDT 2020
    return datetime.fromtimestamp(mod_time_s).strftime("%a %b %d %H:%M:%S MDT %Y")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('netcdf',
                        help='NetCDF file that needs attributes',
                        type=str)
    parser.add_argument('attributes_config',
                        help='NetCDF file that needs attributes',
                        type=str)
    parser.add_argument('-f', '--force',
                        help="Force overwrite if attributes are present",
                        action='store_true',
                        default=False)

    args = parser.parse_args()

    netcdf_file = args.netcdf
    attributes_file = args.attributes_config
    force = args.force

    netcdf = Dataset(netcdf_file, 'r+')

    if not os.path.isfile(attributes_file):
        print("No netcdf_attributes.cfg config file found - Please make one!")
        sys.exit(-1)

    # Read config file
    config = configparser.ConfigParser()
    config.read(attributes_file)

    attributes = {}

    for section in config.keys(): # cfg files may have a few sections
        for attribute in config[section].keys():
            value = config[section][attribute]

            # If creation_date() then use the get_linux_creation_date function to determine
            # creation date.
            if value == 'creation_date()':
                value = get_linux_creation_date(netcdf_file)

            attributes[attribute] = value

    print(attributes)
    netcdf.setncatts(attributes)
    netcdf.close()
