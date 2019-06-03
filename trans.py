#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# how to obtain google translation api key: https://cloud.google.com/translate/docs/quickstart-client-libraries-v3#client-libraries-install-python

import json
import glob
import os
import re
import requests
import json
import time
import logging
from google.cloud import translate_v3beta1 as translate

# from googletrans import Translator
# translator = Translator()

logging.basicConfig(level=logging.INFO)

client = translate.TranslationServiceClient()
project_id = 'your-project-id'
location = 'global'
parent = client.location_path(project_id, location)

def send_request(original):
  # translated = translator.translate(original, dest='vi', src='en').text  
  # time.sleep(0.5)
  response = client.translate_text(
      parent=parent,
      contents=[original],
      mime_type='text/plain',  # mime types: text/plain, text/html
      source_language_code='en-US',
      target_language_code='vi-VN')
  translated = response.translations[0].translated_text
  return(translated)

def translate(original):
  vars = []
  if re.search('plural', original):
    return (original, 'plural')
  translated = send_request(original)
  return (translated, None)

try:
  os.mkdir('../messages_google/')
except FileExistsError:
  pass

issue = None
with open('problems.tsv', 'w') as problems:
  for filename in glob.glob('../messages/*.json'):
    with open(filename, newline='') as jsonfile:
      store = json.load(jsonfile)
      translated_strings = {}
      for key, original in store['en'].items():
        (translation, issue) = translate(original)
        status = ''
        if issue:
          problems.write(f'{filename}\t{original}\n')
          status = '!'
        logging.info(f'{status}{filename}\t{original}\t{translation}')
        translated_strings.update({key: translation})
    with open(f'../messages_google/{os.path.basename(filename)}', 'w', encoding='utf-8') as writefile:
      json.dump({'en': translated_strings}, writefile, ensure_ascii=False, indent=4)
