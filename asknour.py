import subprocess
import sys
from subprocess import *
import numpy as np
import pandas as pd
import json
import re
import pickle


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install("sklearn_crfsuite")
import sklearn_crfsuite


def extract_features(sentence, index):
  return {
      'word':sentence[index],
      'is_first':index==0,
      'is_last':index ==len(sentence)-1,
      'is_capitalized':sentence[index][0].upper() == sentence[index][0],
      'is_all_caps': sentence[index].upper() == sentence[index],
      'is_all_lower': sentence[index].lower() == sentence[index],
      'is_alphanumeric': int(bool((re.match('^(?=.*[0-9]$)(?=.*[a-zA-Z])',sentence[index])))),
      'prefix-1':sentence[index][0],
      'prefix-2':sentence[index][:2],
      'prefix-3':sentence[index][:3],
      'prefix-3':sentence[index][:4],
      'suffix-1':sentence[index][-1],
      'suffix-2':sentence[index][-2:],
      'suffix-3':sentence[index][-3:],
      'suffix-3':sentence[index][-4:],
      'prev_word':'' if index == 0 else sentence[index-1],
      'next_word':'' if index < len(sentence) else sentence[index+1],
      'has_hyphen': '-' in sentence[index],
      'is_numeric': sentence[index].isdigit(),
      'capitals_inside': sentence[index][1:].lower() != sentence[index][1:]
  }


def posTaggerMapper(tags):
  mapper = {
    "ADJ": "صفة",
    "ADP": "حرف جر",
    "ADV": "ظرف",
    "AUX": "فعل مساعد",
    "CONJ": "حرف عطف",
    "DET": "محدد",
    "INTJ": "أداة تعجب",
    "NOUN": "اسم",
    "NUM": "رقم",
    "PART": "حرف",
    "PRON": "ضمير",
    "PROPN": "اسم صحيح",
    "PUNCT": "علامة ترقيم",
    "SCONJ": "رابط تابع",
    "SYM": "رمز",
    "VERB": "فعل",
    "X": "آخر",
    "_" : "آخر"}
  
  result = []
  for t in tags:
    result.append(mapper[t])
  return result


def jarWrapper(*args):
    process = Popen(['java', '-jar']+list(args), stdout=PIPE, stderr=PIPE, encoding='UTF-8')
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        if line != '' and line.endswith('\n'):
            ret.append(line[:-1])
    stdout, stderr = process.communicate()
    ret += stdout.split('\n')
    if stderr != '':
        ret += stderr.split('\n')
    ret.remove('')
    return ret

def getRelatedPhrases(phrase, depth, output="normal"):
  args = ['./asknour/AskNourGetRelatedPhrases.bin', phrase, str(depth)]
  result = str(jarWrapper(*args)).replace("[","").replace("]","").replace("'","").split(", ")
  if output == "pandas":
    result = pd.DataFrame (result)
    result.columns = ["result"]

  return result


def getLemma(text, output="normal"):
  args = ['./asknour/AskNourLemma.bin', text]
  result = str(jarWrapper(*args)).replace("[","").replace("]","").replace("'","").split(", ")
  if output == "pandas":
    series_1 = pd.Series(text.split(" "))
    series_2 = pd.Series(result)
    result = pd.DataFrame(columns = ['word', 'lemma'])
    result['word'] = series_1
    result['lemma'] = series_2
  return result


def getPOSTags(text, output="normal"):
  asknour_taager = pickle.load(open("./asknour/AskNour_ud_tagger.bin", "rb"))
  features = [extract_features(text.split(), idx) for idx in range(len(text.split()))]
  result = asknour_taager.predict_single(features)
  if output == "pandas":
    series_1 = pd.Series(text.split(" "))
    series_2 = pd.Series(result)
    series_3 = pd.Series(posTaggerMapper(result))
    result = pd.DataFrame(columns = ['word', 'pos','pos_ar'])
    result['word'] = series_1
    result['pos'] = series_2
    result['pos_ar'] = series_3
  return result

def getPOSTagsWithLemma(text, output="normal"):

  text_lemma = " ".join(getLemma(text))
  asknour_taager = pickle.load(open("./asknour/AskNour_ud_tagger.bin", "rb"))
  features = [extract_features(text_lemma.split(), idx) for idx in range(len(text.split()))]
  result = asknour_taager.predict_single(features)
  if output == "pandas":
    series_1 = pd.Series(text.split(" "))
    series_2 = pd.Series(result)
    series_3 = pd.Series(posTaggerMapper(result))
    result = pd.DataFrame(columns = ['word', 'pos','pos_ar'])
    result['word'] = series_1
    result['pos'] = series_2
    result['pos_ar'] = series_3
  return result


def getSynonyms(word, output="normal"):
  args = ['./asknour/AskNourSynonyms.bin', word]
  result = str(jarWrapper(*args)).replace("[","").replace("]","").replace("'","").split(", ")
  if output == "pandas":
    result = pd.DataFrame (result)
    result.columns = ["result"]

  return result

def getVerbsConjugation(word):
  args = ['./asknour/AskNourVerbsConjugation.bin', word]
  data = json.loads(json.loads(json.dumps(jarWrapper(*args)))[0])
  return data

def getVerbTashkeel(verb, output="normal"):
  args = ['./asknour/AskNourPossibleVerbTashkeel.bin', verb]
  result = str(jarWrapper(*args)).replace("[","").replace("]","").replace("'","").split(", ")
  if output == "pandas":
    result = pd.DataFrame (result)
    result.columns = ["result"]

  return result


def getVerbWazen(verb, output="normal"):
  args = ['./asknour/AskNourPossibleWazen.bin', verb]
  result = str(jarWrapper(*args)).replace("[","").replace("]","").replace("'","").split(", ")
  if output == "pandas":
    result = pd.DataFrame (result)
    result.columns = ["result"]

  return result
