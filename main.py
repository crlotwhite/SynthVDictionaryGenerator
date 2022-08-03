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


K2J = j2d('japanese-romaji/Korean.json')
K2E = j2d('english-arpabet/Korean.json')
K2M = j2d('mandarin-xsampa/Korean.json')

'''
발음 기호가 없는 것은 생략

ː 기호 제거
[] 제거

1. 원어 처리
2. 중복 확인
3. 발음 항목 확인
4-1. 발음 항목이 비어 있으면 생략
4-2. 있으면 전처리 후 입력
5. 데이터베이스에 행 추가
6. alt 추가 e.g. '가계야카다/가게야카다'
'''
result = {}
header = []
for page_number in range(1, 14):
    with open(f'page{page_number}.csv') as page:
        rdr = csv.reader(page)
        header = next(rdr)
        for row in rdr:
            # 1
            org = row[0]
            org1 = org[:org.rfind('(')] if org.rfind('(') != -1 else org
            org2 = org1.replace('-', '')
            # 2
            if result.get(org2) is None:
                # 3
                pronun = row[8]
                # 4
                if bool(pronun):
                    pronun1 = pronun[1:-1]
                    pronun2 = pronun1.replace('ː', '')
                    pronun3 = pronun2.split('/')
                    # 6
                    if len(pronun3) == 1:
                        pronun3.append('')

                    # 5
                    result.update({
                        org2: pronun3
                    })

    print(f'page {page_number} is complete...')

print('== Created Dict Successfully ==')

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