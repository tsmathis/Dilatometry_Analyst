from dilatometry import Dilatometry
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import rcParams

rcParams.update({"figure.autolayout": True})

test = Dilatometry(ref_thickness=10)

# tis2
# test.load_data(
#     file_str=r"C:\Users\Tyler\Documents\EQCM_dilatometry_paper\Raw data\Dilatometry\TIS2\TiS2_0.1_0.5_1_2_5_mVs_dilatometry_02.txt"
# )

# lfp
# test.load_data(
#     file_str=r"C:\Users\Tyler\Documents\EQCM_dilatometry_paper\Raw data\Dilatometry\LFP\2022_09_12\2022_09_12_LFP_dilatometer_0p1_0p5_1_2_5_mVs_retry_09_07_02_CVA_C07.txt"
# )

# yp50
# test.load_data(
#     file_str=r"C:\Users\Tyler\Desktop\test_files\yp50 derivs\2022_07_06 Giovanna YP50F_04_CVA_C07.txt"
# )

# yp50 ox
# test.load_data(
#     file_str=r"C:\Users\Tyler\Desktop\test_files\yp50 ox derivs\2022_09_02 YP50F chemically oxydation WE 0_05_CVA_C07.txt"
# )

# CDC
# test.load_data(
#     file_str=r"C:\Users\Tyler\Desktop\test_files\CDC derivs\CDC 800C Li2SO4 1M 12.4mg (0_03_CVA_05_CVA_C07_3-10.txt"
# )

# 7 pillar graphene
# test.load_data(
#     file_str=r"C:\Users\Tyler\Desktop\test_files\7 pillar derivs\Giovanna 7RP september 1_9 mg Li2SO4 1M_05_CVA_C07_3-11.txt"
# )

# 8 pillar graphene
# test.load_data(
#     file_str=r"C:\Users\Tyler\Desktop\test_files\8 pillar derivs\8RP september 3 mg CV_05_CVA_C07.txt"
# )

test.normalize_data()
test.subtract_baseline()
test.average_data()

dx = np.diff(test.averaged_data["Average Time (s)"])
dy1 = np.diff(test.averaged_data["Average Displacement (um)"])
dy2 = np.diff(test.averaged_data["Average Charge (C)"])

plt.rc("axes", labelsize=20)
plt.rc("xtick", labelsize=14)
plt.rc("ytick", labelsize=14)

plt.figure("Fig 1", figsize=(6, 6))
plt.plot(
    test.averaged_data["Average Charge (C)"],
    test.averaged_data["Average Displacement (um)"],
)
plt.xlabel("Charge (C)")
plt.ylabel("Average Displacment (um)")
plt.title("Displacement vs. Charge")
# plt.tight_layout()

plt.figure("Fig 2", figsize=(6, 6))
plt.plot(test.averaged_data["Average Potential (V)"][:-1], dy2 / dx)
plt.xlabel("Potential (V)")
plt.ylabel("Current (mA)")
plt.title("dQ/dt vs. Potential")
# plt.tight_layout()

plt.figure("Fig 3", figsize=(6, 6))
plt.plot(test.averaged_data["Average Potential (V)"][:-1], dy1 / dx)
plt.xlabel("Potential (V)")
plt.ylabel("dD/dt (um/s)")
plt.title("dD/dt vs. Potential")
# plt.tight_layout()

plt.figure("Fig 4", figsize=(6, 6))
plt.plot(test.averaged_data["Average Current (mA)"][:-1], -dy1 / dx)
plt.xlabel("Current (mA)")
plt.ylabel("-dD/dt (um/s)")
plt.title("-dD/dt vs. Current")
# plt.tight_layout()

plt.show()
