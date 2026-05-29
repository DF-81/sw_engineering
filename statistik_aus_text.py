#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modul-Description:
Here you can describe what your code should do.
"""

# Import of standard libraries or additional packages
import os

def hauptfunktion():
    """
    Die Hauptlogik Ihres Programms.
    """
    print("Hallo aus der Hauptfunktion!")

# Here follows the 'Entry Point' (Einstiegspunkt)

if __name__ == "__main__":

    with open("text.txt", "r") as file:
        text = file.read()

    # Replace all special characters 
    text = text.replace(",", "").replace(".", "").replace("!", "").replace("?", "").replace(";", "").replace("ü", "ue").replace("ö", "oe").replace("ä", "ae").replace("ß", "ss")
    
    # lowercase the text
    text = text.lower()

    # split and count words
    words = text.split()
    word_count = len(words)
    print(f"Anzahl der Wörter: {word_count}")

    # frequency of each word
    word_frequency = {}    
    for word in words:
        word_frequency[word] = word_frequency.get(word, 0) + 1
    print(word_frequency)

    # which word is the most common
    most_common_word = max(word_frequency, key=word_frequency.get)
    frequency = word_frequency[most_common_word]
    print(f"[('{most_common_word}', {frequency})]")

    # index of the most common word
    index_most_common_word = words.index(most_common_word)
    print(f"Index of the most common word: {index_most_common_word}")

    # show index of the words in the whole text
    # create dictionary again to cleanup integer from the previous step
    word_index = {} 
    # enumerate() liefert den Index (i) und das Wort
    for i, word in enumerate(words):
    # create a new list and add a index to the list for each word
        word_index.setdefault(word, []).append(i)
    print(word_index)

    # Berechnung der Anzahl der Sätze
    #sentences = text.split('.')
    #sentence_count = len(sentences) - 1  # Letztes Element ist leer

    # Berechnung der durchschnittlichen Wortlänge
    #total_characters = sum(len(word) for word in words)
    #average_word_length = total_characters / word_count if word_count > 0 else 0

        #print(f"Anzahl der Sätze: {sentence_count}")
    #print(f"Durchschnittliche Wortlänge: {average_word_length:.2f}")