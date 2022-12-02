from dilatometry import Dilatometry
import matplotlib.pyplot as plt
import numpy as np

test = Dilatometry(ref_thickness=10)
test.load_data(
    file_str=r"C:\Users\Tyler\Documents\EQCM_dilatometry_paper\Raw data\Dilatometry\TIS2\TiS2_0.1_0.5_1_2_5_mVs_dilatometry_02.txt"
)

test.normalize_data()
test.subtract_baseline()
test.average_data()

dx = np.diff(test.averaged_data["Average Time (s)"])
dy1 = np.diff(test.averaged_data["Average Displacement (um)"])
dy2 = np.diff(test.averaged_data["Average Charge (C)"])


plt.figure("Fig 1")
plt.plot(
    test.averaged_data["Average Charge (C)"],
    test.averaged_data["Average Displacement (um)"],
)

plt.figure("Fig 2")
plt.plot(test.averaged_data["Average Potential (V)"][:-1], dy2 / dx)

plt.figure("Fig 3")
plt.plot(test.averaged_data["Average Potential (V)"][:-1], dy1 / dx)

plt.figure("Fig 4")
plt.plot(test.averaged_data["Average Current (mA)"][:-1], -dy1 / dx)

plt.show()
