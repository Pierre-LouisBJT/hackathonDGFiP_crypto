import streamlit as st
import pandas as pd
import numpy as np

import networkx as nx
import plotly.graph_objs as go
import matplotlib.pyplot as plt

from pyvis import network as net
from IPython.core.display import display, HTML
import streamlit.components.v1 as components

from networkx import degree_centrality


### DEV CONSTANTS ###
transactions_path = './data/transactions/000000001665.csv' #csv file path of the ETH transactions 
dataset_keys = ['Name','Account Type','Contract Type','Entity','Label','Tags']
### ####

### PROD CONSTANTS ###
reach = 1
###

#Load datasets
eth_addresses = pd.read_csv('./data/eth_addresses.csv')
df_proprietary = pd.read_csv('./data/db_proprietary.csv', index_col=[0])
DF = pd.read_csv(transactions_path,";")

DF_light = DF[['hash','from_address','to_address','value','block_timestamp','block_number']]

### FUNCTIONS ###
def get_transact(address):
    #Selectionne les transac dans laquelle l'adress est présente
    transac = DF_light[(DF_light['from_address'] == address) | (DF_light['to_address'] == address)]
    #transac = DF_light[(DF_light['from_address'].isin(address)) | (DF_light['to_address'].isin(address))]
    #Trie par timestamp
    transac_sorted = transac.sort_values(by = 'block_timestamp', ascending = True)
    return transac_sorted

def get_deg_centrality(G):
    return degree_centrality(G)

def total_vol_transac(DF_transac_test):
    Total = DF_transac_test['value'].sum()
    return float(Total)/100000000000000000

def total_num_transac(DF_transac_test):
    return len(DF_transac_test)
###

st.title('Inspecteur du réseau Ethereum')

#Add the expander to provide some information about the app
with st.sidebar.expander("À propos"):
     st.write("""
        Cette web application a été développée durant le crypto hackathon de la DGFIP.
     """)

#Add a file uploader to the sidebar
uploaded_file = st.sidebar.file_uploader('',type=['csv']) #Only accepts csv file format

#add an input field for the ETH adress
address = st.text_input('Addresse à inspecter:', '0x')

#if an adress was inputed, display the infos we have
if address != '0x':
    st.header('Adresse inspectée : ' + address)

    st.markdown("""---""")

    #check if we have the adress in the list, and display the infos we have
    if address in eth_addresses['Address'].values:
        st.markdown('**Adresse connue en Open Data**')
        row_indexes = eth_addresses.index[eth_addresses['Address'] == address].tolist()
        row_index = row_indexes[0] #we have the index of the row of the adress

        #display the infos we have
        for key in dataset_keys:
            st.write(key,' : ', eth_addresses[key][row_index])
    
    else:
        st.write('Aucune information disponible sur cette adresse en Open Data')

    st.markdown("""---""")

    #base de données métier
    #if we have an instance in the database
    if address in df_proprietary['Address'].values:
        st.write('Cette adresse est déja dans la base de donnée métier')
        #get the index
        row_indexes = df_proprietary.index[df_proprietary['Address'] == address].tolist()
        row_index = row_indexes[0] #we have the index of the row of the adress

        st.write('Drapeau : ', df_proprietary['Flag'][row_index])
        st.write('Notes :')
        st.write(df_proprietary['Notes'][row_index])



    else:
        st.write("Cette adresse n'est pas encore dans la base de donnée métier")

        #form to add a new adress
        with st.form("add_new_adress"):
            st.write("Ajouter l'adresse à la base de donnée métier")
            # we already have the adress in address
            flag = st.selectbox('Drapeau : ', ('Aucun', 'Vert', 'Jaune', 'Rouge'))
            notes = st.text_area('Notes : ')
            

            submitted = st.form_submit_button("Submit")
            
            if submitted: #if the submit button was pressed
                #add the data to the db_propretary
                list_row = [address, flag, notes]
                new_row = {'Address': address, 'Flag': flag, 'Notes': notes}
                df_proprietary = df_proprietary.append(new_row, ignore_index=True)
                df_proprietary.to_csv('./data/db_proprietary.csv') #overwrite 
                st.write("Nouvelle adresse enregistrée")
        
        st.markdown("""---""")

    #get the data on the adress

    reach2 = st.button('Voir les transactions de deuxième niveau')

    ##############################
    DF_transac_test = get_transact(address)

    from_addresses = pd.unique(DF_transac_test[DF_transac_test.from_address!=address].get('from_address'))
    to_addresses = pd.unique(DF_transac_test[DF_transac_test.to_address!=address].get('to_address'))

    addresses_1 = np.append(from_addresses,to_addresses)

    if reach2 :
        reach = 2 #@PARAM 
        DF_transac_graph = pd.DataFrame(columns=['hash','from_address','to_address','value','block_timestamp','block_number'])
        addresses = [[] for k in range(reach+1)]

        addresses[0]=address
        addresses[1]=addresses_1

        for k in range(1,reach):
            for l in range(len(addresses[k])):
            #for add in addresses:
                print('k',k)
                print('l',l)
                #print(len(addresses))
                add = addresses[k][l]
                print(add)
                print(addresses)
                added_transac = get_transact(add)
                
                DF_transac_graph=pd.concat([DF_transac_graph,added_transac]).drop_duplicates()
                
                new_from_add = pd.unique(added_transac[added_transac['from_address']!=add].get('from_address'))
                new_to_add = pd.unique(added_transac[added_transac['to_address']!=add].get('to_address'))
                
                new_addresses=np.append(new_from_add,new_to_add)
                
                addresses[k+1]=new_addresses
    else:
        DF_transac_graph = DF_transac_test

    G = nx.MultiGraph()

    DF_transac_graph = DF_transac_graph.reset_index()

    G = nx.from_pandas_edgelist(
        df=DF_transac_graph,
        source='from_address',
        target='to_address',
        edge_attr=True,
        create_using=nx.DiGraph()
    )

    g = net.Network(height='700px', width='100%',notebook=False,heading='Transactions')

    g.from_nx(G)
    g.show('block.html')
    source_code =display(HTML('block.html'))

    #raw_html = html_object._repr_html_()
    #components.v1.html(raw_html)
    HtmlFile = open("block.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height = 700,width=700)

    st.markdown("""---""")

    st.write('Volume total de transactions :',total_vol_transac(DF_transac_test), ' ETH')
    st.write('Nombre total de transactions :',total_num_transac(DF_transac_test))
    st.write('Degré de centralité :', get_deg_centrality(G))
    



    ##############################

