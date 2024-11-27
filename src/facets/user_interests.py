from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)

class UserInterests:
    def __init__(self):
        """사용자 관심사 초기화"""
        self.topics = {}          # 관심 주제 분포
        self.main_interests = {}  # 주요 관심사
        self.sub_interests = {    # 세부 관심사
            "activities": {},     # 활동 유형
            "temporal": {},       # 시간 관련
            "spatial": {},        # 공간 관련
            "companions": {}      # 동반자 관련
        }
        self.keywords = {}        # 자주 사용하는 키워드
        self.entities = {}        # 언급된 고유 명사
        self.preferences = {
            "topics": {},         # 주제별 선호도
            "activities": {},     # 활동 선호도
            "locations": {},      # 장소 선호도
            "food": {},           # 음식 선호도
            "accommodation": {},  # 숙박 선호도
            "transportation": {}, # 교통수단 선호도
            "entertainment": {},  # 엔터테인먼트 선호도
            "shopping": {}       # 쇼핑 선호도
        }
        self.last_update = None   # 마지막 업데이트 시간

    def update_interests(self, analysis: Dict) -> None:
        """관심사 및 선호도 업데이트"""
        try:
            self.last_update = datetime.now()

            # 주제 업데이트
            if "main_topic" in analysis:
                self._update_topic(analysis["main_topic"])

            # 키워드 업데이트
            if "keywords" in analysis:
                self._update_keywords(analysis["keywords"])

            # 선호도 업데이트
            if "sub_topics" in analysis:
                self._update_preferences(analysis["sub_topics"])

            # 감정 기반 선호도 가중치 적용
            if "sentiment" in analysis:
                self._apply_sentiment_weight(analysis)

        except Exception as e:
            logger.error(f"Error updating interests: {str(e)}")

    def _update_topic(self, topic: str) -> None:
        """주제 업데이트"""
        try:
            self.topics[topic] = self.topics.get(topic, 0) + 1
            # 주제별 선호도에도 반영
            self.preferences["topics"][topic] = \
                self.preferences["topics"].get(topic, 0) + 1
        except Exception as e:
            logger.error(f"Error updating topic: {str(e)}")

    def _update_keywords(self, keywords: List[str]) -> None:
        """키워드 업데이트"""
        try:
            for keyword in keywords:
                if keyword:  # 빈 문자열 제외
                    self.keywords[keyword] = self.keywords.get(keyword, 0) + 1
        except Exception as e:
            logger.error(f"Error updating keywords: {str(e)}")

    def _update_preferences(self, sub_topics: Dict) -> None:
        """선호도 업데이트"""
        try:
            # 활동 선호도
            if "activity_type" in sub_topics:
                for activity in sub_topics["activity_type"]:
                    self.preferences["activities"][activity] = \
                        self.preferences["activities"].get(activity, 0) + 1

            # 장소 선호도
            if "spatial" in sub_topics:
                for location in sub_topics["spatial"]:
                    self.preferences["locations"][location] = \
                        self.preferences["locations"].get(location, 0) + 1

            # 기타 선호도 업데이트
            self._update_additional_preferences(sub_topics)

        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")

    def _update_additional_preferences(self, sub_topics: Dict) -> None:
        """추가 선호도 업데이트"""
        try:
            # 음식 선호도
            if "food" in sub_topics:
                for food in sub_topics["food"]:
                    self.preferences["food"][food] = \
                        self.preferences["food"].get(food, 0) + 1

            # 숙박 선호도
            if "accommodation" in sub_topics:
                for acc in sub_topics["accommodation"]:
                    self.preferences["accommodation"][acc] = \
                        self.preferences["accommodation"].get(acc, 0) + 1

            # 교통수단 선호도
            if "transportation" in sub_topics:
                for trans in sub_topics["transportation"]:
                    self.preferences["transportation"][trans] = \
                        self.preferences["transportation"].get(trans, 0) + 1

            # 엔터테인먼트 선호도
            if "entertainment" in sub_topics:
                for ent in sub_topics["entertainment"]:
                    self.preferences["entertainment"][ent] = \
                        self.preferences["entertainment"].get(ent, 0) + 1

            # 쇼핑 선호도
            if "shopping" in sub_topics:
                for shop in sub_topics["shopping"]:
                    self.preferences["shopping"][shop] = \
                        self.preferences["shopping"].get(shop, 0) + 1

        except Exception as e:
            logger.error(f"Error updating additional preferences: {str(e)}")

    def _apply_sentiment_weight(self, analysis: Dict) -> None:
        """감정 점수 기반 가중치 적용"""
        try:
            sentiment = analysis.get("sentiment", {})
            if isinstance(sentiment, dict) and "score" in sentiment:
                score = float(sentiment["score"])
                weight = self._calculate_sentiment_weight(score)
                # 최근 업데이트된 항목들에 가중치 적용
                self._apply_weight_to_recent_updates(weight)
        except Exception as e:
            logger.error(f"Error applying sentiment weight: {str(e)}")

    def _calculate_sentiment_weight(self, score: float) -> float:
        """감정 점수를 가중치로 변환"""
        try:
            # 감정 점수(0-100)를 0.5-1.5 범위의 가중치로 변환
            normalized_score = max(0, min(100, score)) / 100
            return 0.5 + normalized_score
        except Exception as e:
            logger.error(f"Error calculating sentiment weight: {str(e)}")
            return 1.0

    def _apply_weight_to_recent_updates(self, weight: float) -> None:
        """최근 업데이트된 항목들에 가중치 적용"""
        try:
            # 마지막으로 업데이트된 항목들의 값을 가중치만큼 조정
            if self.last_update:
                for category, prefs in self.preferences.items():
                    for key in prefs:
                        prefs[key] = int(prefs[key] * weight)
        except Exception as e:
            logger.error(f"Error applying weight to recent updates: {str(e)}")

    def get_top_interests(self, category: str, limit: int = 5) -> List[tuple]:
        """
        특정 카테고리의 상위 관심사 반환
        
        Args:
            category: 관심사 카테고리 (topics, keywords, 등)
            limit: 반환할 항목 수
            
        Returns:
            상위 관심사 목록 (항목, 점수)
        """
        try:
            if category == "topics":
                data = self.topics
            elif category == "keywords":
                data = self.keywords
            elif category in self.preferences:
                data = self.preferences[category]
            else:
                return []

            sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
            return sorted_items[:limit]
        except Exception as e:
            logger.error(f"Error getting top interests: {str(e)}")
            return []

    def get_all_interests(self) -> Dict:
        """모든 관심사 데이터 반환"""
        return {
            "topics": self.topics,
            "keywords": self.keywords,
            "entities": self.entities,
            "preferences": self.preferences,
            "last_update": self.last_update.isoformat() if self.last_update else None
        }

    def get_interest_score(self, item: str, category: str = "topics") -> float:
        """특정 항목의 관심도 점수 반환"""
        try:
            if category == "topics":
                data = self.topics
            elif category == "keywords":
                data = self.keywords
            elif category in self.preferences:
                data = self.preferences[category]
            else:
                return 0.0

            max_score = max(data.values()) if data else 1
            return data.get(item, 0) / max_score
        except Exception as e:
            logger.error(f"Error calculating interest score: {str(e)}")
            return 0.0

    def add_entity(self, entity: str) -> None:
        """고유 명사 추가"""
        self.entities[entity] = self.entities.get(entity, 0) + 1

    def update_topic_preference(self, topic: str, score: float) -> None:
        """주제별 선호도 업데이트"""
        current_score = self.preferences["topics"].get(topic, 0)
        self.preferences["topics"][topic] = (current_score + score) / 2

    def clear_old_interests(self, days: int = 30) -> None:
        """
        오래된 관심사 데이터 정리
        Args:
            days: 보관할 기간 (일)
        """
        try:
            if not self.last_update:
                return
                
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # 오래된 데이터 제거를 위한 임계값 설정
            threshold = 0.3  # 30% 미만인 항목 제거
            
            # 각 카테고리별 데이터 정리
            for category in self.preferences:
                if self.preferences[category]:
                    max_value = max(self.preferences[category].values())
                    threshold_value = max_value * threshold
                    
                    # 임계값 미만인 항목 제거
                    self.preferences[category] = {
                        k: v for k, v in self.preferences[category].items()
                        if v >= threshold_value
                    }
            
            # main_interests 정리
            if self.main_interests:
                max_value = max(self.main_interests.values())
                threshold_value = max_value * threshold
                self.main_interests = {
                    k: v for k, v in self.main_interests.items()
                    if v >= threshold_value
                }
            
            # sub_interests 정리
            for category in self.sub_interests:
                if self.sub_interests[category]:
                    max_value = max(self.sub_interests[category].values())
                    threshold_value = max_value * threshold
                    self.sub_interests[category] = {
                        k: v for k, v in self.sub_interests[category].items()
                        if v >= threshold_value
                    }
            
            logger.info(f"관심사 데이터 정리 완료 (기준일: {cutoff_date.isoformat()})")
            
        except Exception as e:
            logger.error(f"Error clearing old interests: {str(e)}")

    def add_main_interest(self, interest: str) -> None:
        """
        주요 관심사 추가
        Args:
            interest: 관심사 항목
        """
        try:
            # main_interests 업데이트
            self.main_interests[interest] = self.main_interests.get(interest, 0) + 1
            
            # topics에도 반영 (UserProfile에서 참조)
            self.topics[interest] = self.topics.get(interest, 0) + 1
            
            # preferences의 topics에도 반영
            self.preferences["topics"][interest] = \
                self.preferences["topics"].get(interest, 0) + 1
                
            self.last_update = datetime.now()
            logger.debug(f"주요 관심사 추가: {interest}")
            
        except Exception as e:
            logger.error(f"Error adding main interest: {str(e)}")

    def add_sub_interest(self, category: str, interest: str) -> None:
        """
        세부 관심사 추가
        Args:
            category: 관심사 카테고리
            interest: 관심사 항목
        """
        try:
            # sub_interests 업데이트
            if category in self.sub_interests:
                self.sub_interests[category][interest] = \
                    self.sub_interests[category].get(interest, 0) + 1
            
            # preferences 업데이트
            if category in self.preferences:
                self.preferences[category][interest] = \
                    self.preferences[category].get(interest, 0) + 1
                    
            self.last_update = datetime.now()
            logger.debug(f"세부 관심사 추가: {category} - {interest}")
            
        except Exception as e:
            logger.error(f"Error adding sub interest: {str(e)}")

    def get_interests_summary(self) -> Dict:
        """관심사 요약 정보 반환"""
        return {
            "main_interests": self._get_top_items(self.main_interests, 5),
            "sub_interests": {
                category: self._get_top_items(interests, 3)
                for category, interests in self.sub_interests.items()
            },
            "keywords": self._get_top_items(self.keywords, 10),
            "last_update": self.last_update.isoformat() if self.last_update else None
        }

    def _get_top_items(self, items: Dict, limit: int) -> List[Dict]:
        """상위 항목 추출"""
        sorted_items = sorted(
            items.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [
            {"item": item, "count": count}
            for item, count in sorted_items[:limit]
        ]
