---
title: Neural Network Architecture and Notation
type: concept
aliases:
  - Network Architecture
  - Neural Network Notation
  - Two-Layer Network
  - Three-Layer Architecture
  - Fully Connected Network
  - Dense Network
tags:
  - neural-networks
  - architecture
  - notation
  - weights
  - bias
  - matrices
  - supervised-learning
  - backpropagation
  - initialization
sources:
  - "02. Neural Network Architecture and Notation"
created_index: 13
---

To understand neural networks, it is best to view them as a massive collection of adjustable knobs and dials — the **weights** — and to get precise about how those knobs are arranged, counted, and written down. This note is the structural reference for that vocabulary: what a network is, how its layers are named and counted, how nodes and connections become matrices, how to read the indexed notation used in calculus derivations, and how parameters are initialized before training begins. It anchors the [[Neural Network Foundations MOC]] alongside [[Forward Propagation]] and [[Activation Functions]], and it uses one concrete running example — a small drug-dosage prediction network — to make every structural idea tangible.

## What a neural network is

A neural network is a massive collection of adjustable knobs and dials. These "knobs" are mathematically represented as **weights**. When data passes through a network, it interacts with these weights to produce an output; a completely untrained network will inevitably produce incorrect outputs.

The central challenge of machine learning is: **How do we know which knobs to turn, in which direction, and by how much, to make the network more accurate?** This is where **Backpropagation** (short for "backward propagation of errors") comes in. It is the workhorse algorithm of neural networks — a systematic, mathematical process used to calculate how much each individual weight contributed to the final error. Once we know who is to blame for the mistake, we can "nudge" those specific weights in the correct direction using gradient descent to minimize the error in the future. The full algorithm is developed in [[Backpropagation]]; this note supplies the structure and notation it operates on.

## The network architecture

Before diving into the mathematics of how a neural network learns, it is strictly necessary to understand how the network is structured and how data flows through it. A neural network is fundamentally a mathematical model inspired by biological brains, designed to recognize patterns. To compute these patterns efficiently, we rely heavily on **Linear Algebra**, specifically matrices and vectors — the machinery that turns diagrams into software.

### A two-layer network (three-layer architecture)

The standard teaching network is traditionally called a **Two-Layer Network** (counting the layers of *weights*, not the nodes) or a **Three-Layer Architecture** (counting the Input, Hidden, and Output nodes). The network consists of three kinds of layers:

1. **Input Layer:** The raw data entering the system.
2. **Hidden Layer(s):** Where the network extracts abstract features.
3. **Output Layer:** The final prediction or classification.

The network is **Fully Connected** (Dense): every single node in a layer is connected to every single node in the subsequent layer.

```mermaid
graph LR
    subgraph Input Layer
    I1((Input 1))
    I2((Input 2))
    I3((Input 3))
    end

    subgraph Hidden Layer
    H1((Hidden 1))
    H2((Hidden 2))
    end

    subgraph Output Layer
    O1((Output 1))
    O2((Output 2))
    end

    I1 --> H1
    I1 --> H2
    I2 --> H1
    I2 --> H2
    I3 --> H1
    I3 --> H2

    H1 --> O1
    H1 --> O2
    H2 --> O1
    H2 --> O2
```

### A specific example: two inputs, two hidden, one output

The network used in the calculus derivations has:

- **Input Layer:** 2 features ($x_1, x_2$)
- **Hidden Layer:** 2 neurons ($h_1, h_2$)
- **Output Layer:** 1 neuron ($\hat{p}$), outputting the predicted probability

Both the hidden layer and the output layer include a **bias term** (+1), which acts as a constant input multiplied by its own trainable weight.

