import pandas as pd
import time
import os
import matplotlib.pyplot as plt
import json
import math

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
        self.output_df = df

    def run_experiment(self,save_results=True):
        if not os.path.exists(self.exp_dir):
              os.makedirs(self.exp_dir)
        actual_outputs=[]
        similarities = []
        inference_times = []
        input_tokens = []
        output_tokens = []
        for query in self.result_map.keys():
            start_time = time.time()
            actual_output,input_token,output_token = self.inference_func(query)
            actual_outputs.append(actual_output)
            similarity = self.similarity_func(self.result_map[query], actual_output)
            similarities.append(similarity)
            end_time = time.time()
            inference_time = end_time - start_time
            inference_times.append(inference_time)
            input_tokens.append(input_token)
            output_tokens.append(output_token)

        self.save_outputs(actual_outputs,similarities,inference_times,input_tokens,output_tokens)
        self.results = {'Accuracy': sum(similarities)/self.size, 'Average Inference Time': sum(inference_times)/self.size,'Average Input Tokens': sum(input_tokens)/self.size,'Average Output Tokens': sum(output_tokens)/self.size}
        if save_results:
            self.save_results()

    def save_results(self):
        file_name = os.path.join(self.exp_dir, "experiment_results.json")
        with open(file_name, 'w') as file:
            json.dump(self.results, file)

    def save_outputs(self,actual_outputs,similarities,inference_times,input_tokens,output_tokens):
        self.output_df['actual_output'] = actual_outputs
        self.output_df['similarity_score'] = similarities
        self.output_df['inference_time'] = inference_times
        self.output_df['input_token'] = input_tokens
        self.output_df['output_token'] = output_tokens
        file_name = os.path.join(self.exp_dir, "experiment_outputs.csv")
        self.output_df.to_csv(file_name, index=True) 
        self.plot_list(inference_times,'Inference Time')
        self.plot_list(input_tokens,'Input tokens')
        self.plot_list(output_tokens,'Output tokens')  

    def plot_list(self,data,plot_name):
        # Generating x-axis values (assuming it's just the index of the data points)
        plt.figure() 
        x_values = range(1, len(data) + 1)
        # Plotting the line graph
        plt.plot(x_values, data, marker='o', linestyle='-')  # 'o' for markers, '-' for line style
        plt.xlabel('Queries')  # Replace with your X-axis label
        plt.ylabel(f'{plot_name}')  # Replace with your Y-axis label
        plt.title(f'{plot_name} over queries')     # Replace with your plot title
        plt.grid(True)    
        plot_path = os.path.join(self.exp_dir, f"exp_{self.exp_number}_{plot_name}_plot.png")      # Add gridlines if needed
        plt.savefig(plot_path)

    def get_next_experiment_number(self):
        exp_num = 1
        while os.path.exists(os.path.join(self.exp_dir ,f"experiment_{exp_num}")):
            exp_num += 1
        return exp_num



