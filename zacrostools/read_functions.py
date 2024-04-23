def parse_general_output(path):
    dmatch = ['Number of surface species',
              'Total number of lattice sites',
              'Lattice surface area',
              'Site type names and total number of sites of that type']
    data = {}
    with open(f"{path}/general_output.txt", 'r') as file_object:
        line = file_object.readline()
        while len(dmatch) != 0:
            if 'Number of surface species' in line:
                data['n_surf_species'] = int(line.split()[-1])
                dmatch.remove('Number of surface species')
            if 'Total number of lattice sites' in line:
                data['n_sites'] = int(line.split()[-1])
                dmatch.remove('Total number of lattice sites')
            if 'Lattice surface area' in line:
                data['area'] = float(line.split()[-1])
                dmatch.remove('Lattice surface area')
            if 'Site type names and total number of sites of that type' in line:
                line = file_object.readline()
                site_types = {}
                while line.strip():
                    num_sites_of_given_type = int(line.strip().split(' ')[1].replace('(', '').replace(')', ''))
                    site_types[line.strip().split(' ')[0]] = num_sites_of_given_type
                    line = file_object.readline()
                data['site_types'] = site_types
                dmatch.remove('Site type names and total number of sites of that type')
            line = file_object.readline()
        return data
