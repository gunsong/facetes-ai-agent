import json
from datetime import datetime
from typing import Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)

class Activities:
    def __init__(self):
        """활동 정보 초기화"""
        self.planned = []         # 예정된 활동
        self.completed = []       # 완료된 활동
        self.recurring = {        # 반복 활동
            "daily": [],          # 일간 반복
            "weekly": [],         # 주간 반복
            "monthly": [],        # 월간 반복
            "seasonal": []        # 계절별 반복
        }
        self.interests = []       # 관심 활동
        self.patterns = {         # 활동 패턴
            "frequency": {},      # 빈도
            "combinations": {},   # 조합
            "sequences": {}       # 순서
        }
        self.history = {          # 활동 이력
            "by_category": {},    # 카테고리별
            "by_location": {},    # 위치별
            "by_companion": {}    # 동반자별
        }
        self.last_update = None   # 마지막 업데이트 시간

    def update_activity_records(self, analysis_result: Dict, timestamp: str) -> None:
        """
        활동 기록 업데이트
        Args:
            analysis_result: 분석 결과 딕셔너리
            timestamp: 타임스탬프 문자열
        """
        try:
            logger.info("활동 기록 업데이트 시작")
            self.last_update = datetime.now()

            # 활동 기록 생성
            activity_record = self._create_activity_record(analysis_result, timestamp)

            # 반복 활동 체크
            if self._is_recurring_activity(activity_record):
                self._update_recurring_activities(activity_record)
            # 미래 활동 체크
            elif self._is_future_activity(analysis_result):
                self.planned.append(activity_record)
            else:
                self.completed.append(activity_record)

            # 활동 패턴 업데이트
            self._update_activity_patterns(activity_record)

            # 활동 이력 업데이트
            self._update_activity_history(activity_record)

            logger.info("활동 기록 업데이트 완료")

        except Exception as e:
            logger.error(f"Error updating activity records: {str(e)}")

    def _create_activity_record(self, analysis_result: Dict, timestamp: str) -> Dict:
        """
        활동 기록 생성
        Args:
            analysis_result: 분석 결과 딕셔너리
            timestamp: 타임스탬프 문자열
        Returns:
            Dict: 생성된 활동 기록
        """
        try:
            logger.info("활동 기록 생성 시작")
            record = {
                "timestamp": timestamp,
                "type": analysis_result.get("main_topic", "unknown"),
                "details": analysis_result.get("sub_topics", {}),
                "keywords": analysis_result.get("keywords", []),
                "sentiment": analysis_result.get("sentiment", {}),
                "location": self._extract_location(analysis_result),
                "companions": self._extract_companions(analysis_result),
                "intent": analysis_result.get("intent", "unknown"),
                "reliability": analysis_result.get("reliability_score", 0)
            }
            logger.info(f"활동 기록 생성 완료: {json.dumps(record, ensure_ascii=False)}")
            return record

        except Exception as e:
            logger.error(f"Error creating activity record: {str(e)}")
            return {}

    def _extract_location(self, analysis_result: Dict) -> str:
        """
        위치 정보 추출
        Args:
            analysis_result: 분석 결과 딕셔너리
        Returns:
            str: 추출된 위치 정보
        """
        try:
            spatial_info = analysis_result.get("sub_topics", {}).get("spatial", [])
            if spatial_info:
                # 첫 번째 공간 정보 반환
                return spatial_info[0]
            return ""

        except Exception as e:
            logger.error(f"Error extracting location: {str(e)}")
            return ""

    def _extract_companions(self, analysis_result: Dict) -> List[str]:
        """
        동반자 정보 추출
        Args:
            analysis_result: 분석 결과 딕셔너리
        Returns:
            List[str]: 추출된 동반자 목록
        """
        try:
            return analysis_result.get("sub_topics", {}).get("companions", [])

        except Exception as e:
            logger.error(f"Error extracting companions: {str(e)}")
            return []

    def _is_recurring_activity(self, activity_record: Dict) -> bool:
        """반복 활동 여부 확인"""
        try:
            if not self.completed:
                return False

            # 현재 활동과 유사한 활동 찾기
            similar_activities = []
            for past_activity in self.completed[-10:]:  # 최근 10개 활동만 확인
                similarity_score = self._calculate_activity_similarity(
                    past_activity,
                    activity_record
                )
                if similarity_score > 0.7:  # 유사도 임계값
                    similar_activities.append(past_activity)

            # 유사한 활동이 2개 이상이면 반복 활동으로 간주
            return len(similar_activities) >= 2

        except Exception as e:
            logger.error(f"Error checking recurring activity: {str(e)}")
            return False

    def _calculate_activity_similarity(self, activity1: Dict, activity2: Dict) -> float:
        """
        활동 간 유사도 계산
        Returns:
            float: 0과 1 사이의 유사도 점수
        """
        try:
            scores = []
            weights = []

            # 1. 활동 유형 비교 (가중치: 0.4)
            if activity1.get("type") == activity2.get("type"):
                scores.append(1.0)
            else:
                scores.append(0.0)
            weights.append(0.4)

            # 2. 키워드 비교 (가중치: 0.3)
            keywords1 = set(activity1.get("keywords", []))
            keywords2 = set(activity2.get("keywords", []))
            if keywords1 and keywords2:
                common_keywords = keywords1 & keywords2
                scores.append(len(common_keywords) / max(len(keywords1), len(keywords2)))
                weights.append(0.3)

            # 3. 장소 비교 (가중치: 0.2)
            if activity1.get("location") == activity2.get("location"):
                scores.append(1.0)
            else:
                scores.append(0.0)
            weights.append(0.2)

            # 4. 동반자 비교 (가중치: 0.1)
            companions1 = set(activity1.get("companions", []))
            companions2 = set(activity2.get("companions", []))
            if companions1 and companions2:
                common_companions = companions1 & companions2
                scores.append(len(common_companions) / max(len(companions1), len(companions2)))
                weights.append(0.1)

            # 가중 평균 계산
            if not weights:
                return 0.0
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            total_weight = sum(weights)
            return weighted_sum / total_weight

        except Exception as e:
            logger.error(f"Error calculating activity similarity: {str(e)}")
            return 0.0

    def _is_future_activity(self, analysis_result: Dict) -> bool:
        """미래 활동 여부 판단"""
        try:
            temporal_info = analysis_result.get("sub_topics", {}).get("temporal", [])
            future_keywords = [
                "예정", "계획", "할 예정", "하려고", 
                "예약", "다음", "이번", "앞으로"
            ]

            return any(
                keyword in str(temporal_info) 
                for keyword in future_keywords
            )

        except Exception as e:
            logger.error(f"Error checking future activity: {str(e)}")
            return False

    def _update_recurring_activities(self, activity_record: Dict) -> None:
        """반복 활동 업데이트"""
        try:
            # 활동의 주기 파악
            period = self._determine_activity_period(activity_record)
            if period:
                # 해당 주기의 반복 활동 목록에 추가
                self.recurring[period].append(activity_record)

                # 최대 크기 제한 (각 주기별 최근 10개만 유지)
                if len(self.recurring[period]) > 10:
                    self.recurring[period].pop(0)

                logger.debug(f"반복 활동 업데이트 완료: {period}")

        except Exception as e:
            logger.error(f"Error updating recurring activities: {str(e)}")

    def _determine_activity_period(self, activity_record: Dict) -> Optional[str]:
        """활동의 주기 결정"""
        try:
            temporal_info = activity_record.get("details", {}).get("temporal", [])

            # 주기 키워드 매핑
            period_keywords = {
                "daily": ["매일", "daily", "하루", "일간"],
                "weekly": ["매주", "weekly", "주간", "요일"],
                "monthly": ["매월", "monthly", "월간"],
                "seasonal": ["계절", "seasonal", "분기", "철"]
            }

            # 키워드 매칭
            for period, keywords in period_keywords.items():
                if any(keyword in str(temporal_info) for keyword in keywords):
                    logger.debug(f"활동 주기 결정: {period}")
                    return period

            return None

        except Exception as e:
            logger.error(f"Error determining activity period: {str(e)}")
            return None

    def _get_top_items(self, items: Dict, limit: int = 5) -> List[Dict]:
        """
        상위 항목 추출
        Args:
            items: 집계된 항목 딕셔너리
            limit: 반환할 최대 항목 수
        Returns:
            List[Dict]: 상위 항목 목록
        """
        try:
            sorted_items = sorted(
                items.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return [
                {"item": item, "count": count}
                for item, count in sorted_items[:limit]
            ]
        except Exception as e:
            logger.error(f"Error getting top items: {str(e)}")
            return []

    def _update_activity_patterns(self, activity_record: Dict) -> None:
        """활동 패턴 업데이트"""
        try:
            # 빈도 패턴 업데이트
            activity_type = activity_record.get("type", "unknown")
            self.patterns["frequency"][activity_type] = \
                self.patterns["frequency"].get(activity_type, 0) + 1

            # 활동 조합 패턴 업데이트
            if self.completed:
                last_activity = self.completed[-1]
                last_type = last_activity.get("type", "unknown")
                combination = f"{last_type}->{activity_type}"
                self.patterns["combinations"][combination] = \
                    self.patterns["combinations"].get(combination, 0) + 1

            # 활동 시퀀스 패턴 업데이트
            if len(self.completed) >= 2:
                last_two = [a.get("type", "unknown") for a in self.completed[-2:]]
                sequence = f"{last_two[0]}->{last_two[1]}->{activity_type}"
                self.patterns["sequences"][sequence] = \
                    self.patterns["sequences"].get(sequence, 0) + 1

            logger.debug(f"활동 패턴 업데이트 완료: {activity_type}")

        except Exception as e:
            logger.error(f"Error updating activity patterns: {str(e)}")

    def _update_activity_history(self, activity_record: Dict) -> None:
        """활동 이력 업데이트"""
        try:
            # 카테고리별 이력
            category = activity_record.get("type", "unknown")
            if category:
                if category not in self.history["by_category"]:
                    self.history["by_category"][category] = []
                self.history["by_category"][category].append(activity_record)

            # 위치별 이력
            location = activity_record.get("location", "")
            if location:
                if location not in self.history["by_location"]:
                    self.history["by_location"][location] = []
                self.history["by_location"][location].append(activity_record)

            # 동반자별 이력
            companions = activity_record.get("companions", [])
            for companion in companions:
                if companion not in self.history["by_companion"]:
                    self.history["by_companion"][companion] = []
                self.history["by_companion"][companion].append(activity_record)

            logger.debug("활동 이력 업데이트 완료")

        except Exception as e:
            logger.error(f"Error updating activity history: {str(e)}")

    def _update_activity_sequence(self, activity_record: Dict) -> None:
        """활동 시퀀스 업데이트"""
        try:
            if len(self.completed) >= 2:
                last_two = [a.get("type", "unknown") for a in self.completed[-2:]]
                sequence = f"{last_two[0]}->{last_two[1]}->{activity_record.get('type', 'unknown')}"
                self.patterns["sequences"][sequence] = \
                    self.patterns["sequences"].get(sequence, 0) + 1

            logger.debug(f"활동 시퀀스 업데이트 완료")

        except Exception as e:
            logger.error(f"Error updating activity sequence: {str(e)}")

    def get_activity_summary(self) -> Dict:
        """활동 요약 정보 반환"""
        try:
            return {
                "total_activities": len(self.completed) + len(self.planned),
                "completed_activities": len(self.completed),
                "planned_activities": len(self.planned),
                "recurring_activities": {
                    period: len(activities)
                    for period, activities in self.recurring.items()
                },
                "activity_patterns": self.patterns,
                "last_update": self.last_update.isoformat() if self.last_update else None
            }
        except Exception as e:
            logger.error(f"Error getting activity summary: {str(e)}")
            return {}

    def get_recent_activities(self, limit: int = 5) -> List[Dict]:
        """최근 활동 목록 반환"""
        try:
            all_activities = sorted(
                self.completed + self.planned,
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )
            return all_activities[:limit]
        except Exception as e:
            logger.error(f"Error getting recent activities: {str(e)}")
            return []

    def get_recurring_patterns(self) -> Dict:
        """반복 활동 패턴 반환"""
        try:
            return {
                period: len(activities)
                for period, activities in self.recurring.items()
            }
        except Exception as e:
            logger.error(f"Error getting recurring patterns: {str(e)}")
            return {}

    def _get_top_items(self, items: Dict, limit: int = 5) -> List[Dict]:
        """
        상위 항목 추출
        Args:
            items: 집계된 항목 딕셔너리
            limit: 반환할 최대 항목 수
        Returns:
            List[Dict]: 상위 항목 목록
        """
        try:
            sorted_items = sorted(
                items.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return [
                {"item": item, "count": count}
                for item, count in sorted_items[:limit]
            ]
        except Exception as e:
            logger.error(f"Error getting top items: {str(e)}")
            return []

    def get_pattern_summary(self) -> Dict:
        """패턴 요약 정보 반환"""
        try:
            return {
                "most_frequent": self._get_top_items(self.patterns["frequency"], 5),
                "common_combinations": self._get_top_items(self.patterns["combinations"], 3),
                "frequent_sequences": self._get_top_items(self.patterns["sequences"], 3)
            }
        except Exception as e:
            logger.error(f"Error getting pattern summary: {str(e)}")
            return {}

    def get_recurring_summary(self) -> Dict:
        """반복 활동 요약 정보 반환"""
        try:
            return {
                period: {
                    "count": len(activities),
                    "recent": activities[-3:] if activities else []
                }
                for period, activities in self.recurring.items()
                if activities
            }
        except Exception as e:
            logger.error(f"Error getting recurring summary: {str(e)}")
            return {}

    def get_history_summary(self) -> Dict:
        """활동 이력 요약 정보 반환"""
        try:
            return {
                "by_category": self._get_history_stats(self.history["by_category"]),
                "by_location": self._get_history_stats(self.history["by_location"]),
                "by_companion": self._get_history_stats(self.history["by_companion"])
            }
        except Exception as e:
            logger.error(f"Error getting history summary: {str(e)}")
            return {}

    def _get_history_stats(self, history_data: Dict) -> Dict:
        """이력 데이터 통계 생성"""
        try:
            return {
                category: {
                    "total": len(activities),
                    "recent": activities[-3:] if activities else []
                }
                for category, activities in history_data.items()
            }
        except Exception as e:
            logger.error(f"Error getting history stats: {str(e)}")
            return {}
