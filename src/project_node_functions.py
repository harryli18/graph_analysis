### file with all the functions used
###imports
import os
from functools import reduce

import networkx as nx
import pandas as pd
from pyvis.network import Network


# set path to the project directory

# work_dir = 'C:/Users/harry/Documents/data/Project_Node/Helix_Analysis_2021/'
work_dir = 'C:/Users/harry/Documents/data/Project_Node/Helix_Analysis_2022/'

##function to create the data directories
def create_directories():
    import os

    if not os.path.exists(work_dir + "/Data"):
        os.makedirs(work_dir + "/Data")
    if not os.path.exists(work_dir + "/Data/Input"):
        os.makedirs(work_dir + "/Data/Input")
    if not os.path.exists(work_dir + "/Data/Output"):
        os.makedirs(work_dir + "/Data/Output")
    
    if not os.path.exists(work_dir + "/Output"):
        os.makedirs(work_dir + "/Output")        
    return


##functions:
###Function to initialize the graph and calculate the characteristics of the network
def network_characteristics(data, column_name, name):
    ##first analysis
    # create graph from input data
    G = nx.from_pandas_edgelist(
        data,
        source="EmailAddress1",
        target="EmailAddress2",
        edge_attr=[column_name],
        create_using=nx.Graph(),
    )

    ##create a dataframe with all the characteristics per node
    # eigenvector (might give an error about the iterations, if datasset is to large. You can adjust in the max_iter variable)
    eigenvector = nx.eigenvector_centrality(G, weight=column_name, max_iter=100000)
    eigenvector_df = pd.DataFrame.from_dict(

        eigenvector, orient="index", columns=["Eigenvector_centrality"]
    )
    eigenvector_df = eigenvector_df.rename_axis("EmailAdress").reset_index()
    # betweenness
    betweeness = nx.betweenness_centrality(G)
    betweeness_df = pd.DataFrame.from_dict(
        betweeness, orient="index", columns=["Betweeness_centrality"]
    )
    betweeness_df = betweeness_df.rename_axis("EmailAdress").reset_index()

    # closeness
    closeness = nx.closeness_centrality(G)
    closeness_df = pd.DataFrame.from_dict(
        closeness, orient="index", columns=["Closeness_centrality"]
    )
    closeness_df = closeness_df.rename_axis("EmailAdress").reset_index()

    # degreecentrality
    degree_centrality = nx.degree_centrality(G)
    degree_centrality_df = pd.DataFrame.from_dict(
        degree_centrality, orient="index", columns=["Degree_centrality"]
    )
    degree_centrality_df = degree_centrality_df.rename_axis("EmailAdress").reset_index()

    data_frames = [eigenvector_df, betweeness_df, closeness_df, degree_centrality_df]

    df_merged = reduce(
        lambda left, right: pd.merge(left, right, on=["EmailAdress"], how="outer"), data_frames
    )

    ##Output of the data
    df_merged.to_excel(work_dir + "/Output/" + name + "_all_nodes.xlsx")

    ##calculate stats
    characteristics = [
        "Eigenvector_centrality",
        "Betweeness_centrality",
        "Closeness_centrality",
        "Degree_centrality",
    ]
    characteristics_df = pd.DataFrame()
    for i in range(len(characteristics)):
        x = df_merged[characteristics[i]].describe()
        x = pd.DataFrame(x)
        x = x.transpose()
        characteristics_df = pd.concat([characteristics_df, x])
    characteristics_df.rename(columns=lambda s: s, index=lambda s: name + "_" + s, inplace=True)
    return df_merged, characteristics_df


def apply_netw_characteristics(data, name):
    columns = [
        "TotalCallMinutes",
        "TotalSpentinMinutesMails",
        "TotalSpentinMinutesIMS",
        "TotalSpentinMinutesMeetings",
        "connectivity_score",
    ]
    names = ["Calls", "Mails", "IMS", "Meetings", "connectivity_score"]
    combined_list_dfs = []
    for i in range(len(columns)):
        # set the time period
        x = data[["EmailAddress1", "EmailAddress2", columns[i]]]
        # only select edges with values
        x = x[x[columns[i]] > 0]
        x_all, x_characteristics = network_characteristics(x, columns[i], str(names[i] + name))
        combined_list_dfs.append(x_characteristics)
    combined_characteristics = pd.concat(combined_list_dfs)
    ##filepath to the output folder
    combined_characteristics.to_excel(
        work_dir + "/Output/Characteristics_avg_all_communication_" + name + ".xlsx"
    )
    return x_all, combined_characteristics


##function for the difference between


###VISUALIZATIONS
##create visualization
def create_network_visualization(dataset, column):
    data = dataset[dataset[column] > 0]
    Graph = nx.from_pandas_edgelist(
        data, source="EmailAddress1", target="EmailAddress2", edge_attr=column
    )
    net = Network(height=1000, width=2000, notebook=True)
    net.from_nx(Graph, show_edge_weights=True)
    net.show(os.path.join(work_dir, "project_node_network_visualization_" + column + ".html"))
