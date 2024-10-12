from typing import Tuple
import pandas as pd
import numpy as np

from libs.utils import handle_exceptions

@handle_exceptions
def calculate_demand(row: pd.Series, student_count, student_school, e_low, e_medium, e_high, pop_low, pop_high) -> float:
    """
    Calculate demand based on student count and school metrics.

    This function calculates the demand based on the number of students
    and their school metrics. It uses specified thresholds and multipliers
    to determine the demand level.

    Parameters:
        row (pd.Series): A Pandas Series representing a row of data containing
                        student count and school metrics.
        student_count (str): The key in the row for the student count.
        student_school (str): The key in the row for the school metric.
        e_low (float): The multiplier for low demand based on student count.
        e_medium (float): The multiplier for medium demand based on student count.
        e_high (float): The value for high demand when student count exceeds the threshold.
        pop_low (int): The lower threshold for population count.
        pop_high (int): The upper threshold for population count.

    Returns:
        float: The calculated demand, rounded to two decimal places.

    Notes:
        - If the student count is within the specified population thresholds,
        the demand is calculated using the corresponding multiplier.
        - If the student count does not satisfy the conditions, the function
        checks the school metric to determine the demand.
    """

    # Handle student_count
    student_count   = row[student_count] or 0
    student_school  = row[student_school]

    # Default case
    demand_e = np.nan

    # Calculate demand based on student_count
    if pop_low < student_count <= pop_high:
        demand_e = student_count * e_low
    elif student_count > pop_high:
        demand_e = e_high
    elif 0 < student_count <= pop_low:
        demand_e = e_medium

    # Calculate demand based on student_school if student_count doesn't satisfy
    if np.isnan(demand_e):  # Check if demand_e hasn't been set by student_count
        if student_school > pop_high:
            demand_e = e_high
        elif pop_low < student_school <= pop_high:
            demand_e = student_school * e_low
        elif 0 < student_school <= pop_low:
            demand_e = e_medium

    return round(float(demand_e),2)

@handle_exceptions
def calculate_pv_size(row: pd.Series, pv_kw_t:float, bat_kw_t:float) -> Tuple[float, float]:
    """
    Calculate the required size of photovoltaic (PV) and battery systems.

    This function calculates the required sizes of PV and battery systems
    based on the demand and the provided capacity values. The calculations
    are based on the demand and the specified time frame.

    Parameters:
        row (pd.Series): A Pandas Series representing a row of data containing
                        demand and capacity values.
        pv_kw_t (float): The total capacity of the photovoltaic system in kW.
        bat_kw_t (float): The total capacity of the battery system in kW.

    Returns:
        Tuple[float, float]: A tuple containing the calculated sizes of the PV
                            and battery systems, rounded to two decimal places.

    Notes:
        - The demand is retrieved from the row using the key 'demand_e'.
        - The calculations assume a yearly time frame (300 days).
        - If an error occurs during the calculations, an error message is printed,
        and the function will return (0.0, 0.0) as the default values.
    """

    demand_e    = row['demand_e'] or 0
    pv_kw_t     = row['pv_kw_t'] or 0
    bat_kw_t    = row['bat_kw_t'] or 0

    try:
        pv_kw_e  = (pv_kw_t * demand_e) / (300 * 365)
        bat_kw_e = (bat_kw_t * demand_e) / (300 * 365)

    except Exception as e:
        print(f" ... ERROR: {e}")

    return round(pv_kw_e,2), round(bat_kw_e,2)

