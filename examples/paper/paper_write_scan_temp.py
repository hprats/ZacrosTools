# Create the KMC model here

for temperature in [600, 700, 800]: # in K
    for pressure in [1, 2, 5, 10]: # in bar
        kmc_model.create_job_dir(
            job_path=f'job_{temperature}K_{pressure}_bar',
            temperature=temperature,
            pressure={'CO': pressure},
            reporting_scheme={
                'snapshots': 'on event 100000',
                'process_statistics': 'on event 100000',
                'species_numbers': 'on event 100000'},
            stopping_criteria={
                'max_steps': 'infinity',
                'max_time': 5.0e+06,
                'wall_time': 250000}
        )
