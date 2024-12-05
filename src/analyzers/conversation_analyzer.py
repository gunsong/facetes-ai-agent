import json
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional

from analyzers.context_prioritizer import ContextPrioritizer
from analyzers.context_processor import ContextProcessor
from analyzers.conversation_flow_manager import ConversationFlowManager
from facets.user_profile import UserProfile
from generators.response_generator import ResponseGenerator
from openai import AsyncOpenAI
from utils.constants import Domain
from utils.domain_mapper import DomainMapper
from utils.logger import get_logger
from utils.text_parser import TextParser

logger = get_logger(__name__)

class ConversationAnalyzer:
    def __init__(self, openai_api_key: str, openai_base_url: str, temperature: float = 0.7):
        """
        대화 분석기 초기화
        Args:
            openai_api_key: OpenAI API 키
            openai_base_url: OpenAI API 기본 URL
            temperature: 생성 모델의 temperature 값
        """
        self.client = AsyncOpenAI(
            api_key=openai_api_key,
            base_url=openai_base_url
        )
        self.temperature = temperature
        self.conversation_history: List[Dict] = []
        self.current_context = None
        self.user_profile = UserProfile()
        self.text_parser = TextParser()

        self.context_processor = ContextProcessor()
        self.context_prioritizer = ContextPrioritizer()
        self.response_generator = ResponseGenerator()
        self.flow_manager = ConversationFlowManager()

    def _create_analysis_prompt(self) -> str:
        """분석용 프롬프트 템플릿 생성"""
        try:
            template = """
당신은 네 명의 전문가로 구성된 AI 분석 시스템입니다. 각 전문가는 자신의 전문 영역에서 분석을 수행하고, 최종적으로 통합된 결과를 생성합니다.

## 전문가 역할
1. 언어/의도 분석가
- **메인 주제 분류**: 대화 내용의 맥락을 분석해 포괄적이면서도 구체적인 주제를 설정합니다.
  * 1차 분류: [일상/업무/여가/정보] 중 선택
  * 2차 분류: [생활/활동/관계/건강/경제/기술/시사] 등 구체화
  * 예: "강남역 근처 맛집 추천해줘" → 주제: "일상생활". 분류 가능한 예시: [일상생활/여가활동/사회활동/업무/학업/건강/복지/관계/경제활동/기술/IT/시사/정보] 중 선택.
- **의도 파악**: 사용자의 요구나 감정 상태를 반영하여 의도를 설정합니다.
  * 주요 의도: [정보 요청/의견 조언/감정 표현/행동 선언]
  * 세부 의도: [가격 문의/위치 확인/추천 요청/일정 확인/상태 확인] 등
  * 예: "강남역 맛집 추천" → 의도: "정보 요청".
- **핵심 키워드 추출**: 텍스트에서 중요한 키워드를 3~5개로 요약합니다.

2. 맥락 분석가
- **활동 유형**: 대화 속 행동이나 계획을 분석하여 분류합니다.
  * 주요 활동: [이동/식사/업무/여가/쇼핑/운동] 등 자유 기술
  * 부가 활동: 연계된 활동 자유 기술
  * 예: "퇴근 후 카페 가서 공부" → 활동 유형: "여가_학습".
- **시간 정보**: 명시적 또는 암시적인 시간 데이터를 추출합니다.
  * 명시적 시간: 구체적 시간/날짜 정보
  * 상대적 시간: 전/후 관계, 기간, 빈도
  * 맥락적 시간: 업무시간, 식사시간 등
  * 예: "내일 오후 3시" → 시간 요소: ["미래", "특정 시간"].
- **공간 정보**: 장소나 지역 정보를 구조화합니다.
  * 출발지/도착지, 경유지, 목적지 특성
  * 지역 정보 (국가/도시/장소)
  * 예: "강남역 근처" → 공간 요소: ["강남역", "주변 음식점"].
- **동반자 분석**: 대화의 참여자나 관계를 분석합니다. (혼자/가족/친구/직장/단체 등)
  * 예: "가족과 함께 영화 보기" → 동반자 요소: ["가족"].

3. 개인정보 분석가
- **개인 기본 정보**: 나이, 성별, 결혼 상태 등을 텍스트와 문맥에서 추출합니다.
  * 대화 내용에서 언급되거나 암시된 개인정보 추출
  * 추출 방식: [직접 언급(100), 문맥상 추론(80), 간접 추론(50)]
  * 대상 정보: [나이, 성별, 결혼상태, 취미, 선호도 등]
- **직업 정보**: 직장 및 직무 관련 데이터를 추출합니다.
  * 위치 관련 키워드 분석: ["회사", "직장", "근무", "출근", "퇴근"]
  * 업무 관련 키워드 분석: ["회의", "업무", "프로젝트", "동료"]
  * 근무 형태 분석: ["정규직", "계약직", "재택", "하이브리드"]
  * 추출 기준:
    - 위치 + 업무 키워드 조합 시 근무지로 추론
    - 이동 경로에서 출발/도착지와 업무 문맥 연관성 분석
    - 시간대와 활동 유형 기반 업무 관련성 판단
- **거주 정보**: 거주지, 주소, 거주 형태를 분석합니다.
  * 예: "강남에서 잠실 집까지" → 거주 정보: "잠실", "아파트 추정".
  * 위치 관련 키워드 분석: ["집", "자택", "거주", "이사", "동네"]
  * 주거 위치 분석: [도시-구-동] 형식으로 상세 주소
  * 주거 형태 키워드: ["아파트", "주택", "오피스텔", "원룸"]
  * 추출 기준:
    - 위치 + 거주 키워드 조합 시 거주지로 추론
    - 이동 경로에서 출발/도착지와 일상 문맥 연관성 분석
    - 시간대와 활동 유형 기반 거주지 관련성 판단
- 정보 신뢰도 평가:
  * 직접성: 명시적 언급(100), 문맥적 추론(80), 간접 추론(50)
  * 일관성: 이전 대화 내용과의 정합성
  * 최신성: 현재(100), 과거/예정(80), 불명확(50)

4. 감정/품질 평가자
- 감정 상태: 강도: 0-100
  * 유형: [긍정/부정/중립] 및 [기쁨/슬픔/분노/불안/기대/실망] 등 세부 감정
- 신뢰도 점수: 구체성(시간/장소/대상), 명확성(목적/방법) 평가
- 일관성 검증: 전체 분석 결과의 맥락적 정합성 확인

다음 JSON 형식으로만 응답하세요:
{{
    "대화 내용": "<input>",
    "메인 주제": "<topic>",
    "세부 주제": {{
        "활동 유형": [],
        "시간 요소": [],
        "공간 요소": [],
        "동반자": []
    }},
    "개인 정보": {{
        "기본 정보": {{
            "나이": null,
            "성별": null,
            "결혼상태": null,
            "추출_신뢰도": 0
        }},
        "가족 관계": {{
            "구성원": [],
            "가구_크기": null,
            "동거_여부": null,
            "추출_신뢰도": 0
        }},
        "직업 정보": {{
            "직장": {{
                "회사명": null,
                "업종": null,
                "근무지": null
            }},
            "직무": {{
                "직위": null,
                "역할": null,
                "경력기간": null
            }},
            "근무형태": null,
            "추출_신뢰도": 0
        }},
        "거주 정보": {{
            "주소": {{
                "도시": null,
                "동네": null,
                "상세주소": null
            }},
            "주거형태": null,
            "점유형태": null,
            "거주기간": null,
            "추출_신뢰도": 0
        }}
    }},
    "의도 분석": "<intent>",
    "키워드": [],
    "신뢰도 점수": <0-100>,
    "감정 상태": {{
        "유형": "<sentiment>",
        "강도": <0-100>,
        "세부감정": "<emotion>"
    }}
}}

분석 과정:
1. 각 전문가가 담당 영역 분석
2. 분석 결과 교차 검증
3. 통합된 최종 결과 생성

분석할 텍스트: {user_input}
현재 날짜: {current_date}
"""

            logger.debug(f"생성된 프롬프트:\n{template}")
            return template
        except Exception as e:
            logger.error(f"프롬프트 템플릿 생성 중 오류 발생: {str(e)}")
            raise

    @lru_cache(maxsize=1000)
    async def _call_llm(self, prompt: str) -> str:
        """LLM API 호출"""
        try:
            logger.debug(f"LLM API 호출 시작\n프롬프트:\n{prompt}")
            response = await self.client.chat.completions.create(
                model="openai/gpt-4o-mini-2024-07-18",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI analyst that extracts structured information from user input."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=2048,
                response_format={"type": "json_object"}  # JSON 모드 활성화
            )
            result = response.choices[0].message.content
            logger.info(f"LLM 응답 결과:\n{result}")
            return result
        except Exception as e:
            logger.error(f"LLM API 호출 중 오류 발생: {str(e)}")
            raise

    async def analyze_conversation(
        self,
        user_input: str,
        current_date: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        대화 분석 실행
        Args:
            user_input: 사용자 입력 텍스트
            current_date: 현재 날짜 (선택)
            context: 이전 대화 컨텍스트 (선택)
        Returns:
            분석 결과를 포함한 딕셔너리
        """
        try:
            logger.info("대화 분석 시작")
            logger.info(f"입력 텍스트: {user_input}")
            logger.info(f"컨텍스트 존재 여부: {'있음' if context else '없음'}")

            # 컨텍스트 처리 및 우선순위화
            processed_context = self.context_processor.process_context(
                user_input, 
                self.conversation_history
            )
            logger.info(f"context: {context}")
            logger.info(f"processed_context: {processed_context}")

            prioritized_context = self.context_prioritizer.prioritize_contexts(
                processed_context, 
                self.conversation_history
            )
            logger.info(f"prioritized_context: {prioritized_context}")

            # 현재 컨텍스트 설정
            if context:
                self.current_context = context
            elif self.conversation_history:
                self.current_context = self.conversation_history[-1]["analysis"]

            if not current_date:
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"분석 기준 날짜: {current_date}")

            # 프롬프트 생성
            logger.info("프롬프트 생성 시작")
            prompt = self._create_analysis_prompt().format(
                user_input=user_input,
                current_date=current_date
            )
            logger.info("프롬프트 생성 완료")

            # LLM 호출
            logger.info("LLM API 호출 시작")
            raw_analysis = await self._call_llm(prompt)
            logger.debug("LLM 응답 결과:")
            logger.debug("-" * 30)
            logger.debug(raw_analysis)
            logger.debug("-" * 30)
            logger.info("LLM API 호출 완료")

            # 결과 파싱 및 구조화
            logger.info("응답 파싱 시작")
            parsed_analysis = self.text_parser.parse_llm_response(raw_analysis)
            logger.info(f"파싱된 결과:\n{json.dumps(parsed_analysis, indent=2, ensure_ascii=False)}")
            logger.info("응답 파싱 완료")

            # 응답 생성
            response = await self.response_generator.generate_response(
                user_input,
                parsed_analysis,
                processed_context
            )
            logger.info(f"generate_response: {response}")

            # 대화 흐름 상태 업데이트
            self.flow_manager.update_state(
                user_input, 
                parsed_analysis, 
                response
            )
            logger.info(f"flow_state: {self.flow_manager.get_current_state()}")

            # 분석 결과 저장
            logger.info("분석 결과 저장 시작")
            analysis_record = {
                "timestamp": current_date,
                "input": user_input,
                "analysis": parsed_analysis,
                "context": context
            }
            self.conversation_history.append(analysis_record)
            logger.info(f"대화 히스토리 개수: {len(self.conversation_history)}")
            logger.info("분석 결과 저장 완료")

            # 사용자 프로필 업데이트
            logger.info("사용자 프로필 업데이트 시작")
            if "개인 정보" in parsed_analysis:
                logger.debug(f"추출된 개인 정보: {json.dumps(parsed_analysis['개인 정보'], indent=2, ensure_ascii=False)}")
            self.user_profile.update_from_analysis(parsed_analysis)
            logger.info("사용자 프로필 업데이트 완료")
            logger.info(f"업데이트된 프로필: {json.dumps(self.user_profile.get_profile(), ensure_ascii=False)}")

            # 최종 응답 생성
            response = {
                "timestamp": current_date,
                "input": user_input,
                "analysis_result": parsed_analysis,
                "user_profile": self.user_profile.get_profile(),
                "recommendations": self._generate_recommendations(parsed_analysis),
                "insights": self._generate_insights(parsed_analysis)
            }

            logger.info("대화 분석 완료")
            return response

        except Exception as e:
            logger.error(f"Error in analyze_conversation: {str(e)}")
            return self._generate_error_response()

    def _generate_recommendations(self, analysis: Dict) -> Dict:
        """추천 생성"""
        domain = self._map_analysis_to_domain(analysis)
        return {
            "suggested_actions": self.user_profile.get_suggested_actions(domain),
            "related_topics": self.user_profile.get_related_topics(domain),
            "personalized_suggestions": self.user_profile.get_personalized_suggestions(domain)
        }

    def _map_analysis_to_domain(self, analysis: Dict) -> str:
        """분석 결과를 도메인으로 매핑"""
        try:
            main_topic = analysis.get("main_topic", "unknown")
            return DomainMapper.map_topic_to_domain(main_topic)
        except Exception as e:
            logger.error(f"Error mapping analysis to domain: {str(e)}")
            return Domain.UNKNOWN.value

    def _generate_insights(self, analysis: Dict) -> Dict:
        """인사이트 생성"""
        return {
            "patterns": self.user_profile.analyze_patterns(),
            "trends": self.user_profile.analyze_trends(),
            "notable_changes": self.user_profile.detect_changes()
        }

    def _generate_error_response(self) -> Dict:
        """에러 응답 생성"""
        return {
            "analysis_result": {},
            "user_profile": {},
            "recommendations": {
                "suggested_actions": [],
                "related_topics": [],
                "personalized_suggestions": []
            },
            "insights": {
                "patterns": {},
                "trends": {},
                "notable_changes": {}
            }
        }

    def get_user_profile(self) -> Dict:
        """현재 사용자 프로필 반환"""
        return self.user_profile.get_profile()

    def get_conversation_history(self) -> List[Dict]:
        """대화 히스토리 반환"""
        return self.conversation_history
