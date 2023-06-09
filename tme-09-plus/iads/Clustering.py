# -*- coding: utf-8 -*-

"""
Package: iads
File: Clustering.py
Année: LU3IN026 - semestre 2 - 2022-2023, Sorbonne Université
"""

# ---------------------------
# Fonctions de Clustering

# import externe
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import scipy.cluster.hierarchy
import math
import random
from scipy.spatial.distance import cdist
# ------------------------ 

def dist_euclidienne(ex1, ex2):
    
    return math.sqrt(np.sum(np.power((ex1 - ex2), 2)))


def normalisation(df):
    df_norm = (df - df.min()) / (df.max() - df.min())
    return df_norm
    
def centroide(df):
    return np.mean(df, axis=0)
    
def dist_centroides(ex1, ex2):
    return dist_euclidienne(centroide(ex1), centroide(ex2))
    
def initialise_CHA(df):
    return {i:[i] for i in range(len(df))}
    
def fusionne(df, partition, verbose=False):
    dist_min = +np.inf
    k1_min, k2_min = -1,-1
    p_new = dict(partition)
    for k1,v1 in partition.items():
        for k2,v2 in partition.items():
            if k1!=k2:
                dist= dist_centroides(df.iloc[v1], df.iloc[v2])
                if dist < dist_min:
                    dist_min = dist
                    k1_min, k2_min = k1, k2
    if k1_min != -1:
        del p_new[k1_min]
        del p_new[k2_min]
        p_new[max(partition)+1] = [*partition[k1_min], *partition[k2_min]]
        if verbose:
            print(f'Distance mininimale trouvée entre  [{k1_min}, {k2_min}]  =  {dist_min}')
    return p_new, k1_min, k2_min, dist_min
    
    
def CHA_centroid(df):
    partition = initialise_CHA(df)
    distances = []
    for i in range(len(df)-1):
        partition, i, j, dist = fusionne(df, partition)
        distances.append([i, j, dist, len(partition[max(partition.keys())])])
    return distances
    
    

def CHA_centroid(df, verbose=False, dendrogramme=False):
    partition = initialise_CHA(df)
    distances = []
    for i in range(len(df)-1):
        partition, i, j, dist = fusionne(df, partition, verbose)
        distances.append([i, j, dist, len(partition[max(partition.keys())])])
    if dendrogramme:
        plt.figure(figsize=(30, 15)) # taille : largeur x hauteur
        plt.title('Dendrogramme', fontsize=25)    
        plt.xlabel("Indice d'exemple", fontsize=25)
        plt.ylabel('Distance', fontsize=25)

        # Construction du dendrogramme pour notre clustering :
        scipy.cluster.hierarchy.dendrogram(
            CHA_centroid(df), 
            leaf_font_size=24.,  # taille des caractères de l'axe des X
        )

        # Affichage du résultat obtenu:
        plt.show()
        
    return distances


def dist_linkage_clusters(linkage, dist_func, arr1, arr2):
    r = cdist(arr1, arr2, dist_func)
    if linkage == 'complete':
        return np.max(r)
    if linkage == 'simple':
        return np.min(r)
    if linkage == 'average':
        return np.mean(r)
    
def fusionne_linkage(linkage, df, in_partition, dist_func='euclidean', verbose=False):
    dist_min = +np.inf
    k1_min, k2_min = -1, -1
    for k1, v1 in in_partition.items():
        for k2, v2 in in_partition.items():
            if k1 == k2:
                continue
            dist = dist_linkage_clusters(linkage, dist_func, df.iloc[v1], df.iloc[v2])
            if dist < dist_min:
                dist_min = dist
                k1_min, k2_min = k1, k2
    out_partition = dict(in_partition)
    if k1_min != -1:
        del out_partition[k1_min]
        del out_partition[k2_min]
        out_partition[max(in_partition)+1] = [*in_partition[k1_min], *in_partition[k2_min]]
    if verbose:
        print(f'Distance mininimale trouvée entre  [{k1_min}, {k2_min}]  =  {dist_min}')
    return out_partition, k1_min, k2_min, dist_min


