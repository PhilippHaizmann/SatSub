import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.filedialog as fd

def get_data_from_file(skip_rows):
    """Open a file dialog to get a CSV file and return its data as a DataFrame."""
    file_path = fd.askopenfilename(title='Choose a file')
    return pd.read_csv(file_path, names=["Binding_Energy", "Intensity"], skiprows=skip_rows)

def modify_binding_energy(data, offset):
    """Modify binding energy by an offset."""
    data["Binding_Energy"] += offset
    return data

def get_interpolation_functions(x, y, sat_offset_b, satint_b, sat_offset_g, satint_g):
    """Generate and return the interpolation functions."""
    f_o = interp1d(x, y)
    f_s_b = interp1d(x - sat_offset_b, y * satint_b)
    f_s_g = interp1d(x - sat_offset_g, y * satint_g)
    return f_o, f_s_b, f_s_g

def subsat_single(offset, sat_offset_b, satint_b, sat_offset_g, satint_g, extra_inter_points, rows):
    """
    Process a single file for satellite subtraction.
    Plots the data and returns the modified data.
    """
    data = get_data_from_file(rows)
    data = modify_binding_energy(data, offset)
    x, y = data["Binding_Energy"].to_numpy(), data["Intensity"].to_numpy()
    
    f_o, f_s_b, f_s_g = get_interpolation_functions(x, y, sat_offset_b, satint_b, sat_offset_g, satint_g)
    
    xnew = np.linspace(x.max() - sat_offset_g, x.min(), num=len(x) + extra_inter_points, endpoint=True)
    nosat = f_o(xnew) - f_s_b(xnew) - f_s_g(xnew)
    
    plt.plot(xnew, f_o(xnew), "--", xnew, f_s_b(xnew), "o", xnew, f_s_g(xnew), "x", xnew, nosat, "-")
    plt.legend(['org', 'sat beta', 'sat gamma', "no sat"], loc='best')
    plt.show()

    df = pd.DataFrame({'Binding Energy': xnew, 'Intensity': nosat}).set_index("Binding Energy")
    return df

def subsat_batch(offset, sat_offset_b, satint_b, sat_offset_g, satint_g, extra_inter_points, rows):
    """
    Process multiple files for satellite subtraction.
    Saves the modified data to new CSV files.
    """
    root = tk.Tk()
    files = fd.askopenfilenames(parent=root, title='Choose files')
    
    for file_path in files:
        data = pd.read_csv(file_path, names=["Binding_Energy", "Intensity"], skiprows=rows)
        data = modify_binding_energy(data, offset)
        x, y = data["Binding_Energy"].to_numpy(), data["Intensity"].to_numpy()
        
        f_o, f_s_b, f_s_g = get_interpolation_functions(x, y, sat_offset_b, satint_b, sat_offset_g, satint_g)
        
        xnew = np.linspace(x.max() - sat_offset_g, x.min(), num=len(x) + extra_inter_points, endpoint=True)
        nosat = f_o(xnew) - f_s_b(xnew) - f_s_g(xnew)
        
        df = pd.DataFrame({'Binding Energy': xnew, 'Intensity': nosat}).set_index("Binding Energy")
        new_name = input(f"How should {file_path} be renamed?")
        df.to_csv(new_name + '.csv')

# Usage examples:
# subsat_batch(10, 1.87, 0.05, 2.52, 0.01, 300, 3)
x = subsat_single(0, 1.87, 0.055, 2.52, 0.015, 300, 4)
x.to_csv('Test.csv')
