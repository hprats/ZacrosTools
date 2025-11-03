from pathlib import Path
import numpy as np
import pandas as pd
from zacrostools.general_output import parse_general_output_file
from typing import Union, List, Tuple, Optional, Dict
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import warnings


def parse_procstat_output_file(procstat_output_path: Union[str, Path],
                               analysis_range: List[float],
                               range_type: str) -> Tuple[pd.DataFrame, float, int, float]:
    """
    Parses the procstat_output.txt file and extracts raw occurrence data within a specified window.

    Parameters
    ----------
    procstat_output_path : Union[str, Path]
        Path to the **folder** that contains 'procstat_output.txt'.
    analysis_range : List[float], optional
        A list of two elements `[start_percent, end_percent]` specifying the portion of the entire simulation
        to consider for analysis. The values should be between 0 and 100, representing percentages of the
        total simulated time or the total number of events, depending on `range_type`. For example,
        `[50, 100]` would analyze only the latter half of the simulation. Default is `[0.0, 100.0]`.
    range_type : str, optional
        Determines the dimension used when applying `analysis_range`:
        - `'time'`: The percentages in `analysis_range` refer to segments of the total simulated time.
        - `'nevents'`: The percentages in `analysis_range` refer to segments of the total number of simulated events.
        Default is `'time'`.

    Returns
    -------
    Tuple[pd.DataFrame, float, float]
        A tuple containing:
        - A DataFrame where each row corresponds to an elementary step (without _fwd/_rev suffix)
          and the columns are:
            - noccur_fwd
            - noccur_rev
            - noccur_net
        - delta_time : float
            The time interval corresponding to the selected window.
        - delta_events : int
            The number of events corresponding to the selected window.
        - area : float
            The area extracted from general_output.txt.
    """

    procstat_output_path = Path(procstat_output_path)
    output_file = procstat_output_path / "procstat_output.txt"
    if not output_file.is_file():
        raise FileNotFoundError(f"Output file '{output_file}' does not exist.")

    # Read entire file
    with output_file.open('r') as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        raise ValueError("The output file is empty.")

    header_line = lines[0]
    headers = header_line.split()

    if headers[0].lower() != 'overall':
        raise ValueError("The first header in procstat_output.txt must be 'Overall'.")

    # headers looks like: ['Overall', 'elemstep1_fwd', 'elemstep1_rev', 'elemstep2_fwd', 'elemstep2_rev', ...]
    # Group them into events
    event_names = []
    event_fwd_indices = []
    event_rev_indices = []

    i = 1  # Skip the "Overall" column
    while i < len(headers):
        col_name = headers[i]
        if col_name.endswith('_fwd'):
            base_name = col_name.replace('_fwd', '')
            # Check if the next header exists and is the reverse counterpart
            if i + 1 < len(headers) and headers[i + 1] == f"{base_name}_rev":
                event_names.append(base_name)
                event_fwd_indices.append(i)
                event_rev_indices.append(i + 1)
                i += 2  # Skip the next column as well
            else:
                # Treat as an irreversible step even though labeled _fwd
                event_names.append(base_name)
                event_fwd_indices.append(i)
                event_rev_indices.append(None)
                i += 1
        elif col_name.endswith('_rev'):
            # Option: raise an error because a reverse column without a forward is unexpected
            raise ValueError(f"Found a reverse column '{col_name}' without a matching forward column.")
        else:
            # Irreversible step with no suffix
            event_names.append(col_name)
            event_fwd_indices.append(i)
            event_rev_indices.append(None)
            i += 1

    # From line 1 onwards, the file has appended blocks of 3 lines each time the file is updated:
    # 1) "configuration int1 int2 real1"
    #    - int1: configuration count
    #    - int2: number of events so far
    #    - real1: current simulation time
    # 2) line with average waiting times (ignore)
    # 3) line with cumulative event counts:
    #    - int3: total number of events (should match int2)
    #    - int4: occurrences of elemstep1_fwd
    #    - int5: occurrences of elemstep1_rev
    #    etc.

    # We need to extract arrays for:
    #   configurations, nevents, time, and cumulative counts for each event

    # Skip the header line
    data_lines = lines[1:]

    # Every block of interest has 3 lines:
    # pattern:
    #   line0: configuration ...
    #   line1: (ignored waiting times)
    #   line2: cumulative counts line
    # So we need to parse these in groups of 3.
    if len(data_lines) % 3 != 0:
        # The file might end in partial blocks; handle gracefully or raise an error
        # We'll just use complete blocks
        trunc_len = (len(data_lines) // 3) * 3
        data_lines = data_lines[:trunc_len]

    # Initialize lists to store data
    configuration_counts = []
    total_events = []
    times = []
    cumulative_counts = []

    for i in range(0, len(data_lines), 3):
        config_line = data_lines[i]
        # ignored_line = data_lines[i+1]  # Ignored
        counts_line = data_lines[i + 2]

        # Parse configuration line
        # Example: "configuration 1 100 2.5"
        config_parts = config_line.split()
        if config_parts[0].lower() != 'configuration':
            raise ValueError("Expected a 'configuration' line.")
        if len(config_parts) < 4:
            raise ValueError("Configuration line does not have enough elements.")
        try:
            conf_count = int(config_parts[1])
            n_events = int(config_parts[2])
            t_sim = float(config_parts[3])
        except ValueError as e:
            raise ValueError(f"Error parsing configuration line: {e}")

        configuration_counts.append(conf_count)
        total_events.append(n_events)
        times.append(t_sim)

        # Parse counts line
        # This should have the same number of columns as headers
        # Format: int3 int4 int5 ...
        cparts = counts_line.split()
        if len(cparts) != len(headers):
            raise ValueError("Counts line does not match the number of header columns.")
        try:
            cparts_int = list(map(int, cparts))
        except ValueError as e:
            raise ValueError(f"Error parsing counts line: {e}")
        cumulative_counts.append(cparts_int)

    total_events = np.array(total_events, dtype=int)
    times = np.array(times, dtype=float)
    cumulative_counts = np.array(cumulative_counts, dtype=int)  # shape: (Nblocks, Ncolumns_in_header)

    if len(times) == 0:
        raise ValueError("No data found in procstat_output.txt.")

    finaltime = times[-1]
    final_nevents = total_events[-1]

    start_percent = analysis_range[0]
    end_percent = analysis_range[1]

    if range_type not in ['time', 'nevents']:
        raise ValueError("range_type must be either 'time' or 'nevents'.")

    if range_type == 'time':
        # Convert percent of time to actual time
        start_time = (start_percent / 100.0) * finaltime
        end_time = (end_percent / 100.0) * finaltime

        # Find indices that bracket start_time and end_time
        # We want the block that is just before or at start_time and the block at or just after end_time
        start_idx = np.searchsorted(times, start_time, side='right') - 1
        if start_idx < 0:
            start_idx = 0
        end_idx = np.searchsorted(times, end_time, side='right') - 1
        if end_idx < 0:
            end_idx = 0
        end_idx = min(end_idx, len(times) - 1)

    else:  # range_type == 'nevents'
        # Convert percent of events to actual number of events
        start_nevents = (start_percent / 100.0) * final_nevents
        end_nevents = (end_percent / 100.0) * final_nevents

        start_idx = np.searchsorted(total_events, start_nevents, side='right') - 1
        if start_idx < 0:
            start_idx = 0
        end_idx = np.searchsorted(total_events, end_nevents, side='right') - 1
        if end_idx < 0:
            end_idx = 0
        end_idx = min(end_idx, len(total_events) - 1)

    # If start_idx and end_idx are the same, it means zero-length window. Handle gracefully:
    if start_idx == end_idx:
        # This might indicate that the chosen window doesn't contain any interval
        # We can either raise an error or return an empty DataFrame
        return pd.DataFrame(columns=['noccur_fwd', 'noccur_rev', 'noccur_net']), 0.0, 0, 1.0

    # Calculate the differences in times and events
    delta_time = times[end_idx] - times[start_idx]
    delta_events = total_events[end_idx] - total_events[start_idx]

    # If delta_time is zero, that means no time interval. Avoid division by zero:
    if delta_time <= 0.0:
        return pd.DataFrame(columns=['noccur_fwd', 'noccur_rev', 'noccur_net']), 0.0, int(delta_events), 1.0

    # Compute differences in counts for each event
    # cumulative_counts[end_idx] - cumulative_counts[start_idx]
    delta_counts = cumulative_counts[end_idx] - cumulative_counts[start_idx]

    # Create lists to store counts
    noccur_fwd_list = []
    noccur_rev_list = []

    for fwd_idx, rev_idx in zip(event_fwd_indices, event_rev_indices):
        fwd_count = delta_counts[fwd_idx]
        if rev_idx is None:
            rev_count = 0  # Irreversible: no reverse events
        else:
            rev_count = delta_counts[rev_idx]
        noccur_fwd_list.append(fwd_count)
        noccur_rev_list.append(rev_count)

    # Compute net occurrences
    noccur_net = np.array(noccur_fwd_list) - np.array(noccur_rev_list)

    # Create a DataFrame with raw counts
    df = pd.DataFrame({
        'noccur_fwd': noccur_fwd_list,
        'noccur_rev': noccur_rev_list,
        'noccur_net': noccur_net
    }, index=event_names)

    # Parse general_output.txt to get area
    # Assuming general_output.txt is in the same directory as procstat_output.txt
    general_output_path = output_file.parent / "general_output.txt"
    try:
        general_data = parse_general_output_file(general_output_path)
        area = general_data.get('area', 1.0)  # Default to 1.0 if not found
    except Exception as e:
        raise ValueError(f"Error parsing 'general_output.txt': {e}")


    return df, float(delta_time), int(delta_events), float(area)


def plot_event_frequency(
        ax: plt.Axes,
        simulation_path: Union[str, Path],
        analysis_range: List[float],
        range_type: str,
        elementary_steps: Optional[List[str]] = None,
        hide_zero_events: bool = False,
        grouping: Optional[Dict[str, List[str]]] = None,
        show_minimum: bool = True,
        print_pe_ratio: bool = False,
        print_freq: bool = False
) -> plt.Axes:
    """
    Parse the procstat_output.txt file from a given simulation path and produce a
    horizontal bar plot of event frequencies on the given Axes object, with optional grouping of elementary steps.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The matplotlib axes on which to plot the data.
    simulation_path : Union[str, Path]
        The path to the simulation directory containing procstat_output.txt and general_output.txt.
    analysis_range : List[float]
        [start_percent, end_percent] defining the slicing window in terms of simulation time or events.
    range_type : str
        'time' or 'nevents', defining whether the slicing window is based on simulation time or number of events.
    elementary_steps : Optional[List[str]], default None
        If provided, only those steps are included in the plot. Otherwise, all steps are included.
        This will be performed before grouping and affects the original elementary step names before grouping.
    hide_zero_events : bool, default False
        If True, steps with zero occurrences in the fwd and rev directions are omitted from the plot.
    grouping : Optional[Dict[str, List[str]]], default None
        A dictionary defining groups of elementary steps. Each key is the name of the grouped step,
        and each value is a list of elementary steps to be grouped together.
    show_minimum: if True, draw the vertical line for the minimum event frequency.
    print_pe_ratio: if True, print the P/E ratio for each step.
    print_freq: if True, print the computed event frequencies.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the plot drawn on it.
    """

    simulation_path = Path(simulation_path)

    df_counts, delta_time, delta_events, area = parse_procstat_output_file(
        procstat_output_path=simulation_path,
        analysis_range=analysis_range,
        range_type=range_type
    )

    if df_counts.empty:
        raise ValueError(f"No steps have occurred.")

    if elementary_steps:
        # Remove rows from df_counts that are not in elementary_steps
        df_counts_filtered = df_counts.loc[df_counts.index.isin(elementary_steps)].copy()
        # Identify steps in elementary_steps not present in df_counts and trigger a warning for each missing step
        missing_steps = set(elementary_steps) - set(df_counts.index)
        for step in missing_steps:
            warnings.warn(f"Step '{step}' is in elementary_steps but not in df_counts.")
    else:
        df_counts_filtered = df_counts.copy()

    if grouping:
        # Validate the grouping dictionary
        valid_grouping = validate_grouping(grouping, df_counts_filtered)

        # Create a step to group mapping
        step_to_group = {}
        for group, steps in valid_grouping.items():
            for step in steps:
                step_to_group[step] = group

        # Function to map each step to its group or itself
        def map_step(step):
            return step_to_group.get(step, step)

        # Apply the mapping to the index to create new grouping
        new_index = df_counts_filtered.index.to_series().apply(map_step)

        # Group by the new index and sum the counts
        df_counts_grouped = df_counts_filtered.groupby(new_index).sum()

        # Now, to preserve the original order:
        # For each group or individual step, find the first occurrence in original_order
        original_order = df_counts.index.to_list()
        group_order = {}
        for idx, name in enumerate(original_order):
            if name in step_to_group:
                group = step_to_group[name]
                if group not in group_order:
                    group_order[group] = idx
            else:
                group_order[name] = idx
        df_counts_grouped = df_counts_grouped.copy()
        sort_keys = []
        for group in df_counts_grouped.index:
            if group in group_order:
                sort_keys.append(group_order[group])
            else:
                # If group not in group_order, assign a large number to push it to the end
                sort_keys.append(len(original_order))
        df_counts_grouped['sort_key'] = sort_keys
        df_counts_grouped = df_counts_grouped.sort_values('sort_key').drop(columns='sort_key')
    else:
        df_counts_grouped = df_counts_filtered.copy()

    if hide_zero_events:
        condition = (df_counts_grouped['noccur_fwd'] != 0) | (df_counts_grouped['noccur_rev'] != 0)
        df_counts_grouped = df_counts_grouped[condition]

    # print P/E ratios
    if print_pe_ratio:
        for step, row in df_counts_grouped.iterrows():
            n_fwd = row['noccur_fwd']
            n_rev = row['noccur_rev']
            total = n_fwd + n_rev
            pe = n_fwd / total if total > 0 else np.nan
            print(f"Step {step}: P/E ratio = {pe:.3f}")

    # Calculate frequencies: frequencies = counts / (delta_time * area)
    df_freq = df_counts_grouped.copy()
    df_freq['eventfreq_fwd'] = df_freq['noccur_fwd'] / (delta_time * area)
    df_freq['eventfreq_rev'] = df_freq['noccur_rev'] / (delta_time * area)
    df_freq['eventfreq_net'] = df_freq['noccur_net'] / (delta_time * area)

    # Handle any potential infinities or NaNs resulting from division
    df_freq.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_freq.fillna(0.0, inplace=True)

    # print frequencies
    if print_freq:
        for step, row in df_freq.iterrows():
            fwd = row['eventfreq_fwd']
            rev = row['eventfreq_rev']
            net = row['eventfreq_net']
            print(f"Step {step}: freq_fwd={fwd:.3e}, freq_rev={rev:.3e}, freq_net={net:.3e}")

    # Define colors for the barplot
    color_fwd = '#4169e1'      # Royal Blue
    color_rev = '#daa520'      # Goldenrod
    color_net_pos = '#32cd32'  # Lime Green
    color_net_neg = '#dc143c'  # Crimson

    bar_height = 0.22

    offset_map = {
        'Forward': bar_height * (-1.1),
        'Reverse': 0.0,
        'Net (+)': bar_height * 1.1,
        'Net (-)': bar_height * 1.1
    }

    y_tick_positions = []
    y_tick_labels = []

    for i, step in enumerate(df_freq.index):
        fwd = df_freq.loc[step, 'eventfreq_fwd']
        rev = df_freq.loc[step, 'eventfreq_rev']
        net = df_freq.loc[step, 'eventfreq_net']
        # Forward
        if fwd > 0:
            ax.barh(y=i + offset_map['Forward'], width=fwd, height=bar_height,
                    color=color_fwd, align='center', edgecolor='black', linewidth=0.5, zorder=3)
        # Reverse
        if rev > 0:
            ax.barh(y=i + offset_map['Reverse'], width=rev, height=bar_height,
                    color=color_rev, align='center', edgecolor='black', linewidth=0.5, zorder=3)
        # Net (+)
        if net > 0:
            ax.barh(y=i + offset_map['Net (+)'], width=net, height=bar_height,
                    color=color_net_pos, align='center', edgecolor='black', linewidth=0.5, zorder=3)
        # Net (-)
        if net < 0:
            abs_net = abs(net)
            ax.barh(y=i + offset_map['Net (-)'], width=abs_net, height=bar_height,
                    color=color_net_neg, align='center', edgecolor='black', linewidth=0.5, zorder=3)

        y_tick_positions.append(i)
        y_tick_labels.append(step)

    ax.set_yticks(y_tick_positions)
    ax.set_yticklabels(y_tick_labels)
    ax.set_xscale('log')
    ax.set_xlabel(r'Event frequency ($\mathrm{s^{-1}\,\AA^{-2}}$)', fontsize=14)
    ax.set_ylabel('Elementary step', fontsize=14)

    # Vertical line for minimum frequency
    min_eventfreq = 1.0 / (delta_time * area)
    if show_minimum and np.isfinite(min_eventfreq) and min_eventfreq > 0:
        ax.axvline(
            x=min_eventfreq,
            color='black',
            linestyle='-',
            linewidth=1.5,
            zorder=4,
            label='Min. event frequency'
        )

    legend_handles = [
        Line2D([0], [0], color=color_fwd, lw=10, label='Forward'),
        Line2D([0], [0], color=color_rev, lw=10, label='Reverse'),
        Line2D([0], [0], color=color_net_pos, lw=10, label='Net (+)'),
        Line2D([0], [0], color=color_net_neg, lw=10, label='Net (-)')
    ]

    # Add the min_eventfreq line to the legend if it was plotted,
    if np.isfinite(min_eventfreq) and min_eventfreq > 0:
        legend_handles.append(Line2D([0], [0], color='black', linestyle='-', lw=2, label='Min. event frequency'))
        legend_labels = ['Forward', 'Reverse', 'Net (+)', 'Net (-)', 'Min. event frequency']
    else:
        legend_labels = ['Forward', 'Reverse', 'Net (+)', 'Net (-)']

    ax.legend(handles=legend_handles, labels=legend_labels, loc='best')
    ax.grid(True, which='both', axis='x', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.invert_yaxis()
    return ax


def validate_grouping(grouping, df_counts_filtered):
    """
    Validates the grouping dictionary.

    Parameters:
    - grouping (dict): Dictionary defining groups and their corresponding steps.
    - df_counts_filtered (pd.DataFrame): DataFrame containing the steps to be grouped.

    Returns:
    - valid_grouping (dict): A cleaned version of the grouping dictionary with invalid steps removed.
    """

    # 1. Ensure the same elementary step is not in multiple groups
    all_steps = []
    for group, steps in grouping.items():
        if not isinstance(steps, list):
            raise TypeError(f"Steps for group '{group}' must be provided as a list.")
        all_steps.extend(steps)

    duplicate_steps = set([step for step in all_steps if all_steps.count(step) > 1])
    if duplicate_steps:
        raise ValueError(f"The following steps are assigned to multiple groups: {', '.join(duplicate_steps)}")

    # 2. Check if steps in grouping are present in df_counts_filtered.index
    df_steps_set = set(df_counts_filtered.index)
    grouping_steps_set = set(all_steps)
    missing_steps = grouping_steps_set - df_steps_set
    if missing_steps:
        warnings.warn(
            f"The following steps specified in grouping are not present in df_counts_filtered and will be ignored: {', '.join(missing_steps)}")
        # Remove missing steps from grouping
        for group in grouping:
            original_length = len(grouping[group])
            grouping[group] = [step for step in grouping[group] if step in df_steps_set]
            if len(grouping[group]) < original_length:
                warnings.warn(
                    f"In group '{group}', {original_length - len(grouping[group])} step(s) were removed because they are not present in df_counts_filtered.")

    return grouping
