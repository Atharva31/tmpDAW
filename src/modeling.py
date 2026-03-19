"""Modeling module: PCA, clustering, evaluation."""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering, KMeans, DBSCAN
from sklearn.metrics import (
    silhouette_score,
    silhouette_samples,
    davies_bouldin_score,
    calinski_harabasz_score,
)
import matplotlib.pyplot as plt
import seaborn as sns


def standardize_features(feature_matrix):
    """
    Standardize features to zero mean, unit variance.

    Parameters
    ----------
    feature_matrix : pd.DataFrame or np.ndarray

    Returns
    -------
    tuple: (scaler, std_features)
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
    variance_threshold : float

    Returns
    -------
    dict with keys: pca, transformed, n_components, explained_variance_ratio, cumulative_variance
    """
    pca_full = PCA()
    pca_full.fit(std_features)
    cumsum_var = np.cumsum(pca_full.explained_variance_ratio_)
    n_comp = np.argmax(cumsum_var >= variance_threshold) + 1

    pca = PCA(n_components=n_comp)
    transformed = pca.fit_transform(std_features)

    print(f"[PCA] Selected {n_comp} components explaining {cumsum_var[n_comp-1]:.2%} variance")
    print(f"[PCA] Explained variance per component: {pca.explained_variance_ratio_}")

    return {
        'pca': pca,
        'transformed': transformed,
        'n_components': n_comp,
        'explained_variance_ratio': pca.explained_variance_ratio_,
        'cumulative_variance': cumsum_var[:n_comp],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Individual clustering algorithms
# ─────────────────────────────────────────────────────────────────────────────

def apply_clustering(pca_data, k_min=2, k_max=7):
    """
    Agglomerative Hierarchical Clustering (Ward linkage).
    Sweeps k from k_min to k_max, selects optimal k via silhouette score.

    Returns
    -------
    dict with keys: clustering, labels, optimal_k, silhouette_scores, best_silhouette
    """
    transformed = pca_data['transformed']
    silhouette_scores = {}

    for k in range(k_min, k_max + 1):
        labels = AgglomerativeClustering(n_clusters=k, linkage='ward').fit_predict(transformed)
        score = silhouette_score(transformed, labels)
        silhouette_scores[k] = score
        print(f"[Hierarchical] k={k}: silhouette = {score:.4f}")

    optimal_k = max(silhouette_scores, key=silhouette_scores.get)
    print(f"[Hierarchical] Optimal k = {optimal_k} (silhouette = {silhouette_scores[optimal_k]:.4f})")

    final_labels = AgglomerativeClustering(n_clusters=optimal_k, linkage='ward').fit_predict(transformed)

    return {
        'clustering': AgglomerativeClustering(n_clusters=optimal_k, linkage='ward'),
        'labels': final_labels,
        'optimal_k': optimal_k,
        'silhouette_scores': silhouette_scores,
        'best_silhouette': silhouette_scores[optimal_k],
    }


def apply_kmeans(pca_data, k_min=2, k_max=7, random_state=42):
    """
    K-Means clustering. Sweeps k from k_min to k_max.
    Selects optimal k via silhouette score.

    Returns
    -------
    dict with keys: labels, optimal_k, silhouette_scores, inertia_scores, best_silhouette
    """
    transformed = pca_data['transformed']
    silhouette_scores = {}
    inertia_scores = {}

    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = km.fit_predict(transformed)
        sil = silhouette_score(transformed, labels)
        silhouette_scores[k] = sil
        inertia_scores[k] = km.inertia_
        print(f"[K-Means] k={k}: silhouette = {sil:.4f}, inertia = {km.inertia_:.2f}")

    optimal_k = max(silhouette_scores, key=silhouette_scores.get)
    print(f"[K-Means] Optimal k = {optimal_k} (silhouette = {silhouette_scores[optimal_k]:.4f})")

    final_km = KMeans(n_clusters=optimal_k, random_state=random_state, n_init=10)
    final_labels = final_km.fit_predict(transformed)

    return {
        'labels': final_labels,
        'optimal_k': optimal_k,
        'silhouette_scores': silhouette_scores,
        'inertia_scores': inertia_scores,
        'best_silhouette': silhouette_scores[optimal_k],
    }


def apply_dbscan(pca_data, eps_values=None, min_samples=5):
    """
    DBSCAN clustering. Sweeps over eps values to find best configuration
    (ignores noise points for metric computation).

    Returns
    -------
    dict with keys: labels, best_eps, n_clusters, n_noise, silhouette_scores, best_silhouette
    """
    transformed = pca_data['transformed']

    if eps_values is None:
        # Heuristic: try a range around typical PCA-space distances
        eps_values = [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]

    results = {}

    for eps in eps_values:
        labels = DBSCAN(eps=eps, min_samples=min_samples).fit_predict(transformed)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = (labels == -1).sum()

        if n_clusters < 2:
            print(f"[DBSCAN] eps={eps}: {n_clusters} cluster(s), {n_noise} noise — skipping (need ≥2 clusters)")
            continue

        # Silhouette computed only on non-noise points
        mask = labels != -1
        if mask.sum() < 2:
            continue

        sil = silhouette_score(transformed[mask], labels[mask])
        results[eps] = {
            'labels': labels,
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'silhouette': sil,
        }
        print(f"[DBSCAN] eps={eps}: {n_clusters} clusters, {n_noise} noise points, silhouette = {sil:.4f}")

    if not results:
        print("[DBSCAN] No valid configuration found. Try adjusting eps_values or min_samples.")
        return None

    best_eps = max(results, key=lambda e: results[e]['silhouette'])
    best = results[best_eps]
    print(f"[DBSCAN] Best eps={best_eps}: {best['n_clusters']} clusters, silhouette = {best['silhouette']:.4f}")

    return {
        'labels': best['labels'],
        'best_eps': best_eps,
        'n_clusters': best['n_clusters'],
        'n_noise': best['n_noise'],
        'silhouette_scores': {e: r['silhouette'] for e, r in results.items()},
        'best_silhouette': best['silhouette'],
        'all_results': results,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Algorithm comparison
# ─────────────────────────────────────────────────────────────────────────────

def compare_algorithms(pca_data, hierarchical_result, kmeans_result, dbscan_result=None):
    """
    Compute Davies-Bouldin and Calinski-Harabasz scores for each algorithm
    at its optimal k and produce a comparison summary table.

    Parameters
    ----------
    pca_data : dict — output of apply_pca()
    hierarchical_result : dict — output of apply_clustering()
    kmeans_result : dict — output of apply_kmeans()
    dbscan_result : dict or None — output of apply_dbscan()

    Returns
    -------
    pd.DataFrame — comparison table
    """
    transformed = pca_data['transformed']

    rows = []

    # Hierarchical
    h_labels = hierarchical_result['labels']
    rows.append({
        'Algorithm': f"Hierarchical (k={hierarchical_result['optimal_k']})",
        'Silhouette ↑': round(silhouette_score(transformed, h_labels), 4),
        'Davies-Bouldin ↓': round(davies_bouldin_score(transformed, h_labels), 4),
        'Calinski-Harabasz ↑': round(calinski_harabasz_score(transformed, h_labels), 2),
        'n_clusters': hierarchical_result['optimal_k'],
        'n_noise': 0,
    })

    # K-Means
    km_labels = kmeans_result['labels']
    rows.append({
        'Algorithm': f"K-Means (k={kmeans_result['optimal_k']})",
        'Silhouette ↑': round(silhouette_score(transformed, km_labels), 4),
        'Davies-Bouldin ↓': round(davies_bouldin_score(transformed, km_labels), 4),
        'Calinski-Harabasz ↑': round(calinski_harabasz_score(transformed, km_labels), 2),
        'n_clusters': kmeans_result['optimal_k'],
        'n_noise': 0,
    })

    # DBSCAN (if valid)
    if dbscan_result is not None:
        db_labels = dbscan_result['labels']
        mask = db_labels != -1
        if mask.sum() >= 2 and len(set(db_labels[mask])) >= 2:
            rows.append({
                'Algorithm': f"DBSCAN (eps={dbscan_result['best_eps']})",
                'Silhouette ↑': round(silhouette_score(transformed[mask], db_labels[mask]), 4),
                'Davies-Bouldin ↓': round(davies_bouldin_score(transformed[mask], db_labels[mask]), 4),
                'Calinski-Harabasz ↑': round(calinski_harabasz_score(transformed[mask], db_labels[mask]), 2),
                'n_clusters': dbscan_result['n_clusters'],
                'n_noise': dbscan_result['n_noise'],
            })

    comparison_df = pd.DataFrame(rows).set_index('Algorithm')

    print("\n" + "=" * 70)
    print("ALGORITHM COMPARISON SUMMARY")
    print("=" * 70)
    print(comparison_df.to_string())
    print("\nBest Silhouette  :", comparison_df['Silhouette ↑'].idxmax())
    print("Best Davies-Bouldin:", comparison_df['Davies-Bouldin ↓'].idxmin())
    print("Best Calinski-Harabasz:", comparison_df['Calinski-Harabasz ↑'].idxmax())

    return comparison_df


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation (cluster profiling)
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_clustering(df, pca_data, clustering_data):
    """
    Evaluate clustering: silhouette samples, cluster profiles, city distribution.

    Parameters
    ----------
    df : pd.DataFrame — original dataset with ZIP, city, features
    pca_data : dict — output of apply_pca()
    clustering_data : dict — output of any clustering function

    Returns
    -------
    dict with keys: df_clustered, silhouette_values, profiles, city_distribution
    """
    transformed = pca_data['transformed']
    labels = clustering_data['labels']

    df_clustered = df.copy()
    df_clustered['cluster'] = labels

    silhouette_vals = silhouette_samples(transformed, labels)

    profile_cols = [
        'electricity_per_customer',
        'electricity_per_capita',
        'renter_occupancy_rate',
        'housing_age',
        'income_log',
        'median_income',
    ]

    profiles = df_clustered.groupby('cluster')[profile_cols].mean()
    city_dist = pd.crosstab(df_clustered['cluster'], df_clustered['city'], margins=True)

    print(f"\n[Evaluation] Cluster Profiles (means):")
    print(profiles)
    print(f"\n[Evaluation] Cluster distribution by city:")
    print(city_dist)

    return {
        'df_clustered': df_clustered,
        'silhouette_values': silhouette_vals,
        'profiles': profiles,
        'city_distribution': city_dist,
    }
