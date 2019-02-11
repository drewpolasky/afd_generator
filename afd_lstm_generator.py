#Trying to create an rnn for generating text, trained on area forecast dicussions from an individual weather forecast office.
#Download script for the AFDs graciously provided by Eric Allen, of the University of Delaware

from __future__ import print_function
import os
import re
import datetime
import random
import sys
import io

from keras.callbacks import LambdaCallback
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.optimizers import RMSprop
from keras.utils.data_utils import get_file
import numpy as np

import afd_download

def main():
    wfo = 'ctp'
    wfo = wfo.upper()
    check_downloaded(wfo)
    afd_dict = parse_afd(wfo, [2019])
    convert_text(afd_dict)

def check_downloaded(wfo, afd_path = 'AFD_DATA/'):
    #check if the AFDs for a given forecast office have already been downloaded, and download for any missing years
    years = []
    currentYear = datetime.datetime.now().year
    for filename in os.listdir(afd_path):
        if re.search(wfo, filename):
            years.append(re.search(r'\d\d\d\d',filename).group())
    for year in range(1996, currentYear):   #AFD database goes back to 1996
        if str(year) not in years:
            afd_download.get_single_data('AFD'+wfo, year)

def parse_afd(wfo, years = None, afd_path = 'AFD_DATA/'):
    #load the afd data into memory and keep it as a dictionary
    #Note that 2016 was the year that AFDs where no longer all caps
    if years is None:
        years = range(1996, datetime.datetime.now().year)

    afd_dict = {}
    afd = []
    for year in years:
        afd_dict[year] = []
        afd_file = open(afd_path+'/AFD'+wfo+'_'+str(year)+'.txt','r')

        for line in afd_file:
            if line.strip() == 'AFD'+wfo:
                afd_dict[year].append(afd)
                afd = []
            else:
                afd.append(line)   
    return afd_dict

'''def convert_text(text_dict):
    #convert input text into index values
    #input text is a dictonary of lists
    #This is adapted from keras example for generating text
    
    #to be cleaned up
    global maxlen
    global text 
    global chars
    global char_indices
    global indices_char'''

def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

def on_epoch_end(epoch, _):
    # Function invoked at end of each epoch. Prints generated text.
    print()
    print('----- Generating text after Epoch: %d' % epoch)

    start_index = random.randint(0, len(text) - maxlen - 1)
    for diversity in [0.2, 0.5, 1.0]:
        print('----- diversity:', diversity)

        generated = ''
        sentence = text[start_index: start_index + maxlen]
        generated += sentence
        print('----- Generating with seed: "' + sentence + '"')
        sys.stdout.write(generated)

        for i in range(600):
            x_pred = np.zeros((1, maxlen, len(chars)))
            for t, char in enumerate(sentence):
                x_pred[0, t, char_indices[char]] = 1.

            preds = model.predict(x_pred, verbose=0)[0]
            next_index = sample(preds, diversity)
            next_char = indices_char[next_index]

            generated += next_char
            sentence = sentence[1:] + next_char

            sys.stdout.write(next_char)
            sys.stdout.flush()
        model.save('afd_lstm_model.h5')
        print()



if __name__ == '__main__':
    wfo = 'ctp'
    wfo = wfo.upper()
    check_downloaded(wfo)
    text_dict = parse_afd(wfo, [2018])

    all_text = []
    for year in text_dict:
        for afd in text_dict[year]:
            all_text.append(''.join(afd))
    text = ''.join(all_text)
    chars = sorted(list(set(text)))
    print('total chars:', len(chars))
    char_indices = dict((c, i) for i, c in enumerate(chars))
    indices_char = dict((i, c) for i, c in enumerate(chars))
    
    # cut the text in semi-redundant sequences of maxlen character 
    maxlen = 40
    step = 10
    sentences = []
    next_chars = []
    #make sentances for each afd seperately, to keep from wrapping past the end of a discussion
    for afd in all_text:
        for i in range(0, len(afd) - maxlen, step):
            sentences.append(afd[i: i + maxlen])
            next_chars.append(afd[i + maxlen])
    print('nb sequences:', len(sentences))
        
    print('Vectorization...')
    x = np.zeros((len(sentences), maxlen, len(chars)), dtype=np.bool)
    y = np.zeros((len(sentences), len(chars)), dtype=np.bool)
    for i, sentence in enumerate(sentences):
        for t, char in enumerate(sentence):
            x[i, t, char_indices[char]] = 1
        y[i, char_indices[next_chars[i]]] = 1

    print('Build model...')
    model = Sequential()
    model.add(LSTM(128, input_shape=(maxlen, len(chars))))
    model.add(Dense(len(chars), activation='softmax'))

    optimizer = RMSprop(lr=0.001)
    model.compile(loss='categorical_crossentropy', optimizer=optimizer)

    print_callback = LambdaCallback(on_epoch_end=on_epoch_end)
    model.fit(x, y,
          batch_size=128,
          epochs=60,
          callbacks=[print_callback])
    model.save('afd_lstm_model.h5')