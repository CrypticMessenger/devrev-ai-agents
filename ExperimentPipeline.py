import pandas as pd
import itertools
import time
import random
import math
import os
import matplotlib.pyplot as plt
import json
from sentence_transformers import SentenceTransformer, util
import math

from Langchain.customLangchain import Inference
from constants import template,all_tools
from utils.OutputChecker import compare_lists_of_tools


"""# Experiment Setup

"""
class ExperimentPipeline:
    def __init__(self, inference_func, result_map, similarity_func, EXP_DIR, df):
        self.inference_func = inference_func
        self.similarity_func = similarity_func
        self.result_map = result_map
        self.results = []
        self.size = len(result_map)
        self.exp_dir = EXP_DIR
        self.exp_number = self.get_next_experiment_number()
        self.exp_dir = os.path.join(EXP_DIR , f"experiment_{self.exp_number}")
        self.master_excel_file = 'Results/Master_Results.xlsx'
        self.output_df = df


    def run_experiment(self,save_results=True):
        if not os.path.exists(self.exp_dir):
              os.makedirs(self.exp_dir)
        total_inference_time = 0
        total_similarity = 0
        outputs=[]
        similarities = []
        for query in self.result_map.keys():
            start_time = time.time()
            output = self.inference_func(query)
            outputs.append(output)

            similarity = self.similarity_func(self.result_map[query], output)
            similarities.append(similarity)

            end_time = time.time()
            inference_time = end_time - start_time

            total_inference_time += inference_time
            total_similarity += similarity

        self.save_outputs(outputs,similarities)
        self.results.append({'Similarity': total_similarity, 'Inference_Time': total_inference_time})
        if save_results:
            self.save_results()

    def save_results(self):
        self.create_dataframe()
        self.plot_metrics()
        self.add_to_master_excel()

    def create_dataframe(self):
        file_name = os.path.join(self.exp_dir, "experiment_results.csv")
        self.df = pd.DataFrame(self.results)
        self.df.to_csv(file_name, index=True)

    def save_outputs(self,outputs,similarities):
        self.output_df['Output'] = outputs
        self.output_df['Similarity Score'] = similarities
        file_name = os.path.join(self.exp_dir, "experiment_outputs.csv")
        self.output_df.to_csv(file_name, index=True)
        self.output_df.drop(columns='Output',inplace=True)

    def plot_metrics(self):
        plt.figure(figsize=(10, 6))

        # Bar plot for Similarity
        plt.subplot(1, 2, 1)
        plt.bar(self.df.index, self.df['Similarity'], color='skyblue')
        plt.xlabel('Index')
        plt.ylabel('Similarity')
        plt.title('Similarity vs. Index')

        # Bar plot for Inference_Time
        plt.subplot(1, 2, 2)
        plt.bar(self.df.index, self.df['Inference_Time'], color='salmon')
        plt.xlabel('Index')
        plt.ylabel('Inference Time')
        plt.title('Inference Time vs. Index')

        plt.tight_layout()

        # Save plots
        if not os.path.exists(self.exp_dir):
            os.makedirs(self.exp_dir)

        plot_similarity_name = os.path.join(self.exp_dir, f"exp_{self.exp_number}_metrics_plot.png")
        plt.savefig(plot_similarity_name)
        # plt.show()

    def get_next_experiment_number(self):
        exp_num = 1
        while os.path.exists(os.path.join(self.exp_dir ,f"experiment_{exp_num}")):
            exp_num += 1
        return exp_num

    def add_to_master_excel(self):
      print(self.master_excel_file)
      if not os.path.exists(self.master_excel_file):
          with pd.ExcelWriter(self.master_excel_file, engine='openpyxl') as writer:
              empty_df = pd.DataFrame(columns=['Placeholder'])
              empty_df.to_excel(writer, sheet_name='Placeholder', index=False)

      with pd.ExcelWriter(self.master_excel_file, mode='a', engine='openpyxl') as writer:
          sheet_name = f"Experiment_{self.exp_number}"
          self.df.to_excel(writer, sheet_name=sheet_name, index=False)



