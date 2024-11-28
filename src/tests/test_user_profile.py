import json
import os
import sys
import unittest
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user_profile import UserProfile


class TestUserProfile(unittest.TestCase):
    def setUp(self):
        """테스트 설정"""
        logger.info("=== 테스트 시작 ===")
        self.profile = UserProfile()
        self.test_analysis = {
            "main_topic": "여가활동",
            "sub_topics": {
                "activity_type": ["여행", "관광"],
                "temporal": ["주말", "2024-11-18"],
                "spatial": ["속초", "롯데 호텔"],
                "companions": ["친구"],
                "purpose": ["휴식/즐거움"]
            },
            "keywords": ["속초", "여행", "2024-11-18"],
            "sentiment": {
                "type": "긍정적",
                "score": 75
            },
            "reliability_score": 80,
            "intent": "여행 계획 수립"
        }
        logger.info("테스트 데이터 초기화 완료")

    def tearDown(self):
        """테스트 종료"""
        logger.info("=== 테스트 종료 ===\n")

    def test_profile_initialization(self):
        """프로필 초기화 테스트"""
        logger.info("프로필 초기화 테스트 시작")
        profile = self.profile.get_profile()

        # 컴포넌트 존재 확인
        components = ["user_interests", "behavior_patterns", "knowledge_base", 
                     "activities", "context_memory", "interaction_metrics"]
        for component in components:
            self.assertIn(component, profile)
            logger.info(f"컴포넌트 '{component}' 확인 완료")
        logger.info("프로필 초기화 테스트 완료")

    def test_update_from_analysis(self):
        """분석 결과 업데이트 테스트"""
        logger.info("분석 결과 업데이트 테스트 시작")

        # 업데이트 전 초기값 확인
        initial_metrics = self.profile.interaction_metrics.get_metrics_summary()
        logger.info(f"초기 상호작용 수: {initial_metrics['total_interactions']}")

        # 분석 결과 업데이트
        self.profile.update_from_analysis(self.test_analysis)
        profile_data = self.profile.get_profile()

        # 각 컴포넌트 업데이트 확인
        self.assertIn("user_interests", profile_data)
        self.assertIn("behavior_patterns", profile_data)
        self.assertIn("knowledge_base", profile_data)
        self.assertIn("activities", profile_data)
        self.assertIn("context_memory", profile_data)
        self.assertIn("interaction_metrics", profile_data)

        # 업데이트 후 값 확인
        updated_metrics = self.profile.interaction_metrics.get_metrics_summary()
        logger.info(f"업데이트 후 상호작용 수: {updated_metrics['total_interactions']}")
        logger.info(f"업데이트 후 평균 감정 점수: {updated_metrics['average_sentiment']}")

        # 구체적인 값 검증
        self.assertEqual(updated_metrics["total_interactions"], 1)
        self.assertEqual(updated_metrics["average_sentiment"], 75.0)

        logger.info("분석 결과 업데이트 테스트 완료")

    def test_user_interests_update(self):
        """관심사 업데이트 테스트"""
        logger.info("관심사 업데이트 테스트 시작")
        self.profile.update_from_analysis(self.test_analysis)

        # 토픽 확인
        topics = self.profile.user_interests.get_top_interests("topics")
        logger.info(f"상위 관심사: {topics}")
        self.assertIn("여가활동", [topic for topic, _ in topics])

        # 키워드 확인
        keywords = self.profile.user_interests.get_top_interests("keywords")
        logger.info(f"상위 키워드: {keywords}")
        self.assertIn("여행", [keyword for keyword, _ in keywords])

        # 선호도 확인
        preferences = self.profile.user_interests.preferences
        logger.info(f"활동 선호도: {preferences['activities']}")
        self.assertIn("여행", preferences["activities"])

        logger.info("관심사 업데이트 테스트 완료")

    def test_behavior_patterns_update(self):
        """행동 패턴 업데이트 테스트"""
        logger.info("행동 패턴 업데이트 테스트 시작")
        self.profile.update_from_analysis(self.test_analysis)

        patterns = self.profile.behavior_patterns

        # 시간 패턴 확인
        logger.info(f"시간 패턴: {patterns.temporal['weekly']}")
        self.assertIn("주말", patterns.temporal["weekly"])
        self.assertEqual(patterns.temporal["weekly"]["주말"], 1)

        # 공간 패턴 확인
        logger.info(f"공간 패턴: {patterns.spatial['locations']}")
        self.assertIn("속초", patterns.spatial["locations"])
        self.assertIn("롯데 호텔", patterns.spatial["locations"])

        # 사회적 패턴 확인
        logger.info(f"사회적 패턴: {patterns.social['companions']}")
        self.assertIn("친구", patterns.social["companions"])

        logger.info("행동 패턴 업데이트 테스트 완료")

    def test_knowledge_base_update(self):
        """지식 베이스 업데이트 테스트"""
        logger.info("지식 베이스 업데이트 테스트 시작")
        self.profile.update_from_analysis(self.test_analysis)

        # 도메인 지식 확인
        travel_knowledge = self.profile.knowledge_base.get_domain_knowledge("travel")
        logger.info(f"여행 도메인 지식: {travel_knowledge}")

        # 도메인 지식 업데이트 확인
        self.assertIsNotNone(travel_knowledge)
        self.assertTrue(travel_knowledge.get("frequency", 0) > 0)

        # 토픽 정보 확인
        if "topics" in travel_knowledge:
            logger.info(f"도메인 토픽: {travel_knowledge['topics']}")

        # 선호도 정보 확인
        if "preferences" in travel_knowledge:
            logger.info(f"도메인 선호도: {travel_knowledge['preferences']}")

        logger.info("지식 베이스 업데이트 테스트 완료")

    def test_activities_update(self):
        """활동 기록 업데이트 테스트"""
        logger.info("활동 기록 업데이트 테스트 시작")
        self.profile.update_from_analysis(self.test_analysis)

        activity_summary = self.profile.activities.get_activity_summary()

        # 활동 기록 확인
        logger.info(f"활동 요약: {activity_summary}")

        # 구체적인 값 검증
        self.assertEqual(activity_summary["total_activities"], 1)
        self.assertEqual(activity_summary["completed_activities"], 1)
        self.assertEqual(activity_summary["planned_activities"], 0)

        # 활동 패턴 확인
        self.assertIn("여가활동", activity_summary["activity_patterns"]["frequency"])

        logger.info("활동 기록 업데이트 테스트 완료")

    def test_context_memory_update(self):
        """컨텍스트 메모리 업데이트 테스트"""
        logger.info("컨텍스트 메모리 업데이트 테스트 시작")
        self.profile.update_from_analysis(self.test_analysis)

        # 최근 컨텍스트 확인
        recent_context = self.profile.context_memory.get_recent_context(1)
        logger.info(f"최근 컨텍스트: {recent_context}")

        # 컨텍스트 메모리 검증
        self.assertTrue(len(recent_context) > 0)
        self.assertEqual(recent_context[0].get("topic"), "여가활동")

        # 장기 메모리 확인
        long_term = self.profile.context_memory.get_long_term_memories()
        logger.info(f"장기 메모리 상태: {long_term}")

        logger.info("컨텍스트 메모리 업데이트 테스트 완료")

    def test_interaction_metrics_update(self):
        """상호작용 메트릭스 업데이트 테스트"""
        logger.info("상호작용 메트릭스 업데이트 테스트 시작")

        # 초기 상태 확인
        initial_metrics = self.profile.interaction_metrics.get_metrics_summary()
        logger.info(f"초기 메트릭스: {initial_metrics}")

        # 업데이트 수행
        self.profile.update_from_analysis(self.test_analysis)

        # 업데이트 후 상태 확인
        updated_metrics = self.profile.interaction_metrics.get_metrics_summary()
        logger.info(f"업데이트 후 메트릭스: {updated_metrics}")

        # 메트릭스 검증
        self.assertEqual(updated_metrics["total_interactions"], 1)
        self.assertTrue(updated_metrics["average_sentiment"] > 0)

        # 상세 메트릭스 확인
        detailed_metrics = self.profile.interaction_metrics.get_detailed_metrics()
        logger.info(f"상세 메트릭스:\n- 도메인 분포: {detailed_metrics['counts']['by_domain']}\n" 
                   f"- 감정 이력: {detailed_metrics['sentiment']['history']}")

        logger.info("상호작용 메트릭스 업데이트 테스트 완료")

    def test_consecutive_updates(self):
        """연속 업데이트 테스트"""
        logger.info("연속 업데이트 테스트 시작")

        # 첫 번째 업데이트
        logger.info("첫 번째 업데이트 실행")
        self.profile.update_from_analysis(self.test_analysis)

        first_metrics = self.profile.interaction_metrics.get_metrics_summary()
        logger.info(f"첫 번째 업데이트 후 메트릭스: {first_metrics}")

        # 두 번째 분석 결과
        second_analysis = {
            "main_topic": "여가활동",
            "sub_topics": {
                "activity_type": ["식사", "미식"],
                "temporal": ["저녁", "2024-11-18"],
                "spatial": ["속초", "맛집"],
                "companions": ["친구"],
                "purpose": ["즐거움"]
            },
            "keywords": ["맛집", "저녁", "속초"],
            "sentiment": {
                "type": "긍정적",
                "score": 80
            },
            "reliability_score": 85,
            "intent": "맛집 탐방"
        }

        # 두 번째 업데이트
        logger.info("두 번째 업데이트 실행")
        self.profile.update_from_analysis(second_analysis)

        # 최종 결과 확인
        final_metrics = self.profile.interaction_metrics.get_metrics_summary()
        logger.info(f"최종 상호작용 수: {final_metrics['total_interactions']}")
        logger.info(f"최종 평균 감정 점수: {final_metrics['average_sentiment']}")

        # 구체적인 값 검증
        self.assertEqual(final_metrics["total_interactions"], 2)
        self.assertEqual(final_metrics["average_sentiment"], 77.5)

        logger.info("연속 업데이트 테스트 완료")

    def test_suggested_actions(self):
        """추천 활동 테스트"""
        logger.info("추천 및 인사이트 테스트 시작")
        self.profile.update_from_analysis(self.test_analysis)

        # 추천 활동 확인
        suggestions = self.profile.get_suggested_actions("travel")
        logger.info(f"추천 활동: {suggestions}")
        self.assertTrue(len(suggestions) > 0)
        self.assertTrue(any("여행" in suggestion for suggestion in suggestions))

    def test_related_topics(self):
        """연관 주제 테스트"""
        logger.info("연관 주제 테스트 시작")
        self.profile.update_from_analysis(self.test_analysis)

        # 연관 주제 추출
        related = self.profile.get_related_topics("travel")
        logger.info(f"연관 주제: {related}")

        # 연관 주제 검증
        self.assertTrue(len(related) > 0)

        # 주제 관련성 확인
        travel_related = ["여행", "관광", "숙박", "레저"]
        has_travel_topic = any(
            any(topic in related_topic for topic in travel_related)
            for related_topic in related
        )
        self.assertTrue(has_travel_topic)

        logger.info("연관 주제 테스트 완료")

    def test_personalized_suggestions(self):
        """개인화된 제안 테스트"""
        logger.info("개인화된 제안 테스트 시작")

        # 프로필 업데이트를 통해 컨텍스트 생성
        self.profile.update_from_analysis(self.test_analysis)

        # 개인화된 제안 생성
        personalized = self.profile.get_personalized_suggestions("travel")
        logger.info(f"개인화된 제안: {personalized}")

        # 기본 검증
        self.assertTrue(len(personalized) > 0)

        # 제안 관련성 확인
        relevant_keywords = ["여행", "관광", "속초", "호텔"]
        has_relevant_suggestion = False

        for suggestion in personalized:
            for keyword in relevant_keywords:
                if keyword in suggestion.lower():
                    has_relevant_suggestion = True
                    logger.info(f"관련 키워드 '{keyword}' 발견됨: {suggestion}")
                    break
            if has_relevant_suggestion:
                break

        self.assertTrue(has_relevant_suggestion, 
                    f"제안에서 관련 키워드를 찾을 수 없음: {relevant_keywords}")

        logger.info("개인화된 제안 테스트 완료")

    def test_trend_analysis(self):
        """트렌드 분석 테스트"""
        logger.info("트렌드 분석 테스트 시작")
        self.profile.update_from_analysis(self.test_analysis)

        # 트렌드 분석 수행
        trends = self.profile.analyze_trends()
        logger.info(f"트렌드 분석 결과: {trends}")

        # 트렌드 구성요소 확인
        self.assertIn("interests", trends)
        self.assertIn("behavior", trends)
        self.assertIn("engagement", trends)

        # 세부 트렌드 확인
        logger.info(f"관심사 트렌드: {trends['interests']}")
        logger.info(f"행동 트렌드: {trends['behavior']}")
        logger.info(f"참여도 트렌드: {trends['engagement']}")

        # 트렌드 데이터 검증
        self.assertTrue(len(trends["interests"].get("rising_topics", [])) > 0)
        self.assertTrue(len(trends["behavior"].get("spatial", [])) > 0)

        logger.info("트렌드 분석 테스트 완료")

if __name__ == '__main__':
    unittest.main(verbosity=2)
