import os

# ═══════════════════════════════════════════
# Generate rich AI/ML sample datasets
# ═══════════════════════════════════════════

TXT_DIR = "data/ai_ml/articles"
os.makedirs(TXT_DIR, exist_ok=True)

articles = {
    "transformers_architecture.txt": """
The Transformer Architecture: A Deep Dive

The Transformer architecture was introduced in the landmark paper "Attention Is All You Need" by Vaswani et al. in 2017. It fundamentally changed how we approach sequence modeling tasks in natural language processing and beyond.

Before Transformers, the dominant paradigm for sequence modeling was based on Recurrent Neural Networks (RNNs) and their variants like Long Short-Term Memory (LSTM) networks and Gated Recurrent Units (GRUs). These models processed sequences one token at a time, maintaining a hidden state that was updated at each step. This sequential nature created two major problems: it prevented parallelization during training, making it slow on modern GPU hardware, and it made it difficult to capture long-range dependencies due to the vanishing gradient problem.

The key innovation of the Transformer is the Self-Attention Mechanism. Instead of processing tokens sequentially, self-attention allows the model to look at all positions in the input sequence simultaneously when computing the representation of each position. This is done through three learned projections: Query (Q), Key (K), and Value (V). The attention score between any two positions is computed as the dot product of their query and key vectors, scaled by the square root of the dimension, and then passed through a softmax function to obtain weights. These weights are used to compute a weighted sum of the value vectors.

Multi-Head Attention extends this idea by running multiple attention operations in parallel, each with different learned projections. This allows the model to attend to information from different representation subspaces at different positions. The outputs of all attention heads are concatenated and linearly projected to produce the final output.

The Transformer architecture consists of an encoder stack and a decoder stack. The encoder processes the input sequence and produces a set of continuous representations. Each encoder layer contains two sub-layers: a multi-head self-attention mechanism and a position-wise fully connected feed-forward network. Layer normalization and residual connections are applied around each sub-layer.

The decoder generates the output sequence one token at a time. Each decoder layer contains three sub-layers: a masked multi-head self-attention mechanism (to prevent attending to future positions), a multi-head attention mechanism that attends to the encoder output, and a position-wise feed-forward network.

Since Transformers process all positions simultaneously, they have no inherent notion of sequence order. Positional encodings are added to the input embeddings to provide information about the position of each token in the sequence. The original paper used sinusoidal functions of different frequencies, though learned positional embeddings have also been successfully used.

The impact of Transformers has been enormous. They led directly to the development of BERT (Bidirectional Encoder Representations from Transformers), GPT (Generative Pre-trained Transformer), T5 (Text-to-Text Transfer Transformer), and many other models that have achieved state-of-the-art results across virtually all NLP benchmarks.
""",
    
    "rag_systems_overview.txt": """
Retrieval-Augmented Generation: Engineering Production RAG Systems

Retrieval-Augmented Generation (RAG) represents a paradigm shift in how we build AI systems that need to work with large, dynamic knowledge bases. Rather than relying solely on the parametric knowledge stored in a language model's weights during pre-training, RAG combines the generative capabilities of LLMs with real-time information retrieval from external data sources.

The fundamental architecture of a RAG system consists of three core components: the Ingestion Pipeline, the Retrieval Engine, and the Generation Module.

The Ingestion Pipeline is responsible for processing raw documents into a searchable format. This involves several stages: document loading (parsing PDFs, HTML, markdown, etc.), text cleaning (removing noise, normalizing formatting), chunking (splitting documents into semantically coherent segments), embedding (converting text chunks into dense vector representations), and indexing (storing vectors in a searchable index like FAISS, Pinecone, or Weaviate).

Chunking strategy is arguably the most critical decision in RAG system design. Chunks that are too small lose context and produce noisy retrievals. Chunks that are too large dilute the relevant information and waste context window budget. The optimal chunk size depends on the domain, document structure, and downstream task. For technical documentation, chunks of 800-1500 characters with 100-200 character overlap tend to work well. Recursive character splitting, which attempts to split on paragraph boundaries first, then sentences, then words, preserves semantic coherence better than naive fixed-size splitting.

The Retrieval Engine performs similarity search to find the most relevant chunks for a given query. Vector similarity search using embeddings is the most common approach, but hybrid retrieval combining dense vectors with sparse keyword matching (like BM25) often produces superior results. Re-ranking models can further improve retrieval quality by scoring the relevance of retrieved chunks using cross-encoder models.

The Generation Module takes the retrieved chunks and the original query, constructs a prompt, and generates a response using an LLM. Prompt engineering is crucial here: the prompt must clearly distinguish between the system instructions, the retrieved context, and the user query. Including source attribution in the generated output helps users verify the information and builds trust.

Advanced RAG techniques include query transformation (decomposing complex queries into sub-queries), iterative retrieval (using initial results to refine the search), knowledge graph integration (combining vector search with structured knowledge), and agentic RAG (using AI agents to orchestrate multi-step retrieval and reasoning).

Production RAG systems must also handle several operational concerns: monitoring retrieval quality, managing embedding model versioning, handling document updates and deletions, implementing access control, and optimizing latency and cost.
""",
    
    "llm_training_fundamentals.txt": """
Large Language Model Training: From Pre-training to RLHF

Training a Large Language Model (LLM) is a multi-stage process that requires careful engineering, massive computational resources, and sophisticated optimization techniques. Understanding this process is essential for anyone working with or building AI systems.

Pre-training is the foundation of LLM development. During pre-training, the model learns general language understanding by processing vast amounts of text data. For decoder-only models like GPT, the training objective is next-token prediction: given a sequence of tokens, predict the next token. For encoder-only models like BERT, the objectives include masked language modeling (predicting randomly masked tokens) and next sentence prediction. The scale of pre-training is staggering: modern LLMs are trained on trillions of tokens using thousands of GPUs for weeks or months.

The training data quality significantly impacts model performance. Data curation involves collecting text from diverse sources (web pages, books, code repositories, scientific papers), deduplicating the data, filtering out low-quality or harmful content, and balancing the representation of different domains and languages. The Common Crawl dataset, which contains petabytes of web text, is a primary data source, but it requires extensive cleaning and filtering.

Tokenization converts raw text into a sequence of integer tokens that the model can process. Modern LLMs typically use subword tokenization algorithms like Byte-Pair Encoding (BPE) or SentencePiece. These algorithms learn a vocabulary of common subword units from the training data, balancing vocabulary size with the ability to represent any text without out-of-vocabulary tokens.

The Transformer architecture serves as the backbone of modern LLMs. Key architectural choices include the number of layers (depth), the hidden dimension (width), the number of attention heads, the feed-forward network dimension, and the context length. Scaling laws, discovered by researchers at OpenAI and DeepMind, provide guidelines for how to allocate a fixed compute budget across model size and training data to achieve optimal performance.

Distributed training is necessary for models that are too large to fit on a single GPU. Techniques include data parallelism (splitting training batches across GPUs), tensor parallelism (splitting individual layers across GPUs), pipeline parallelism (splitting the model across GPUs by layers), and expert parallelism (for Mixture-of-Experts models). Frameworks like DeepSpeed, Megatron-LM, and FSDP (Fully Sharded Data Parallelism) implement these strategies.

After pre-training, models undergo supervised fine-tuning (SFT) on high-quality instruction-following datasets. These datasets contain examples of prompts paired with ideal responses, curated by human annotators. SFT teaches the model to follow instructions, maintain appropriate tone, and produce helpful outputs.

Reinforcement Learning from Human Feedback (RLHF) further aligns the model with human preferences. First, a reward model is trained on human comparisons of model outputs. Then, the language model is optimized using Proximal Policy Optimization (PPO) to maximize the reward model's scores while staying close to the SFT model using a KL divergence penalty. Recent alternatives like Direct Preference Optimization (DPO) simplify this process by directly optimizing the language model on preference data without a separate reward model.
""",
    
    "vector_databases_guide.txt": """
Vector Databases: Architecture and Engineering for AI Applications

Vector databases have become a critical infrastructure component for modern AI applications, particularly for similarity search, recommendation systems, and Retrieval-Augmented Generation (RAG). Understanding their architecture and trade-offs is essential for building performant AI systems.

A vector database is specialized for storing, indexing, and querying high-dimensional vector embeddings. Unlike traditional databases that excel at exact match queries on structured data, vector databases are optimized for approximate nearest neighbor (ANN) search in high-dimensional spaces. This is fundamentally different from traditional database operations because the dimensionality curse makes exact nearest neighbor search computationally infeasible for high-dimensional vectors.

The core indexing algorithms used by vector databases include:

Flat Index (Brute Force): Compares the query vector against every stored vector. Provides exact results but has O(n) time complexity, making it impractical for large datasets. Useful as a baseline for measuring the recall of approximate methods.

Inverted File Index (IVF): Partitions the vector space into clusters using k-means clustering. During search, only the vectors in the nearest clusters are compared. This reduces the search space significantly but may miss relevant vectors that fall in neighboring clusters. Using a larger nprobe parameter (number of clusters to search) improves recall at the cost of speed.

Hierarchical Navigable Small World (HNSW): Builds a multi-layer graph where each node is connected to its nearest neighbors. Search starts at the top layer and progressively moves to lower, denser layers. HNSW provides excellent query performance with high recall and is the default index type in many vector databases.

Product Quantization (PQ): Compresses vectors by splitting them into sub-vectors and quantizing each sub-vector independently. This dramatically reduces memory usage (often 10-100x compression) with a modest loss in recall. PQ is often combined with IVF for large-scale deployments.

Major vector database solutions include:

FAISS (Facebook AI Similarity Search): An open-source library that provides efficient implementations of various ANN algorithms. FAISS is highly optimized for GPU acceleration and is often used as the indexing engine within other systems. It is not a full database but rather a similarity search library.

Pinecone: A fully managed vector database service that handles scaling, replication, and infrastructure management. It provides a simple API for upserting and querying vectors with metadata filtering.

Weaviate: An open-source vector database that supports hybrid search (combining vector and keyword search), GraphQL-based queries, and module-based extensibility for different embedding models and integrations.

Qdrant: A high-performance open-source vector database written in Rust, offering advanced filtering, payload management, and distributed deployment options.

pgvector: A PostgreSQL extension that adds vector similarity search capabilities to existing PostgreSQL databases. This is particularly useful when you want to keep vectors alongside relational data without introducing a separate database system.

When choosing a vector database, key considerations include: query latency requirements, dataset size, memory constraints, filtering capabilities, operational complexity, and integration with your existing infrastructure.
""",
    
    "prompt_engineering_advanced.txt": """
Advanced Prompt Engineering: Techniques for Production LLM Systems

Prompt engineering has evolved from simple instruction writing to a sophisticated discipline that significantly impacts the quality, reliability, and safety of LLM-powered applications. This guide covers advanced techniques used in production systems.

Zero-Shot Prompting is the simplest form, where the model is given a task description without any examples. While modern LLMs are surprisingly capable in zero-shot settings, the quality heavily depends on how clearly the task is described. Key principles include being specific about the desired output format, explicitly stating constraints, and providing context about the intended audience or use case.

Few-Shot Prompting provides the model with examples of the desired input-output behavior. The choice of examples significantly impacts performance: examples should be diverse, representative of edge cases, and ordered from simple to complex. Research has shown that even the order of few-shot examples can affect model output quality by up to 20 percent.

Chain-of-Thought (CoT) prompting instructs the model to show its reasoning step by step before arriving at an answer. This technique dramatically improves performance on tasks requiring multi-step reasoning, mathematical computation, and logical deduction. The simple addition of "Let's think step by step" to a prompt can improve accuracy on complex reasoning tasks from 18 percent to 79 percent.

Self-Consistency extends CoT by sampling multiple reasoning paths and selecting the most frequent answer. This reduces the impact of individual reasoning errors and provides a measure of confidence in the output.

Tree-of-Thoughts (ToT) generalizes CoT by having the model explore multiple reasoning branches at each step, evaluate partial solutions, and backtrack when necessary. This is particularly effective for complex planning and puzzle-solving tasks.

ReAct (Reasoning + Acting) combines reasoning traces with action steps, allowing the model to interact with external tools (search engines, calculators, APIs) as part of its reasoning process. This pattern is foundational for building AI agents that can accomplish complex real-world tasks.

Structured Output Prompting ensures the model returns responses in a specific format (JSON, XML, markdown tables, etc.). This is critical for production systems where downstream processes need to parse the model's output programmatically. Techniques include providing a JSON schema in the prompt, using output parsers with retry logic, and leveraging features like OpenAI's function calling or response format parameters.

Prompt Chaining decomposes complex tasks into a series of simpler prompts, where the output of one prompt feeds into the next. This modular approach improves reliability, makes debugging easier, and allows different prompts to be optimized independently.

System Prompts in chat-based models set the persona, behavior guidelines, and constraints for the entire conversation. Well-crafted system prompts include: role definition, output format specifications, safety guidelines, knowledge boundaries, and examples of desired behavior.

Prompt Injection Defense is a critical concern in production systems. Techniques include input sanitization, delimiter-based separation of instructions and user input, instruction hierarchy (system prompt takes precedence), and output validation. Regular red-teaming and adversarial testing help identify vulnerabilities.

Evaluation of prompts should be systematic: maintain a test suite of diverse inputs, measure performance on accuracy, format compliance, safety, and latency. A/B testing different prompt variations on production traffic provides the most reliable signal for prompt optimization.
""",

    "neural_network_optimization.txt": """
Neural Network Optimization: From Gradient Descent to Modern Techniques

Optimization lies at the heart of deep learning. The process of training a neural network is fundamentally an optimization problem: finding the set of parameters (weights and biases) that minimize a loss function measuring the discrepancy between the model's predictions and the ground truth.

Stochastic Gradient Descent (SGD) is the foundational optimization algorithm. Instead of computing the gradient over the entire dataset (batch gradient descent), SGD computes the gradient on a randomly sampled mini-batch. This introduces noise into the gradient estimates but enables training on large datasets and often helps escape local minima. The update rule is simple: parameters are updated by subtracting the product of the learning rate and the gradient.

Momentum adds a velocity term to SGD that accumulates past gradients, helping the optimizer build up speed in consistent gradient directions and dampen oscillations in inconsistent directions. This is analogous to a ball rolling down a hill: it accelerates in the downhill direction and is less affected by small bumps.

Adam (Adaptive Moment Estimation) combines momentum with adaptive learning rates for each parameter. It maintains exponentially decaying averages of both the gradient (first moment) and the squared gradient (second moment), and uses these to adapt the learning rate for each parameter. Adam is the default optimizer for many deep learning applications due to its robustness and minimal hyperparameter tuning requirements.

Learning Rate Scheduling adjusts the learning rate during training. Common schedules include step decay (reducing the learning rate by a factor at fixed intervals), cosine annealing (following a cosine curve from a high to low learning rate), warmup (linearly increasing the learning rate from zero over the first few training steps), and one-cycle policy (increasing then decreasing the learning rate over training).

Weight Decay (L2 regularization) adds a penalty proportional to the squared magnitude of the weights to the loss function. This encourages the model to learn smaller, more distributed weight values, which generally improves generalization.

Batch Normalization normalizes the activations of each layer to have zero mean and unit variance, then applies a learned scale and shift. This stabilizes training, allows higher learning rates, and provides some regularization effect. Layer Normalization is a variant that normalizes across features rather than across the batch, making it more suitable for sequence models and variable-length inputs.

Gradient Clipping prevents exploding gradients by capping the gradient norm at a maximum value. This is essential for training recurrent networks and large Transformers, where gradients can grow exponentially through deep computational graphs.

Dropout randomly sets a fraction of activations to zero during training, forcing the network to learn redundant representations. This is one of the most effective regularization techniques and is widely used in practice.

Mixed Precision Training uses half-precision (FP16) arithmetic for forward and backward passes while maintaining a master copy of weights in full precision (FP32). This reduces memory usage by approximately 2x and speeds up training on modern GPUs that have dedicated FP16 compute units.

Gradient Accumulation simulates larger batch sizes by accumulating gradients over multiple forward-backward passes before performing a parameter update. This is useful when the desired batch size exceeds GPU memory capacity.
""",

    "embedding_models_comparison.txt": """
Embedding Models: Architecture, Training, and Selection Guide

Embedding models convert text into dense vector representations that capture semantic meaning, enabling similarity search, clustering, and classification tasks. Understanding the landscape of embedding models is crucial for building effective RAG systems and other AI applications.

Word2Vec, introduced by Mikolov et al. in 2013, was one of the first widely successful embedding approaches. It learns word-level embeddings using either the Skip-gram model (predicting context words from a center word) or the CBOW model (predicting a center word from context words). While revolutionary at the time, word-level embeddings cannot capture the meaning of phrases or handle polysemy (words with multiple meanings).

Sentence-BERT (SBERT), introduced in 2019, adapted the BERT architecture for generating sentence-level embeddings. By adding a pooling layer on top of BERT and training with a siamese network structure on sentence pairs, SBERT can produce semantically meaningful sentence embeddings in a single forward pass. This made it practical to use embeddings for large-scale similarity search, unlike vanilla BERT which requires encoding pairs of sentences together.

The E5 family of models (Embeddings from Bidirectional Encoder Representations) uses a contrastive learning approach with carefully curated training data. E5 models achieve strong performance across diverse tasks by training on a mixture of labeled and synthetic data. The instruction-tuned variant, E5-Instruct, accepts a task description as part of the input, allowing a single model to generate task-specific embeddings.

OpenAI's text-embedding-ada-002 and its successor text-embedding-3 models are widely used commercial embedding models. They provide a good balance of quality and convenience, with the newer models offering adjustable output dimensions (matryoshka representations) that allow trading off between embedding quality and storage/compute requirements.

Google's Gemini embedding models, accessible through the Gemini API, provide high-quality embeddings optimized for retrieval tasks. The models support different task types (retrieval_document, retrieval_query, semantic_similarity, classification) that optimize the embedding for specific use cases.

Cohere's Embed v3 focuses on multilingual embeddings and supports compression to binary or int8 representations, dramatically reducing storage requirements while maintaining search quality.

BGE (BAAI General Embedding) models are open-source alternatives that achieve competitive performance with commercial offerings. The BGE family includes models of various sizes and specialized variants for specific domains.

Key factors for choosing an embedding model include: the quality of embeddings for your specific domain and task, the dimensionality of the output vectors (higher dimensions capture more information but require more storage and compute), inference speed (important for real-time applications), cost (for commercial APIs), and language support.

For RAG systems specifically, it is important to use the same embedding model for both document indexing and query embedding. Mixing models will produce incompatible vector spaces and degraded retrieval quality. Some models provide separate modes for encoding documents versus queries, which can improve retrieval by optimizing the embedding for each side of the similarity computation.

Matryoshka Representation Learning (MRL) is a recent technique where models are trained to produce embeddings where the first N dimensions are a valid embedding of lower quality. This allows dynamically choosing the embedding dimension at inference time, trading off between quality and efficiency without retraining the model.
""",

    "fine_tuning_strategies.txt": """
Fine-Tuning Strategies for Large Language Models: A Practical Guide

Fine-tuning adapts a pre-trained language model to a specific task or domain by continuing the training process on a smaller, task-specific dataset. The choice of fine-tuning strategy depends on the available compute resources, dataset size, and the degree of specialization required.

Full Fine-Tuning updates all parameters of the pre-trained model. This provides maximum flexibility for the model to adapt to the new task but requires significant GPU memory (proportional to the model size) and risks catastrophic forgetting of the pre-trained knowledge if the fine-tuning dataset is too small or too domain-specific. Full fine-tuning is typically reserved for cases where abundant compute is available and the target domain is significantly different from the pre-training data.

LoRA (Low-Rank Adaptation) is the most popular parameter-efficient fine-tuning method. Instead of updating all weight matrices, LoRA decomposes the weight update into two small matrices of much lower rank. For a weight matrix W of dimensions d x k, LoRA learns two matrices A (d x r) and B (r x k) where r is much smaller than both d and k. The effective weight becomes W + AB. This reduces the number of trainable parameters by orders of magnitude while maintaining competitive performance. Typical rank values range from 4 to 64.

QLoRA (Quantized LoRA) extends LoRA by quantizing the base model to 4-bit precision using NormalFloat4 (NF4) quantization, while keeping the LoRA adapters in higher precision (FP16 or BF16). This dramatically reduces memory requirements, making it possible to fine-tune a 65-billion parameter model on a single 48GB GPU. QLoRA uses double quantization (quantizing the quantization constants themselves) and paged optimizers to further reduce memory usage.

Prefix Tuning prepends learnable continuous vectors (prefixes) to the input of each Transformer layer. Only these prefix vectors are trained while the model weights remain frozen. The prefix acts as a task-specific prompt that steers the model's behavior.

Prompt Tuning is a simplified version of prefix tuning that only adds learnable tokens to the input layer (rather than every layer). It is computationally cheaper than prefix tuning but may require more trainable tokens to achieve comparable performance.

Adapter Layers insert small trainable modules between the existing layers of the Transformer. Each adapter typically consists of a down-projection, a non-linear activation, and an up-projection. Adapters add very few parameters relative to the model size and can be easily swapped or composed for multi-task scenarios.

Data Preparation for fine-tuning is often more important than the choice of fine-tuning method. Key considerations include: data quality (clean, well-formatted examples), data diversity (covering edge cases and variations), data balance (avoiding overrepresentation of common patterns), and instruction format consistency (matching the format used during the model's original instruction tuning).

Evaluation during fine-tuning should use held-out validation sets representative of the production use case. It is important to track not only task-specific metrics but also general capabilities to detect catastrophic forgetting. Periodic evaluation on diverse benchmarks helps ensure the model maintains its broad knowledge while improving on the target task.

Hyperparameter tuning for fine-tuning typically involves the learning rate (usually 1e-5 to 5e-4 for LoRA, 1e-6 to 1e-5 for full fine-tuning), batch size, number of epochs (often just 1-3 to avoid overfitting), LoRA rank and alpha, and the choice of which layers to apply LoRA to. The learning rate is the most impactful hyperparameter, and a brief learning rate sweep is usually worthwhile.
""",

    "ai_agents_architecture.txt": """
AI Agent Architecture: Building Autonomous Systems with LLMs

AI agents represent the next evolution of LLM-powered systems, moving beyond simple question-answering to autonomous task execution. An AI agent is a system that uses an LLM as its reasoning engine to observe its environment, plan actions, execute tools, and iteratively work towards accomplishing a goal.

The core architecture of an AI agent consists of four components: the Brain (LLM), Memory, Tools, and the Planning and Execution Loop.

The Brain is the central reasoning engine, typically a large language model. It receives observations (current state, tool outputs, user messages), reasons about what to do next, and generates actions. The quality of the LLM directly impacts the agent's capability: stronger models can handle more complex reasoning chains, recover from errors more gracefully, and make better decisions about which tools to use.

Memory systems in AI agents come in several forms. Short-term memory (working memory) is implemented as the conversation context window, containing recent observations, thoughts, and actions. Long-term memory uses external storage (vector databases, key-value stores) to persist information across sessions. Episodic memory stores records of past task executions, enabling the agent to learn from experience. Semantic memory stores factual knowledge that the agent can retrieve when needed.

Tools are external functions that the agent can invoke to interact with the world. Examples include web search, code execution, file manipulation, API calls, database queries, and browser automation. The tool interface typically includes a name, description, parameter schema, and execution function. Well-designed tool descriptions are critical because the LLM uses them to decide when and how to use each tool.

The Planning and Execution Loop is the control flow that drives the agent. The most common pattern is the ReAct (Reasoning + Acting) loop. In each iteration, the agent: observes the current state, thinks about what to do next (reasoning), decides on an action (tool call or response), executes the action, and observes the result. This loop continues until the task is complete or a termination condition is met.

Planning strategies vary in sophistication. Simple agents use a flat ReAct loop without explicit planning. More advanced agents create a plan before execution, breaking the task into subtasks and tracking progress. Hierarchical planning decomposes complex tasks into sub-goals, each handled by specialized sub-agents.

Error handling is crucial for robust agent systems. Common strategies include retry with backoff (for transient failures), self-reflection (asking the LLM to analyze what went wrong and try a different approach), escalation (asking the user for help when stuck), and graceful degradation (providing partial results when full completion is not possible).

Multi-agent systems use multiple specialized agents that collaborate to accomplish complex tasks. Each agent has a specific role (researcher, coder, reviewer, etc.) and communicates with others through a shared workspace or message passing. Orchestration patterns include hierarchical (a coordinator agent delegates to specialists), debate (agents argue different positions to reach a conclusion), and pipeline (each agent handles a stage of the workflow).

Safety and guardrails are essential in production agent systems. These include sandboxed execution environments for code, confirmation prompts before destructive actions, rate limiting and budget controls for API calls, output validation against expected schemas, and human-in-the-loop checkpoints for high-stakes decisions.

Real-world applications of AI agents include software development automation, research assistants, customer support automation, data analysis pipelines, and autonomous testing systems. The field is rapidly evolving, with new frameworks like LangGraph, CrewAI, and AutoGen making it easier to build sophisticated agent systems.
""",

    "evaluation_metrics_nlp.txt": """
Evaluation Metrics for NLP and RAG Systems: A Comprehensive Guide

Evaluating the quality of NLP systems and RAG pipelines requires a diverse set of metrics that capture different aspects of performance. Understanding these metrics is essential for iterating on system design and comparing different approaches.

BLEU (Bilingual Evaluation Understudy) measures the overlap of n-grams between generated text and reference translations. Originally designed for machine translation evaluation, BLEU computes precision for n-grams of different sizes (typically 1 through 4) and combines them with a brevity penalty to discourage overly short translations. While still widely used, BLEU has known limitations: it does not account for semantic similarity, synonyms, or paraphrases, and it correlates poorly with human judgments for open-ended generation tasks.

ROUGE (Recall-Oriented Understudy for Gisting Evaluation) focuses on recall rather than precision. ROUGE-N measures the overlap of n-grams between the generated text and reference summaries. ROUGE-L measures the longest common subsequence. ROUGE is commonly used for evaluating summarization systems.

BERTScore uses contextual embeddings from BERT to compute similarity between tokens in the generated and reference texts. It aligns tokens using greedy matching based on cosine similarity and reports precision, recall, and F1 scores. BERTScore correlates better with human judgments than n-gram based metrics because it captures semantic similarity.

For RAG-specific evaluation, several specialized metrics have been developed. Retrieval metrics measure how well the system finds relevant documents. Hit Rate measures whether any of the retrieved documents contain the answer. Mean Reciprocal Rank (MRR) considers the rank of the first relevant document. Normalized Discounted Cumulative Gain (NDCG) accounts for the relevance grade and position of all retrieved documents.

Faithfulness measures whether the generated answer is supported by the retrieved context. This is critical for RAG systems because the model may hallucinate information not present in the retrieved documents. Faithfulness is typically evaluated by decomposing the answer into atomic claims and verifying each claim against the context.

Answer Relevance measures how well the generated answer addresses the original question. A system might retrieve relevant documents and generate a faithful response that nonetheless does not answer what was asked.

Context Relevance evaluates whether the retrieved chunks are actually relevant to the query. Low context relevance indicates problems in the retrieval pipeline: either the embeddings do not capture the semantic relationship, or the chunking strategy is too coarse.

LLM-as-Judge is an increasingly popular evaluation approach where another LLM is used to evaluate the quality of generated outputs. The judge model is prompted with the question, the generated answer, and optionally a reference answer, and asked to provide a quality rating. While not a replacement for human evaluation, LLM judges provide scalable, consistent evaluation that correlates reasonably well with human preferences.

Human Evaluation remains the gold standard for assessing generation quality. Common approaches include side-by-side comparison (showing evaluators outputs from different systems and asking which is better), Likert scale rating (rating individual outputs on dimensions like helpfulness, accuracy, and fluency), and error annotation (identifying and categorizing specific errors in the output).

End-to-end evaluation for RAG systems should combine retrieval metrics with generation quality metrics. A system might have excellent retrieval but poor generation (e.g., the model ignores the retrieved context), or vice versa. Tracking both separately helps identify bottlenecks and guide optimization efforts.
""",
}

for filename, content in articles.items():
    filepath = os.path.join(TXT_DIR, filename)
    with open(filepath, "w") as f:
        f.write(content.strip())
    print(f"✅ Created: {filepath} ({len(content)} chars)")

print(f"\n🎉 Created {len(articles)} article files!")
