import pandas as pd
import numpy as np
import peakutils
import glob
from pyexcelerate import Workbook

pd.options.mode.chained_assignment = None


class Dilatometry:
    def __init__(self):
        self.normalized_data = {}
        self.data_minus_baseline = {}
        self.averaged_data = {}

    def load_files(self, file_path):
        self.file_path = file_path + "/"
        file_list = glob.glob("*.txt", root_dir=self.file_path)
        file_list.sort()
        return file_list

    def process_data(self, file_list):
        """
        Normalizes, subtracts baseline, and averages data for each file loaded iwth the load_files function
        """
        for idx, file in enumerate(file_list):
            with open(f"{self.file_path}{file}", "r") as f:
                data = pd.read_table(f)
                cycle_num = data["cycle number"].unique()

                # Nomalizing displacement data for all cycles
                if idx == 0:
                    zero_val = data["Analog IN 1/V"].iloc[0]

                data["normalized displacement"] = data["Analog IN 1/V"] - zero_val
                data["absolute percent change"] = (
                    (data["Analog IN 1/V"] - zero_val) / abs(zero_val) * 100
                )
                data["percent change per cycle"] = 0

                for cycle in cycle_num:
                    cycle_zero = data["Analog IN 1/V"][
                        data["cycle number"] == cycle
                    ].iloc[0]
                    data["percent change per cycle"][data["cycle number"] == cycle] = (
                        (
                            data["Analog IN 1/V"][data["cycle number"] == cycle]
                            - cycle_zero
                        )
                        / abs(cycle_zero)
                        * 100
                    )

                self.normalized_data[idx] = data

                # Subtracting baseline from displacement data for second to n-1 cycles
                baseline_data = data[
                    (data["cycle number"] > 1) & (data["cycle number"] < cycle_num[-1])
                ]

                y = (
                    baseline_data["normalized displacement"]
                    - baseline_data["normalized displacement"].iloc[0]
                )

                y2 = (
                    (
                        baseline_data["Analog IN 1/V"]
                        - baseline_data["Analog IN 1/V"].iloc[0]
                    )
                    / abs(baseline_data["Analog IN 1/V"].iloc[0])
                    * 100
                )
                base1 = peakutils.baseline(y, 3)
                base2 = peakutils.baseline(y2, 3)

                baseline_data["disp minus baseline"] = y - base1
                baseline_data["percent disp minus baseline"] = y2 - base2

                self.data_minus_baseline[idx] = baseline_data

                # Getting average and standard devaition of displacement data
                time = []
                potential = []
                current = []
                disp = []
                percent_disp = []

                for cycle in cycle_num[1:-1]:
                    time.append(
                        np.asarray(
                            baseline_data["time/s"][
                                baseline_data["cycle number"] == cycle
                            ]
                            - baseline_data["time/s"][
                                baseline_data["cycle number"] == cycle
                            ].iloc[0]
                        )
                    )
                    potential.append(
                        np.asarray(
                            baseline_data["Ewe/V"][
                                baseline_data["cycle number"] == cycle
                            ]
                        )
                    )
                    current.append(
                        np.asarray(
                            baseline_data["<I>/mA"][
                                baseline_data["cycle number"] == cycle
                            ]
                        )
                    )
                    disp.append(
                        np.asarray(
                            baseline_data["disp minus baseline"][
                                baseline_data["cycle number"] == cycle
                            ]
                        )
                    )
                    percent_disp.append(
                        np.asarray(
                            baseline_data["percent disp minus baseline"][
                                baseline_data["cycle number"] == cycle
                            ]
                        )
                    )

                time = pd.DataFrame(time).transpose()
                avg_time = np.mean(time, axis=1)

                potential = pd.DataFrame(potential).transpose()
                avg_potential = np.mean(potential, axis=1)

                current = pd.DataFrame(current).transpose()
                avg_current = np.mean(current, axis=1)
                dev_current = np.std(current, axis=1)

                disp = pd.DataFrame(disp).transpose()
                avg_disp = np.mean(disp, axis=1)
                dev_disp = np.std(disp, axis=1)

                percent_disp = pd.DataFrame(percent_disp).transpose()
                avg_percent_disp = np.mean(percent_disp, axis=1)
                dev_percent_disp = np.std(percent_disp, axis=1)

                avg_df = pd.DataFrame(
                    {
                        "Average Time (s)": avg_time,
                        "Average Potential (V)": avg_potential,
                        "Average Current (mA)": avg_current,
                        "Current Stand Dev (mA)": dev_current,
                        "Average Displacement (um)": avg_disp,
                        "Displacement Stand Dev (um)": dev_disp,
                        "Average Displacement (%)": avg_percent_disp,
                        "Displacement Stand Dev (%)": dev_percent_disp,
                    }
                )

                self.averaged_data[idx] = avg_df

    def export_data(self, destination):
        """
        Generate excel files for processed data.
        """
        wb1 = Workbook()
        wb2 = Workbook()
        wb3 = Workbook()

        for key in self.averaged_data:

            values1 = [self.normalized_data[key].columns] + list(
                self.normalized_data[key].values
            )
            wb1.new_sheet(f"File_0{key + 1}", data=values1)

            values2 = [self.data_minus_baseline[key].columns] + list(
                self.data_minus_baseline[key].values
            )
            wb2.new_sheet(f"File_0{key + 1}", data=values2)

            values3 = [self.averaged_data[key].columns] + list(
                self.averaged_data[key].values
            )
            wb3.new_sheet(f"File_0{key + 1}", data=values3)

        wb1.save(f"{destination}Normalized dilatometry data.xlsx")
        wb2.save(f"{destination}Dilatometry data minus baseline.xlsx")
        wb3.save(f"{destination}Averaged dilatometry data.xlsx")