```mermaid
graph LR
    %% Input Layer
    B1((+1 Bias)):::bias --> |b1_1| Z1
    B1 --> |b1_2| Z2
    X1((x1)):::input --> |w1_11| Z1
    X1 --> |w1_12| Z2
    X2((x2)):::input --> |w1_21| Z1
    X2 --> |w1_22| Z2

    %% Hidden Layer
    subgraph Hidden Layer
        Z1[z1_1] --> |Sigma| H1((h1)):::hidden
        Z2[z1_2] --> |Sigma| H2((h2)):::hidden
    end

    %% Output Layer
    B2((+1 Bias)):::bias --> |b2| Zout
    H1 --> |w2_1| Zout[z_out]
    H2 --> |w2_2| Zout

    Zout --> |Sigma| P((p_hat)):::output

    classDef input fill:#e0f7fa,stroke:#006064,stroke-width:2px;
    classDef hidden fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;
    classDef output fill:#fce4ec,stroke:#880e4f,stroke-width:2px;
    classDef bias fill:#fff3e0,stroke:#e65100,stroke-width:2px;
```

### Parameter count

A crucial step in backpropagation is knowing exactly how many parameters (weights and biases) we need to update:

- **Input to Hidden Layer:** 2 inputs × 2 hidden nodes = 4 weights. Plus 2 bias weights = **6 parameters**.
- **Hidden to Output Layer:** 2 hidden nodes × 1 output node = 2 weights. Plus 1 bias weight = **3 parameters**.
- **Total Parameters to optimize:** **9 parameters**.

The goal of backpropagation and gradient descent is to find the optimal specific numerical values for all parameters so that the network makes accurate predictions — nine numbers for this little network, and millions or billions of numbers for a production model.

### The "green" vs "red" parameter concept

In reality, backpropagation optimizes *all* parameters simultaneously. However, doing that on paper is conceptually overwhelming when first learning the mechanics. To learn the mechanics step by step, we isolate the problem:

- **Green Parameters:** We assume that certain parameters have **already been optimized**. We treat them as constants.
- **Red Parameter:** We calculate backpropagation for just one parameter at a time, focusing on the "unknown" parameter.

For example, when first learning, we might assume $W_1, W_2, W_3, W_4, b_1,$ and $b_2$ are already optimized (Green), and only calculate backpropagation for the very last parameter in the network: **the final bias, $b_3$** (Red).

> [!warning] Essential conceptual reminder
> Conceptually, backpropagation always starts at the *end* of the network (the Output) and works its way *backwards* to the Input. By focusing on $b_3$ first, we are executing the literal first step of the backpropagation algorithm.

```mermaid
graph LR
    Input((Input: Dosage))
    
    subgraph Hidden Layer
        H1(Top Node: Softplus)
        H2(Bottom Node: Softplus)
    end
    
    Output((Output: Prediction))
    
    Input -- "W1 (Green)" --> H1
    Input -- "W2 (Green)" --> H2
    
    H1 -. "b1 (Green)" .-> H1
    H2 -. "b2 (Green)" .-> H2
    
    H1 -- "W3 (Green)" --> Output
    H2 -- "W4 (Green)" --> Output
    
    Output -. "b3 (Red/Unknown)" .-> Output
```

## From nodes to matrices

Drawing lines between nodes is helpful for intuition, but terrible for computation. In software, we represent these connections using matrices.

- **Inputs ($X$):** A single-column matrix (a vector) representing the incoming data. If we have 3 inputs, it's a $3 \times 1$ matrix.
- **Weights ($W$):** A matrix representing the strength of the connections.
  - $W_{ih}$: Weights between the Input and Hidden layer.
  - $W_{ho}$: Weights between the Hidden and Output layer.
- **Outputs ($Y$):** A vector representing the final guess of the network.
- **Biases ($B$):** Vectors that shift the activation function left or right.

### How to read weight indices

A weight is often denoted as $w_{ij}$. This represents the weight of the connection *from* node $j$ in the previous layer *to* node $i$ in the current layer. Note that different textbooks sometimes flip this convention, but keeping the "to-from" convention makes matrix multiplication row-by-column alignment much easier.

