# Sentiment Analysis with TFLearn

In this notebook, we'll build upon our previous project - ["Sentiment Analysis from Scratch"](https://srikanthpagadala.github.io/notes/2017/02/05/sentiment-analysis-from-scratch)  by building a network for sentiment analysis on the movie review data. Instead of a network written with Numpy, we'll be using [TFLearn](http://tflearn.org/), a high-level library built on top of TensorFlow. TFLearn makes it simpler to build networks just by defining the layers. It takes care of most of the details for you.

[TFLearn](http://tflearn.org/) does a lot of things for you such as initializing weights, running the forward pass, and performing backpropagation to update the weights. You end up just defining the architecture of the network (number and type of layers, number of units, etc.) and how it is trained.


[Report](http://htmlpreview.github.io/?https://github.com/srikanthpagadala/udacity/blob/master/Deep%20Learning%20Nanodegree%20Foundation/Sentiment%20Analysis%20with%20TFLearn/report.html)