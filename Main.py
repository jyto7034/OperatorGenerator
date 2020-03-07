import cv2
import pytesseract
import sys, os, re

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\BlasterDinray\AppData\Local\Tesseract-OCR\tesseract.exe'

BASE_CODE, CHOSUNG, JUNGSUNG = 44032, 588, 28
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

# additionalScoreElements = ['ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

TagTable = [
    "신입", "특별채용", "고급 특별 채용",
    "근거리", "원거리", "뱅가드", "가드", "디펜더",
    "스나이퍼", "캐스터", "메딕", "서포터", "스페셜리스트",
    "힐링", "서포트", "딜러", "범위공격", "감속", "생존형", "방어형",
    "디버프", "강제이동", "제어형", "누커", "소환", "쾌속부활", "코스트", "로봇"
]

MiddleOperatorTable = { 
    #-----------뱅가드-----------#
    "지마": [["뱅가드", "서포트"], ["코스트", "서포트"]],
    "텍사스": [["뱅가드", "군중제어"], ["코스트", "군중제어"], ["군중제어", "근거리"], ["군중제어"]],

    #-----------스나이퍼-----------#
    "파이어워치": ["누커"],
    "메테오리테": ["범위공격", "디버프"],

    #-----------메딕-----------#
    "프틸" : [["메딕", "서포트"],["힐링", "서포트"],  ["원거리", "서포트"]],
    "와파린" : [["메딕", "서포트"],["힐링", "서포트"],  ["원거리", "서포트"]],
    
    #-----------디펜더-----------#
    "불칸":[["디펜더", "생존형"], ["방어형", "생존형"], ["방어형", "생존형", "딜러"], ["방어형", "딜러"]], 
    "리스캄": ["방어형", "딜러"],
    "크루아상": [["방어형", "강제이동"], ["디펜더", "강제이동"]],

    #-----------서포터-----------#
    "프라마닉스": ["디버프", "서포터"],
    "이스티나":["딜러", "서포터"],
    "메이어": [["군중제어", "서포터"], ["군중제어", "원거리"]],

    #-----------스페셜리스트-----------#
    "클리프하트": [["스페셜리스트", "딜러"], ["스페셜리스트", "생존형"], ["강제이동", "딜러"], ["스페셜리스트", "강제이동"]],
    "만티코어": [["스페셜리스트", "딜러"], ["스페셜리스트", "생존형"]],
    "에프이터": [["스페셜리스트", "감속"], ["강제이동", "감속"], ["스페셜리스트", "강제이동"]],
    "레드": [["군중제어", "스페셜리스트"], ["군중제어", "쾌속부활"], ["군중제어", "근거리"], ["스페셜리스트", "방어형"]],
}

LowOperatorTable = {
    #-----------스나이퍼-----------#
    "메테오리테": [["범위공격", "스나이퍼"], ["디버프", "스나이퍼"]],
    "시라유키": [["범위공격", "스나이퍼"], ["범위공격", "감속"]],
    "메테오": ["디버프", "스나이퍼"],
    "제시카": [["생존형", "스나이퍼"], ["생존형", "원거리"]],

    #-----------캐스터-----------#
    "헤이즈": ["디버프", "캐스터"],

    #-----------가드-----------#
    "도베르만": [["서포트", "가드"], ["서포트", "딜러"]],
    "에스텔": [["범위공격", "생존형"], ["범위공격", "근거리"], ["범위공격", "가드"]],
    "스펙터": [["범위공격", "생존형"], ["범위공격", "근거리"], ["범위공격", "가드"]],
    "프로스트리프": ["감속", "가드"],

    #-----------디펜더-----------#
    "니어":[["힐링", "방어형"], ["힐링", "디펜더"], ["힐링", "근거리"]],
    "굼":[["힐링", "방어형"], ["힐링", "디펜더"], ["힐링", "근거리"]],
    "마터호른": [["방어형", "남성대원"], ["디펜더", "남성대원"], ["근거리", "남성대원"]],

    #-----------스페셜리스트-----------#
    "쇼":["스페셜리스트", "강제이동"],
    "로프":["스페셜리스트", "강제이동"],
    "그라벨":[["스페셜리스트", "방어형"], ["쾌속부활", "방어형"]],

    # #-----------기타-----------#
    # ["감속", "근거리"]: ["프로스트리프", "에프이터"],
    # ["감속", "딜러"]: ["프로스트리프", "이스티나"],
    # ["서포트", "근거리"]: ["도베르만", "지마"],
    # ["디버프", "딜러"]: ["헤이즈", "메테오"]
}


