import csv

'''
1. json 읽기
2. dict로 바꾸기
'''


def j2d(file_name):
    import json

    result = {}
    with open(file_name, encoding='utf-8-sig') as file:
        data = json.load(file)['data']
        for d in data:
            result[d['w']] = d['p']

        return result


K2J = j2d('synthv-dictionaries/japanese-romaji/Korean.json')
K2E = j2d('synthv-dictionaries/english-arpabet/Korean.json')
K2M = j2d('synthv-dictionaries/mandarin-xsampa/Korean.json')

'''
발음 기호가 없는 것은 생략

ː 기호 제거
[] 제거

1. 원어 처리
2. 중복 확인
3. 발음 항목 확인
4-1. 발음 항목이 비어 있으면 복사
4-2. 있으면 전처리 후 입력
5. 데이터베이스에 행 추가
6. alt 추가 e.g. '가계야카다/가게야카다'
7. 활용 항목 처리 
e.g. 피핵되어[피ː핵뙤어/피ː핵뛔여](피핵돼[피ː핵뙈]), 피핵되니[피ː핵뙤니/피ː핵뛔니]

예외
1. 빈 발음이 떨어져 나온 경우, 추가 않함.
결과적으로 겹쳐서 저장되므로 마지막에 수동으로 삭제 
e.g. 완합되니[완합뙤니/완합뛔니]([완합뙈])
'''

result = {}
header = []
for page_number in range(1, 14):
    with open(f'page{page_number}.csv') as page:
        rdr = csv.reader(page)
        header = next(rdr)
        for row in rdr:
            # 1 원어 정리
            org = row[0]
            org1 = org[:org.rfind('(')] if org.rfind('(') != -1 else org
            org2 = org1.replace('-', '')
            # 2 중복 확인
            if result.get(org2) is None:
                # 3 발음 항목 확인
                pronun = row[8]
                # 4-2 있으면 전처리 시작
                if bool(pronun):
                    pronun1 = pronun[1:-1]
                    pronun2 = pronun1.replace('ː', '')

                    pronun3 = pronun2.split('/')

                    # 6 alt 발음 분리
                    if len(pronun3) == 1:
                        pronun3.append('')

                    # 5 행에 추가
                    result.update({
                        org2: pronun3
                    })
                else:
                    # 4-1 비어 있으면 복사
                    result.update({
                        org2: [org2, '']
                    })

            # 7 활용법들 처리
            raw_adv_words = row[9]
            if bool(raw_adv_words):
                raw_adv_words2 = raw_adv_words.replace(' ', '')
                adv_words = raw_adv_words2.split(',')
                for adv_word in adv_words:
                    # 괄호로 둘러 싸인 변형 분리
                    word_split_list = adv_word.split('(')
                    for word_split in word_split_list:
                        # 괄호 정리
                        word = word_split.replace(')', '')
                        pronun_point = word.find('[')
                        # 발음 기호가 없을 때
                        if pronun_point == -1:
                            result.update({
                                word: [word, '']
                            })
                        else:
                            org = word[:pronun_point]

                            # 중복 확인
                            if result.get(org) is not None:
                                continue

                            # 예외 체크
                            if org.find('-') != -1:
                                print(f'{org}에 - 가 있음')

                            pronun = word[pronun_point + 1:-1]
                            pronun2 = pronun.replace('ː', '')

                            # 이 부분에서 \xad 발생, find로 찾아서 감싸도 생성됨
                            # 원인 찾으면 수정 필요
                            # '몰아닥쳐' 이 한 단어에서만 발생함
                            pronun3 = pronun2.split('/')

                            # 빈공간 보정
                            if len(pronun3) == 1:
                                pronun3.append('')

                            result.update({
                                org: pronun3
                            })

    print(f'page {page_number} is complete...')

print('== Created Dict Successfully ==')

# 사전 검증
for k, v in result.items():
    for _v in v:
        if 'ㄱ' in k \
                or 'ㄲ' in k \
                or 'ㄴ' in k \
                or 'ㄷ' in k \
                or 'ㄸ' in k \
                or 'ㄹ' in k \
                or 'ㅁ' in k \
                or 'ㅂ' in k \
                or 'ㅃ' in k \
                or 'ㅅ' in k \
                or 'ㅆ' in k \
                or 'ㅇ' in k \
                or 'ㅈ' in k \
                or 'ㅉ' in k \
                or 'ㅊ' in k \
                or 'ㅋ' in k \
                or 'ㅌ' in k \
                or 'ㅍ' in k \
                or 'ㅎ' in k:
            continue

        if '[' in _v or ']' in _v or '(' in _v or ')' in _v or  '­' in _v:
            print(f'{k}의 발음 기호가 올바르지 않습니다. {v}')
            continue

        if _v != '' and len(k) != len(_v):
            print(f'{k}의 발음 기호가 올바르지 않습니다. {v}')
            continue

# 예외 1 처리
del result['']

# 예외 단어 수정
result['등가계'] = ['등까계', '등까게']
result['몰아닥쳐'] = ['모라닥처', '']
result['외떡잎만'] = ['외떵님만', '웨떵님만']

# 사전 오류, 제보한 상태
del result['진선진미니하니']
result['진선진미하니'] = ['진선진미하니', '']

err = []


def k2jem(words):
    """
    글자 단위로 나눠서 각 발음 기호로 전환한다.
    """

    j = []
    e = []
    m = []

    for word in words:
        _j = ''
        _e = ''
        _m = ''
        if not bool(word):
            j.append('')
            e.append('')
            m.append('')

        for ch in word:
            try:
                _j += K2J[ch] + ' '
                _e += K2E[ch] + ' '
                _m += K2M[ch] + ' '
            except:
                err.append(ch)
                if ch == '­':
                    print(f'이상한 문자 {ch}가 {word}에 있음.')
                    err.pop()

                j.append('')
                e.append('')
                m.append('')
                break
        else:
            j.append(_j[:-1])
            e.append(_e[:-1])
            m.append(_m[:-1])

    return j, e, m


'''
1. 사전 데이터 가져오기
2. k->j,e,m
3. 합치기
4. 데이터베이스에 추가하기
'''
with open('output.csv', 'w', newline='') as f:
    wrt = csv.writer(f)
    for word, pron in result.items():
        j, e, m = k2jem(pron)
        wrt.writerow(
            [
                word,
                pron[0],
                pron[1],
                j[0],
                j[1],
                e[0],
                e[1],
                m[0],
                m[1],
            ]
        )

print('== end of create result ==')

err = list(set(err))
with open('error.csv', 'w', newline='') as f:
    wrt = csv.writer(f)
    for e in err:
        wrt.writerow([e])

print('== complete ==')