### The forgotten parameter: bias

> [!warning] Common pitfall
> It is incredibly common to forget the **bias**.

While weights determine the *slope* or *strength* of a connection, the bias is an extra parameter added to the weighted sum before passing it through the activation function. It acts like the $y$-intercept in a linear equation, allowing the activation function to shift left or right. Without a bias, a network fed an input of exactly $0$ would always output $0$, regardless of the weights. You must have a bias vector for the hidden layer and a bias vector for the output layer.

## Mathematical notation: fancy indexing

As we move data through the network, we are calculating coordinates for multiple data points through multiple nodes. If we just call everything $x$ and $y$, the math becomes unreadable. To calculate derivatives using the chain rule, we must introduce structured mathematical indexing.

Two indices carry the structure. **The index $i$** represents the **data point** in our dataset: if $i = 1$, we are talking about the first dosage; if $i = 3$, the third dosage. **The node index (1 or 2)** identifies which hidden node produced the value: the number 1 represents the **top node** in the hidden layer; the number 2 represents the **bottom node**.

In practice the indices read as follows. If you see the variable $x_{1,i}$:

- $x$ means we are calculating the raw horizontal axis input for an activation function.
- $1$ means we are calculating this for the **top node**.
- $i$ means we are doing this for the $i$-th data point in our dataset.

If you see $y_{2,3}$:

- $y$ means we are looking at the vertical axis output *after* the activation function is applied.
- $2$ means this is coming from the **bottom node**.
- $3$ means this is the result of feeding the **3rd data point** into the network.

## The drug dosage running example

A concrete running example used throughout the foundations notes involves predicting drug effectiveness based on **dosage**:

- **Input (X-axis):** Dosage, scaled from `0` (low) to `1` (high).
- **Output (Y-axis):** Virus effectiveness (0 or 1).
- **Observation:** Both low and high dosages are ineffective, but a medium dosage is highly effective. This creates a non-linear arch shape.

The network parameters are explicitly named:

- **Weights:** $W_1$ (Input → Top Hidden), $W_2$ (Input → Bottom Hidden), $W_3$ (Top Hidden → Output), $W_4$ (Bottom Hidden → Output)
- **Biases:** $b_1$ (Top Hidden), $b_2$ (Bottom Hidden), $b_3$ (Output)

```mermaid
graph LR
    Input((Input: Dosage))
    
    subgraph Hidden Layer
        H1(Top Node: Softplus)
        H2(Bottom Node: Softplus)
    end
    
    Output((Output: Prediction))
    
    Input -- "W1" --> H1
    Input -- "W2" --> H2
    
    H1 -. "b1" .-> H1
    H2 -. "b2" .-> H2
    
    H1 -- "W3" --> Output
    H2 -- "W4" --> Output
    
    Output -. "b3" .-> Output
```

### The computational graph (full forward path)

The same network can be drawn as the computational graph that a feedforward pass actually executes — multiply, add bias, activate, multiply, then sum and add the final bias:

```mermaid
graph LR
    Input["Input (Dosage)"] -->|times W1| Mult1{"x W1"}
    Mult1 -->|plus b1| Add1{"+ b1"}
    Add1 -->|x1| Act1["Softplus f(x1)"]
    Act1 -->|y1| Mult3{"x W3"}
    
    Input -->|times W2| Mult2{"x W2"}
    Mult2 -->|plus b2| Add2{"+ b2"}
    Add2 -->|x2| Act2["Softplus f(x2)"]
    Act2 -->|y2| Mult4{"x W4"}
    
    Mult3 --> SumNode{"Sum"}
    Mult4 --> SumNode
    SumNode -->|plus b3| FinalAdd{"+ b3"}
    FinalAdd --> Output["Predicted Output"]
```

### The problem scope: multiple parameter optimization