def convert(keyword):
    split_keyword_list = list(keyword)
    result = list()
    for keyword in split_keyword_list:
        if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', keyword) is not None:
            char_code = ord(keyword) - BASE_CODE
            char1 = int(char_code / CHOSUNG)
            result.append(CHOSUNG_LIST[char1])
            char2 = int((char_code - (CHOSUNG * char1)) / JUNGSUNG)
            result.append(JUNGSUNG_LIST[char2])
            char3 = int((char_code - (CHOSUNG * char1) - (JUNGSUNG * char2)))
            if char3==0:
                result.append('#')
            else:
                result.append(JONGSUNG_LIST[char3])
        else:
            result.append(keyword)
    return result

def CheckHowSimilar(ExtractionTag, CurrentTag):
    _ExtractionTag = convert(ExtractionTag)
    _CurrentTag = convert(CurrentTag)

    stdScore = 0
    Score = 0

    for item in _ExtractionTag:
        if item in _CurrentTag:
            if item in CHOSUNG_LIST:
                Score += 2
                _ExtractionTag.remove(item)
            elif item in JUNGSUNG_LIST:
                Score += 1
                _ExtractionTag.remove(item)
        else:
            Score -= 1
    
    for item in _CurrentTag:
        if item in CHOSUNG_LIST:
            stdScore += 2
            _CurrentTag.remove(item)
        elif item in JUNGSUNG_LIST:
            stdScore += 1
            _CurrentTag.remove(item)
    stdScore /= 2
    
    # print("stdScore :", stdScore)
    # print("Score :", Score)

    if Score > stdScore:
        return True
    else:
        return False

