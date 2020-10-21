from multiprocessing import Process
import multiprocessing
import time
from konlpy.tag import Kkma
import shutil
import os
import sys
import argparse
from nltk.tokenize import word_tokenize
from langdetect import detect
import nltk

def parse_args(argv):
    parser = argparse.ArgumentParser(description='make file used in vecmap')
    parser.add_argument('--input', default=None, help='토큰화를 하려고 하는 원본 txt파일 경로')
    parser.add_argument('--output', default=None, help='토큰화 완료 된 output txt 파일 경로')
    parser.add_argument('--lang', default='en', help='language mode(ko/en/en_filter')
    parser.add_argument('--tag', action='store_true', help='토큰에 tag붙이기')
    return parser.parse_args(argv[1:])

# 한국어 kkma 토크나이즈
def ko_token_func(i, sentences, tag):
    print('{} process 시작--------------------'.format(i))
    kkma = Kkma()

    temp_dir = './temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if tag:
        print('token+tag')
        with open('temp/{}th.txt'.format(i), 'wt', encoding='utf-8') as fw:
            for sentence in sentences:
                pos = kkma.pos(sentence.strip())
                tok = []
                for j in pos:
                    tok.append(j[0]+'/'+j[1])
                fw.write(' '.join(tok)+'\n')
    else:
        print('None tag')
        with open('temp/{}th.txt'.format(i), 'wt', encoding='utf-8') as fw:
            for sentence in sentences:
                fw.write(' '.join(kkma.morphs(sentence.strip()))+'\n')
    print('{}번째 process 진행 완료'.format(i))    

# 영어 nltk 토크나이즈
def en_token_func(i, sentences, tag):
    print('{} process 시작--------------------'.format(i))

    temp_dir = './temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if tag:
        print('token+tag')
        with open('temp/{}th.txt'.format(i), 'wt', encoding='utf-8') as fw:
            for sentence in sentences:
                pos = nltk.pos_tag(sentence.strip())
                tok = []
                for j in pos:
                    tok.append(j[0].lower()+'/'+j[1])
                fw.write(' '.join(tok)+'\n')

    else:
        print('None tag')
        with open('temp/{}th.txt'.format(i), 'wt', encoding='utf-8') as fw:
            for sentence in sentences:
                fw.write(' '.join(word_tokenize(sentence.strip().lower()))+'\n')

    print('{}번째 process 진행 완료'.format(i)) 

def enfilter_func(i, sentences, tag):
    print('{} process 시작--------------------'.format(i))
    temp_dir = './temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    print('영어문장만 걸러내기')
    with open('temp/{}th.txt'.format(i), 'wt', encoding='utf-8') as fw:
        for idx, sentence in enumerate(sentences):
            try:
                if detect(sentence)=='en':
                    fw.write(sentence+'\n')
            except: print(idx, sentence)

def batch(iterable, n):
    iterable=iter(iterable)
    while True:
        chunk=[]
        for i in range(n):
            try:
                chunk.append(next(iterable))
            except StopIteration:
                yield chunk
                return
        yield chunk

# 나누어서 처리하고 저장된 파일들을 하나로 합치고 나머지는 제거
def cleaning(result_file_name):
    temp_dir = './temp'
    temps = [temp_dir + '/' + name for name in os.listdir(temp_dir)]
    with open(result_file_name,'wt', encoding='utf-8') as fw:
        for tempfile in temps:
            with open(tempfile, 'rt', encoding='utf-8') as fr:
                fw.writelines(fr.readlines())
    shutil.rmtree(temp_dir)
    print('done')


if __name__ == "__main__":  # confirms that the code is under main function
    args = parse_args(sys.argv)
    if not (args.input and args.input):
        print('input , output 인자를 입력하시오')

    n_core = multiprocessing.cpu_count()
    print('컴퓨터 cpu core수 : {}'.format(n_core))
    
    with open(args.input, 'rt', encoding='utf-8') as fr:
        sentences = fr.readlines()
    num = len(sentences)//n_core+1
    sentences_list = list(batch(sentences, num))
    print('전체process : {}개\n'.format(n_core))

    procs = []

    if args.lang=='ko': target = ko_token_func 
    elif args.lang=='en_filter': target = enfilter_func 
    else : target = en_token_func
    
    for i, sents in enumerate(sentences_list):
        proc = Process(target=target, args=(i+1, sents, args.tag))
        procs.append(proc)
        proc.start()

    # complete the processes

    for proc in procs:
        proc.join()

    cleaning(args.output)