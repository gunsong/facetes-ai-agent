from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)

class ContextMemory:
    def __init__(self):
        """컨텍스트 메모리 초기화"""
        self.short_term = []  # 최근 대화 컨텍스트
        self.long_term = {    # 장기 기억
            "preferences": {}, # 누적된 선호도
            "experiences": {}, # 과거 경험
            "decisions": {},   # 과거 결정들
            "patterns": {}     # 장기 패턴
        }

        self.max_short_term_size = 10    # 단기 메모리 최대 크기
        self.memory_retention_days = 30  # 장기 메모리 보존 기간
        self.last_update = None          # 마지막 업데이트 시간

    def update_context_memory(self, analysis_result: Dict) -> None:
        """컨텍스트 메모리 업데이트"""
        try:
            if not analysis_result:
                logger.warning("Empty analysis result provided - skipping context memory update")
                return

            self.last_update = datetime.now()

            # 단기 메모리 업데이트
            self.update_short_term_memory(analysis_result)

            # 장기 메모리 업데이트
            self.update_long_term_memory(analysis_result)

            # 오래된 메모리 정리
            self.cleanup_old_memories()

            logger.info("컨텍스트 메모리 업데이트 완료")

        except Exception as e:
            logger.error(f"Error updating context memory: {str(e)}")

    def update_short_term_memory(self, analysis_result: Dict) -> None:
        """단기 메모리 업데이트"""
        try:
            # 새로운 컨텍스트 생성
            context_record = {
                "timestamp": datetime.now().isoformat(),
                "content": analysis_result,
                "references": self._extract_references(analysis_result),
                "metadata": {
                    "type": analysis_result.get("main_topic", "unknown"),
                    "importance": self._calculate_importance(analysis_result)
                }
            }
            logger.info(f"context_record: {context_record}")

            # 단기 메모리에 추가
            self.short_term.append(context_record)

            # 최대 크기 초과 시 처리
            if len(self.short_term) > self.max_short_term_size:
                # 중요도 기반 컨텍스트 선택
                context_to_move = self._select_context_for_transfer()

                # 선택된 컨텍스트를 장기 메모리로 이동
                if context_to_move:
                    self._move_to_long_term(context_to_move)
                    self.short_term.remove(context_to_move)
                else:
                    # 중요도가 낮은 가장 오래된 컨텍스트 제거
                    self.short_term.pop(0)

            logger.debug(f"단기 메모리 크기: {len(self.short_term)}")

        except Exception as e:
            logger.error(f"Error updating short term memory: {str(e)}")

    def _move_to_long_term(self, context: Dict) -> None:
        """단기 메모리에서 장기 메모리로 이동"""
        try:
            content = context.get("content", {})

            # 선호도 정보 추출 및 저장
            if "preferences" in content:
                self._update_preferences(content["preferences"])

            # 경험 정보 저장
            self._update_experiences(content)

            # 결정 정보 저장
            if "decisions" in content:
                self._update_decisions(content["decisions"])

            # 패턴 정보 업데이트
            self._update_patterns(content)

        except Exception as e:
            logger.error(f"Error moving context to long term: {str(e)}")

    def _extract_references(self, analysis_result: Dict) -> Dict:
        """
        분석 결과에서 참조 정보 추출

        Args:
            analysis_result: 분석 결과 딕셔너리

        Returns:
            Dict: 카테고리별 참조 정보
        """
        try:
            references = {
                "topics": [],      # 주제 관련 참조
                "keywords": [],    # 키워드 참조
                "temporal": [],    # 시간 관련 참조
                "spatial": [],     # 공간 관련 참조
                "entities": []     # 고유 명사 참조
            }

            # 1. 주제 참조 추출
            if main_topic := analysis_result.get("main_topic"):
                references["topics"].append(main_topic)

            # 2. 키워드 참조 추출
            if keywords := analysis_result.get("keywords", []):
                references["keywords"].extend(keywords)

            # 3. 시공간 참조 추출
            sub_topics = analysis_result.get("sub_topics", {})
            if temporal := sub_topics.get("temporal"):
                references["temporal"].extend(temporal)
            if spatial := sub_topics.get("spatial"):
                references["spatial"].extend(spatial)

            # 4. 엔티티 참조 추출 (있는 경우)
            if entities := analysis_result.get("entities", []):
                references["entities"].extend(entities)

            # 각 카테고리 내 중복 제거
            for category in references:
                references[category] = list(set(references[category]))

            logger.debug(f"참조 정보 추출 완료: {references}")
            return references

        except Exception as e:
            logger.error(f"Error extracting references: {str(e)}")
            return {
                "topics": [],
                "keywords": [],
                "temporal": [],
                "spatial": [],
                "entities": []
            }

    def _calculate_importance(self, analysis: Dict) -> float:
        """컨텍스트 중요도 계산"""
        try:
            score = 0.0

            # 신뢰도 점수 반영
            reliability = analysis.get("reliability_score", 0)
            score += reliability * 0.3

            # 감정 강도 반영
            sentiment = analysis.get("sentiment", {})
            intensity = sentiment.get("intensity", 50)
            score += intensity * 0.2

            # 키워드 수 반영
            keywords = analysis.get("keywords", [])
            score += len(keywords) * 5

            # 상세 정보 존재 여부 반영
            if analysis.get("sub_topics"):
                score += 20

            return min(score, 100)  # 최대 100점

        except Exception as e:
            logger.error(f"Error calculating importance: {str(e)}")
            return 0.0

    def _select_context_for_transfer(self) -> Optional[Dict]:
        """장기 메모리로 이동할 컨텍스트 선택"""
        try:
            # 중요도와 시간을 고려한 점수 계산
            scored_contexts = []
            current_time = datetime.now()

            for context in self.short_term:
                time_diff = (current_time - datetime.fromisoformat(context["timestamp"])).total_seconds()
                importance = context["metadata"]["importance"]

                # 시간이 오래될수록, 중요도가 높을수록 이동 대상이 됨
                transfer_score = (time_diff / 3600) * 0.6 + importance * 0.4
                scored_contexts.append((context, transfer_score))

            # 이동 대상 선정
            if scored_contexts:
                return max(scored_contexts, key=lambda x: x[1])[0]

            return None

        except Exception as e:
            logger.error(f"Error selecting context for transfer: {str(e)}")
            return None

    def update_long_term_memory(self, analysis_result: Dict) -> None:
        """장기 메모리 업데이트"""
        try:
            # 선호도 업데이트
            self._update_preferences(analysis_result)

            # 경험 업데이트
            self._update_experiences(analysis_result)

            # 결정 업데이트
            self._update_decisions(analysis_result)

            # 패턴 업데이트
            self._update_patterns(analysis_result)

            logger.debug("장기 메모리 업데이트 완료")

        except Exception as e:
            logger.error(f"Error updating long term memory: {str(e)}")

    def _update_preferences(self, analysis_result: Dict) -> None:
        """선호도 정보 업데이트"""
        try:
            if "preferences" in analysis_result:
                for category, preference in analysis_result["preferences"].items():
                    if category not in self.long_term["preferences"]:
                        self.long_term["preferences"][category] = {}

                    for item, score in preference.items():
                        current_score = self.long_term["preferences"][category].get(item, 0)
                        self.long_term["preferences"][category][item] = current_score + score

                    logger.debug(f"선호도 업데이트 완료: {category}")

        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")

    def _update_experiences(self, analysis_result: Dict) -> None:
        """경험 정보 업데이트"""
        try:
            experience_record = {
                "timestamp": datetime.now().isoformat(),
                "type": analysis_result.get("main_topic", "unknown"),
                "details": analysis_result.get("sub_topics", {}),
                "sentiment": analysis_result.get("sentiment", {}),
                "reliability": analysis_result.get("reliability_score", 0)
            }

            category = experience_record["type"]
            if category not in self.long_term["experiences"]:
                self.long_term["experiences"][category] = []

            self.long_term["experiences"][category].append(experience_record)
            logger.debug(f"경험 정보 업데이트 완료: {category}")

        except Exception as e:
            logger.error(f"Error updating experiences: {str(e)}")

    def _update_decisions(self, analysis_result: Dict) -> None:
        """결정 정보 업데이트"""
        try:
            if "decisions" in analysis_result:
                for decision in analysis_result["decisions"]:
                    category = decision.get("category", "unknown")
                    if category not in self.long_term["decisions"]:
                        self.long_term["decisions"][category] = []

                    decision_record = {
                        "timestamp": datetime.now().isoformat(),
                        "context": decision.get("context", ""),
                        "choice": decision.get("choice", ""),
                        "reasoning": decision.get("reasoning", ""),
                        "outcome": decision.get("outcome", "")
                    }

                    self.long_term["decisions"][category].append(decision_record)
                    logger.debug(f"결정 정보 업데이트 완료: {category}")

        except Exception as e:
            logger.error(f"Error updating decisions: {str(e)}")

    def _update_patterns(self, analysis_result: Dict) -> None:
        """패턴 정보 업데이트"""
        try:
            if "patterns" in analysis_result:
                for pattern_type, pattern_data in analysis_result["patterns"].items():
                    if pattern_type not in self.long_term["patterns"]:
                        self.long_term["patterns"][pattern_type] = {}

                    for pattern, count in pattern_data.items():
                        current_count = self.long_term["patterns"][pattern_type].get(pattern, 0)
                        self.long_term["patterns"][pattern_type][pattern] = current_count + count

                    logger.debug(f"패턴 업데이트 완료: {pattern_type}")

        except Exception as e:
            logger.error(f"Error updating patterns: {str(e)}")

    def get_relevant_context(self, current_analysis: Dict) -> Optional[Dict]:
        """
        현재 분석과 관련된 컨텍스트 검색

        Args:
            current_analysis: 현재 분석 결과

        Returns:
            Optional[Dict]: 관련된 컨텍스트 또는 None
        """
        try:
            if not current_analysis or not isinstance(current_analysis, dict):
                return None

            # 현재 분석의 키워드와 주제 추출
            current_keywords = set(current_analysis.get("keywords", []))
            current_topic = current_analysis.get("main_topic", "")

            best_match = None
            highest_score = 0

            # 단기 메모리에서 관련 컨텍스트 검색
            for context in reversed(self.short_term):
                if not isinstance(context, dict):
                    continue

                # 컨텍스트 키워드와 주제 추출
                context_keywords = set(context.get("keywords", []))
                context_topic = context.get("main_topic", "")

                # 유사도 점수 계산
                score = self._calculate_context_similarity(
                    current_keywords, context_keywords,
                    current_topic, context_topic
                )

                if score > highest_score:
                    highest_score = score
                    best_match = context

            # 유사도 임계값 (0.3) 이상인 경우만 반환
            return best_match if highest_score >= 0.3 else None

        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            return None

    def _calculate_context_similarity(self, 
                                   current_keywords: set, 
                                   context_keywords: set,
                                   current_topic: str,
                                   context_topic: str) -> float:
        """
        컨텍스트 유사도 계산

        Returns:
            float: 0과 1 사이의 유사도 점수
        """
        try:
            score = 0.0

            # 키워드 유사도 (가중치: 0.6)
            if current_keywords and context_keywords:
                keyword_similarity = len(current_keywords & context_keywords) / \
                                  max(len(current_keywords), len(context_keywords))
                score += 0.6 * keyword_similarity

            # 주제 유사도 (가중치: 0.4)
            if current_topic and context_topic:
                topic_similarity = 1.0 if current_topic == context_topic else 0.0
                score += 0.4 * topic_similarity

            return score

        except Exception as e:
            logger.error(f"Error calculating context similarity: {str(e)}")
            return 0.0

    def get_recent_context(self, limit: int = 5) -> List[Dict]:
        """최근 컨텍스트 반환"""
        try:
            return sorted(
                self.short_term,
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )[:limit]
        except Exception as e:
            logger.error(f"Error getting recent context: {str(e)}")
            return []

    def get_memory_summary(self) -> Dict:
        """메모리 요약 정보 반환"""
        try:
            return {
                "short_term": {
                    "size": len(self.short_term),
                    "recent": self.short_term[-3:] if self.short_term else []
                },
                "long_term": {
                    "preferences": self._get_top_items(self.long_term["preferences"]),
                    "experiences": self._get_top_items(self.long_term["experiences"]),
                    "decisions": self._get_top_items(self.long_term["decisions"]),
                    "patterns": self._get_top_items(self.long_term["patterns"])
                },
                "last_update": self.last_update.isoformat() if self.last_update else None
            }
        except Exception as e:
            logger.error(f"Error getting memory summary: {str(e)}")
            return {}

    def cleanup_old_memories(self) -> None:
        """오래된 메모리 정리"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.memory_retention_days)

            # 단기 메모리 정리
            while (self.short_term and 
                   datetime.fromisoformat(self.short_term[0]["timestamp"]) < cutoff_date):
                self.short_term.pop(0)

            # 장기 메모리 정리
            for category in self.long_term.values():
                if isinstance(category, dict):
                    for key, items in list(category.items()):
                        if isinstance(items, list):
                            category[key] = [
                                item for item in items
                                if datetime.fromisoformat(item["timestamp"]) >= cutoff_date
                            ]

            logger.info(f"메모리 정리 완료 (기준일: {cutoff_date.isoformat()})")

        except Exception as e:
            logger.error(f"Error cleaning up old memories: {str(e)}")

    def _get_top_items(self, items: Dict, limit: int = 5) -> Dict:
        """상위 항목 추출"""
        try:
            if isinstance(items, dict):
                return {
                    category: dict(
                        sorted(
                            patterns.items(),
                            key=lambda x: x[1],
                            reverse=True
                        )[:limit]
                    )
                    for category, patterns in items.items()
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting top items: {str(e)}")
            return {}