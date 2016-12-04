# coding: utf-8

# # Assignment 3:  Recommendation systems
#
# Here we'll implement a content-based recommendation algorithm.
# It will use the list of genres for a movie as the content.
# The data come from the MovieLens project: http://grouplens.org/datasets/movielens/

# Please only use these imports.
from collections import Counter, defaultdict
import math
import numpy as np
import os
import pandas as pd
import re
from scipy.sparse import csr_matrix
import urllib.request
import zipfile

def download_data():
    """ DONE. Download and unzip data.
    """
    url = 'https://www.dropbox.com/s/h9ubx22ftdkyvd5/ml-latest-small.zip?dl=1'
    urllib.request.urlretrieve(url, 'ml-latest-small.zip')
    zfile = zipfile.ZipFile('ml-latest-small.zip')
    zfile.extractall()
    zfile.close()


def tokenize_string(my_string):
    """ DONE. You should use this in your tokenize function.
    """
    return re.findall('[\w\-]+', my_string.lower())


def tokenize(movies):
    """
    Append a new column to the movies DataFrame with header 'tokens'.
    This will contain a list of strings, one per token, extracted
    from the 'genre' field of each movie. Use the tokenize_string method above.
    Note: you may modify the movies parameter directly; no need to make
    a new copy.
    Params:
      movies...The movies DataFrame
    Returns:
      The movies DataFrame, augmented to include a new column called 'tokens'.
    >>> movies = pd.DataFrame([[123, 'Horror|Romance'], [456, 'Sci-Fi']], columns=['movieId', 'genres'])
    >>> movies = tokenize(movies)
    >>> movies['tokens'].tolist()
    [['horror', 'romance'], ['sci-fi']]
    """
    movies['tokens']=np.empty((len(movies), 0)).tolist()
    a=[]
    for ID in sorted(movies.movieId):
        a.append(tokenize_string(movies["genres"][movies.movieId==ID].iloc[0]))
    se=pd.Series(a)
    movies['tokens']=se.values
    return(movies)

def featurize(movies):
    """
    Append a new column to the movies DataFrame with header 'features'.
    Each row will contain a csr_matrix of shape (1, num_features). Each
    entry in this matrix will contain the tf-idf value of the term, as
    defined in class:
    tfidf(i, d) := tf(i, d) / max_k tf(k, d) * log10(N/df(i))
    where:
    i is a term
    d is a document (movie)
    tf(i, d) is the frequency of term i in document d
    max_k tf(k, d) is the maximum frequency of any term in document d
    N is the number of documents (movies)
    df(i) is the number of unique documents containing term i
    Params:
      movies...The movies DataFrame
    Returns:
      A tuple containing:
      - The movies DataFrame, which has been modified to include a column named 'features'.
      - The vocab, a dict from term to int. Make sure the vocab is sorted alphabetically as in a2 (e.g., {'aardvark': 0, 'boy': 1, ...})
    """
    ###TODO
    pass
    N=len(movies)
    featlist=[]
    a=[]
    lis=movies['tokens'].tolist()
    for i in lis:
        for ii in set(i):
            a.append(ii)
    C=Counter(a)
    def tf(term,D):
        CCC=dict.fromkeys(C,0)
        x=0
        for i in D:
            if term==i:
                x+=1
            CCC[i]+=1
        return x,CCC[max(CCC, key=CCC.get)]
    for i,j in movies.iterrows():
        CC=dict.fromkeys(C,0)
        for tok in j.tokens:
            tval,mf=tf(tok,j.tokens)
            df=math.log10(N/C[tok])
            CC[tok]+=(tval/mf)*df
        featlist.append(csr_matrix([CC[ii] for ii in sorted(CC)],shape=(1,len(C)),dtype=np.float64))
        #print(j.tokens,[CC[ii] for ii in sorted(CC)])
    se=pd.Series(featlist)
    movies['features']=se.values   
    count=0
    CC=dict.fromkeys(C,0)
    for k,v in sorted(C.items()):
        CC[k]=count
        count+=1
    return(movies,CC)

def train_test_split(ratings):
    """DONE.
    Returns a random split of the ratings matrix into a training and testing set.
    """
    test = set(range(len(ratings))[::1000])
    train = sorted(set(range(len(ratings))) - test)
    test = sorted(test)
    return ratings.iloc[train], ratings.iloc[test]

