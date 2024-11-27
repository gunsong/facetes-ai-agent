import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)

class TextParser:
    """LLM 응답을 구조화된 형식으로 파싱하는 클래스"""
    
    def __init__(self):
        """LLM 응답을 구조화된 형식으로 파싱하는 클래스"""
        # 주요 카테고리 및 관련 키워드 정의
        self.topic_categories = {
            "일상생활": [
                "식사", "수면", "휴식", "집안일",
                "요리", "청소", "빨래", "설거지",
                "장보기", "식사준비", "집정리", "생활용품",
                "아침", "점심", "저녁", "간식",
                "출퇴근", "등하교", "샤워", "목욕",
                "TV시청", "인터넷", "스마트폰"
            ],
            "여가활동": [
                "여행", "관광", "취미", "운동", "문화생활", "레저",
                "영화", "공연", "전시", "독서", "게임", "등산",
                "캠핑", "낚시", "쇼핑", "드라이브",
                "음악감상", "그림", "사진", "요가",
                "수영", "자전거", "골프", "테니스",
                "스포츠", "공예", "원예", "반려동물"
            ],
            "사회활동": [
                "모임", "봉사", "종교활동", "지역활동",
                "동호회", "친목회", "동창회", "동아리",
                "자원봉사", "기부", "후원", "멘토링",
                "강연", "세미나", "워크샵", "컨퍼런스",
                "시위", "집회", "투표", "선거",
                "지역행사", "축제", "바자회"
            ],
            "업무/학업": [
                "직장", "학교", "자기개발", "연구",
                "회의", "프로젝트", "발표", "보고",
                "수업", "과제", "시험", "공부",
                "자격증", "어학", "취업준비", "이직",
                "인터뷰", "교육", "훈련", "실습",
                "논문", "리서치", "조사", "분석"
            ],
            "건강/복지": [
                "의료", "운동", "심리", "복지서비스",
                "병원", "치료", "검진", "예방접종",
                "재활", "물리치료", "심리상담", "명상",
                "건강검진", "영양관리", "다이어트", "식이요법",
                "금연", "금주", "스트레스관리", "수면관리",
                "요양", "돌봄", "간병"
            ],
            "관계": [
                "가족", "친구", "동료", "연인",
                "부모", "자녀", "형제", "자매",
                "친척", "이웃", "선후배", "스승",
                "배우자", "약혼자", "데이트", "소개팅",
                "상담", "대화", "갈등", "화해",
                "모임", "파티", "경조사"
            ],
            "경제활동": [
                "소비", "투자", "재테크", "쇼핑",
                "저축", "대출", "보험", "연금",
                "주식", "부동산", "가계부", "예산",
                "세금", "급여", "월급", "수입",
                "지출", "할인", "적금", "펀드",
                "창업", "부업", "아르바이트"
            ]
        }
        
        # 키워드별 서브카테고리 매핑
        self.keyword_subcategories = {
            # 일상생활 관련
            "요리": "일상생활",
            "청소": "일상생활",
            "빨래": "일상생활",
            "설거지": "일상생활",
            "장보기": "일상생활",
            "식사준비": "일상생활",
            "집정리": "일상생활",
            "출퇴근": "일상생활",
            "등하교": "일상생활",
            
            # 여가활동 관련
            "영화감상": "여가활동",
            "공연관람": "여가활동",
            "전시관람": "여가활동",
            "독서": "여가활동",
            "게임": "여가활동",
            "등산": "여가활동",
            "캠핑": "여가활동",
            "낚시": "여가활동",
            
            # 사회활동 관련
            "봉사활동": "사회활동",
            "종교활동": "사회활동",
            "동호회": "사회활동",
            "친목회": "사회활동",
            "동창회": "사회활동",
            
            # 업무/학업 관련
            "회의": "업무/학업",
            "프로젝트": "업무/학업",
            "발표": "업무/학업",
            "수업": "업무/학업",
            "과제": "업무/학업",
            "시험": "업무/학업",
            
            # 건강/복지 관련
            "병원진료": "건강/복지",
            "치료": "건강/복지",
            "검진": "건강/복지",
            "상담": "건강/복지",
            "운동": "건강/복지",
            "요가": "건강/복지",
            
            # 관계 관련
            "가족모임": "관계",
            "친구만남": "관계",
            "데이트": "관계",
            "소개팅": "관계",
            "결혼식": "관계",
            "장례식": "관계",
            
            # 경제활동 관련
            "쇼핑": "경제활동",
            "투자": "경제활동",
            "저축": "경제활동",
            "재테크": "경제활동",
            "가계부": "경제활동",
            "은행업무": "경제활동"
        }

    def parse_llm_response(self, response: str) -> Dict:
        """LLM 응답 파싱"""
        # try:
        #     # JSON 형식 검증 및 파싱
        #     if not response or not response.strip():
        #         return self._generate_default_analysis()
                
        #     # JSON 블록 추출
        #     json_block = self._extract_json_block(response)
        #     if not json_block:
        #         return self._generate_default_analysis()
                
        #     # JSON 파싱
        #     parsed_data = json.loads(json_block)
            
        #     # 필수 필드 검증 및 보완
        #     return self._validate_and_complete_analysis(parsed_data)
            
        # except json.JSONDecodeError as e:
        #     logger.error(f"JSON parsing error: {str(e)}")
        #     return self._generate_default_analysis()
        # except Exception as e:
        #     logger.error(f"Error parsing LLM response: {str(e)}")
        #     return self._generate_default_analysis()
        try:
            # JSON 문자열에서 실제 JSON 부분 추출
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                return self._generate_default_analysis()
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # 키 매핑 수정
            return {
                "main_topic": data.get("메인 주제", "unknown"),
                "sub_topics": {
                    "activities": data.get("세부 주제", {}).get("활동 유형", []),
                    "temporal": data.get("세부 주제", {}).get("시간 요소", []),
                    "spatial": data.get("세부 주제", {}).get("공간 요소", []),
                    "companions": data.get("세부 주제", {}).get("동반자", [])
                },
                "intent": data.get("의도 분석", "unknown"),
                "keywords": data.get("키워드", []),
                "reliability_score": data.get("신뢰도 점수", 0),
                "sentiment": {
                    "type": data.get("감정 상태", {}).get("유형", "neutral"),
                    "intensity": data.get("감정 상태", {}).get("강도", 50),
                    "detail": data.get("감정 상태", {}).get("세부감정", "unknown")
                }
            }
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return self._generate_default_analysis()

    def _extract_json_block(self, text: str) -> str:
        """JSON 블록 추출"""
        try:
            # JSON 블록을 찾기 위한 정규식 패턴
            pattern = r'\{(?:[^{}]|(?R))*\}'
            matches = re.finditer(pattern, text)
            return max((m.group() for m in matches), key=len, default='{}')
        except Exception:
            return '{}'

    def _validate_and_complete_analysis(self, data: Dict) -> Dict:
        """분석 결과 검증 및 보완"""
        default = self._generate_default_analysis()
        
        # 메인 토픽 검증
        if not data.get("main_topic"):
            data["main_topic"] = self._infer_main_topic(data)
            
        # 서브 토픽 검증
        if "sub_topics" not in data or not isinstance(data["sub_topics"], dict):
            data["sub_topics"] = default["sub_topics"]
        else:
            for key in default["sub_topics"]:
                if key not in data["sub_topics"]:
                    data["sub_topics"][key] = []
                    
        # 키워드 검증
        if "keywords" not in data or not isinstance(data["keywords"], list):
            data["keywords"] = []
            
        # 감정 분석 검증
        if "sentiment" not in data or not isinstance(data["sentiment"], dict):
            data["sentiment"] = default["sentiment"]
            
        # 신뢰도 점수 검증
        if "reliability_score" not in data:
            data["reliability_score"] = self._calculate_reliability_score(data)
            
        # 의도 분석 검증
        if "intent" not in data or data["intent"] == "unknown":
            data["intent"] = self._infer_intent(data)
            
        return data

    def _infer_intent(self, text: str) -> str:
        """사용자 입력의 의도를 추론"""
        intent_patterns = {
            "정보 요청": ["뭐", "어떻게", "언제", "어디서", "누가"],
            "의견/조언 요청": ["조언", "생각", "추천", "괜찮을까"],
            "확인/검증": ["맞나요", "확실한가요", "맞죠"],
            "제안/추천": ["추천", "제안", "알려주세요"],
            "감정 표현": ["좋아", "싫어", "기뻐", "슬퍼"],
            "행동 선언": ["하겠습니다", "할게요", "해야겠어"]
        }

        for intent, patterns in intent_patterns.items():
            if any(pattern in text for pattern in patterns):
                return intent

        return "기타"  # 기본값

    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """텍스트를 섹션별로 분리"""
        try:
            sections = {}
            current_section = None
            current_content = []

            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # 새로운 섹션 시작 확인
                if line.startswith('*') and ':' in line:
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = line.split(':')[0].replace('*', '').strip()
                    current_content = [line.split(':', 1)[1].strip()]
                elif current_section:
                    current_content.append(line)

            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()

            return sections

        except Exception as e:
            logger.error(f"Error splitting sections: {str(e)}")
            return {}

    def _parse_main_topic(self, text: str) -> Union[str, tuple]:
        """
        메인 주제 파싱
        Returns:
            Union[str, tuple]: 카테고리 또는 (카테고리, 서브카테고리) 튜플
        """
        try:
            # 대괄호 안의 내용 추출
            match = re.search(r'\[(.*?)\]', text)
            if match:
                topic = match.group(1).strip().lower()
                
                # 1. 직접 카테고리 매칭
                if topic in self.topic_categories:
                    logger.info(f"직접 카테고리 매칭 성공: {topic}")
                    return topic

                # 2. 키워드 기반 카테고리 매칭
                for category, keywords in self.topic_categories.items():
                    if any(keyword in topic for keyword in keywords):
                        logger.info(f"키워드 기반 카테고리 매칭 성공: {topic} -> {category}")
                        return category

                # 3. 서브카테고리 매핑 확인
                for keyword, main_category in self.keyword_subcategories.items():
                    if keyword in topic:
                        logger.info(f"서브카테고리 매핑 성공: {topic} -> {main_category}/{keyword}")
                        return (main_category, keyword)

                # 4. 키워드가 의미있는 경우 독립 카테고리로 처리
                if self._is_meaningful_keyword(topic):
                    logger.info(f"독립 키워드 카테고리 생성: {topic}")
                    return topic

                logger.warning(f"주제 매칭 실패, 기타로 처리: {topic}")
                return "기타"

        except Exception as e:
            logger.error(f"Error parsing main topic: {str(e)}")
            return "기타"

    def _is_meaningful_keyword(self, keyword: str) -> bool:
        """
        키워드가 의미있는 독립 카테고리가 될 수 있는지 확인
        """
        # 의미있는 키워드 판단 기준:
        # 1. 최소 길이 확인
        if len(keyword) < 2:
            return False
            
        # 2. 불용어 체크
        stop_words = ["및", "또는", "그리고", "하는", "있는", "등"]
        if keyword in stop_words:
            return False
            
        # 3. 특수문자나 숫자로만 구성된 경우 제외
        if re.match(r'^[\W\d]+$', keyword):
            return False
            
        return True

    def _parse_sub_topics(self, text: str) -> Dict[str, List[str]]:
        """세부 주제 파싱"""
        sub_topics = {
            "activity_type": [],
            "temporal": [],
            "spatial": [],
            "companions": [],
            "purpose": []
        }

        try:
            current_category = None
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # 카테고리 확인
                if "활동 유형:" in line:
                    current_category = "activity_type"
                elif "시간적 요소:" in line:
                    current_category = "temporal"
                elif "공간적 요소:" in line:
                    current_category = "spatial"
                elif "동반자:" in line:
                    current_category = "companions"
                elif "목적/의도:" in line:
                    current_category = "purpose"
                elif current_category and line.startswith('-'):
                    item = line.replace('-', '').strip()
                    if item:
                        if current_category == "temporal":
                            item = self._normalize_date(item)
                        sub_topics[current_category].append(item)

            return sub_topics

        except Exception as e:
            logger.error(f"Error parsing sub topics: {str(e)}")
            return sub_topics

    def _parse_keywords(self, text: str) -> List[str]:
        """키워드 파싱"""
        try:
            keywords = []
            # 대괄호 안의 내용 추출
            match = re.search(r'\[(.*?)\]', text)
            if match:
                keywords = [
                    k.strip() 
                    for k in match.group(1).split(',') 
                    if k.strip()
                ]
            return keywords

        except Exception as e:
            logger.error(f"Error parsing keywords: {str(e)}")
            return []

    def _parse_sentiment(self, sentiment_text: str, score_text: str) -> Dict:
        """감정 분석 결과 파싱"""
        try:
            # 감정 타입 결정
            sentiment_type = "중립적"
            if "긍정적" in sentiment_text:
                sentiment_type = "긍정적"
            elif "부정적" in sentiment_text:
                sentiment_type = "부정적"

            # 점수 추출
            score_match = re.search(r'(\d+)', score_text)
            score = int(score_match.group(1)) if score_match else 50

            return {
                "type": sentiment_type,
                "score": score
            }

        except Exception as e:
            logger.error(f"Error parsing sentiment: {str(e)}")
            return {"type": "중립적", "score": 50}

    def _parse_reliability_score(self, text: str) -> int:
        """신뢰도 점수 파싱"""
        try:
            score_match = re.search(r'(\d+)', text)
            if score_match:
                score = int(score_match.group(1))
                return max(0, min(100, score))  # 0-100 범위로 제한
            return 0

        except Exception as e:
            logger.error(f"Error parsing reliability score: {str(e)}")
            return 0

    def _parse_intent(self, text: str) -> str:
        """의도 분석 결과 파싱"""
        try:
            # 대괄호 안의 내용 추출
            match = re.search(r'\[(.*?)\]', text)
            return match.group(1).strip() if match else "unknown"

        except Exception as e:
            logger.error(f"Error parsing intent: {str(e)}")
            return "unknown"

    def _normalize_date(self, date_text: str) -> str:
        """날짜 형식 정규화"""
        try:
            current_date = datetime.now()
            
            # 상대적 날짜 표현 처리
            if "이번 주" in date_text:
                return current_date.strftime("%Y-%m-%d")
            elif "다음 주" in date_text:
                return (current_date + timedelta(days=7)).strftime("%Y-%m-%d")
            elif "내일" in date_text:
                return (current_date + timedelta(days=1)).strftime("%Y-%m-%d")
            elif "모레" in date_text:
                return (current_date + timedelta(days=2)).strftime("%Y-%m-%d")
            
            # YYYY-MM-DD 형식 확인
            if re.match(r'\d{4}-\d{2}-\d{2}', date_text):
                return date_text
            
            return current_date.strftime("%Y-%m-%d")
            
        except Exception as e:
            logger.error(f"Error normalizing date: {str(e)}")
            return datetime.now().strftime("%Y-%m-%d")

    def _generate_default_analysis(self) -> Dict:
        """기본 분석 결과 생성"""
        return {
            "main_topic": "기타",
            "sub_topics": {
                "activity_type": [],
                "temporal": [],
                "spatial": [],
                "companions": [],
                "purpose": []
            },
            "keywords": [],
            "sentiment": {
                "type": "unknown",
                "score": 0
            },
            "reliability_score": 0,
            "intent": "unknown"
        }

    def _infer_main_topic(self, data: Dict) -> str:
        """메인 토픽 추론"""
        keywords = data.get("keywords", [])
        topic_keywords = {
            "일상생활": ["식사", "수면", "휴식", "집안일", "일상", "생활"],
            "여가활동": ["취미", "운동", "여행", "문화생활", "레저", "놀이"],
            "업무/학업": ["회의", "공부", "프로젝트", "일", "학교", "과제"],
            "건강/복지": ["병원", "운동", "치료", "건강", "복지", "의료"],
            "관계": ["가족", "친구", "연인", "동료", "대화", "만남"],
            "경제활동": ["쇼핑", "구매", "투자", "재테크", "소비"],
            "기술/IT": ["컴퓨터", "스마트폰", "인터넷", "앱", "기기"],
            "시사/정보": ["뉴스", "정보", "시사", "사회", "이슈"],
            "사회활동": ["모임", "봉사", "단체", "활동", "참여"]
        }
        
        # 키워드 매칭 점수 계산
        topic_scores = {topic: 0 for topic in topic_keywords}
        for keyword in keywords:
            for topic, kw_list in topic_keywords.items():
                if any(kw in keyword for kw in kw_list):
                    topic_scores[topic] += 1
                    
        # 최고 점수 토픽 반환
        if topic_scores:
            max_score = max(topic_scores.values())
            if max_score > 0:
                return max(topic_scores.items(), key=lambda x: x[1])[0]
                
        return "기타"  # 기본값

    def _calculate_reliability_score(self, data: Dict) -> int:
        """신뢰도 점수 계산"""
        score = 0
        
        # 구체성 점수
        if data["sub_topics"]["temporal"]: score += 20
        if data["sub_topics"]["spatial"]: score += 20
        if data["sub_topics"]["companions"]: score += 20
        
        # 명확성 점수
        if data["sub_topics"]["purpose"]: score += 20
        if data["keywords"]: score += 20
        
        return score

