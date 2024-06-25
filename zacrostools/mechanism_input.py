import ast
import pandas as pd
from zacrostools.write_functions import write_header
from zacrostools.calc_functions import calc_ads, calc_surf_proc
from zacrostools.custom_exceptions import ReactionModelError, enforce_types


class ReactionModel:
    """A class that represents a KMC reaction model.

    Parameters:

    mechanism_data: Pandas DataFrame
        Information on the reaction model
        The reaction name is taken as the index of each row

        The following columns are required:
            - site_types (str): the types of each site in the pattern
            - initial (list): initial configuration in Zacros format, e.g. ['1 CO* 1','2 * 1']
            - final (list): final configuration in Zacros format, e.g. ['1 C* 1','2 O* 1']
            - activ_eng (float): activation energy (in eV)
            - vib_energies_is (list of floats): vibrational energies for the initial state (in meV)
            - vib_energies_ts (list of floats): vibrational energies for the transition state (in meV).
              For non-activated adsorption, define this as an empty list i.e. []
            - vib_energies_fs (list of floats): vibrational energies for the final state (in meV)
            - molecule (str): gas-phase molecule involved. Only required for adsorption steps. Default value: None
            - area_site (float): area of adsorption site (in Å^2). Only required for adsorption steps. Default value:
            None
        The following columns are optional:
            - neighboring (str): connectivity between sites involved, e.g. 1-2. Default value: None
            - prox_factor (float): proximity factor. Default value: 0.5
            - angles (str): Angle between sites in Zacros format, e.g. '1-2-3:180'. Default value: None
    """

    @enforce_types
    def __init__(self, mechanism_data: pd.DataFrame = None):
        self.df = mechanism_data

    @classmethod
    def from_dictionary(cls, path):
        """Not implemented yet"""
        pass

    def write_mechanism_input(self, path, temperature, gas_data, manual_scaling, auto_scaling_steps, sig_figs_energies,
                              sig_figs_pe):
        """Writes the mechanism_input.dat file"""
        write_header(f"{path}/mechanism_input.dat")
        with open(f"{path}/mechanism_input.dat", 'a') as infile:
            infile.write('mechanism\n\n')
            infile.write('############################################################################\n\n')
            for step in self.df.index:
                initial_state = ast.literal_eval(self.df.loc[step, 'initial'])
                final_state = ast.literal_eval(self.df.loc[step, 'final'])
                if len(initial_state) != len(final_state):
                    raise ReactionModelError("Error in {step}: len IS is {len(initial_state)} but len FS is {len("
                                             "final_state)}.")
                infile.write(f"reversible_step {step}\n\n")
                if not pd.isna(self.df.loc[step, 'molecule']):
                    infile.write(f"  gas_reacs_prods {self.df.loc[step, 'molecule']} -1\n")
                infile.write(f"  sites {len(initial_state)}\n")
                if not pd.isna(self.df.loc[step, 'neighboring']):
                    infile.write(f"  neighboring {self.df.loc[step, 'neighboring']}\n")
                infile.write(f"  initial\n")
                for element in initial_state:
                    infile.write(f"    {' '.join(element.split())}\n")   # remove additional white spaces
                infile.write(f"  final\n")
                for element in final_state:
                    infile.write(f"    {' '.join(element.split())}\n")
                if 'site_types' in self.df.columns:
                    if not pd.isna(self.df.loc[step, 'site_types']):
                        infile.write(f"  site_types {self.df.loc[step, 'site_types']}\n")
                pre_expon, pe_ratio = self.get_pre_expon(step=step, temperature=temperature, gas_data=gas_data,
                                                         manual_scaling=manual_scaling)
                if step in manual_scaling:
                    infile.write(f"  pre_expon {pre_expon:.{sig_figs_pe}e}   # scaled {manual_scaling[step]:.8e}\n")
                else:
                    infile.write(f"  pre_expon {pre_expon:.{sig_figs_pe}e}\n")
                infile.write(f"  pe_ratio {pe_ratio:.{sig_figs_pe}e}\n")
                infile.write(f"  activ_eng {self.df.loc[step, 'activ_eng']:.{sig_figs_energies}f}\n")
                for keyword in ['prox_factor', 'angles']:
                    if keyword in self.df.columns:
                        if not pd.isna(self.df.loc[step, keyword]):
                            infile.write(f"  {keyword} {self.df.loc[step, keyword]}\n")
                if step in auto_scaling_steps:
                    infile.write(f"  stiffness_scalable \n")
                infile.write(f"\nend_reversible_step\n\n")
                infile.write('############################################################################\n\n')
            infile.write(f"end_mechanism\n")

    def get_pre_expon(self, step, temperature, gas_data, manual_scaling):
        """Calculates the forward pre-exponential and the pre-exponential ratio, required for the mechanism_input.dat
        file """
        vib_energies_is = ast.literal_eval(self.df.loc[step, 'vib_energies_is'])
        vib_energies_ts = ast.literal_eval(self.df.loc[step, 'vib_energies_ts'])
        vib_energies_fs = ast.literal_eval(self.df.loc[step, 'vib_energies_fs'])
        if not pd.isna(self.df.loc[step, 'molecule']):  # adsorption
            molecule = self.df.loc[step, 'molecule']
            molec_mass = gas_data.loc[molecule, 'gas_molec_weight']
            inertia_moments = ast.literal_eval(gas_data.loc[molecule, 'inertia_moments'])
            if 'degeneracy' in gas_data:  # test that it works
                if not pd.isna(gas_data.loc[molecule, 'degeneracy']):
                    degeneracy = int(gas_data.loc[molecule, 'degeneracy'])
                else:
                    degeneracy = 1
            else:
                degeneracy = 1
            pe_fwd, pe_rev = calc_ads(area_site=self.df.loc[step, 'area_site'],
                                      molec_mass=molec_mass,
                                      temperature=temperature,
                                      vib_energies_is=vib_energies_is,
                                      vib_energies_ts=vib_energies_ts,
                                      vib_energies_fs=vib_energies_fs,
                                      inertia_moments=inertia_moments,
                                      sym_number=int(gas_data.loc[molecule, 'sym_number']),
                                      degeneracy=degeneracy)
        else:  # surface process
            pe_fwd, pe_rev = calc_surf_proc(temperature=temperature,
                                            vib_energies_is=vib_energies_is,
                                            vib_energies_ts=vib_energies_ts,
                                            vib_energies_fs=vib_energies_fs)

        if step in manual_scaling:
            pe_fwd = pe_fwd * manual_scaling[step]
            pe_rev = pe_rev * manual_scaling[step]
        pe_ratio = pe_fwd / pe_rev
        return pe_fwd, pe_ratio