def clustering_hierarchique_linkage(linkage, df, dist_func='euclidean', 
                                    verbose=False, dendrogramme=False):
    partition = initialise_CHA(df)
    results = []
    for _ in range(len(df)):
        partition, k1, k2, dist = fusionne_linkage(linkage, df, partition, 
                                                   dist_func, verbose)
        results.append([k1, k2, dist, len(partition[max(partition.keys())])])
    results = results[:-1]
    if dendrogramme:
        plt.figure(figsize=(30, 15))
        plt.title('Dendrogramme', fontsize=25)    
        plt.xlabel("Indice d'exemple", fontsize=25)
        plt.ylabel('Distance', fontsize=25)
        scipy.cluster.hierarchy.dendrogram(results, leaf_font_size=24.)
        plt.show()
    return results

def clustering_hierarchique_complete(df, dist_func='euclidean', 
                                    verbose=False, dendrogramme=False):
    return clustering_hierarchique_linkage('complete', df, dist_func,
                                          verbose, dendrogramme)
def clustering_hierarchique_simple(df, dist_func='euclidean', 
                                    verbose=False, dendrogramme=False):
    return clustering_hierarchique_linkage('simple', df, dist_func,
                                          verbose, dendrogramme)
def clustering_hierarchique_average(df, dist_func='euclidean', 
                                    verbose=False, dendrogramme=False):
    return clustering_hierarchique_linkage('average', df, dist_func,
                                          verbose, dendrogramme)
                                          
def CHA(DF,linkage='centroid', dist="euclidiean", verbose=False,dendrogramme=False):
    """
    
    """
    if linkage == "simple" :
        return clustering_hierarchique_simple(DF,dist, verbose, dendrogramme)
    elif linkage == "complete" :
        return clustering_hierarchique_complete(DF,dist, verbose, dendrogramme)
    elif linkage == "average" :
        return clustering_hierarchique_average(DF,dist, verbose, dendrogramme)
    elif linkage == "centroid" :
        return CHA_centroid(DF,verbose, dendrogramme)



def inertie_cluster(Ens):
    centre = Ens.mean()
    inertie = np.sum(np.linalg.norm(Ens - centre, axis=1) ** 2)
    return inertie
    
    
def init_kmeans(K,Ens):
    return np.asarray(random.sample(list(np.array(Ens)), K))
    
    
def plus_proche(Exe,Centres):
    l = [dist_euclidienne(Exe,c) for c in Centres]
    return np.argmin(l)
    

def affecte_cluster(Base,Centres):
    Y = np.argmin(cdist(Base, Centres), axis=1)
    return {c:list(np.where(Y==c)[0]) for c in range(len(Centres))}


def nouveaux_centroides(Base,U):
    return np.array([np.mean(np.array(Base)[i], axis=0) for i in U.values()])

def inertie_globale(Base, U):
    somme = 0
    for key in U:
        newBase = Base.iloc[U[key]]
        somme += inertie_cluster(newBase)
    return somme

def kmoyennes(K, base, epsilon, iter_max, verbose=True):
    #initialisation :
    ig = 0 #inertie globale
    Centres = init_kmeans(K, base) #ensemble des centroides
    U = {} #matrice d'affectation vide au début
    for i in range(iter_max):
        U = affecte_cluster(base, Centres) 
        ig_cur = inertie_globale(base, U) 
        print(f'iteration {i} Inertie : {ig_cur:.4f} Difference: {np.abs(ig_cur-ig):.4f}')
        if np.abs(ig_cur-ig) < epsilon: 
            break
        ig = ig_cur
        Centres = nouveaux_centroides(base, U)
    return Centres, U

def affiche_resultat(Base,Centres,Affect):
    couleurs = cm.tab20(np.linspace(0, 1, 20))
    c = 0
    for v in Affect.values():
        for i in v:
            plt.scatter(Base.iloc[i,0],Base.iloc[i,1],color=couleurs[c])
        c += 1
    plt.scatter(Centres[:,0], Centres[:,1], color='r', marker='x')
    plt.show()