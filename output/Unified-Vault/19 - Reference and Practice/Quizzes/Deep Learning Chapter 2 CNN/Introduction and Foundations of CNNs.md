---
title: Introduction and Foundations of CNNs
type: example
aliases:
  - "Q1 - Introduction and Foundations of CNNs"
  - "Introduction and Foundations of CNNs Quiz"
  - "CNN Foundations Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - cnn
  - neural-networks
  - artificial-neuron
  - weights
  - bias
  - activation-functions
  - layers
  - fully-connected
sources:
  - "Q1 - Introduction and Foundations of CNNs"
created_index: 34
---

This quiz bank opens the CNN chapter at its foundations: what a neural network is, what an individual neuron computes, and why weights, biases, activation functions, and layers together give networks their expressive power. Its twenty-nine questions — ten true-or-false, nine multiple choice, and ten matching — cover the biological inspiration behind the model, the division of labor between weights, bias, and activation, the collapse into a single linear transformation when non-linearity is missing, and the roles of input, hidden, output, and fully connected layers. The concepts are developed in [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]] and [[Artificial Neural Networks]], with the activation functions themselves treated in [[Activation Functions]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: four on the artificial neuron and its weights and bias, three on activation functions and the non-linearity they supply, and three on layer types and what their names mean. The false statements credit a component with power it does not have — complex functions from a single neuron, learnable parameters in the input layer, "hidden" meaning observed rather than unobserved — so check each claim against what the part actually does.

### The artificial neuron

Four statements on the biological inspiration behind the model, the job of the bias, the job of the weights, and the limits of a single neuron on its own.

> [!question] A neural network is a computational model loosely inspired by the way biological neurons in the human brain process information.
>> [!success]- Answer
>> True

> [!question] The bias in a neuron shifts the entire weighted sum up or down before the activation function is applied.
>> [!success]- Answer
>> True

> [!question] In a neural network, weights determine how much influence each input has on the neuron's output.
>> [!success]- Answer
>> True

> [!question] A single artificial neuron by itself can learn very complex functions without being organized into layers.
>> [!success]- Answer
>> False

### Activation and non-linearity

Three statements on what a network can and cannot learn without an activation function, the definition of ReLU, and the collapse that missing non-linearity causes regardless of depth.

> [!question] Without an activation function, a neural network could still learn complex non-linear patterns.
>> [!success]- Answer
>> False

> [!question] The ReLU activation function is defined as f(z) = max(0, z).
>> [!success]- Answer
>> True

> [!question] Without non-linearity introduced by activation functions, a neural network would collapse into a single linear transformation regardless of its depth.
>> [!success]- Answer
>> True

### Layer types and their names

Three statements on full connectivity, the learnable-parameter status of the input layer, and why hidden layers are called "hidden".

> [!question] In a fully connected layer, every neuron is connected to every neuron in the previous layer.
>> [!success]- Answer
>> True

> [!question] The input layer of a neural network consists of neurons with learnable parameters.
>> [!success]- Answer
>> False

> [!question] Hidden layers in a neural network are called "hidden" because their values are directly observed and not learned from data.
>> [!success]- Answer
>> False

## Multiple choice

Nine questions work through the neuron's parts, the mathematics of its output, and the naming and purpose of the layers. The wrong options usually attach a real job to the wrong component — non-linearity credited to the bias, decision-making credited to the input layer — so match each role to the part that actually performs it.

### The building block and its parts

Two questions on the fundamental unit of every network and the primary purpose of the bias.

> [!question] What is the fundamental building block of every neural network?
> a) Layer
> b) Activation function
> c) Artificial neuron
> d) Weight matrix
>> [!success]- Answer
>> c) Artificial neuron

> [!question] What is the primary purpose of the bias in an artificial neuron?
> a) To determine how much influence each input has
> b) To shift the entire weighted sum before activation
> c) To introduce non-linearity into the network
> d) To normalize the inputs
>> [!success]- Answer
>> b) To shift the entire weighted sum before activation

### Activation functions and their outputs

Three questions on the consequence of using no activation, the definition of the sigmoid, and ReLU evaluated at a negative input.

> [!question] What would happen if you used no activation function in a neural network?
> a) The network would become more powerful
> b) The network would collapse into a single linear transformation
> c) The network would only be able to classify binary problems
> d) The network would require more training data
>> [!success]- Answer
>> b) The network would collapse into a single linear transformation

> [!question] Which activation function is defined as f(z) = 1/(1+e^-z)?
> a) ReLU
> b) Sigmoid
> c) Tanh
> d) Softmax
>> [!success]- Answer
>> b) Sigmoid

> [!question] What is the output of a ReLU activation function when the input is -0.5?
> a) -0.5
> b) 0
> c) 0.5
> d) 1
>> [!success]- Answer
>> b) 0

### Layers and the network equation

Four questions on the layer type that does not exist, the meaning of w⊤x in y = f(w⊤x + b), the role of the input layer, and the reason hidden layers carry their name.

> [!question] Which of the following is NOT a common type of layer in a neural network?
> a) Input layer
> b) Hidden layer
> c) Output layer
> d) Bias layer
>> [!success]- Answer
>> d) Bias layer

> [!question] In the equation y = f(w⊤x + b), what does the term w⊤x represent?
> a) The activation function
> b) The bias term
> c) The weighted sum of inputs
> d) The final output
>> [!success]- Answer
>> c) The weighted sum of inputs

