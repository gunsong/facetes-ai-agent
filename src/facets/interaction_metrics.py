from datetime import datetime
from typing import Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)

class InteractionMetrics:
    def __init__(self):
        """상호작용 지표 초기화"""
        self.counts = {
            "total": 0,        # 전체 상호작용 수
            "by_type": {},     # 유형별 상호작용
            "by_domain": {}    # 도메인별 상호작용
        }
        
        self.sentiment = {
            "average": 0,      # 평균 감정 점수
            "history": [],     # 감정 이력
            "by_context": {}   # 상황별 감정
        }
        
        self.engagement = {
            "level": 0,        # 참여도 레벨
            "trends": [],      # 참여 트렌드
            "peaks": {}        # 최고 참여 시점
        }
        
        self.query_history = []    # 질의 이력
        self.response_feedback = {} # 응답 피드백
        self.satisfaction_scores = {} # 만족도 점수
        
        self.last_update = None    # 마지막 업데이트 시간

    def update_metrics(self, analysis: Dict) -> None:
        """상호작용 지표 업데이트"""
        try:
            self.last_update = datetime.now()
            
            # 각 지표 업데이트
            self.update_counts(analysis)
            self.update_sentiment(analysis)
            self.update_engagement(analysis)
            
            # 히스토리 업데이트
            self._update_query_history(analysis)
            self._update_response_feedback(analysis)
            self._update_satisfaction_scores(analysis)
            
            logger.info("상호작용 지표 업데이트 완료")
            
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")

    def update_counts(self, analysis: Dict) -> None:
        """상호작용 횟수 업데이트"""
        try:
            # 전체 상호작용 수 증가
            self.counts["total"] += 1
            
            # 유형별 상호작용 수 업데이트
            interaction_type = analysis.get("intent")
            if isinstance(interaction_type, dict):
                # 딕셔너리인 경우 '유형' 키의 값을 사용
                logger.info(f"interaction_type: {interaction_type}")
                interaction_type = interaction_type.get('유형', 'unknown')
            elif not interaction_type:
                interaction_type = 'unknown'
            else:
                interaction_type = str(interaction_type)

            self.counts["by_type"][interaction_type] = \
                self.counts["by_type"].get(interaction_type, 0) + 1

            # 도메인별 상호작용 수 업데이트
            domain = analysis.get("main_topic")
            if isinstance(domain, dict):
                # 딕셔너리인 경우 첫 번째 키의 값을 사용
                logger.info(f"domain: {domain}")
                domain = next(iter(domain.values()), 'unknown')
            elif not domain:
                domain = 'unknown'
            else:
                domain = str(domain)

            self.counts["by_domain"][domain] = \
                self.counts["by_domain"].get(domain, 0) + 1

            logger.info(f"상호작용 횟수 업데이트 완료: {interaction_type}, {domain}")

        except Exception as e:
            logger.error(f"Error updating counts: {str(e)}")

    def update_sentiment(self, analysis: Dict) -> None:
        """감정 상태 업데이트"""
        try:
            if "sentiment" in analysis:
                sentiment_data = analysis["sentiment"]
                
                # 감정 이력 추가
                sentiment_record = {
                    "timestamp": datetime.now().isoformat(),
                    "type": sentiment_data.get("type", "neutral"),
                    "score": sentiment_data.get("score", 0),
                    "context": analysis.get("main_topic", "unknown")
                }
                self.sentiment["history"].append(sentiment_record)
                
                # 평균 감정 점수 업데이트
                scores = [record["score"] for record in self.sentiment["history"]]
                self.sentiment["average"] = sum(scores) / len(scores)
                
                # 상황별 감정 업데이트
                context = analysis.get("main_topic", "unknown")
                if context not in self.sentiment["by_context"]:
                    self.sentiment["by_context"][context] = []
                self.sentiment["by_context"][context].append(sentiment_record)
                
                logger.debug(f"감정 상태 업데이트 완료: {sentiment_data['type']}")
                
        except Exception as e:
            logger.error(f"Error updating sentiment: {str(e)}")

    def update_engagement(self, analysis: Dict) -> None:
        """참여도 업데이트"""
        try:
            # 참여도 점수 계산
            engagement_score = self.get_engagement_score(analysis)
            
            # 참여도 트렌드 업데이트
            self.engagement["trends"].append({
                "timestamp": datetime.now().isoformat(),
                "score": engagement_score,
                "context": analysis.get("main_topic", "unknown")
            })
            
            # 참여도 레벨 업데이트
            self.engagement["level"] = self._calculate_engagement_level()
            
            # 최고 참여 시점 업데이트
            if engagement_score >= 0.8:  # 80% 이상일 때
                context = analysis.get("main_topic", "unknown")
                if context not in self.engagement["peaks"]:
                    self.engagement["peaks"][context] = []
                self.engagement["peaks"][context].append({
                    "timestamp": datetime.now().isoformat(),
                    "score": engagement_score
                })
                
            logger.debug(f"참여도 업데이트 완료: {engagement_score}")
            
        except Exception as e:
            logger.error(f"Error updating engagement: {str(e)}")

    def get_engagement_score(self, analysis: Dict) -> float:
        """참여도 점수 계산"""
        try:
            score = 0.0
            weights = {
                "sentiment": 0.3,    # 감정 상태
                "detail": 0.2,       # 상세도
                "interaction": 0.3,   # 상호작용 품질
                "reliability": 0.2    # 신뢰도
            }
            
            # 감정 점수
            if "sentiment" in analysis:
                sentiment_score = analysis["sentiment"].get("score", 0)
                score += sentiment_score * weights["sentiment"]
            
            # 상세도 점수
            if "detail_level" in analysis:
                detail_score = min(analysis["detail_level"] / 100, 1.0)
                score += detail_score * weights["detail"]
            
            # 상호작용 품질 점수
            interaction_score = self._calculate_interaction_quality(analysis)
            score += interaction_score * weights["interaction"]
            
            # 신뢰도 점수
            if "reliability_score" in analysis:
                reliability_score = min(analysis["reliability_score"] / 100, 1.0)
                score += reliability_score * weights["reliability"]
            
            return min(max(score, 0.0), 1.0)  # 0과 1 사이로 정규화
            
        except Exception as e:
            logger.error(f"Error calculating engagement score: {str(e)}")
            return 0.0

    def _calculate_engagement_level(self) -> int:
        """참여도 레벨 계산"""
        try:
            if not self.engagement["trends"]:
                return 0
                
            # 최근 5개 트렌드의 평균 점수 계산
            recent_scores = [
                trend["score"] 
                for trend in self.engagement["trends"][-5:]
            ]
            average_score = sum(recent_scores) / len(recent_scores)
            
            # 레벨 결정 (0-10)
            return int(average_score * 10)
            
        except Exception as e:
            logger.error(f"Error calculating engagement level: {str(e)}")
            return 0

    def _calculate_interaction_quality(self, analysis: Dict) -> float:
        """상호작용 품질 점수 계산"""
        try:
            quality_score = 0.0
            
            # 1. 응답 상세도 체크
            if "detail_level" in analysis:
                quality_score += min(analysis["detail_level"] / 100, 0.4)
                
            # 2. 키워드 매칭 체크
            if "keywords" in analysis:
                keyword_count = len(analysis["keywords"])
                quality_score += min(keyword_count * 0.1, 0.3)
                
            # 3. 컨텍스트 활용도 체크
            if "context_usage" in analysis:
                quality_score += min(analysis["context_usage"] / 100, 0.3)
                
            return quality_score
            
        except Exception as e:
            logger.error(f"Error calculating interaction quality: {str(e)}")
            return 0.0

    def _update_query_history(self, analysis: Dict) -> None:
        """질의 이력 업데이트"""
        try:
            query_record = {
                "timestamp": datetime.now().isoformat(),
                "type": analysis.get("intent", "unknown"),
                "topic": analysis.get("main_topic", "unknown"),
                "keywords": analysis.get("keywords", []),
                "sentiment": analysis.get("sentiment", {})
            }
            self.query_history.append(query_record)
            
        except Exception as e:
            logger.error(f"Error updating query history: {str(e)}")

    def _update_response_feedback(self, analysis: Dict) -> None:
        """응답 피드백 업데이트"""
        try:
            if "feedback" in analysis:
                feedback = analysis["feedback"]
                response_id = feedback.get("response_id", "unknown")
                
                if response_id not in self.response_feedback:
                    self.response_feedback[response_id] = []
                    
                self.response_feedback[response_id].append({
                    "timestamp": datetime.now().isoformat(),
                    "rating": feedback.get("rating", 0),
                    "comment": feedback.get("comment", ""),
                    "context": analysis.get("main_topic", "unknown")
                })
                
        except Exception as e:
            logger.error(f"Error updating response feedback: {str(e)}")

    def _update_satisfaction_scores(self, analysis: Dict) -> None:
        """만족도 점수 업데이트"""
        try:
            if "satisfaction" in analysis:
                satisfaction = analysis["satisfaction"]
                context = analysis.get("main_topic", "unknown")
                
                if context not in self.satisfaction_scores:
                    self.satisfaction_scores[context] = []
                    
                self.satisfaction_scores[context].append({
                    "timestamp": datetime.now().isoformat(),
                    "score": satisfaction.get("score", 0),
                    "factors": satisfaction.get("factors", [])
                })
                
        except Exception as e:
            logger.error(f"Error updating satisfaction scores: {str(e)}")

    def get_metrics_summary(self) -> Dict:
        """메트릭스 요약 정보 반환"""
        try:
            return {
                "interaction_counts": self.counts,
                "sentiment_analysis": {
                    "average_score": self.sentiment["average"],
                    "recent_trends": self.sentiment["history"][-5:],
                    "context_distribution": self.sentiment["by_context"]
                },
                "engagement_metrics": {
                    "current_level": self.engagement["level"],
                    "recent_trends": self.engagement["trends"][-5:],
                    "peak_moments": self.engagement["peaks"]
                },
                "last_update": self.last_update.isoformat() if self.last_update else None
            }
        except Exception as e:
            logger.error(f"Error getting metrics summary: {str(e)}")
            return {}

    def _calculate_engagement_level(self) -> int:
        """참여도 레벨 계산"""
        try:
            if not self.engagement["trends"]:
                return 0
                
            # 최근 5개 트렌드의 평균 점수 계산
            recent_scores = [
                trend["score"] 
                for trend in self.engagement["trends"][-5:]
            ]
            average_score = sum(recent_scores) / len(recent_scores)
            
            # 레벨 결정 (0-10)
            return int(average_score * 10)
            
        except Exception as e:
            logger.error(f"Error calculating engagement level: {str(e)}")
            return 0

    def _calculate_interaction_quality(self, analysis: Dict) -> float:
        """상호작용 품질 점수 계산"""
        try:
            quality_score = 0.0
            
            # 1. 응답 상세도 체크
            if "detail_level" in analysis:
                quality_score += min(analysis["detail_level"] / 100, 0.4)
                
            # 2. 키워드 매칭 체크
            if "keywords" in analysis:
                keyword_count = len(analysis["keywords"])
                quality_score += min(keyword_count * 0.1, 0.3)
                
            # 3. 컨텍스트 활용도 체크
            if "context_usage" in analysis:
                quality_score += min(analysis["context_usage"] / 100, 0.3)
                
            return quality_score
            
        except Exception as e:
            logger.error(f"Error calculating interaction quality: {str(e)}")
            return 0.0