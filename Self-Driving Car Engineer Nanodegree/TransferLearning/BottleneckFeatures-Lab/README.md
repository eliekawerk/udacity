# Transfer Learning Lab with VGG, Inception and ResNet

In this lab, you will continue exploring transfer learning. You've already explored feature extraction with AlexNet and TensorFlow. Next, you will use Keras to explore feature extraction with the VGG, Inception and ResNet architectures. The models you will use were trained for days or weeks on the [ImageNet dataset](http://www.image-net.org/). Thus, the weights encapsulate higher-level features learned from training on thousands of classes.

We'll use two datasets in this lab:

1. German Traffic Sign Dataset
2. Cifar10

Unless you have a powerful GPU, running feature extraction on these models will take a significant amount of time. To make things we precomputed **bottleneck features** for each (network, dataset) pair, this will allow you experiment with feature extraction even on a modest CPU. You can think of bottleneck features as feature extraction but with caching.  Because the base network weights are frozen during feature extraction, the output for an image will always be the same. Thus, once the image has already been passed once through the network we can cache and reuse the output.

The files are encoded as such:

- {network}_{dataset}_bottleneck_features_train.p
- {network}_{dataset}_bottleneck_features_validation.p

network can be one of 'vgg', 'inception', or 'resnet'

dataset can be on of 'cifar10' or 'traffic'

How will the pretrained model perform on the new datasets?

Bottleneck Features

- [VGG Bottleneck Features 100](https://d17h27t6h515a5.cloudfront.net/topher/2016/November/5834b432_vgg-100/vgg-100.zip)
- [ResNet Bottleneck Features 100](https://d17h27t6h515a5.cloudfront.net/topher/2016/November/5834b634_resnet-100/resnet-100.zip)
- [InceptionV3 Bottleneck Features 100](https://d17h27t6h515a5.cloudfront.net/topher/2016/November/5834b498_inception-100/inception-100.zip)