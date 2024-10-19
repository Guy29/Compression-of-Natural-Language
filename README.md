## Compression of Natural Language

This repo contains my final year project for my undergraduate degree at the University of Sussex.

The goal of this project was to investigate different methods of compression of natural language and their effectiveness.

I start by taking a high level overview of relevant ideas from information theory, showing the relationship between text prediction and compression. I then implement a simple n-gram-based method of compression (which outperforms `gzip` and `zlib`), use simple machine learning-based language models (with Long-Short Term Memory and Recurrent Neural Network architectures) to predict and compress text, and finally create a novel method that outperforms all four compression algorithms examined (`gzip`, `zlib`, `bzip2`, and `lzma`).
