import IsaricAnalytics as ia
import IsaricDraw as idw
import numpy as np
import pandas as pd


def define_button():
    '''Defines the button in the main dashboard menu'''
    # Insight panels are grouped together by the button_item. Multiple insight
    # panels can share the same button_item are grouped in the dashboard menu
    # according to this
    # However, the combination of button_item and button_label must be unique
    button_item = 'Outcomes'
    button_label = 'Outcomes and Complications - Abs. Value'
    output = {'item': button_item, 'label': button_label}
    return output


def create_visuals(
        df_map, df_forms_dict, dictionary, quality_report,
        filepath, suffix, save_inputs):
    
    '''
    Create all visuals in the insight panel from the RAP dataframe
    '''
    # Interventions descriptive table
    # split_column = 'demog_sex'
    # split_column_order = ['Female', 'Male', 'Other / Unknown']
    split_column = 'outco_binary_outcome'
    split_column_order = ['Discharged', 'Death', 'Censored']
    df_table = ia.get_descriptive_data(
        df_map, dictionary, by_column=split_column,
        include_sections=['compl', 'outco'])
    table, table_key = ia.descriptive_table(
        df_table, dictionary, by_column=split_column,
        column_reorder=split_column_order)
    fig_table = idw.fig_table(
        table, table_key=table_key + '<br><b>(SYNTHETIC DATA)</b>',
        suffix=suffix, filepath=filepath, save_inputs=save_inputs,
        graph_label='Descriptive Table',
        graph_about='Summary of outcomes and complications.')
    
     # Treatments frequency and upset charts
    section = 'compl'
    section_name = 'Complications'
    df_upset = ia.get_descriptive_data(
        df_map, dictionary, include_sections=[section],
        include_types=['binary', 'categorical'], include_subjid=False)
    
    counts = ia.get_counts(df_upset, dictionary)
    
    about = f'Absolute value of the ten most common {section_name.lower()}'
    cnt_chart_compl = idw.fig_count_chart(
        counts,
        title=f'Counts of {section_name} (SYNTHETIC DATA)',
        suffix=suffix, filepath=filepath, save_inputs=save_inputs,
        graph_label=section_name + ': Absolute',
        graph_about=about)
    
    return (fig_table, cnt_chart_compl)