In standard machine learning, **optimization** is the process of finding the mathematical parameters (weights and biases) that allow a model to make the most accurate predictions possible. Initially, we may assume that almost all parameters are already perfectly tuned, leaving only a single parameter to be optimized. However, real-world neural networks require us to optimize **all parameters simultaneously**.

Our example network's architecture features:

1. **An Input Layer:** A single node receiving a numerical dosage.
2. **A Hidden Layer:** Two nodes utilizing a specific activation function.
3. **An Output Layer:** A single node that sums the results to generate a prediction.

```mermaid
graph LR
    Input((Input)) -->|w1 = 3.34| TopHidden[Top Node]
    Input -->|w2 = -3.53| BotHidden[Bottom Node]
    
    TopHidden -->|w3 = ?| Output((Output))
    BotHidden -->|w4 = ?| Output
    
    style TopHidden fill:#e1f5fe,stroke:#01579b
    style BotHidden fill:#fff3e0,stroke:#e65100
```

*Note: The network also contains biases $b_1, b_2, b_3$. In the early stages of learning, we may assume $w_1, w_2, b_1, b_2$ are already optimized. We need to find the optimal values for $w_3, w_4,$ and $b_3$.*

### Why the chain rule?

When optimizing just one parameter (e.g., $b_3$), a simple derivative suffices. But when changes to $w_3$ and $w_4$ interact with changes to $b_3$, we must use **the chain rule** of calculus. The chain rule allows us to isolate the specific impact that *one* parameter has on the final error, by tracing its effect backward through the network's operations.

## Parameter initialization

Before a neural network can learn, it must have a starting point: we must **initialize** our parameters.

### Standard practice

- **Weights ($w_1, w_2, w_3, w_4$):** Initialized using a **standard normal distribution** (Mean = 0, Standard Deviation = 1).
- **Biases ($b_1, b_2, b_3$):** Initialized to exactly **0**.

*Example initializations:* $w_1 = 2.74$, $w_2 = -1.13$, $w_3 = 0.36$, $w_4 = 0.63$; and $b_1 = b_2 = b_3 = 0.00$.

### Why random weights?

If we initialize all weights to 0 (or the same number), every neuron in the hidden layer would compute the exact same output. During backpropagation, the gradients would also be identical, meaning every weight would be updated by the exact same amount. This is called the **symmetry problem**. By initializing with random numbers, we "break symmetry," allowing different weights to learn different features of the data.

### Why the normal distribution?

We draw from a distribution centered at 0 to ensure our initial outputs are not wildly huge or infinitely small, which would cause the activation functions to saturate — leading to the "vanishing gradient" problem where learning stops (see [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]).

### Why start biases at 0?

Unlike weights, biases do not interact multiplicatively with the input data — they just shift the activation function left or right. Starting them at 0 is perfectly safe because the random weights have already broken the symmetry.

> [!warning] Student tip: a very common interview question
> "Can you initialize all weights in a neural network to zero?" The answer is an emphatic **no**, due to the symmetry problem. However, initializing biases to zero is entirely correct and standard practice.

## Supervised learning and data strategy

### What supervised learning is

Supervised learning is a paradigm of machine learning where the algorithm is trained on **labeled data**: for every set of inputs fed into the network, there is a known, correct "target" output. The network acts like a student taking a test where the teacher has the answer key.

1. The network is given an input (e.g., an image).
2. The network makes a prediction, which we call the **Guess**.
3. We, acting as the "Teacher," know the actual, correct **Answer** (the target label).
4. We compare the Guess to the Answer to calculate the **Error**.

Once the error is calculated at the final output layer, backpropagation allows us to take that error and feed it backwards through the network, layer by layer, adjusting the weights as we go.

### The data split strategy

When training a network, you cannot simply feed it all your data at once and hope it learns perfectly. If you do this, the network will simply memorize the data (a problem known as **overfitting**) and will fail completely when presented with data it has never seen before. To prevent this, datasets are rigorously split into three categories:

