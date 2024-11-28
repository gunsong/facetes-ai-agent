from datetime import datetime
from typing import Dict, List

from utils.logger import get_logger

logger = get_logger(__name__)

class ContextPrioritizer:
    """컨텍스트 우선순위 관리 클래스"""

    def __init__(self):
        self.time_weights = {
            'recent': 0.6,    # 최근 1시간 이내
            'today': 0.3,     # 오늘 내
            'older': 0.1      # 이전
        }
        self.type_weights = {
            'location': 0.4,  # 위치 정보
            'temporal': 0.3,  # 시간 정보
            'topic': 0.2,     # 주제 연관성
            'intent': 0.1     # 의도 연관성
        }

    def prioritize_contexts(self, current: Dict, history: List[Dict]) -> List[Dict]:
        """컨텍스트 우선순위화"""
        try:
            scored_contexts = []
            current_time = datetime.now()

            for context in history:
                score = self._calculate_context_score(current, context, current_time)
                scored_contexts.append({
                    'context': context,
                    'score': score
                })

            # 점수 기준 정렬
            return sorted(scored_contexts, key=lambda x: x['score'], reverse=True)

        except Exception as e:
            logger.error(f"Error prioritizing contexts: {str(e)}")
            return []

    def _calculate_context_score(self, current: Dict, context: Dict, current_time: datetime) -> float:
        """컨텍스트 점수 계산"""
        try:
            # 시간 가중치
            time_weight = self._calculate_time_weight(context, current_time)

            # 유형별 가중치
            type_weights = {
                'location': self._calculate_location_weight(current, context),
                'temporal': self._calculate_temporal_weight(current, context),
                'topic': self._calculate_topic_weight(current, context),
                'intent': self._calculate_intent_weight(current, context)
            }

            # 최종 점수 계산
            final_score = time_weight * sum(
                weight * self.type_weights[key] 
                for key, weight in type_weights.items()
            )

            return min(1.0, final_score)

        except Exception as e:
            logger.error(f"Error calculating context score: {str(e)}")
            return 0.0

    def _calculate_time_weight(self, context: Dict, current_time: datetime) -> float:
        """시간 가중치 계산"""
        try:
            context_time = datetime.strptime(
                context['timestamp'], 
                "%Y-%m-%d %H:%M:%S"
            )
            time_diff = current_time - context_time

            if time_diff.total_seconds() <= 3600:  # 1시간 이내
                return self.time_weights['recent']
            elif time_diff.days == 0:  # 오늘 내
                return self.time_weights['today']
            else:
                return self.time_weights['older']

        except Exception as e:
            logger.error(f"Error calculating time weight: {str(e)}")
            return 0.0

    def _calculate_location_weight(self, current: Dict, context: Dict) -> float:
        """위치 관련성 가중치 계산"""
        try:
            current_locations = self._extract_locations(current)
            context_locations = self._extract_locations(context)

            if not current_locations or not context_locations:
                return 0.0

            common_locations = set(current_locations) & set(context_locations)
            return len(common_locations) / max(len(current_locations), len(context_locations))

        except Exception as e:
            logger.error(f"Error calculating location weight: {str(e)}")
            return 0.0

    def _calculate_temporal_weight(self, current: Dict, context: Dict) -> float:
        """시간 관련성 가중치 계산"""
        try:
            current_temporal = current.get('analysis', {}).get('sub_topics', {}).get('temporal', [])
            context_temporal = context.get('analysis', {}).get('sub_topics', {}).get('temporal', [])

            if not current_temporal or not context_temporal:
                return 0.0

            common_temporal = set(current_temporal) & set(context_temporal)
            return len(common_temporal) / max(len(current_temporal), len(context_temporal))

        except Exception as e:
            logger.error(f"Error calculating temporal weight: {str(e)}")
            return 0.0

    def _extract_locations(self, context: Dict) -> List[str]:
        """위치 정보 추출"""
        try:
            return context.get('analysis', {}).get('sub_topics', {}).get('spatial', [])
        except Exception as e:
            logger.error(f"Error extracting locations: {str(e)}")
            return []

    def _calculate_topic_weight(self, current: Dict, context: Dict) -> float:
        """주제 관련성 가중치 계산"""
        try:
            current_topic = current.get('analysis', {}).get('main_topic')
            context_topic = context.get('analysis', {}).get('main_topic')

            if not current_topic or not context_topic:
                return 0.0

            return 1.0 if current_topic == context_topic else 0.0

        except Exception as e:
            logger.error(f"Error calculating topic weight: {str(e)}")
            return 0.0

    def _calculate_intent_weight(self, current: Dict, context: Dict) -> float:
        """의도 관련성 가중치 계산"""
        try:
            current_intent = current.get('analysis', {}).get('intent')
            context_intent = context.get('analysis', {}).get('intent')

            if not current_intent or not context_intent:
                return 0.0

            return 1.0 if current_intent == context_intent else 0.0

        except Exception as e:
            logger.error(f"Error calculating intent weight: {str(e)}")
            return 0.0