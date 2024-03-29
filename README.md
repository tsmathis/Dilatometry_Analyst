# Dilatometry Analyst Documentation

***Installer for current release can be found in the "Releases" tab to the right -->***
<br/>

## *Quick Start Guide*

**Data Import**: This application was designed to process data generated with an El-Cell ECD-3-nano electrochemical dilatometer[^1] used in conjunction with a BioLogic potentiostat. Dilatometry Analyst requires your data to be in the form of .txt or .mpt files that were generated by BioLogic's EC-Lab software[^2], see below for instructions for exporting data from EC-lab. **Please ensure you label your imported files appropriately** ("File Label" column), these labels will be used to label your data once it is exported to excel files. It is recommended to use the scan rate or charging rate associated with each file, *e.g.*, 5 mV/s, 10 mV/s, C/10, 1C, etc. 

Files can be removed from the file import by selecting an entry from the list and pressing the "Delete" key.
<br/>
<br/>

## *Data Processing*

*A recent Open Access review paper, which has engineers from El-Cell amoungst its authors, is available for a thorough discussion and review of the collection and intrepretation of electrochemical dilatometry data.*[^3]

Dilatometry Analyst primarily serves as tool for automating some simple, albiet tedious, data processing procedures. The main processes are as follows:

1. *Normalization of displacement data to reference thickness and Displacement change as a percentage*  
        
   Since dilatometers only record relative displacement values, an initial electrode thickness (*h*<sub>0</sub>) needs to be defined. The displacment can also be expressed as a percentage, which is sometimes referred to as "Relative Strain (%)" in the literature:
     
   <p align=center>Percent displacement change = (<i>h<sub>n</sub></i> - <i>h<sub>0</sub></i>) / <i>h<sub>0</sub></i> * <i>100</i> (<i>eq.</i> 1)</p>
     
   A similar calculation is performed to get the per-cycle percentage change in displacement. All displacement values in the UI of Dilatometry Analyst are presented in terms of Percent displacement change relative to the
   initial electrode thickness. Displacement values in microns can be found in the exported excel files.
   <br/>
   <br/>
2. *Baseline subtraction for **qualitative** interpretation and comparison of dilatometry data from different systems (electrodes, electrolytes, etc.)*
     
   While it is important to not disregard irreversible changes (and their causes) occurring in the displacement over time, any drift in the signal can make comparison of cycle-to-cycle behavior difficult. Assuming that the *reversible* behavior/mechanism for an electrochemical system in the dilatometer should at least be self-consistent on a cycle-to-cycle basis, it is reasonable to treat the drift in the system as a baseline and subtract it. Dilatometry Analyst finds the baseline in your data by fitting the local maxima of the 2nd to 2nd-to-last cycles (to avoid artifacts that arise when changing techniques/scanning rates) using cubic spline fitting.
   <br/>
   <br/>
3. *Averaging displacment and electrochemical data and calculating standard error*
     
   The data for the 2nd to 2nd-to-last cycle which had its the baseline removed is then averaged and then plotted along with the error (shaded regions in plots) in the "Averaged Data Preview" tab. Averaging is also performed on your electrochemical data as well. An aggregate view of the averaged data from all imported files can be viewed by pressing the "Aggregate Data" button.
   <br/>
   <br/>
4. *Displacement derivatives*

   Interesting insights into the electrochemical processes occuring during charging/discharging can be found by taking the derivative of the displacement over time and plotting the result versus the applied potential, resulting in a "mechanical cyclic voltammogram". See ref 4 for further information.[^4] Dilatometry Analyst will calculate these "strain-derivatives" for you. Clicking the "Displacement Derivatives" button will show these plots. The derivative plots can be quite noisy and have noticable outliers. These plots support picking and deleting points, simply left-mouse click a point you want to delete and press the "Delete" key. The "Curve smoothing" slider will apply a Savitzky-Golay filter[^5] to your data to smooth the data to presentable levels. 

Even though Dilatomery Analyst is not a full-fledged data visualization tool, the generated plots could in theory be used for publication. Many customization options are available in the plot customization controls (Arrow button in the control bar of each plot). For fully customized plots, it's recommended to export your data to excel files and then use your preferred data visualization software.
<br/>
<br/>

## *Exported Data*

Dilatometry Analyst will produce three excel files when the "Data Export" button is pressed. The files are <your_file_name>_Normalized_Data.xlsx, <your_file_name>_Baseline_Subtracted_Data.xlsx, and <your_file_name>_Averaged_Data.xlsx. Each file has sheets for each of the files that were imported that have been named using the labels that were provided at import.
<br/>
<br/>

