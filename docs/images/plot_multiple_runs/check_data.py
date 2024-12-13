from zacrostools.kmc_output import KMCOutput

conditions = 'CH4_3.728e+00#O2_2.683e-07'
kmc_output = KMCOutput(path=f'./scan_results_POM_1000K_PtHfC/{conditions}',
                       analysis_range=[50, 100], range_type='time')

kmc_output_ref = KMCOutput(path=f'./scan_results_POM_1000K_HfC/{conditions}',
                           analysis_range=[50, 100], range_type='time')

print(f"TOF = {kmc_output.tof['H2']}")
print(f"TOF (ref) = {kmc_output_ref.tof['H2']}")
print(f"∆TOF = {kmc_output.tof['H2'] - kmc_output_ref.tof['H2']}")