> [!question] What is the role of the input layer in a neural network?
> a) It contains neurons with learnable parameters
> b) It processes the raw input data
> c) It makes the final decision or prediction
> d) It normalizes the data before processing
>> [!success]- Answer
>> b) It processes the raw input data

> [!question] Why are hidden layers called "hidden"?
> a) Because they use hidden activation functions
> b) Because their values are not directly observed
> c) Because they are not used during training
> d) Because they are located in the middle of the network
>> [!success]- Answer
>> b) Because their values are not directly observed

## Matching

Ten matching questions pair the network's components with their descriptions, mathematical representations, and purposes, the activation functions with their formulas, the layer types with their characteristics and positions, and the big ideas — function approximation, expressive power, decision boundaries, excitation and inhibition — with their meanings. The truth-value question mixes True and False targets among its options, so anchor each pair on its definition rather than its position in the list.

### Components and their definitions

Three questions matching network components to their descriptions, their mathematical representations, and their purposes.

> [!question] Match the neural network components with their descriptions.
>> [!example] Group A
>> a) Weights
>> b) Bias
>> c) Activation function
>
>> [!example] Group B
>> n) Learnable parameter that determines influence of each input
>> o) Special number that shifts the weighted sum
>> p) Introduces non-linearity into the network
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the following neural network components with their mathematical representations.
>> [!example] Group A
>> a) Weighted sum
>> b) Bias term
>> c) Activation output
>
>> [!example] Group B
>> n) ∑wi*xi
>> o) b
>> p) f(w⊤x + b)
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the following neural network concepts with their purposes.
>> [!example] Group A
>> a) Weights
>> b) Biases
>> c) Activation functions
>
>> [!example] Group B
>> n) Determine influence of each input
>> o) Shift the decision boundary
>> p) Enable learning of complex patterns
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Activation functions and their mathematics

One question pairing ReLU, Sigmoid, and Tanh with their definitions.

> [!question] Match the activation functions with their mathematical definitions.
>> [!example] Group A
>> a) ReLU
>> b) Sigmoid
>> c) Tanh
>
>> [!example] Group B
>> n) f(z) = max(0, z)
>> o) f(z) = 1/(1+e^-z)
>> p) f(z) = tanh(z)
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Layer types

Two questions on the characteristics that distinguish input, hidden, and fully connected layers, and on the position each layer type occupies in a typical network.

> [!question] Match the types of neural network layers with their characteristics.
>> [!example] Group A
>> a) Input layer
>> b) Hidden layer
>> c) Fully connected layer
>
>> [!example] Group B
>> n) Contains the raw input data
>> o) Internal representations that the network learns
>> p) Every neuron connected to every neuron in previous layer
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the following layer types with their positions in a typical neural network.
>> [!example] Group A
>> a) Input layer
>> b) Hidden layer
>> c) Output layer
>
>> [!example] Group B
>> n) First layer that receives raw data
>> o) Middle layers between input and output
>> p) Final layer that produces predictions
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### What networks compute

Two questions on function approximation, linear transformation, and non-linearity as roles, and on expressive power, decision boundary, and internal representations as properties.

> [!question] Match the following terms with their roles in a neural network.
>> [!example] Group A
>> a) Function approximator
>> b) Linear transformation
>> c) Non-linearity
>
>> [!example] Group B
>> n) What neural networks essentially do
>> o) What a neuron computes without activation
>> p) What gives neural networks their expressive power
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the following neural network properties with their descriptions.
>> [!example] Group A
>> a) Expressive power
>> b) Decision boundary
>> c) Internal representations
>
>> [!example] Group B
>> n) The ability of a network to learn complex patterns
>> o) The surface that separates different classes
>> p) Hidden layer values that the network learns
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### How inputs influence a neuron

One question on excitation, inhibition, and the ignored input.

> [!question] Match the following concepts with their explanations.
>> [!example] Group A
>> a) Excitation
>> b) Inhibition
>> c) Ignored input
>
>> [!example] Group B
>> n) When input has strong positive influence on neuron
>> o) When input has strong negative influence on neuron
>> p) When input has near zero influence on neuron
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

### Statements with truth values

One question matching three claims about single neurons, bias-free outputs, and activation-induced linearity with True and False.

> [!question] Match the following statements with their truth values in the context of neural networks.
>> [!example] Group A
>> a) Single neuron can learn complex functions
>> b) Without bias, neuron outputs 0 when all inputs are 0
>> c) Activation functions make neural networks linear
>
>> [!example] Group B
>> n) False
>> o) True
>> p) False
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

## See also

- [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]]
- [[Artificial Neural Networks]]
- [[Activation Functions]]
- [[Perceptrons and Multi-Layer Perceptrons]]
- [[Forward Propagation]]
- [[06 - Computer Vision/CNN Foundations and Philosophy/Core Architecture and Philosophy|Core Architecture and Philosophy]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Core Architecture and Philosophy|Core Architecture and Philosophy]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 2 CNN/Activation and Pooling Layers|Activation and Pooling Layers]]
- [[The Convolution Operation Deep Dive]]
- [[The Perceptron and the Chain Rule]]
- [[Activation Functions in Deep Learning]]
- [[Glossary MOC]]
