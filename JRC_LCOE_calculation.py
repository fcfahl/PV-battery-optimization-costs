#!/usr/bin/python
# -*- coding: utf-8 -*-

#===========================================================================#
#                     PV-battery-optimization-costs                         #
#===========================================================================#

""" description """

__credits__       = "..."
__authors__       = "..."
__copyright__     = "..."
__license__       = "check licence file"
__version__       = "1.0.0"
__date__          = "Oct 8 2024"

#===========================================================================#
import libs.utils as utl
import libs.models as mdl


def main():
    """
    Main function to execute the LCOE calculation workflow.

    This function performs the following steps:
    1. Initializes the Constructor to load configuration settings from the config.yaml file.
    2. Sets up input/output file paths using the configuration.
    3. Initializes the LCEO processing parameters.
    4. Loads the input data from a CSV file into a DataFrame.
    5. Calculates the Levelized Cost of Energy (LCOE) using the loaded data.
    6. Saves the resulting DataFrame with LCOE calculations to a CSV file.

    The function is intended to be run as a standalone script.
    """

    # Initialize the Constructor to load configuration settings
    cnt = mdl.Constructor()

    # Set up input and output file paths
    io = cnt.set_IO()

    # Initialize the LCEO processing parameters
    prc = cnt.set_LCEO()

    # Load the input data from the specified CSV file into a DataFrame
    df_data = utl.load_df_from_csv(io.in_file)

    # Calculate the LCOE based on the loaded data
    df_lcoe = prc.calculate_LCOE(df_data)

    # Save the resulting DataFrame with LCOE calculations to the specified output CSV file
    utl.save_df_to_csv(df_lcoe, io.out_file)

    # print (df_lcoe)


if __name__ == "__main__":
    utl.print_message('START', tab=0)
    main()
    utl.print_message('END', tab=0)
