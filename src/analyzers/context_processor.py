from datetime import datetime
from typing import Dict, List
from collections import Counter
from utils.logger import get_logger

logger = get_logger(__name__)

class ContextProcessor:
    """컨텍스트 처리 클래스"""
    
    def __init__(self):
        self.context_weights = {
            'location': 0.4,
            'temporal': 0.3,
            'topic': 0.2,
            'intent': 0.1
        }
        self.time_window = {
            'recent': 3,  # 최근 3개 대화
            'relevant': 5  # 관련성 있는 최대 5개 대화
        }
        
    def process_context(self, current_query: str, history: List[Dict]) -> Dict:
        """컨텍스트 처리 및 분석"""
        try:
            context = {
                'location': self._extract_location_context(history),
                'temporal': self._extract_temporal_context(history),
                'topic': self._extract_topic_context(history),
                'intent': self._extract_intent_context(history),
                'history': history[-self.time_window['recent']:],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            weighted_context = self._apply_context_weights(context)
            logger.info(f"Processed context for query: {current_query}")
            
            return weighted_context
            
        except Exception as e:
            logger.error(f"Error processing context: {str(e)}")
            return {}

    def _extract_location_context(self, history: List[Dict]) -> Dict:
        """위치 컨텍스트 추출"""
        try:
            locations = []
            for conv in reversed(history[-self.time_window['recent']:]):
                if 'analysis' in conv:
                    spatial_info = conv['analysis'].get('sub_topics', {}).get('spatial', [])
                    locations.extend(spatial_info)
            
            return {
                'recent_locations': locations,
                'frequency': self._calculate_location_frequency(locations)
            }
        except Exception as e:
            logger.error(f"Error extracting location context: {str(e)}")
            return {}

    def _calculate_location_frequency(self, locations: List[str]) -> Dict[str, int]:
        """위치 빈도 계산"""
        try:
            return dict(Counter(locations))
        except Exception as e:
            logger.error(f"Error calculating location frequency: {str(e)}")
            return {}

    def _extract_temporal_context(self, history: List[Dict]) -> Dict:
        """시간 컨텍스트 추출"""
        try:
            temporal_info = []
            for conv in reversed(history[-self.time_window['recent']:]):
                if 'analysis' in conv:
                    time_info = conv['analysis'].get('sub_topics', {}).get('temporal', [])
                    temporal_info.extend(time_info)
            
            return {
                'recent_temporal': temporal_info,
                'patterns': self._analyze_temporal_patterns(temporal_info)
            }
        except Exception as e:
            logger.error(f"Error extracting temporal context: {str(e)}")
            return {}

    def _analyze_temporal_patterns(self, temporal_info: List[str]) -> Dict:
        """시간 패턴 분석"""
        try:
            patterns = {
                'time_of_day': {},
                'day_of_week': {},
                'period': {}
            }
            
            for info in temporal_info:
                # 시간대 분석
                if any(time in info for time in ['아침', '오전', '오후', '저녁', '밤']):
                    patterns['time_of_day'][info] = patterns['time_of_day'].get(info, 0) + 1
                
                # 요일 분석
                if any(day in info for day in ['평일', '주말', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']):
                    patterns['day_of_week'][info] = patterns['day_of_week'].get(info, 0) + 1
                
                # 기간 분석
                if any(period in info for period in ['단기', '중기', '장기']):
                    patterns['period'][info] = patterns['period'].get(info, 0) + 1
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing temporal patterns: {str(e)}")
            return {}

    def _extract_topic_context(self, history: List[Dict]) -> Dict:
        """주제 컨텍스트 추출"""
        try:
            topics = []
            for conv in reversed(history[-self.time_window['recent']:]):
                if 'analysis' in conv:
                    topic = conv['analysis'].get('main_topic')
                    if topic:
                        topics.append(topic)
            
            return {
                'recent_topics': topics,
                'frequency': self._calculate_topic_frequency(topics)
            }
        except Exception as e:
            logger.error(f"Error extracting topic context: {str(e)}")
            return {}

    def _calculate_topic_frequency(self, topics: List[str]) -> Dict[str, int]:
        """주제 빈도 계산"""
        try:
            return dict(Counter(topics))
        except Exception as e:
            logger.error(f"Error calculating topic frequency: {str(e)}")
            return {}

    def _extract_intent_context(self, history: List[Dict]) -> Dict:
        """의도 컨텍스트 추출"""
        try:
            intents = []
            for conv in reversed(history[-self.time_window['recent']:]):
                if 'analysis' in conv:
                    intent = conv['analysis'].get('intent')
                    if intent:
                        intents.append(intent)
            
            return {
                'recent_intents': intents,
                'patterns': self._analyze_intent_patterns(intents)
            }
        except Exception as e:
            logger.error(f"Error extracting intent context: {str(e)}")
            return {}

    def _analyze_intent_patterns(self, intents: List[str]) -> Dict:
        """의도 패턴 분석"""
        try:
            patterns = {
                'frequency': dict(Counter(intents)),
                'sequence': self._analyze_intent_sequence(intents)
            }
            return patterns
        except Exception as e:
            logger.error(f"Error analyzing intent patterns: {str(e)}")
            return {}

    def _analyze_intent_sequence(self, intents: List[str]) -> Dict[str, int]:
        """의도 시퀀스 분석"""
        try:
            sequences = {}
            if len(intents) >= 2:
                for i in range(len(intents) - 1):
                    sequence = f"{intents[i]}->{intents[i+1]}"
                    sequences[sequence] = sequences.get(sequence, 0) + 1
            return sequences
        except Exception as e:
            logger.error(f"Error analyzing intent sequence: {str(e)}")
            return {}

    def _apply_context_weights(self, context: Dict) -> Dict:
        """컨텍스트 가중치 적용"""
        try:
            weighted_context = {}
            for key, weight in self.context_weights.items():
                if key in context:
                    weighted_context[key] = {
                        'data': context[key],
                        'weight': weight,
                        'confidence': self._calculate_confidence(context[key])
                    }
            return weighted_context
        except Exception as e:
            logger.error(f"Error applying context weights: {str(e)}")
            return {}

    def _calculate_confidence(self, context_data: Dict) -> float:
        """컨텍스트 신뢰도 계산"""
        try:
            if not context_data:
                return 0.0
            
            # 기본 신뢰도 점수
            base_confidence = 0.7
            
            # 데이터 완성도에 따른 보정
            completeness = len(context_data) / 4  # 예상되는 최대 키 수로 나눔
            
            # 최신성에 따른 보정
            recency_factor = 0.9  # 최신 데이터 가중치
            
            return min(1.0, base_confidence * completeness * recency_factor)
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.0