@handle_exceptions
def calculate_capex(row: pd.Series, pv_costs:float, bat_costs:float, oem:float, soft_cost:float) -> Tuple[float, float]:
    """
    Calculate the capital expenditure (CAPEX) for photovoltaic (PV) and battery systems.

    This function calculates the total CAPEX and the OEM (Original Equipment Manufacturer)
    CAPEX based on the sizes of the PV and battery systems, their respective costs, and
    soft costs associated with the installation.

    Parameters:
        row (pd.Series): A Pandas Series representing a row of data containing
                        the sizes of the PV and battery systems.
        pv_costs (float): The cost per kW of the photovoltaic system.
        bat_costs (float): The cost per kW of the battery system.
        oem (float): The OEM factor to be applied to the total CAPEX.
        soft_cost (float): The soft costs associated with the installation.

    Returns:
        Tuple[float, float]: A tuple containing the calculated total CAPEX and
                            OEM CAPEX, both rounded to two decimal places.

    Notes:
        - If an error occurs during the calculations, the function will return
        (NaN, NaN) for both CAPEX values.
    """

    pv_kw_e    = row['pv_kw_e'] or 0
    bat_kw_e   = row['bat_kw_e'] or 0

    pv         = pv_kw_e * pv_costs
    bat        = bat_kw_e * bat_costs

    try:
        capex       = soft_cost * (pv + bat)
        capex_oem   = capex * oem
    except:
        capex = np.nan
        capex_oem = np.nan

    return round(capex,2), round(capex_oem,2)

@handle_exceptions
def calculate_npv_e(row: pd.Series, bat_costs:float, t_pv:int, r:float, bat_life_time:int) -> float:
    """
    Calculate the net present value (NPV) of an energy system over a specified time period.

    This function calculates the NPV of an energy system, taking into account
    the capital expenditure (CAPEX), operational expenditure (OPEX), and the
    costs associated with replacing batteries at specified intervals.

    Parameters:
        row (pd.Series): A Pandas Series representing a row of data containing
                        CAPEX and battery size information.
        bat_costs (float): The cost of the battery system per kW.
        t_pv (int): The total period (in years) over which to calculate the NPV.
        r (float): The discount rate for the NPV calculation.
        bat_life_time (int): The lifespan of the battery in years, which determines
                            when the battery needs to be replaced.

    Returns:
        Optional[float]: The calculated NPV, rounded to two decimal places.
                        Returns NaN if an error occurs during the calculation.

    Notes:
        - The NPV is calculated by summing the CAPEX and the present value of
        replacement battery costs and CAPEX over the specified time period.
        - The function assumes that the battery is replaced every `bat_life_time`
        years, except for the last year of the analysis period.
    """

    capex       = row['capex'] or 0
    capex_oem   = row['capex_oem'] or 0
    bat_kw_e    = row['bat_kw_e'] or 0

    try:

        npv_e = capex

        for n, year in enumerate(range(1, t_pv+1)):

            if year % bat_life_time == 0 and n+1 != t_pv: # replace battery every [bat_life_time] except for the last year
                replace_battery_cost = bat_kw_e * bat_costs
            else:
                replace_battery_cost = 0

            npv_e += replace_battery_cost + capex_oem / pow((1+r),year)

    except:
        npv_e = np.nan

    return round(npv_e,2)

@handle_exceptions
def calculate_npv_demand_e(row: pd.Series, t_pv:int, r:float) -> float:
    """
    Calculate the net present value (NPV) of demand over a specified time period.

    This function calculates the NPV of demand based on the provided demand value
    and a discount rate over a specified time horizon.

    Parameters:
        row (pd.Series): A Pandas Series representing a row of data containing
                        the demand value.
        t_pv (int): The total period (in years) over which to calculate the NPV.
        r (float): The discount rate for the NPV calculation.

    Returns:
        Optional[float]: The calculated NPV of demand, rounded to two decimal places.
                        Returns NaN if an error occurs during the calculation.

    Notes:
        - The NPV is calculated by summing the present value of demand over the
        specified time period.
    """

    demand_e    = row['demand_e'] or 0

    try:
        npv_demand_e = sum((demand_e) / pow((1+r),x) for x in range(0, t_pv+1))
    except:
        npv_demand_e = np.nan

    return round(npv_demand_e,2)

