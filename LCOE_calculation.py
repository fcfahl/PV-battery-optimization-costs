#!/usr/bin/python
# -*- coding: utf-8 -*-

#===========================================================================#
#                     PV-battery-optimization-costs                         #
#===========================================================================#

""" description """

__authors__       = "Moner, M. and Fahl, F."
__license__       = "see LICENSE file"
__version__       = "1.0.0"
__date__          = "Nov 18th, 2024"
__paper__         = "http://..."

#===========================================================================#
import libs.utils as utl
import libs.models as mdl

from libs.utils import save_df_to_csv, print_message


def main():
    """
    Main function to execute the LCOE calculation workflow.
    The function is intended to be run as a standalone script.
    """

    print_message('START', tab=0)

    # Initializes the Constructor to load configuration settings from the config.yaml file.
    cnt = mdl.Constructor()

    # Sets up input/output file paths using the configuration.
    io = cnt.set_IO()

    # Initialize the LCEO processing parameters
    prc = cnt.set_LCEO()

    # Load the input data from the specified CSV file into a DataFrame
    df_data = utl.load_df_from_csv(io.in_file)

    # Calculate the LCOE based on the loaded data
    df_lcoe = prc.calculate_LCOE(df_data)

    # Save the resulting DataFrame with LCOE calculations to the specified output CSV file
    save_df_to_csv(df_lcoe, io.out_file)

    print_message('END', tab=0)

    # print (df_lcoe)


if __name__ == "__main__":

    main()