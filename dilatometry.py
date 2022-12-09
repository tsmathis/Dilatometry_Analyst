import pandas as pd
import numpy as np

from scipy.interpolate import interp1d

pd.options.mode.chained_assignment = None


class Dilatometry:
    def __init__(self, ref_thickness):
        self.ref_thickness = ref_thickness
        self.data_minus_baseline = None
        self.averaged_data = None

    def load_data(self, file_str):
        with open(file_str, "r") as f:
            self.data = pd.read_table(f)

        self.cycle_num = self.data["cycle number"].unique()
        self.zero_val = self.data["Analog IN 1/V"].iloc[0]

    def normalize_data(self):
        # Normalize data to first value in displacement column
        self.data["Normalized displacement"] = (
            self.data["Analog IN 1/V"] - self.zero_val
        )

        # Displacement change in % relative to reference thickness - Raw displacment
        # values are already the delta in thickness, don't have to subtract ref thickness
        self.data["Percent change displacement (total)"] = (
            (self.data["Normalized displacement"]) / abs(self.ref_thickness) * 100
        )

        # % displacement change on cycle-to-cycle basis, normalizing to first disp val of each cycle
        self.data["Percent change displacement (per cycle)"] = 0

        for cycle in self.cycle_num:
            cycle_zero = self.data["Analog IN 1/V"][
                self.data["cycle number"] == cycle
            ].iloc[0]
            cycle_norm = (
                self.data["Analog IN 1/V"][self.data["cycle number"] == cycle]
                - cycle_zero
            )
            self.data["Percent change displacement (per cycle)"][
                self.data["cycle number"] == cycle
            ] = (cycle_norm / abs(self.ref_thickness) * 100)

    def subtract_baseline(self):
        # Subtracting baseline (found with cubic spline fitting of local maxima) from displacement data, excluding first cycle
        self.data_minus_baseline = self.data[self.data["cycle number"] > 1].copy()

        maxima = []
        times = []

        for cycle in self.cycle_num[1:]:
            ref = self.data_minus_baseline[
                self.data_minus_baseline["cycle number"] == cycle
            ]

            idx = ref.index[
                ref["Normalized displacement"] == max(ref["Normalized displacement"])
            ]

            maxima.append(ref.loc[idx, "Normalized displacement"].values[0])
            times.append(ref.loc[idx, "time/s"].values[0])

        fit = interp1d(
            np.array(times),
            np.array(maxima),
            kind="cubic",
            fill_value="extrapolate",
        )

        x = self.data_minus_baseline["time/s"]
        y = self.data_minus_baseline["Normalized displacement"]
        cubic = fit(x)

        # Have to renormalize to first value due to fit subtraction offsetting the data
        offset_corrected_disp = (y - cubic) - (y - cubic).iloc[0]

        self.data_minus_baseline["Displacement minus baseline"] = offset_corrected_disp

        # Getting % change
        self.data_minus_baseline["Percent change minus baseline"] = (
            offset_corrected_disp / abs(self.ref_thickness) * 100
        )

    def tolerant_mean(self, arrs):
        # Calculates means/std devs for arrays that are different lengths
        lens = [len(i) for i in arrs]
        arr = np.ma.empty((np.max(lens), len(arrs)))
        arr.mask = True
        for idx, l in enumerate(arrs):
            arr[: len(l), idx] = l
        return arr.mean(axis=1), arr.std(axis=1)

    def average_data(self):
        # Averaging all data and getting std dev, excluding first and last cycle
        # to avoid weirdness that comes when switching scan rates/cycling procedure
        ref_data = self.data_minus_baseline.copy()

        time = []
        potential = []
        current = []
        charge = []
        disp = []
        percent_disp = []

        for cycle in self.cycle_num[1:-1]:
            # Rormalize time values for each cycle for averaging
            time.append(
                np.asarray(
                    ref_data["time/s"][ref_data["cycle number"] == cycle]
                    - ref_data["time/s"][ref_data["cycle number"] == cycle].iloc[0]
                )
            )

            potential.append(
                np.asarray(ref_data["Ewe/V"][ref_data["cycle number"] == cycle])
            )

            current.append(
                np.asarray(ref_data["<I>/mA"][ref_data["cycle number"] == cycle])
            )

            charge.append(
                np.asarray(ref_data["(Q-Qo)/C"][ref_data["cycle number"] == cycle])
            )

            disp.append(
                np.asarray(
                    ref_data["Displacement minus baseline"][
                        ref_data["cycle number"] == cycle
                    ]
                )
            )

            percent_disp.append(
                np.asarray(
                    ref_data["Percent change minus baseline"][
                        ref_data["cycle number"] == cycle
                    ]
                )
            )

        avg_time, _ = self.tolerant_mean(time)
        avg_potential, _ = self.tolerant_mean(potential)
        avg_current, dev_current = self.tolerant_mean(current)
        avg_charge, dev_charge = self.tolerant_mean(charge)
        avg_disp, dev_disp = self.tolerant_mean(disp)
        avg_percent_disp, dev_percent_disp = self.tolerant_mean(percent_disp)

        # Renormalize displacement to first value
        avg_disp = avg_disp - avg_disp[0]
        avg_percent_disp = avg_percent_disp - avg_percent_disp[0]

        self.averaged_data = pd.DataFrame(
            {
                "Average Time (s)": avg_time,
                "Average Potential (V)": avg_potential,
                "Average Current (mA)": avg_current,
                "Current Stand Dev (mA)": dev_current,
                "Average Charge (C)": avg_charge,
                "Charge Stand Dev (C)": dev_charge,
                "Average Displacement (um)": avg_disp,
                "Displacement Stand Dev (um)": dev_disp,
                "Average Displacement (%)": avg_percent_disp,
                "Displacement Stand Dev (%)": dev_percent_disp,
            }
        )

    def calc_derivatives(self):
        dt = np.gradient(self.averaged_data["Average Time (s)"])
        dD = np.gradient(self.averaged_data["Average Displacement (um)"])

        self.averaged_data["dD/dt"] = dD / dt