def test_parse_temporal():
    parser = TextParser()
    text = "주말 (2024-11-18)"
    result = parser._parse_sub_topics(text)
    print(f"Temporal parsing result: {result['temporal']}")  # 디버깅용 출력
    assert "주말" in result["temporal"], "주말이 temporal 리스트에 없습니다"
    assert "2024-11-18" in result["temporal"], "날짜가 temporal 리스트에 없습니다"

def test_parse_companions():
    parser = TextParser()
    text = "혼자"
    result = parser._parse_sub_topics(text)
    print(f"Companions parsing result: {result['companions']}")  # 디버깅용 출력
    assert len(result["companions"]) == 1, "companions 리스트의 길이가 1이 아닙니다"
    assert "혼자" in result["companions"], "'혼자'가 companions 리스트에 없습니다"

def test_extract_keywords():
    parser = TextParser()
    text = "2024-11-18 속초 여행"
    result = parser._extract_keywords(text)
    print(f"Keywords extraction result: {result}")  # 디버깅용 출력
    assert "2024-11-18" in result, "날짜가 키워드에 없습니다"
    assert "속초" in result, "'속초'가 키워드에 없습니다"
    assert "여행" in result, "'여행'이 키워드에 없습니다"

if __name__ == "__main__":
    try:
        print("\n=== 시간 정보 파싱 테스트 ===")
        test_parse_temporal()
        print("✓ 시간 정보 파싱 테스트 성공")
        
        print("\n=== 동반자 정보 파싱 테스트 ===")
        test_parse_companions()
        print("✓ 동반자 정보 파싱 테스트 성공")
        
        print("\n=== 키워드 추출 테스트 ===")
        test_extract_keywords()
        print("✓ 키워드 추출 테스트 성공")
        
        print("\n모든 테스트가 성공적으로 완료되었습니다!")
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {str(e)}")