from datetime import datetime
from typing import Dict, List, Optional, Union

from utils.constants import Domain
from utils.logger import get_logger

logger = get_logger(__name__)

class KnowledgeBase:
    def __init__(self):
        """지식 베이스 초기화"""
        self.domains = {
            Domain.LEISURE.value: {  # leisure
                "locations": {},
                "preferences": {},
                "frequency": 0,
                "style": {},
                "history": {},
                "plans": {}
            },
            Domain.WORK.value: {     # work
                "field": {},
                "style": {},
                "schedule": {},
                "preferences": {},
                "skills": {},
                "projects": {}
            },
            Domain.DAILY.value: {    # daily
                "routine": {},
                "habits": {},
                "schedule": {},
                "preferences": {}
            },
            Domain.SOCIAL.value: {   # social
                "groups": {},
                "activities": {},
                "preferences": {},
                "frequency": 0
            },
            Domain.HEALTH.value: {   # health
                "activities": {},
                "metrics": {},
                "preferences": {},
                "history": {}
            },
            Domain.RELATIONSHIP.value: {  # relationship
                "contacts": {},
                "interactions": {},
                "preferences": {},
                "history": {}
            },
            Domain.FINANCE.value: {  # finance
                "transactions": {},
                "patterns": {},
                "preferences": {},
                "goals": {}
            },
            Domain.TECH.value: {     # tech
                "devices": {},
                "services": {},
                "preferences": {},
                "usage": {}
            },
            Domain.NEWS.value: {     # news
                "topics": {},
                "sources": {},
                "preferences": {},
                "history": {}
            }
        }

        self.connections = {}     # 도메인 간 연결 정보
        self.cross_domain_patterns = {} # 도메인 간 패턴
        self.context_awareness = {} # 상황 인식
        
        self.last_update = None   # 마지막 업데이트 시간

    def update_domain_knowledge(self, domain: str, analysis: Dict) -> None:
        """도메인별 지식 업데이트"""
        try:
            if domain not in self.domains:
                logger.warning(f"Unknown domain: {domain}")
                return
                
            self.last_update = datetime.now()
            
            # 도메인별 토픽 업데이트
            self._update_domain_topics(domain, analysis)
            
            # 도메인별 선호도 업데이트
            self._update_domain_preferences(domain, analysis)
            
            # 도메인별 빈도 업데이트
            self._update_domain_frequency(domain)
            
            # 도메인 간 연결 업데이트
            self._update_domain_connections(domain, analysis)
            
            # 상황 인식 업데이트
            self.update_context_awareness(domain, analysis)
            
            logger.info(f"도메인 지식 업데이트 완료: {domain}")
            
        except Exception as e:
            logger.error(f"Error updating domain knowledge: {str(e)}")

    def get_domain_knowledge(self, domain: str) -> Dict:
        """도메인별 지식 조회"""
        try:
            if domain in self.domains:
                return self.domains[domain]
            logger.warning(f"Unknown domain: {domain}")
            return {}
        except Exception as e:
            logger.error(f"Error getting domain knowledge: {str(e)}")
            return {}

    def update_cross_domain_patterns(self, analysis: Dict) -> None:
        """도메인 간 패턴 업데이트"""
        try:
            main_topic = analysis.get("main_topic", "")
            sub_topics = analysis.get("sub_topics", {})
            
            # 주제 간 연관성 분석
            for category, topics in sub_topics.items():
                if isinstance(topics, list):
                    for topic in topics:
                        pattern_key = f"{main_topic}->{category}:{topic}"
                        self.cross_domain_patterns[pattern_key] = \
                            self.cross_domain_patterns.get(pattern_key, 0) + 1
                        
            logger.debug("도메인 간 패턴 업데이트 완료")
            
        except Exception as e:
            logger.error(f"Error updating cross domain patterns: {str(e)}")

    def update_context_awareness(self, domain: str, analysis: Dict) -> None:
        """상황 인식 정보 업데이트"""
        try:
            if domain not in self.context_awareness:
                self.context_awareness[domain] = {
                    "temporal": {},  # 시간적 상황
                    "spatial": {},   # 공간적 상황
                    "social": {},    # 사회적 상황
                    "emotional": {}, # 감정적 상황
                    "environmental": {} # 환경적 상황
                }
            
            # 시간적 상황 업데이트
            if "temporal" in analysis.get("sub_topics", {}):
                for time_info in analysis["sub_topics"]["temporal"]:
                    self.context_awareness[domain]["temporal"][time_info] = \
                        self.context_awareness[domain]["temporal"].get(time_info, 0) + 1
            
            # 공간적 상황 업데이트
            if "spatial" in analysis.get("sub_topics", {}):
                for location in analysis["sub_topics"]["spatial"]:
                    self.context_awareness[domain]["spatial"][location] = \
                        self.context_awareness[domain]["spatial"].get(location, 0) + 1
            
            # 사회적 상황 업데이트
            if "companions" in analysis.get("sub_topics", {}):
                for companion in analysis["sub_topics"]["companions"]:
                    self.context_awareness[domain]["social"][companion] = \
                        self.context_awareness[domain]["social"].get(companion, 0) + 1
            
            # 감정적 상황 업데이트
            if "sentiment" in analysis:
                sentiment = analysis["sentiment"]
                self.context_awareness[domain]["emotional"][sentiment["type"]] = \
                    self.context_awareness[domain]["emotional"].get(sentiment["type"], 0) + 1
            
            logger.debug(f"상황 인식 정보 업데이트 완료: {domain}")
            
        except Exception as e:
            logger.error(f"Error updating context awareness: {str(e)}")

    def _update_domain_topics(self, domain: str, analysis: Dict) -> None:
        """도메인별 토픽 업데이트"""
        try:
            if "topics" not in self.domains[domain]:
                self.domains[domain]["topics"] = {}
                
            if "sub_topics" in analysis:
                for category, topics in analysis["sub_topics"].items():
                    if category not in self.domains[domain]["topics"]:
                        self.domains[domain]["topics"][category] = {}
                        
                    if isinstance(topics, list):
                        for topic in topics:
                            self.domains[domain]["topics"][category][topic] = \
                                self.domains[domain]["topics"][category].get(topic, 0) + 1
                            
            logger.debug(f"도메인 토픽 업데이트 완료: {domain}")
            
        except Exception as e:
            logger.error(f"Error updating domain topics: {str(e)}")

    def _update_domain_preferences(self, domain: str, analysis: Dict) -> None:
        """도메인별 선호도 업데이트"""
        try:
            if "preferences" not in self.domains[domain]:
                self.domains[domain]["preferences"] = {}
                
            if "sub_topics" in analysis:
                for category, items in analysis["sub_topics"].items():
                    if category not in self.domains[domain]["preferences"]:
                        self.domains[domain]["preferences"][category] = {}
                        
                    if isinstance(items, list):
                        for item in items:
                            self.domains[domain]["preferences"][category][item] = \
                                self.domains[domain]["preferences"][category].get(item, 0) + 1
                            
            logger.debug(f"도메인 선호도 업데이트 완료: {domain}")
            
        except Exception as e:
            logger.error(f"Error updating domain preferences: {str(e)}")

    def _update_domain_frequency(self, domain: str) -> None:
        """도메인별 빈도 업데이트"""
        try:
            if domain in self.domains:
                self.domains[domain]["frequency"] = \
                    self.domains[domain].get("frequency", 0) + 1
                logger.debug(f"도메인 빈도 업데이트 완료: {domain}")
            else:
                logger.warning(f"Unknown domain: {domain}")
        except Exception as e:
            logger.error(f"Error updating domain frequency: {str(e)}")

    def _update_domain_connections(self, domain: str, analysis: Dict) -> None:
        """도메인 간 연결 업데이트"""
        try:
            main_topic = analysis.get("main_topic", "")
            if not main_topic:
                return
                
            if domain not in self.connections:
                self.connections[domain] = {}
                
            # 서브 토픽과의 연결 분석
            if "sub_topics" in analysis:
                for category, topics in analysis["sub_topics"].items():
                    if isinstance(topics, list):
                        for topic in topics:
                            connection_key = f"{category}:{topic}"
                            self.connections[domain][connection_key] = \
                                self.connections[domain].get(connection_key, 0) + 1
                            
            logger.debug(f"도메인 연결 업데이트 완료: {domain}")
            
        except Exception as e:
            logger.error(f"Error updating domain connections: {str(e)}")

    def get_knowledge_summary(self) -> Dict:
        """지식 베이스 요약 정보 반환"""
        try:
            return {
                "domains": {
                    domain: {
                        "frequency": info.get("frequency", 0),
                        "top_topics": self._get_top_items(info.get("topics", {})),
                        "top_preferences": self._get_top_items(info.get("preferences", {}))
                    }
                    for domain, info in self.domains.items()
                },
                "cross_domain_patterns": self._get_top_items(self.cross_domain_patterns),
                "context_awareness": {
                    domain: {
                        category: self._get_top_items(patterns)
                        for category, patterns in contexts.items()
                    }
                    for domain, contexts in self.context_awareness.items()
                },
                "last_update": self.last_update.isoformat() if self.last_update else None
            }
        except Exception as e:
            logger.error(f"Error getting knowledge summary: {str(e)}")
            return {}

    def _get_top_items(self, data: Dict, limit: int = 5) -> Dict:
        """상위 항목 추출"""
        try:
            return dict(
                sorted(
                    data.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:limit]
            )
        except Exception as e:
            logger.error(f"Error getting top items: {str(e)}")
            return {}