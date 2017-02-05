# Deep Traffic

[DeepTraffic](http://selfdrivingcars.mit.edu/deeptrafficjs/) is a gamified simulation of typical highway traffic. Your task is to build a neural agent – more specifically design and train a neural network that performs well on high traffic roads. Your neural network gets to control one of the cars (displayed in red) and has to learn how to navigate efficiently to go as fast as possible. The car already comes with a safety system, so you don’t have to worry about the basic task of driving – the net only has to tell the car if it should accelerate/slow down or change lanes, and it will do so if that is possible without crashing into other cars.

The network here is attempting to learn a driving strategy such that the car is moving as fast as possible using [reinforcement learning](https://en.wikipedia.org/wiki/Reinforcement_learning). The network is rewarded when the car chooses actions that result in it moving fast. It's this feedback that allows the network to find a strategy of actions for optimal speed.

To learn more about setting the parameters and training the network, read the overview [here](http://selfdrivingcars.mit.edu/deeptraffic/).

