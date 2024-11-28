import json
from datetime import datetime
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
        template = """
당신은 사용자의 입력을 분석하여 구조화된 정보를 추출하는 AI 분석가입니다.

1. 분석 기준:
* 모든 응답은 JSON 변환 가능한 구조로 제공
* 각 항목은 명확한 카테고리로 분류
* 불확실한 경우 가장 관련성 높은 항목 선택

2. 필수 분석 항목:
* **대화 내용**: [원문]
* **메인 주제**: [아래 분류 중 1개만 필수 선택]
	- 일상생활: 식사, 수면, 휴식, 집안일
	- 여가활동: 취미, 운동, 여행, 문화생활
	- 사회활동: 모임, 봉사, 종교활동, 지역활동
	- 업무/학업: 직장, 학교, 자기개발, 연구
	- 건강/복지: 의료, 운동, 심리, 복지서비스
	- 관계: 가족, 친구, 동료, 연인 관계
	- 경제활동: 소비, 투자, 재테크, 쇼핑
	- 기술/IT: 기기, 소프트웨어, 디지털 서비스
	- 시사/정보: 뉴스, 정보 검색, 시사 이슈
	- 기타: 위 카테고리에 명확히 속하지 않는 주제

* **세부 주제**: [관련 항목 모두 선택하여 배열로 반환]
  1. 활동 유형: [배열]
     - 여가_취미: 독서, 게임, 예술활동
     - 여가_운동: 실내운동, 야외운동, 스포츠
     - 여가_여행: 국내여행, 해외여행, 당일치기
     - 여가_문화: 영화, 공연, 전시, 축제
     - 업무_회의: 대면회의, 화상회의, 미팅
     - 업무_업무: 프로젝트, 보고, 발표
     - 업무_교육: 강의, 세미나, 워크샵
     - 학습_공부: 자격증, 어학, 전공
     - 학습_연구: 논문, 실험, 조사
     - 건강_운동: 헬스, 요가, 필라테스
     - 건강_치료: 병원, 한의원, 치료
     - 건강_관리: 식단, 영양, 생활습관
     - 휴식_수면: 취침, 낮잠, 숙면
     - 휴식_휴식: 휴식, 명상, 산책
     - 사교_모임: 친목모임, 동호회, 동창회
     - 사교_가족: 가족모임, 기념일, 행사
     - 사교_데이트: 연인, 미팅, 소개팅

  2. 시간 요소: [배열]
     - 시점: 과거, 현재, 미래
     - 기간: 단기, 중기, 장기
     - 빈도: 일회성, 정기적, 비정기적
     - 시간대: 아침, 오전, 오후, 저녁, 심야
     - 요일: 평일, 주말, 공휴일
     - 계절: 봄, 여름, 가을, 겨울

  3. 공간 요소: [배열]
     - 실내: 집, 사무실, 상업시설, 공공시설
     - 실외: 공원, 거리, 광장, 자연
     - 온라인: 화상, 메타버스, 온라인플랫폼
     - 지역: 국내(시/도), 해외(국가)
      * 국내: 구체적 도시/지역명 포함 (예: 국내(서울), 국내(부산), 국내(속초), 국내(판교), 국내(강남))
      * 해외: 국가명/도시명 포함 (예: 해외(일본), 해외(프랑스), 해외(도쿄), 해외(파리))
     - 이동: 도보, 대중교통, 자가용, 기타

  4. 동반자: [배열]
     - 혼자: 개인활동
     - 가족: 부모, 배우자, 자녀, 친척
     - 친구: 친구, 동창, 지인
     - 직장: 상사, 동료, 부하직원
     - 단체: 동호회, 모임, 팀

* **의도 분석**: [아래 분류 중 1개만 필수 선택]
  1. 정보 요청 (Information Request)
     - 사실정보: 객관적 정보 문의
     - 방법절차: 프로세스/방법 문의
     - 상태확인: 현황/진행상태 확인
     - 위치문의: 장소/경로 문의
     - 시간문의: 일정/기간 문의

  2. 의견/조언 요청 (Opinion/Advice)
     - 개인의견: 주관적 견해 요청
     - 전문조언: 전문적 조언 요청
     - 추천요청: 선택지 추천 요청
     - 결정지원: 의사결정 도움 요청

  3. 감정/태도 표현 (Emotional/Attitude)
     - 긍정감정: 기쁨, 만족, 기대
     - 부정감정: 불만, 걱정, 분노
     - 중립태도: 관찰, 서술, 중립
     - 의지표명: 결심, 다짐, 약속

  4. 행동 선언 (Action)
     - 계획선언: 향후 계획 언급
     - 결정통보: 의사결정 전달
     - 변경알림: 기존 내용 변경
     - 수행보고: 행동 완료 보고

* **키워드**: [핵심 단어 3-5개 배열로 반환]

* **신뢰도 점수**: [0-100점]
  - 구체성: 시간(+20), 장소(+20), 대상(+20)
  - 명확성: 목적(+20), 방법(+20)
  - 감점: 모호한 표현당 -10점

* **감정 상태**: [객체로 반환]
  - 유형: [긍정/부정/중립] 중 1개
  - 강도: 0-100점
  - 세부감정: [기쁨/슬픔/분노/불안/기대/실망] 중 1개

3. 응답 형식:
  - 모든 분석 결과는 JSON 구조로 변환 가능하게 작성
  - 각 항목은 명시된 형식(문자열/배열/객체)으로 반환
  - 날짜는 YYYY-MM-DD, 시간은 HH:MM 형식 사용

분석할 텍스트: {user_input}
현재 날짜: {current_date}
"""
        return template

    async def _call_llm(self, prompt: str) -> str:
        """LLM API 호출"""
        try:
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
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in _call_llm: {str(e)}")
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
            logger.info("LLM 응답 결과:")
            logger.info("-" * 30)
            logger.info(raw_analysis)
            logger.info("-" * 30)
            logger.info("LLM API 호출 완료")

            # 결과 파싱 및 구조화
            logger.info("답 파싱 시작")
            parsed_analysis = self.text_parser.parse_llm_response(raw_analysis)
            logger.info(f"파싱된 결과:\n{json.dumps(parsed_analysis, indent=2, ensure_ascii=False)}")
            logger.info("답 파싱 완료")

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
            self.user_profile.update_from_analysis(parsed_analysis)
            logger.info("사용자 프로필 업데이트 완료")

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