class OperatorGenerator:
    OutImgList = []
    ScannedTags = []
    Operator = {}

    def pretreatment(self, img):
        for item in img:
            ImgFullName = item
            OutImg = item[:len(item) - 4] + '_pred' + item[len(item) - 4:]

            cvimg = cv2.imread('./Input/' + ImgFullName,cv2.IMREAD_COLOR)
            (h, w) = cvimg.shape[:2]
            wStart = int(w * 0.29)
            wEnd = int(w * 0.67)
            hStart = int(h*0.5)
            hEnd = int(h*0.66)   

            cvimg = cvimg[hStart:hEnd, wStart:wEnd]
            gray = cv2.cvtColor(cvimg, cv2.COLOR_RGB2GRAY)
            ret, re = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
            cv2.imwrite('./Output/' + OutImg, re)
            self.OutImgList.append(OutImg)
        return 0

    def DeepExtractionTag(self, tag, ScanResult):
        #ScanResult = "ㅁㄴ포ㅇㅂㅈㄷㅋㅌㅊ서포터ㅁㄴㅇㅂㅈㄷㅋ터ㅌㅊ"
        #tag = 서포터
        strLen = len(tag)
        ratedZone = []
        rateList = []
        for tagIdx in range(0, strLen):
            for idx in range(0, ScanResult.count(tag[tagIdx])):
                rateItem = ScanResult[ScanResult.find(tag[tagIdx]): ScanResult.find(tag[tagIdx]) + 4].replace(" ", "").replace("\n", "")
                if len(rateItem) == 1:
                    ScanResult = ScanResult.replace(ScanResult[ScanResult.find(tag[tagIdx]): ScanResult.find(tag[tagIdx]) + 4], " ", 1)
                elif len(rateItem) > 1:
                    ratedZone.append(rateItem)
                    # ScanResult = ScanResult.replace(ScanResult[ScanResult.find(tag[tagIdx]): ScanResult.find(tag[tagIdx]) + 4], " ", 1)
                else:
                    pass
        
        if len(ratedZone) == 0:
            return False

        for item in ratedZone:
            if len(item) > 1:
                rateList.append(0)
                for idx in item:
                    if idx in tag:
                        rateList[ratedZone.index(item)] += 1

        _return = [ratedZone[rateList.index(max(rateList))], ScanResult]
        return _return

    def ExtractionTag(self, ScanResult):
        TagList = []
        if ScanResult.count("가드") == 2:
            TagList.extend(["뱅가드", "가드"])
            ScanResult = ScanResult.replace("가드", " ")
        elif ScanResult.count("가드") == 1:
            if "뱅가드" in ScanResult:
                TagList.append("뱅가드")
                ScanResult = ScanResult.replace("뱅가드", " ")
            else:
                TagList.append("가드")
                ScanResult = ScanResult.replace("가드", " ")
        for tag in TagTable:
            if tag in ScanResult:
                TagList.append(tag)
        return TagList

    def ScanText(self):
        print("#######################")
        for item in self.OutImgList:
            print(item)
            ScanResult = pytesseract.image_to_string('./Output/' + item, lang='kor', config='--psm 6')
            tags = self.ExtractionTag(ScanResult)
            if len(tags) != 5:
                for tag in TagTable:
                    # print("Current Tag :", tag)
                    if tag not in tags:
                        temp = self.DeepExtractionTag(tag, ScanResult)
                        if  temp == False:
                            pass
                        else:
                            ScanResult = temp[1]
                            result = temp[0]
                            # print("DeepExtraction result :", result)
                            # print("tag :", tag)
                            if CheckHowSimilar(result, tag) == True:
                                print("[*]Found tag :", tag)
                                tags.append(tag)
                            else:
                                # print("Wrong Tag :", tag)
                                pass
            if len(tags) != 5:
                print(tags)
                print("태그인식불가")
            print(tags)
            self.ScannedTags.append(tags)
        return 0

    def ExtractionOperator(self):
        for operatorName in MiddleOperatorTable:
            for ScannedTags in self.ScannedTags:
                for MiddleOperatorList in MiddleOperatorTable[operatorName]:
                    MiddleIntersectionTags = set(MiddleOperatorList) & set(ScannedTags)
                    # print("ScannedTags : ",ScannedTags)
                    # print("MiddleOperatorTable :",MiddleOperatorList)
                    # print("MiddleIntersectionTags : ", MiddleIntersectionTags)
                    # print("\n")
                    Size = len(MiddleIntersectionTags)
                    if Size == 1 and len(MiddleOperatorTable[operatorName]) == 1:
                        self.Operator[operatorName] = MiddleIntersectionTags
                        break
                    elif Size == 2:
                        self.Operator[operatorName] = MiddleIntersectionTags
                        break

        for operatorName in LowOperatorTable:
            for ScannedTags in self.ScannedTags:
                for LowOperatorList in LowOperatorTable[operatorName]:
                    LowIntersectionTags = set(LowOperatorList) & set(ScannedTags)
                    # print("ScannedTags : ",ScannedTags)
                    # print("LowOperatorTable :",LowOperatorList)
                    # print("LowIntersectionTags : ", LowIntersectionTags)
                    # print("\n")
                    Size = len(LowIntersectionTags)
                    if Size == 1 and len(LowOperatorList) == 1:
                        self.Operator[operatorName] = LowIntersectionTags
                        break
                    elif Size == 2:
                        self.Operator[operatorName] = LowIntersectionTags
                        break

if __name__ == "__main__":
    Generator = OperatorGenerator()
    img = os.listdir("./Input")
    Generator.pretreatment(img)
    Generator.ScanText()
    Generator.ExtractionOperator()
    print("Result", Generator.Operator)