def cosine_sim(a, b):
    """
    Compute the cosine similarity between two 1-d csr_matrices.
    Each matrix represents the tf-idf feature vector of a movie.
    Params:
      a...A csr_matrix with shape (1, number_features)
      b...A csr_matrix with shape (1, number_features)
    Returns:
      The cosine similarity, defined as: dot(a, b) / ||a|| * ||b||
      where ||a|| indicates the Euclidean norm (aka L2 norm) of vector a.
    """
    return (np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)))

def make_predictions(movies, ratings_train, ratings_test):
    """
    Using the ratings in ratings_train, predict the ratings for each
    row in ratings_test.
    To predict the rating of user u for movie i: Compute the weighted average
    rating for every other movie that u has rated.  Restrict this weighted
    average to movies that have a positive cosine similarity with movie
    i. The weight for movie m corresponds to the cosine similarity between m
    and i.
    If there are no other movies with positive cosine similarity to use in the
    prediction, use the mean rating of the target user in ratings_train as the
    prediction.
    Params:
      movies..........The movies DataFrame.
      ratings_train...The subset of ratings used for making predictions. These are the "historical" data.
      ratings_test....The subset of ratings that need to predicted. These are the "future" data.
    Returns:
      A numpy array containing one predicted rating for each element of ratings_test.
    """
    ###TODO
    pass
    val=0
    rat=0
    prediction=list()
    #in case no other movies with positive cosine similarity, using Mean user rating in place of nan
    meanval=ratings_train.groupby(ratings_train.userId).mean()
    def isNaN(val,userID):
        if(math.isnan(val)):
            return meanval.rating[meanval.index==userID].iloc[0]
        else:
            return val
    for indexi,rowi in ratings_test.iterrows():
        for indexj,rowj in ratings_train[ratings_train.userId==rowi.userId].iterrows():
            #print(movies['tokens'][movies.movieId==rowi.movieId].iloc[0],movies['tokens'][movies.movieId==rowj.movieId].iloc[0],cosine(movies["features"][movies.movieId==rowj.movieId].iloc[0],movies["features"][movies.movieId==rowi.movieId].iloc[0]),ratings_train['rating'][(ratings_train['movieId']==rowj.movieId) & (ratings_train['userId'] == rowj.userId)].iloc[0])
            cosine_val=cosine_sim(movies["features"][movies.movieId==rowj.movieId].iloc[0].toarray().tolist()[0],movies["features"][movies.movieId==rowi.movieId].iloc[0].toarray().tolist()[0])
            #print(cosine_val)
            if(cosine_val>0):
                val+=cosine_val*rowj.rating
                rat+=cosine_val
            elif(np.isnan(cosine_val)):
                val+=cosine_val*rowj.rating
                rat+=cosine_val
        #print("User",rowi.userId,"rated Movie'",movies['title'][movies.movieId==rowi.movieId].iloc[0],"'as::",isNaN(val/rat)," Orginal Rating::",rowi.rating)
        if(rat==0):
            prediction.append(isNaN(float('nan'),rowi.userId))
        else:
            prediction.append(isNaN(val/rat,rowi.userId))
        val=0
        rat=0
    return np.array(prediction)

def mean_absolute_error(predictions, ratings_test):
    """DONE.
    Return the mean absolute error of the predictions.
    """
    return np.abs(predictions - np.array(ratings_test.rating)).mean()


def main():
    download_data()
    path = 'ml-latest-small'
    ratings = pd.read_csv(path + os.path.sep + 'ratings.csv')
    movies = pd.read_csv(path + os.path.sep + 'movies.csv')
    movies = tokenize(movies)
    movies, vocab = featurize(movies)
    print('vocab:')
    print(sorted(vocab.items())[:10])
    ratings_train, ratings_test = train_test_split(ratings)
    print('%d training ratings; %d testing ratings' % (len(ratings_train), len(ratings_test)))
    predictions = make_predictions(movies, ratings_train, ratings_test)
    print('error=%f' % mean_absolute_error(predictions, ratings_test))
    print(predictions[:10])


if __name__ == '__main__':
    main()