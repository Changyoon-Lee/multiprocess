# multiprocess

python의 multiprocess 패키지의 process를 이용하여 시간이 오래걸리는 nlp 전처리 작업에 적용해보며 효율적으로 작업을 수행해보고자 하였다.

비지도 학습을 이용한 번역을 하기 위하여한 여러 전처리 작업

1. 한글 4백만 문장corpus konlpy의 kkma를 이용하여 토큰화
2. 영어 5백만 문장corpus(wmt14) 내의 불필요 문장(주소, email, 타 외국어 문장)을 제거
   langdetect 패키지의 detect 함수 이용