## *Exporting .txt files from EC-Lab*

If you have never exported your data as .txt files from EC-Lab, the "Text File Export" dialog can be found under Experiment->Export as Text..., or by using the shortcut Ctrl+T. Selecting "Custom*" in the Template menu will allow you to choose what data (referred to as "Variables" in EC-Lab) will be included in your .txt file. You can choose to export all, or just the required data. Dilatometry Analyst requires the following columns, or "Variables": 'time/s', 'Ewe/V', '\<I>/ma', 'cycle number', and 'Analog IN 1/V'. 'Analog IN 1/V' is how EC-Lab referes to the displacement data that was recorded by the El-Cell dilatometer.
<br/>
<br/>

## *Directly Recording Signals from External Devices with EC-Lab*

In order for EC-Lab to properly record the input signals from the dilatometer, it is important to load the experiment settings for the dilatometer in the "External Devices" menu of EC-Lab ***before*** starting your experiment, Consult the dilatometer manual provided by El-Cell for further instruction.[^6]

If you do not have a BioLogic branded potentiostat, your system likely has a similar process for recording signals from external devices with your potentiostat, so it is best to consult your instrument's user manual.

If you cannot directly record the input signals from your dilatometer using EC-Lab, it is still possible to use Dilatometry Analyst to process your data. However, you will have to perform some extra work to successfully join your electrochemical data to your dilatometry data prior to use. See the "*How to Externally Combine Electrochemical and Dilatometry Data*" section at the bottom of this page.
<br/>
<br/>

## *How to Combine Electrochemical and Dilatometry Data after your Experiment has Finished*

*Note: The EC-Link software from El-Cell allows for recording potential, current, and there is a mention of a method of distinguishing between cycles in the documentaion for EC-Link. So it may be possible to directly generate files with EC-Link that are compatible with Dilatometry Analyst, but this has not been tested at this point.*

If it is not possible for you to directly record signals from your dilatometer using EC-Lab, or your non-BioLogic branded potentiostat's software, the data recorded using El-Cell's software (EC-Link[^7]) can still be joined with your electrochemical data. This will first require you to match the data sampling rates of your potentiostat's software with the EC-Link software as closely as you can. 

Unfortunately, you will have to stop and restart the EC-Link software before changing electrochemical techniques, *e.g.*, changing the scan rate or the C-rate, to ensure you will have individual EC-Link dilatometry data files corresponding to your electrochemical measurements.

The next step relies on the fact that EC-Link automatically records your system time during measurements. It is also possible to export data from EC-Lab in the "Text File Export" dialog with the elasped time in your measurements being expressed in system time (absolute time).

From here, you will have to perform a database-style inner join on your electrochemical and dilatometry data files using the system time as the field name to join on. The Pandas library from Python has a convienent funciton for this (pandas.merge_asof[^8]) that will join your data files on the *nearest* key, instead of on exact matches. This will help to minimize the amount of data lost in the join due to any differences in the sampling rates of EC-Lab (or your pontentiostat's software) and EC-Link. You will need then need to convert the system time, or absolute time, into elapsed time (in units of seconds). At this point your files will be compatible with Dilatometry Analyst. Feel free to get in touch, or open an issue, if you have persistent trouble with importing files into Dilatometry Analyst. 
<br/>
<br/>

## *References and External Links*

[^1]: [ECD-3-nano Dilatometer](https://el-cell.com/products/test-cells/electrochemical-dilatometer/ecd-3-nano-aqu/)
[^2]: [BioLogic EC-Lab](https://www.biologic.net/support-software/ec-lab-software/)
[^3]: [A Practical Guide for Using Electrochemical Dilatometry as Operando Tool in Battery and Supercapacitor Research](https://onlinelibrary.wiley.com/doi/full/10.1002/ente.202101120)
[^4]: [Probing local electrochemistry via mechanical cyclic voltammetry curves](https://www.sciencedirect.com/science/article/abs/pii/S2211285520311654)
[^5]: [Savitzky-Golay filter](https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter)
[^6]: [El-Cell manuals](https://el-cell.com/support/manuals/)
[^7]: [EC-Link software](https://el-cell.com/support/el-cell-software/ec-link/)
[^8]: [Pandas merge_asof documentation](https://pandas.pydata.org/docs/reference/api/pandas.merge_asof.html)