@handle_exceptions
def calculate_lcoe_e(row: pd.Series) -> float:
    """
    Calculate the levelized cost of energy (LCOE) based on NPV values.

    This function calculates the LCOE using the net present value (NPV) of the
    energy system and the NPV of demand.

    Parameters:
        row (pd.Series): A Pandas Series representing a row of data containing
                        the NPV of energy and the NPV of demand.

    Returns:
        Optional[float]: The calculated LCOE, rounded to four decimal places.
                        Returns NaN if an error occurs during the calculation.

    Notes:
        - The LCOE is calculated as the ratio of the NPV of energy to the NPV of demand.
        - The function assumes that the NPV of demand is not zero to avoid division by zero.
    """

    npv_e        = row['npv_e'] or 0
    npv_demand_e = row['npv_demand_e'] or 0

    try:
        lcoe_e = (npv_e) / (npv_demand_e) # range from 0.05 to 0.8
    except:
        lcoe_e = np.nan

    return round(lcoe_e,4)

@handle_exceptions
def calculate_opex(row: pd.Series, bat_costs:float, t_pv:int, bat_life_time:int) -> float:
    """
    Calculate the operational expenditure (OPEX) of an energy system.

    This function calculates the annual OPEX based on the costs associated
    with battery replacement and OEM costs over a specified time period.

    Parameters:
        row (pd.Series): A Pandas Series representing a row of data containing
                        the OEM capital expenditure and battery sizes.
        bat_costs (float): The cost of the battery system per kW.
        t_pv (int): The total period (in years) over which to calculate the OPEX.
        bat_life_time (int): The lifespan of the battery in years, which determines
                            when the battery needs to be replaced.

    Returns:
        Optional[float]: The calculated OPEX in EUR/year, rounded to two decimal places.
                        Returns NaN if an error occurs during the calculation.

    Notes:
        - The OPEX is calculated by summing the costs of battery replacements and
        OEM costs over the specified time period and dividing by the total years.
        - The function assumes that the battery is replaced every `bat_life_time`
        years, except for the last year of the analysis period.
    """

    capex_oem   = row['capex_oem'] or 0
    # pv_kw_e     = row['pv_kw_e'] or 0
    bat_kw_e    = row['bat_kw_e'] or 0

    try:

        opex_acc = 0

        for n, year in enumerate(range(1, t_pv+1)):

            if year % bat_life_time == 0 and n+1 != t_pv: # replace battery every [bat_life_time] except for the last year
                replace_battery_cost = bat_kw_e * bat_costs
            else:
                replace_battery_cost = 0

            opex_acc += replace_battery_cost + capex_oem

        opex = opex_acc / (t_pv ) # * pv_kw_e

    except:
        opex = np.nan

    return round(opex,2)

@handle_exceptions
def calculate_co2_e(row: pd.Series, lca_diesel:float, lca_pv:float) -> float:
    """
    Calculate the CO2 emissions associated with energy demand.

    This function calculates the CO2 emissions based on the lifecycle assessment
    (LCA) values for diesel and photovoltaic (PV) systems, adjusted for the
    energy demand.

    Parameters:
        row (pd.Series): A Pandas Series representing a row of data containing
                        the energy demand.
        lca_diesel (float): The lifecycle assessment value for diesel in gCO2/kWh.
        lca_pv (float): The lifecycle assessment value for PV in gCO2/kWh.

    Returns:
        Optional[float]: The calculated CO2 emissions in tons, rounded to four decimal places.
                        Returns NaN if an error occurs during the calculation.

    Notes:
        - The CO2 emissions are calculated as the difference between the LCA values
        for diesel and PV, multiplied by the energy demand, and converted to tons.
    """

    demand_e   = row['demand_e'] or 0

    try:
        co2_e = ((lca_diesel - lca_pv) * demand_e) / 1000
    except:
        co2_e = np.nan

    return round(co2_e,4)
