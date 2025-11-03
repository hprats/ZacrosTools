from zacrostools.kmc_output import KMCOutput

# Read simulation output
kmc_output = KMCOutput(
    job_path='temp_600K',
    analysis_range=[50, 100],
    range_type='time',
    weights='time')

# Print TOF of all gas-phase species
for gas_spec in kmc_output.gas_specs_names:
    tof = kmc_output.tof[gas_spec]
    print(f"{gas_spec}: {tof:.3e} molec·s⁻¹·Å⁻²")

# Compute selectivity of CH4 vs CO2 and CH3OH
select_ch4 = kmc_output.get_selectivity(
    main_product='CH4',
    side_products=['CO2', 'CH3OH'])
print(f"Selectivity of CH4: {select_ch4:.2f}%")

# Print average coverage of all surface species
for surf_spec in kmc_output.surf_specs_names:
    av_cov = kmc_output.av_coverage[surf_spec]
    print(f"{surf_spec}: {av_cov:.2f}%")
