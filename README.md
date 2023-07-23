# BardGPT
BardGPT is a miniature GPT model for generating poetry coded from scratch in TensorFlow. To run it, you will need numpy and tensorflow.

Sample poem (bard model, 39M parameters, perplexity 40.05):
>  ༄༅༅  the frozen pang  
o thou life! returning now to open suns, ascend  
to find unseen she dwelt! thy gleam thy bright loom act girl  
to ransom radiant order crown the righteous speed.  
loss of many whose gifts fail! string thou further,  
bring to spy my anguish ajax, king heir!  
thy elder burial hand must heart abhor,  
think me canst thou then time these cared forbear,  
thine sister here posterity, she need,  
and my loosened passion stoops in vain.

In addition to the GPT-style technology, BardGPT has a layer of poetry-specific data processing incorporated into the model. This consists of the rhymes and syllable counts of the poem passed through linear layers and then joined with the transformer's prediction to generate the final outputs.

## Instructions

### Quick Start
1. `python download.py` to download the raw poetry data from Project Gutenberg.
2. `python preprocess.py` to preprocess the data including subword tokenization.
3. `python tokens.py` to convert the preprocessed tokens into a format that can be directly used in the model.
4. `python model.py` to train the model on the training data and produce sample generated poems.

### Google Colab Instructions
In addition to these files, there is a file `colab-model.ipynb` that has a similar function to `model.py` but should be used to train the model on Google Colab in order to access the GPU. Here are instructions for doing this:
1. Run `download.py`, `preprocess.py`, and `tokens.py` locally.
2. Create a folder `bardgpt` in the `My Drive` directory of your Google Drive.
3. Copy the `inputs` and `lemmas` folders into this `bardgpt` folder in Drive along with `colab-model.ipynb`.
4. In `colab-model.ipynb` in Drive, change any constants in the code to match values used in `tokens.py` and set `OVERRIDE_CONSTANTS` to `True` if you used custom values. More details on custom arguments below, in the [More Instructions](#more-instructions) section.
5. Set any other constants to the values you wish to use.
6. Run the notebook.

### More Instructions
This repository contains **three model types**: a naive n-gram model, a transformer model in the style of GPT, and a new "bard" model that uses mainly a transformer along with some linear layers that handle specific poetry-related information. The main files as listed above are `download.py`, `preprocess.py`, `tokens.py`, and `model.py`. They should be run in order.

1. `download.py` should be run first and takes no arguments, but downloads all the raw data from Project Gutenberg (11.9 MB) to a `data` folder.

2. `preprocess.py` should be run second. It formats the raw data as tokens including `<title>` and `<newline>` tokens and a significant amount of subword tokenization, including suffix tokens such as `=ing` (`run =ing -> running`). It saves information for correctly using these suffix tokens in a `lemmas` folder. It takes one argument:
    * `--kaggle`: this argument indicates to use data from a [Kaggle poetry foundation dataset](https://www.kaggle.com/datasets/tgdivy/poetry-foundation-poems) in addition to the Project Gutenberg data. If you would like to use this dataset, please follow the link and place `PoetryFoundationData.csv` in a new folder `kaggle`, and then run `kaggle.py`. This is not recommended because the dataset, while larger, is not as consistent in formatting and so had worse performance.
    
    In the end, `preprocess.py` saves its result in an `inputs` folder.

3. `tokens.py` should be run third. It converts the tokens into groups of formatted numpy arrays that can be fed directly into the model as training data. In the case of the bard model, it also computes data related to rhyme and meter. `tokens.py` saves its results in the `inputs` folder. It takes the following arguments:
    * `--model-type`: one of `n` (for the n-gram model), `t` (for the transformer model), or `b` (for the bard model). Default: `b`.
    * `--vocab-size`: vocab size for the model. Default: `4096`.
    * `--ngram-n`: $n$ for the n-gram model. Default: `4`.
    * `--transformer-n`: context size for the transformer. Default: `32`.
    * `--rhyme-size`: number of lines whose rhyme information is used at a time. Default: `4`.
    * `--meter-size`: number of lines whose meter information is used at a time. Default: `3`.
    * `--kaggle`: a flag you should use if you used it in `preprocess.py`.

    Example: `python tokens.py --model-type t --transformer-n 64 --kaggle`.
    
    As a shortcut, you can also put the model type at the beginning: `python tokens.py n --ngram-n 3`.

4. `model.py` should be run last. In general, it trains the model of your choice, but it can also load and run a pretrained model allowing custom length and prompts for poem generation. It takes the following arguments:
    * `--load`: a flag to load a pretrained model in the `saved_models` folder rather than training a new model from scratch.
    * `--epochs`: number of epochs to train for. Default: `10`.
    * `--batch-size`: batch size for training and validation. Default: `256`.
    * `--warmup-steps`: number of initial steps during which the learning rate increase from zero before it begins to decrease.
    * `--embed-dim`: vector size of embeddings. Not used for n-gram model. Default: `512`.
    * `--transformer-layers`: number of layers used in the transformer. Not used for n-gram model. Default: `8`.
    * `--transformer-heads`: number of attention heads used in the transformer. Not used for n-gram model. Default: `4`.
    * `--val-split`: proportion of data to use for validation. Default: `0.2`.
    * `--save-at-end`: a flag indicating to save the final model after all epochs regardless of whether it had the lowest validation loss. The default behavior is to save the model with the lowest validation loss.
    * `--verbose`: a flag used to print extra information about the input data, a model summary, and additional sample outputs after training.

    Example: `python model.py t --vocab-size 2048 --transformer-layers 4 --verbose --save-at-end`.

    In addition, `model.py` takes all the arguments of `tokens.py` except `--kaggle`, and if you used custom values for any, make sure to use the same values in `model.py`.

## Data Sources
* Emily Dickinson ([Plain Text](https://www.gutenberg.org/cache/epub/12242/pg12242.txt))
* Robert Frost ([Plain Text](https://www.gutenberg.org/files/59824/59824-0.txt))
* John Keats ([Plain Text](https://www.gutenberg.org/cache/epub/23684/pg23684.txt))
* Edgar Allan Poe ([Plain Text](https://www.gutenberg.org/files/50852/50852-0.txt))
* Percy Bysshe Shelley ([Plain Text](https://www.gutenberg.org/cache/epub/4800/pg4800.txt))
* Lord Byron ([Plain Text](https://www.gutenberg.org/cache/epub/8861/pg8861.txt), [Don Juan Plain Text](https://www.gutenberg.org/files/21700/21700-0.txt))
* *Lyrical Ballads* by William Wordsworth and Samuel Taylor Coleridge ([Plain Text](https://www.gutenberg.org/files/9622/9622-0.txt))
* Alfred Tennyson ([Plain Text](https://www.gutenberg.org/files/56913/56913-0.txt))
* Ralph Waldo Emerson ([Plain Text](https://www.gutenberg.org/cache/epub/12843/pg12843.txt))
* William Blake ([Plain Text](https://www.gutenberg.org/cache/epub/574/pg574.txt))
* Henry Wadsworth Longfellow ([Plain Text](https://www.gutenberg.org/cache/epub/25153/pg25153.txt))
* Oliver Wendell Holmes ([Plain Text](https://www.gutenberg.org/cache/epub/7400/pg7400.txt))
* Oscar Wilde ([Plain Text](https://www.gutenberg.org/files/1057/1057-0.txt))
* Elizabeth Barrett Browning ([Volume II Plain Text](https://www.gutenberg.org/cache/epub/33363/pg33363.txt), [Volume IV Plain Text](https://www.gutenberg.org/cache/epub/31015/pg31015.txt))
* W. B. Yeats ([Plain Text](https://www.gutenberg.org/cache/epub/38877/pg38877.txt))
* Rabindranath Tagore ([Gitanjali Plain Text](https://www.gutenberg.org/cache/epub/7164/pg7164.txt), [The Gardener Plain Text](https://www.gutenberg.org/cache/epub/6686/pg6686.txt))
* Selections from Modern Poets ([Plain Text](https://www.gutenberg.org/files/53206/53206-0.txt))
* William Shakespeare's Sonnets ([Plain Text](https://www.gutenberg.org/cache/epub/1041/pg1041.txt))
* William Cullen Bryant ([Plain Text](https://www.gutenberg.org/cache/epub/16341/pg16341.txt))
* John Greenleaf Whittier ([Plain Text](https://www.gutenberg.org/cache/epub/9580/pg9580.txt))
* Homer, translated by Alexander Pope ([Iliad Plain Text](https://www.gutenberg.org/cache/epub/6130/pg6130.txt), [Odyssey Plain Text](https://www.gutenberg.org/files/3160/3160-0.txt))
* Rumi, translated by William Hastie ([Plain Text](https://www.gutenberg.org/files/57068/57068-0.txt))
* John Milton ([Paradise Lost Plain Text](https://www.gutenberg.org/cache/epub/26/pg26.txt))
* *Mahabharata*, translated and condensed by Romesh Chunder Dutt ([Plain Text](https://www.gutenberg.org/ebooks/19630))
* ~~Poetry Foundation dataset from Kaggle~~ ([Kaggle link, CSV](https://www.kaggle.com/datasets/tgdivy/poetry-foundation-poems); not recommended)