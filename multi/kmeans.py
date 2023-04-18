import pandas as pd
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits
import warnings
from pathlib import Path




def kmeans_n_times_csv(X, n, num_clusters, csv_file, newcsv=True, **kwargs):
    """
    Run k-means clustering `n` times on data `X`, with `num_clusters` clusters,
    and append the resulting cluster assignments to a CSV file `csv_file`.
    The reason the clustering and file writing are tied into the same function
    is so you still save the data if it crashes halfway through, which may
    not happen for kmeans but is much more likely for other similar functions
    with other clustering, e.g. deep embedded clustering.
    In the saved csv file, each sample is a row and each run of kmeans is a
    column.
    
    Parameters
    ----------
    X : array
        The data to be clustered. Each row is a set of data
    n : int
        The number of times to run kmeans
    num_clusters : int
        The number of clusters
    csv_file : string
        Path to CSV output file
    newcsv : bool, default = True
        If this is true, create a new csv and overwrite any that was there
        before. If false, appends to existing csv if one exists.
            
    **kwargs: 
        labels : Array of labels for the data. If these are provided, it adds
        these as the first column to the csv.
        
    Returns
    -------
    df_kmeans : pandas DataFrame
        DataFrame of the same data from the csv. Rows are samples and columns
        are cluster labels from different runs of kmeans.

    """
      
    
    #Make empty dataframe
    df_kmeans = pd.DataFrame(index=[f'sample_{i}' for i in range(len(X))],dtype='int32')
    
    #Add the corresponding labels
    if 'labels' in kwargs:
        df_kmeans['labels'] = kwargs.get('labels')

    
    #Check if file exists- if not it needs creating
    #Note that newcsv can also be true from the input arguments
    csv_path = Path(csv_file)
    if csv_path.exists() is False:
        newcsv = True
    
    
    if newcsv:
        #Make a new csv. Make the directory first.
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df_kmeans.to_csv(csv_file)
        
    
    for i in range(n):
        
        #Control the number of threads in kmeans
        with threadpool_limits(limits=1, user_api='blas'):
            #Ignore the warning about the memory leak
            warnings.filterwarnings('ignore')
        
            # Fit the k-means model to the data
            kmeans = KMeans(n_clusters=num_clusters).fit(X)

        #Load the csv, add a column for the kmeans cluster labels, then save
        df_kmeans = pd.read_csv(csv_file,index_col=0)
        df_kmeans[f'kmeans_{i+1}'] = kmeans.labels_
        df_kmeans.to_csv(csv_file)
        

    return df_kmeans