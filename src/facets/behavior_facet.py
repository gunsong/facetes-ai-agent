from datetime import datetime
from typing import Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)

class BehaviorPatterns:
    def __init__(self):
        """행동 패턴 클래스 초기화"""
        self.temporal = {
            "daily": {},      # 하루 중 선호 시간
            "weekly": {},     # 주간 선호 패턴
            "monthly": {},    # 월간 패턴
            "seasonal": {},   # 계절별 선호도
            "periodic": {}    # 주기적 패턴
        }

        self.spatial = {
            "locations": {},    # 선호 장소
            "regions": {},      # 선호 지역
            "venue_types": {},  # 선호 시설 유형
            "types": {}         # 장소 유형
        }

        self.social = {
            "companions": {},     # 동반자 유형
            "group_size": {},     # 선호 그룹 크기
            "social_context": {}, # 사회적 상황
            "contexts": {}        # 상황별 패턴
        }

        self.spending = {
            "amount_range": {},   # 소비 금액대
            "frequency": {},      # 소비 빈도
            "categories": {}      # 소비 카테고리
        }

        self.interaction_style = {
            "query_types": {},    # 질문 유형 분포
            "tone": {},           # 대화 톤 분포
            "detail_level": {}    # 상세도 선호도
        }

        self.last_update = None   # 마지막 업데이트 시간

    def update_patterns(self, analysis: Dict) -> None:
        """모든 행동 패턴 업데이트"""
        try:
            logger.info("행동 패턴 업데이트 시작")
            self.last_update = datetime.now()

            if "sub_topics" in analysis:
                sub_topics = analysis["sub_topics"]

                # 시간 패턴 업데이트
                if "temporal" in sub_topics:
                    self.update_temporal_patterns(sub_topics["temporal"])

                # 공간 패턴 업데이트
                if "spatial" in sub_topics:
                    self.update_spatial_patterns(sub_topics["spatial"])

                # 사회적 패턴 업데이트
                if "companions" in sub_topics:
                    self.update_social_patterns(sub_topics["companions"])

                # 소비 패턴 업데이트
                if "spending" in sub_topics:
                    self.update_spending_patterns(sub_topics["spending"])

            # 상호작용 스타일 업데이트
            self.update_interaction_style(analysis)

            logger.info("행동 패턴 업데이트 완료")

        except Exception as e:
            logger.error(f"Error updating patterns: {str(e)}")

    def update_temporal_patterns(self, temporal_info: List[str]) -> None:
        """시간 관련 패턴 업데이트"""
        try:
            for time_info in temporal_info:
                time_info = str(time_info).lower()

                # 일간 패턴 (아침, 점심, 저녁, 밤)
                if any(keyword in time_info for keyword in ["아침", "점심", "저녁", "밤"]):
                    self.temporal["daily"][time_info] = \
                        self.temporal["daily"].get(time_info, 0) + 1
                    logger.debug(f"일간 패턴 업데이트: {time_info}")

                # 주간 패턴 (평일, 주말)
                elif any(keyword in time_info for keyword in ["평일", "주말"]):
                    self.temporal["weekly"][time_info] = \
                        self.temporal["weekly"].get(time_info, 0) + 1
                    logger.debug(f"주간 패턴 업데이트: {time_info}")

                # 월간 패턴 (월초, 월말, 중순)
                elif any(keyword in time_info for keyword in ["월초", "월말", "중순"]):
                    self.temporal["monthly"][time_info] = \
                        self.temporal["monthly"].get(time_info, 0) + 1
                    logger.debug(f"월간 패턴 업데이트: {time_info}")

                # 계절 패턴
                elif any(season in time_info for season in ["봄", "여름", "가을", "겨울"]):
                    self.temporal["seasonal"][time_info] = \
                        self.temporal["seasonal"].get(time_info, 0) + 1
                    logger.debug(f"계절 패턴 업데이트: {time_info}")

                # 주기적 패턴
                elif any(keyword in time_info for keyword in ["매일", "매주", "매월", "매년"]):
                    self.temporal["periodic"][time_info] = \
                        self.temporal["periodic"].get(time_info, 0) + 1
                    logger.debug(f"주기적 패턴 업데이트: {time_info}")

        except Exception as e:
            logger.error(f"Error updating temporal patterns: {str(e)}")

    def update_spatial_patterns(self, spatial_info: List[str]) -> None:
        """공간 관련 패턴 업데이트"""
        try:
            for location in spatial_info:
                # 선호 장소 업데이트
                self.spatial["locations"][location] = \
                    self.spatial["locations"].get(location, 0) + 1
                logger.debug(f"장소 선호도 업데이트: {location}")

                # 지역 정보 추출 및 업데이트
                if "/" in location:
                    region = location.split("/")[0]
                    self.spatial["regions"][region] = \
                        self.spatial["regions"].get(region, 0) + 1
                    logger.debug(f"지역 선호도 업데이트: {region}")

                # 시설 유형 분류 및 업데이트
                venue_type = self._classify_venue_type(location)
                if venue_type:
                    self.spatial["venue_types"][venue_type] = \
                        self.spatial["venue_types"].get(venue_type, 0) + 1
                    logger.debug(f"시설 유형 업데이트: {venue_type}")

                # 장소 유형 분류 및 업데이트
                location_type = self._classify_location_type(location)
                if location_type:
                    self.spatial["types"][location_type] = \
                        self.spatial["types"].get(location_type, 0) + 1
                    logger.debug(f"장소 유형 업데이트: {location_type}")

        except Exception as e:
            logger.error(f"Error updating spatial patterns: {str(e)}")

    def update_social_patterns(self, companions: List[str]) -> None:
        """사회적 패턴 업데이트"""
        try:
            # 동반자 유형 업데이트
            for companion in companions:
                self.social["companions"][companion] = \
                    self.social["companions"].get(companion, 0) + 1
                logger.debug(f"동반자 유형 업데이트: {companion}")

            # 그룹 크기 업데이트
            group_size = str(len(companions))
            self.social["group_size"][group_size] = \
                self.social["group_size"].get(group_size, 0) + 1
            logger.debug(f"그룹 크기 업데이트: {group_size}")

            # 사회적 상황 분류 및 업데이트
            social_context = self._classify_social_context(companions)
            if social_context:
                self.social["social_context"][social_context] = \
                    self.social["social_context"].get(social_context, 0) + 1
                logger.debug(f"사회적 상황 업데이트: {social_context}")

            # 상황별 패턴 업데이트
            context_key = f"{group_size}_people_{companions[0] if companions else '혼자'}"
            self.social["contexts"][context_key] = \
                self.social["contexts"].get(context_key, 0) + 1
            logger.debug(f"상황별 패턴 업데이트: {context_key}")

        except Exception as e:
            logger.error(f"Error updating social patterns: {str(e)}")

    def update_spending_patterns(self, spending_info: Dict) -> None:
        """소비 패턴 업데이트"""
        try:
            # 금액대 업데이트
            if "amount" in spending_info:
                amount_range = self._classify_amount_range(spending_info["amount"])
                self.spending["amount_range"][amount_range] = \
                    self.spending["amount_range"].get(amount_range, 0) + 1
                logger.debug(f"금액대 패턴 업데이트: {amount_range}")

            # 소비 빈도 업데이트
            if "frequency" in spending_info:
                self.spending["frequency"][spending_info["frequency"]] = \
                    self.spending["frequency"].get(spending_info["frequency"], 0) + 1
                logger.debug(f"소비 빈도 업데이트: {spending_info['frequency']}")

            # 소비 카테고리 업데이트
            if "category" in spending_info:
                self.spending["categories"][spending_info["category"]] = \
                    self.spending["categories"].get(spending_info["category"], 0) + 1
                logger.debug(f"소비 카테고리 업데이트: {spending_info['category']}")

        except Exception as e:
            logger.error(f"Error updating spending patterns: {str(e)}")

    def update_interaction_style(self, analysis: Dict) -> None:
        """상호작용 스타일 업데이트"""
        try:
            # intent가 딕셔너리인 경우 처리
            if "intent" in analysis:
                intent = analysis["intent"]
                if isinstance(intent, dict):
                    query_type = intent.get("유형", "unknown")
                else:
                    query_type = str(intent)

                self.interaction_style["query_types"][query_type] = \
                    self.interaction_style["query_types"].get(query_type, 0) + 1
                logger.debug(f"질문 유형 업데이트: {query_type}")

            # 대화 톤 업데이트
            if "sentiment" in analysis:
                tone = analysis["sentiment"].get("type", "neutral")
                self.interaction_style["tone"][tone] = \
                    self.interaction_style["tone"].get(tone, 0) + 1
                logger.debug(f"대화 톤 업데이트: {tone}")

        except Exception as e:
            logger.error(f"Error updating interaction style: {str(e)}")

    def _classify_venue_type(self, location: str) -> Optional[str]:
        """시설 유형 분류"""
        venue_keywords = {
            "restaurant": ["식당", "레스토랑", "카페"],
            "shopping": ["마트", "백화점", "상점"],
            "entertainment": ["영화관", "공연장", "놀이공원"],
            "education": ["학교", "도서관", "학원"],
            "sports": ["체육관", "운동장", "수영장"],
            "medical": ["병원", "의원", "약국"],
            "office": ["사무실", "회사", "업체"],
            "cultural": ["박물관", "미술관", "문화센터"]
        }

        for venue_type, keywords in venue_keywords.items():
            if any(keyword in location for keyword in keywords):
                return venue_type
        return None

    def _classify_location_type(self, location: str) -> Optional[str]:
        """장소 유형 분류"""
        location_types = {
            "indoor": ["실내", "건물", "홀"],
            "outdoor": ["야외", "공원", "거리"],
            "public": ["공공", "관공서", "도서관"],
            "private": ["개인", "자택", "사무실"],
            "commercial": ["상가", "매장", "시장"],
            "residential": ["주거", "아파트", "빌라"]
        }

        for location_type, keywords in location_types.items():
            if any(keyword in location for keyword in keywords):
                return location_type
        return None

    def _classify_social_context(self, companions: List[str]) -> Optional[str]:
        """사회적 상황 분류"""
        context_keywords = {
            "family": ["가족", "부모", "자녀", "친척"],
            "friends": ["친구", "동창", "지인"],
            "work": ["동료", "상사", "직장", "부하"],
            "date": ["연인", "파트너", "데이트"],
            "group": ["모임", "단체", "팀", "동호회"]
        }

        for context, keywords in context_keywords.items():
            if any(any(keyword in companion.lower() for keyword in keywords) 
                  for companion in companions):
                return context
        return None

    def _classify_amount_range(self, amount: Union[int, float]) -> str:
        """금액대 분류"""
        try:
            amount = float(amount)
            if amount < 10000:
                return "low"
            elif amount < 50000:
                return "medium"
            elif amount < 100000:
                return "high"
            else:
                return "very_high"
        except (ValueError, TypeError):
            return "unknown"

    def _classify_query_type(self, intent: str) -> str:
        """질문 유형 분류"""
        query_types = {
            "information": ["정보", "방법", "언제", "어디", "누구", "어떻게"],
            "confirmation": ["맞나요", "인가요", "될까요", "가능한가요"],
            "preference": ["선호", "좋아", "원해", "바라"],
            "suggestion": ["추천", "제안", "조언", "알려주세요"],
            "opinion": ["생각", "느낌", "의견", "판단"]
        }

        intent = intent.lower()
        for query_type, keywords in query_types.items():
            if any(keyword in intent for keyword in keywords):
                return query_type
        return "other"

    def get_pattern_summary(self) -> Dict:
        """패턴 요약 정보 반환"""
        try:
            return {
                "temporal": self._get_top_patterns(self.temporal),
                "spatial": self._get_top_patterns(self.spatial),
                "social": self._get_top_patterns(self.social),
                "spending": self._get_top_patterns(self.spending),
                "interaction_style": self._get_top_patterns(self.interaction_style),
                "last_update": self.last_update.isoformat() if self.last_update else None
            }
        except Exception as e:
            logger.error(f"Error getting pattern summary: {str(e)}")
            return {}

    def analyze_trends(self) -> Dict:
        """트렌드 분석 결과 반환"""
        try:
            return {
                "temporal": self._analyze_category_trends(self.temporal),
                "spatial": self._analyze_category_trends(self.spatial),
                "social": self._analyze_category_trends(self.social),
                "spending": self._analyze_category_trends(self.spending),
                "interaction": self._analyze_category_trends(self.interaction_style)
            }
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {}

    def _analyze_category_trends(self, category_data: Dict) -> Dict:
        """카테고리별 트렌드 분석"""
        trends = {}
        for category, patterns in category_data.items():
            if patterns:
                sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
                trends[category] = {
                    "top_items": sorted_patterns[:3],
                    "total_occurrences": sum(patterns.values()),
                    "unique_patterns": len(patterns)
                }
        return trends

    def detect_changes(self) -> Dict:
        """주요 변화 감지 결과 반환"""
        try:
            return {
                "temporal": self._detect_category_changes(self.temporal),
                "spatial": self._detect_category_changes(self.spatial),
                "social": self._detect_category_changes(self.social),
                "spending": self._detect_category_changes(self.spending),
                "interaction": self._detect_category_changes(self.interaction_style)
            }
        except Exception as e:
            logger.error(f"Error detecting changes: {str(e)}")
            return {}

    def _detect_category_changes(self, category_data: Dict) -> Dict:
        """카테고리별 변화 감지"""
        changes = {}
        for category, patterns in category_data.items():
            if patterns:
                sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
                changes[category] = {
                    "most_frequent": sorted_patterns[0],
                    "least_frequent": sorted_patterns[-1],
                    "pattern_count": len(patterns)
                }
        return changes