1. **Training Data:** The data with known labels used to adjust the network's weights.
2. **Test/Validation Data:** Data with known labels that is *hidden* from the network during training. It is used periodically to test if the network is actually learning underlying patterns or just memorizing the training set.
3. **Unknown/Production Data:** Completely new data the network will encounter in the real world once deployed.

> [!warning] Overfitting
> Overfitting is one of the most dangerous pitfalls in machine learning. If a network achieves near-perfect accuracy on training data but performs poorly on test data, it has overfit — it has memorized the training examples rather than learning the underlying patterns. Always evaluate your model on held-out test/validation data!

The practical split fractions and the augmentation option are covered in [[Data Preparation for Neural Networks]].

### Calculating the error

When training data is fed forward through the network (feedforward), the network produces a "guess" ($Y$). Because this is supervised learning, we also have the absolute "target" value. To figure out how wrong the network is, we calculate the error:

$$ \text{Error} = \text{Target} - \text{Output (Guess)} $$

> [!tip] Target − Guess vs. Guess − Target
> In many strict mathematical cost functions (like Mean Squared Error), we square the error: $(Target - Y)^2$. Because a negative squared is a positive, the order doesn't matter for the raw *magnitude* of the error.
> **However**, when we perform calculus to find the direction to adjust our weights, the sign (positive or negative) determines which direction down the error curve we step. Standard convention dictates $Target - Output$ so that a positive error implies we need to increase our weights, and a negative error implies we need to decrease them.

### Cost functions

The simple subtraction above is the raw error. In professional machine learning, we aggregate these raw errors over a batch of data using a **cost function** (or loss function). The most common for simple regressions is the **Mean Squared Error (MSE)**. The goal of training a neural network is singular: **minimize the cost function** — find the exact combination of millions of weights and biases that results in the lowest possible error.

## Essential prerequisites for backpropagation

To fully understand backpropagation, you must be comfortable with three concepts. These are the "engines" under the hood of neural networks:

1. **Neural networks (inside the black box).** You must understand how data moves forward through a network (Input → Weights/Biases → Activation Function → Output). *Reminder:* Activation functions (like the Softplus function) allow the network to bend and warp data to fit complex, non-linear shapes — see [[Activation Functions]].
2. **The chain rule (calculus).** The chain rule is used to take the derivative of composite functions (functions inside of functions). Because a neural network is essentially one massive nested mathematical function, the chain rule allows us to unpack it layer by layer. *Formula reminder:* If $y = f(g(x))$, then $\frac{dy}{dx} = f'(g(x)) \times g'(x)$.
3. **Gradient descent.** Once backpropagation uses the chain rule to find the *slope* (derivative) of the error at a given point, gradient descent is the algorithm that takes a "step" down that slope to find the minimum error.

> [!tip] What students often miss
> Backpropagation and gradient descent are **not** the same thing.
> - **Backpropagation** only calculates the derivatives (the slopes).
> - **Gradient descent** uses those derivatives to physically update the weights and biases. They work together as a two-part team.

### High-level workflow diagram

```mermaid
graph TD
    A[Input Data: Drug Dosage] --> B[Forward Pass: Neural Network]
    B --> C[Generate Prediction]
    C --> D[Calculate Error/Loss: SSR]
    D --> E[Backpropagation: Use Chain Rule to find Slopes]
    E --> F[Gradient Descent: Update Weights & Biases]
    F --> B
```

## See also

- [[Neural Network Foundations MOC]]
- [[Forward Propagation]]
- [[Activation Functions]]
- [[Perceptrons and Multi-Layer Perceptrons]]
- [[Artificial Neural Networks]]
- [[Data Preparation for Neural Networks]]
- [[Backpropagation]]
- [[Matrix Implementation of Backpropagation]]
- [[Formal Neuron Lab]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Hyperparameters and Network Configuration|Hyperparameters and Network Configuration]]
