"""Modeling module: PCA, clustering, evaluation."""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score, silhouette_samples
import matplotlib.pyplot as plt
import seaborn as sns


def standardize_features(feature_matrix):
    """
    Standardize features to zero mean, unit variance.
    
    Parameters
    ----------
    feature_matrix : pd.DataFrame or np.ndarray
        Feature matrix (n_samples, n_features).
    
    Returns
    -------
    np.ndarray
        Standardized features.
    tuple
        (scaler, std_features) for later inverse transform if needed.
    """
    scaler = StandardScaler()
    std_features = scaler.fit_transform(feature_matrix)
    
    print(f"[Standardize] Standardized {std_features.shape[1]} features for {std_features.shape[0]} ZIPs")
    
    return scaler, std_features


def apply_pca(std_features, variance_threshold=0.85):
    """
    Apply PCA and select components explaining >= variance_threshold.
    
    Parameters
    ----------
    std_features : np.ndarray
        Standardized feature matrix.
    variance_threshold : float
        Cumulative variance explained threshold (default 0.85 = 85%).
    
    Returns
    -------
    dict
        {
            'pca': PCA model,
            'transformed': transformed features,
            'n_components': number of components,
            'explained_variance_ratio': explained variance per component,
            'cumulative_variance': cumulative explained variance
        }
    """
    # Fit PCA with all components
    pca_full = PCA()
    pca_full.fit(std_features)
    
    # Calculate cumulative variance
    cumsum_var = np.cumsum(pca_full.explained_variance_ratio_)
    
    # Find number of components for threshold
    n_comp = np.argmax(cumsum_var >= variance_threshold) + 1
    
    # Refit with selected components
    pca = PCA(n_components=n_comp)
    transformed = pca.fit_transform(std_features)
    
    print(f"[PCA] Selected {n_comp} components explaining {cumsum_var[n_comp-1]:.2%} variance")
    print(f"[PCA] Explained variance per component: {pca.explained_variance_ratio_}")
    
    return {
        'pca': pca,
        'transformed': transformed,
        'n_components': n_comp,
        'explained_variance_ratio': pca.explained_variance_ratio_,
        'cumulative_variance': cumsum_var[:n_comp]
    }


def apply_clustering(pca_data, k_min=2, k_max=7):
    """
    Apply agglomerative hierarchical clustering, select k via silhouette score.
    
    Parameters
    ----------
    pca_data : dict
        Output from apply_pca().
    k_min : int
        Minimum number of clusters to test.
    k_max : int
        Maximum number of clusters to test.
    
    Returns
    -------
    dict
        {
            'clustering': fitted clustering model,
            'labels': cluster labels,
            'optimal_k': selected number of clusters,
            'silhouette_scores': scores for each k,
            'best_silhouette': best silhouette score
        }
    """
    transformed = pca_data['transformed']
    
    silhouette_scores = {}
    
    for k in range(k_min, k_max + 1):
        clusterer = AgglomerativeClustering(n_clusters=k, linkage='ward')
        cluster_labels = clusterer.fit_predict(transformed)
        
        score = silhouette_score(transformed, cluster_labels)
        silhouette_scores[k] = score
        print(f"[Clustering] k={k}: silhouette score = {score:.4f}")
    
    # Select k with best silhouette score
    optimal_k = max(silhouette_scores, key=silhouette_scores.get)
    best_score = silhouette_scores[optimal_k]
    
    print(f"[Clustering] Optimal k = {optimal_k} with silhouette score = {best_score:.4f}")
    
    # Fit final clustering
    final_clustering = AgglomerativeClustering(n_clusters=optimal_k, linkage='ward')
    final_labels = final_clustering.fit_predict(transformed)
    
    return {
        'clustering': final_clustering,
        'labels': final_labels,
        'optimal_k': optimal_k,
        'silhouette_scores': silhouette_scores,
        'best_silhouette': best_score
    }


def evaluate_clustering(df, pca_data, clustering_data):
    """
    Evaluate clustering: silhouette samples, cluster profiles, etc.
    
    Parameters
    ----------
    df : pd.DataFrame
        Original dataset with ZIP, city, etc.
    pca_data : dict
        Output from apply_pca().
    clustering_data : dict
        Output from apply_clustering().
    
    Returns
    -------
    dict
        Evaluation metrics and cluster profiles.
    """
    transformed = pca_data['transformed']
    labels = clustering_data['labels']
    optimal_k = clustering_data['optimal_k']
    
    # Add cluster labels to dataframe
    df_clustered = df.copy()
    df_clustered['cluster'] = labels
    
    # Silhouette samples
    silhouette_vals = silhouette_samples(transformed, labels)
    
    # Cluster profiles: mean values per cluster
    profile_cols = [
        'electricity_per_customer',
        'electricity_per_capita',
        'renter_occupancy_rate',
        'housing_age',
        'income_log',
        'median_income'
    ]
    
    profiles = df_clustered.groupby('cluster')[profile_cols].mean()
    
    # Distribution across cities
    city_dist = pd.crosstab(df_clustered['cluster'], df_clustered['city'], margins=True)
    
    print(f"\n[Evaluation] Cluster Profiles (means):")
    print(profiles)
    print(f"\n[Evaluation] Cluster distribution by city:")
    print(city_dist)
    
    return {
        'df_clustered': df_clustered,
        'silhouette_values': silhouette_vals,
        'profiles': profiles,
        'city_distribution': city_dist
    }
