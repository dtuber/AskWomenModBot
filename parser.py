import re

# as the name implies, this is the beginning of a parsing module
# i'm not huge on object orientation right now, just looking to get
# something going for being able to break down and analyze strings
# in a regular way

def breakdown(text):
	'''Chops up text into a list containing the sentences, with their
	punctuation stripped, that were in the original text. Empty sentences
	are removed automatically. The letters are converted to lower case.'''
	sentences = [x.strip().lower() for x in text.split(".")]
	return [re.sub('[^a-z0-9 ]', "", x) for x in sentences if x != ""]

def has_words(text_list, word_list):
	'''Looking at the sentences now in text_list, search for matches of
	the words in word_list, including pluralizations. Returns a list
	containing the words it found, if it happened to find any. Otherwise
	it returns None object.'''
	resultant = []
	for word in word_list:
		for sentence in text_list:
			if sentence.find(word) != -1:
				resultant.append(word)
	if resultant != []: return resultant
	else: return None

