#!/usr/bin/env python

import argparse
from pandas import read_csv
from pandas import DataFrame
from pandas import Grouper
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

def plot_excs(csv_file, put, runs, cut_off, step, out_file):
  #Read the results
  df = read_csv(csv_file)
  
  #Calculate the mean of code coverage
  #Store in a list first for efficiency
  mean_list = []
  for subject in [put]:
    for fuzzer in ['aflnet', 'aflnwe']:
      
      df1 = df[(df['subject'] == subject) & 
                         (df['fuzzer'] == fuzzer)]
      
      if df1.empty:
          continue
        
      mean_list.append(np.array((subject, fuzzer, 0, 0.0, 0.0, 0.0, 0.0)))
      
      for time in range(1, cut_off + 1, step):
        totals = np.array([0, 0, 0, 0], dtype=float)
        run_count = 0
        
        for run in range(1, runs + 1, 1):
          #get run-specific data frame
          df2 = df1[df1['run'] == run]
          
          #get the starting time for this run
          start = df2.iloc[0, 0]

          #get all rows given a cutoff time
          df3 = df2[df2['time'] <= start + time * 60]
          
          #update total coverage and #runs
          totals += df3.tail(1).iloc[0, 4:8]
          run_count += 1
          
        #add a new row
        mean_list.append(np.concatenate(([subject, fuzzer, time], totals / run_count)))
      
  #Convert the list to a dataframe
  mean_df = pd.DataFrame(mean_list, columns = ['subject', 'fuzzer', 'time', 'paths','crashes','hangs','executions'])

  fig, axes = plt.subplots(4, 1, figsize = (10, 20))
  fig.suptitle("Executions analysis")
  
  for i, k in enumerate(mean_df.columns[-4:]):
    axes[i].plot(mean_df['time'].astype(int), mean_df[k].astype(float))
    axes[i].set_xlabel('Time (in min)')
    axes[i].set_ylabel(k)

  for i, ax in enumerate(fig.axes):
    ax.legend(('AFLNet', 'AFLNwe'), loc='upper left')
    ax.grid()

  #Save to file
  plt.savefig(out_file)
  

def plot_cov(csv_file, put, runs, cut_off, step, out_file):
  #Read the results
  df = read_csv(csv_file)

  #Calculate the mean of code coverage
  #Store in a list first for efficiency
  mean_list = []

  for subject in [put]:
    for fuzzer in ['aflnet', 'aflnwe']:
      for cov_type in ['b_abs', 'b_per', 'l_abs', 'l_per']:
        #get subject & fuzzer & cov_type-specific dataframe
        df1 = df[(df['subject'] == subject) & 
                         (df['fuzzer'] == fuzzer) & 
                         (df['cov_type'] == cov_type)]
        
        if df1.empty:
          continue

        mean_list.append((subject, fuzzer, cov_type, 0, 0.0))
        for time in range(1, cut_off + 1, step):
          cov_total = 0
          run_count = 0

          for run in range(1, runs + 1, 1):
            #get run-specific data frame
            df2 = df1[df1['run'] == run]

            #get the starting time for this run
            start = df2.iloc[0, 0]

            #get all rows given a cutoff time
            df3 = df2[df2['time'] <= start + time*60]
            
            #update total coverage and #runs
            cov_total += df3.tail(1).iloc[0, 5]
            run_count += 1
          
          #add a new row
          mean_list.append((subject, fuzzer, cov_type, time, cov_total / run_count))

  #Convert the list to a dataframe
  mean_df = pd.DataFrame(mean_list, columns = ['subject', 'fuzzer', 'cov_type', 'time', 'cov'])

  fig, axes = plt.subplots(2, 2, figsize = (20, 10))
  fig.suptitle("Code coverage analysis")

  for key, grp in mean_df.groupby(['fuzzer', 'cov_type']):
    if key[1] == 'b_abs':
      axes[0, 0].plot(grp['time'], grp['cov'])
      #axes[0, 0].set_title('Edge coverage over time (#edges)')
      axes[0, 0].set_xlabel('Time (in min)')
      axes[0, 0].set_ylabel('#edges')
    if key[1] == 'b_per':
      axes[1, 0].plot(grp['time'], grp['cov'])
      #axes[1, 0].set_title('Edge coverage over time (%)')
      axes[1, 0].set_ylim([0,100])
      axes[1, 0].set_xlabel('Time (in min)')
      axes[1, 0].set_ylabel('Edge coverage (%)')
    if key[1] == 'l_abs':
      axes[0, 1].plot(grp['time'], grp['cov'])
      #axes[0, 1].set_title('Line coverage over time (#lines)')
      axes[0, 1].set_xlabel('Time (in min)')
      axes[0, 1].set_ylabel('#lines')
    if key[1] == 'l_per':
      axes[1, 1].plot(grp['time'], grp['cov'])
      #axes[1, 1].set_title('Line coverage over time (%)')
      axes[1, 1].set_ylim([0,100])
      axes[1, 1].set_xlabel('Time (in min)')
      axes[1, 1].set_ylabel('Line coverage (%)')

  for i, ax in enumerate(fig.axes):
    ax.legend(('AFLNet', 'AFLNwe'), loc='upper left')
    ax.grid()

  #Save to file
  plt.savefig(out_file)

# Parse the input arguments
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--type',type=str,required=True,help="Cov or Exec", choices=["cov", "exec"])
    parser.add_argument('-i','--csv_file',type=str,required=True,help="Full path to results.csv")
    parser.add_argument('-p','--put',type=str,required=True,help="Name of the subject program")
    parser.add_argument('-r','--runs',type=int,required=True,help="Number of runs in the experiment")
    parser.add_argument('-c','--cut_off',type=int,required=True,help="Cut-off time in minutes")
    parser.add_argument('-s','--step',type=int,required=True,help="Time step in minutes")
    parser.add_argument('-o','--out_file',type=str,required=True,help="Output file")
    args = parser.parse_args()
    if args.type == "cov":
      plot_cov(args.csv_file, args.put, args.runs, args.cut_off, args.step, args.out_file)
    elif args.type == "exec":
      plot_excs(args.csv_file, args.put, args.runs, args.cut_off, args.step, args.out_file)
    else:
      print("Unknown plotting type")
