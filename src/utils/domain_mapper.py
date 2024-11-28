from typing import Optional

from utils.logger import get_logger

from .constants import Domain

logger = get_logger(__name__)

class DomainMapper:
    """도메인 매핑 유틸리티"""

    @classmethod
    def map_topic_to_domain(cls, topic: Optional[str]) -> str:
        """
        토픽을 도메인으로 매핑

        Args:
            topic: 매핑할 토픽

        Returns:
            매핑된 도메인 문자열
        """
        try:
            if not topic or not isinstance(topic, str):
                logger.warning(f"Invalid topic value: {topic}")
                return Domain.UNKNOWN.value

            topic = topic.strip()

            # 1. 직접 매핑 확인
            domain_mapping = Domain.get_domain_mapping()
            if topic in domain_mapping:
                return domain_mapping[topic]

            # 2. 하위 카테고리 매핑 확인
            sub_category_mapping = Domain.get_sub_category_mapping()
            for domain, keywords in sub_category_mapping.items():
                if any(keyword in topic for keyword in keywords):
                    return domain

            logger.warning(f"No mapping found for topic: {topic}")
            return Domain.UNKNOWN.value

        except Exception as e:
            logger.error(f"Error mapping topic to domain: {str(e)}")
            return Domain.UNKNOWN.value