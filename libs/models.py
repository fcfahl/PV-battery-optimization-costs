from pathlib import Path
from types import SimpleNamespace
from dataclasses import dataclass
from typing import ClassVar

import pandas as pd
import libs.utils as utl
import libs.process as lcoe

@dataclass
class IO():
    """
    Class representing input and output file paths.

    Attributes:
        in_file (Path): The path to the input file.
        out_file (Path): The path to the output file.
    """

    in_file: Path
    out_file: Path

@dataclass
class LCEO():
    """
    Class for calculating Levelized Cost of Energy (LCOE).

    Attributes:
        data_columns (SimpleNamespace): A namespace containing data column configurations.
        pv_parameters (SimpleNamespace): A namespace containing photovoltaic parameters.
        lcoe_parameters (SimpleNamespace): A namespace containing LCOE calculation parameters.
    """

    data_columns: SimpleNamespace
    pv_parameters: SimpleNamespace
    lcoe_parameters: SimpleNamespace

    def calculate_LCOE(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the Levelized Cost of Energy (LCOE) based on the provided DataFrame.

        This method performs various calculations on the input DataFrame to derive
        LCOE-related metrics, including demand, PV size, CAPEX, NPV, OPEX, and CO2 emissions.

        Args:
            df (pd.DataFrame): The input DataFrame containing necessary data for calculations.

        Returns:
            pd.DataFrame: A DataFrame with additional columns for calculated LCOE metrics.
        """

        _df = df.copy()

        utl.print_message('Calculating Demand')

        _df['demand_e'] = _df.apply(
            lcoe.calculate_demand,
            axis=1,
            student_count   = self.data_columns.student_count,
            e_low           = self.lcoe_parameters.demand.e_low,
            e_medium        = self.lcoe_parameters.demand.e_medium,
            e_high          = self.lcoe_parameters.demand.e_high,
            pop_low         = self.lcoe_parameters.students.p_low,
            pop_high        = self.lcoe_parameters.students.p_high,
        )

        utl.print_message('Calculating PV and Battery Sizes')

        _df[['pv_kw_e', 'bat_kw_e']] = _df.apply(
            lcoe.calculate_pv_size,
            axis=1,
            result_type     = 'expand',
            pv_kw_t         = self.data_columns.pv_size,
            bat_kw_t        = self.data_columns.baterry_size,
            )

        utl.print_message('Calculating CAPEX')

        _df[['capex', 'capex_oem']] = _df.apply(
            lcoe.calculate_capex,
            axis=1,
            result_type     = 'expand',
            pv_costs        = self.pv_parameters.costs.pv_eur,
            bat_costs       = self.pv_parameters.costs.bat_eur,
            oem             = self.pv_parameters.OEM.O_M,
            soft_cost       = self.pv_parameters.costs.soft_cost,
            )

        utl.print_message('Calculating NPV')

        _df['npv_e'] = _df.apply(
            lcoe.calculate_npv_e,
            axis=1,
            bat_costs       = self.pv_parameters.costs.bat_eur,
            t_pv            = self.pv_parameters.OEM.t_PV,
            r               = self.pv_parameters.OEM.r,
            bat_life_time   = self.pv_parameters.OEM.life_time_bat,
            )

        utl.print_message('Calculating NPV_e')

        _df['npv_demand_e'] = _df.apply(
            lcoe.calculate_npv_demand_e,
            axis=1,
            t_pv            = self.pv_parameters.OEM.t_PV,
            r               = self.pv_parameters.OEM.r,
            )

        utl.print_message('Calculating LCOE')

        _df['lcoe_e'] = _df.apply(
            lcoe.calculate_lcoe_e,
            axis=1,
            )

        utl.print_message('Calculating OPEX')

        _df['opex'] = _df.apply(
            lcoe.calculate_opex,
            axis=1,
            bat_costs       = self.pv_parameters.costs.bat_eur,
            t_pv            = self.pv_parameters.OEM.t_PV,
            bat_life_time   = self.pv_parameters.OEM.life_time_bat,
            )

        utl.print_message('Calculating CO2_e')

        _df['co2_e'] = _df.apply(
            lcoe.calculate_co2_e,
            axis=1,
            lca_diesel       = self.pv_parameters.LCA.diesel,
            lca_pv           = self.pv_parameters.LCA.PV,
            )

        return _df


@dataclass
class Constructor:
    """
    Class responsible for configuring and initializing input/output and LCOE parameters.

    Attributes:
        config (ClassVar[dict]): A class variable that holds the configuration loaded from a YAML file.
    """

    config: ClassVar[dict]      = utl.dict_to_namespace(utl.load_yaml('config.yaml'))


    @classmethod
    def set_IO(cls) -> IO:
        """
        Set the input and output file paths based on the configuration.

        Returns:
            IO: An instance of the IO class initialized with the input and output file paths.
        """

        in_file     = cls.config.input.path
        out_file    = cls.config.output.path
        return IO(in_file, out_file)

    @classmethod
    def set_LCEO(cls) -> LCEO:
        """
        Set the parameters for the LCEO calculation based on the configuration.

        Returns:
            LCEO: An instance of the LCEO class initialized with data columns,
                  PV parameters, and LCOE parameters.
        """
        data_columns    = cls.config.data_columns
        pv_parameters   = cls.config.pv_parameters
        lcoe_parameters = cls.config.lcoe_parameters
        return LCEO(data_columns, pv_parameters, lcoe_parameters)
