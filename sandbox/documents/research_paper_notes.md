# Research Paper Notes

## Attention Is All You Need (Vaswani et al., 2017)

### Key Contributions
- Introduced the Transformer architecture
- Eliminated recurrence entirely, using only attention mechanisms
- Achieved state-of-the-art results on machine translation

### Architecture Components
1. **Multi-Head Attention**
   - Allows model to attend to different positions
   - Uses scaled dot-product attention
   - Formula: Attention(Q,K,V) = softmax(QK^T/√d_k)V

2. **Position-wise Feed-Forward Networks**
   - Applied to each position separately
   - Two linear transformations with ReLU

3. **Positional Encoding**
   - Sine and cosine functions of different frequencies
   - Allows model to learn relative positions

### Results
- WMT 2014 English-German: 28.4 BLEU
- WMT 2014 English-French: 41.8 BLEU
- Training time significantly reduced compared to RNNs

### Impact
- Foundation for BERT, GPT, and modern LLMs
- Enabled parallelization during training
- Scaled to billions of parameters

## BERT: Pre-training of Deep Bidirectional Transformers (Devlin et al., 2018)

### Key Ideas
- Masked Language Model (MLM) pre-training
- Next Sentence Prediction (NSP)
- Bidirectional context understanding

### Applications
- Question answering
- Named entity recognition
- Text classification
- Sentiment analysis

### Variants
- RoBERTa: Improved training approach
- ALBERT: Parameter sharing
- DistilBERT: Smaller, faster version
