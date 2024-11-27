from enum import Enum
from typing import Dict, List


class Domain(Enum):
    """도메인 상수 정의"""
    DAILY = "daily"          # 일상생활
    LEISURE = "leisure"      # 여가활동
    SOCIAL = "social"        # 사회활동
    WORK = "work"           # 업무/학업
    HEALTH = "health"       # 건강/복지
    RELATIONSHIP = "relationship"  # 관계
    FINANCE = "finance"     # 경제활동
    TECH = "tech"          # 기술/IT
    NEWS = "news"          # 시사/정보
    UNKNOWN = "unknown"     # 미분류

    @classmethod
    def get_domain_mapping(cls) -> Dict[str, str]:
        """도메인 매핑 딕셔너리 반환"""
        return {
            "일상생활": cls.DAILY.value,
            "여가활동": cls.LEISURE.value,
            "사회활동": cls.SOCIAL.value,
            "업무/학업": cls.WORK.value,
            "건강/복지": cls.HEALTH.value,
            "관계": cls.RELATIONSHIP.value,
            "경제활동": cls.FINANCE.value,
            "기술/IT": cls.TECH.value,
            "시사/정보": cls.NEWS.value
        }

    @classmethod
    def get_sub_category_mapping(cls) -> Dict[str, List[str]]:
        """하위 카테고리 매핑 딕셔너리 반환"""
        return {
            cls.DAILY.value: ["식사", "수면", "휴식", "집안일"],
            cls.LEISURE.value: ["취미", "운동", "여행", "문화생활"],
            cls.SOCIAL.value: ["모임", "봉사", "종교활동", "지역활동"],
            cls.WORK.value: ["직장", "학교", "자기개발", "연구"],
            cls.HEALTH.value: ["의료", "운동", "심리", "복지서비스"],
            cls.RELATIONSHIP.value: ["가족", "친구", "동료", "연인"],
            cls.FINANCE.value: ["소비", "투자", "재테크", "쇼핑"],
            cls.TECH.value: ["기기", "소프트웨어", "디지털서비스"],
            cls.NEWS.value: ["뉴스", "정보검색", "시사이슈"]
        }
