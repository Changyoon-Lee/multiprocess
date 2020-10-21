# multiprocess

python  multiprocess 패키지의 process를 이용하여 시간이 오래걸리는 nlp 전처리 작업에 적용해보며 효율적으로 작업을 수행해보고자 하였다.

비지도 학습을 이용한 번역([undreamt](https://github.com/Changyoon-Lee/unsupervised_nmt))을 구현하기 위하여 여러 전처리 작업 병렬 처리 수행

1. 한글 4백만 문장corpus konlpy의 kkma를 이용하여 토큰화
2. 영어 5백만 문장corpus(wmt14) 내의 불필요 문장(주소, email, 타 외국어 문장)을 제거
   langdetect 패키지의 detect 함수 이용

3. 위의 영어 corpus nltk이용하여 토큰화



위의 작업 뿐 아니라 필요한 다양한 기능을 병렬 처리로 구현 할 수 있다.



## usage

```
$ python multiprocess.py --input INPUT.TXT --output OUTPUT.TXT
```

INPUT.TXT 는 여기서 전처리 작업할 문서

OUTPUT.TXT는 작업 후 완료 된 문서

#### OPTION

- --lang [ko/en_filter/en] : 사용할 작업(kkma토큰화/langdetect/nltk토큰화) 선택

- --tag : 토큰화 진행시 토큰/tag 형식(ex 사과/NN)으로  tagging을 붙여 진행 





## code flow

- cpu count 함수

```python
n_core = multiprocessing.cpu_count()
```



- iterable 자료 slicing

```python
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
        
sentences_list = list(batch(sentences, num))
```



- process 진행(target에는 진행할 작업의 함수, args에는 그 함수에 들어가는 인자들)

```python
# sentences_list의 수 많큼 process 생성 및 시작
procs = []
for i, sents in enumerate(sentences_list):
    proc = Process(target=target, args=(i+1, sents, args.tag))
    procs.append(proc)
    proc.start()

# complete the processes
for proc in procs:
    proc.join()
```







#### 작업관련

- temp 폴더생성

```python
temp_dir = './temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
```

- 각 process 별로 진행한 작업을 txt형식으로 저장

```python
with open('temp/{}th.txt'.format(i), 'wt', encoding='utf-8') as fw:
    for sentence in sentences:
        pos = kkma.pos(sentence.strip())
        tok = []
        for j in pos:
            tok.append(j[0]+'/'+j[1])
            fw.write(' '.join(tok)+'\n')
```

- cleaning : temp 폴더안의 txt문서들을 OUTPUT.txt의 하나의 파일로 합쳐준다
  그후 shutil 을 이용 하여 temp폴더 및 내부 파일 들을 삭제 시킨다 

```python
def cleaning(result_file_name):
    temp_dir = './temp'
    temps = [temp_dir + '/' + name for name in os.listdir(temp_dir)]
    with open(result_file_name,'wt', encoding='utf-8') as fw:
        for tempfile in temps:
            with open(tempfile, 'rt', encoding='utf-8') as fr:
                fw.writelines(fr.readlines())
    shutil.rmtree(temp_dir)
    print('done')
```



