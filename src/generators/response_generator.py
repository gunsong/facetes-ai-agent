from typing import Callable, Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)

class ResponseGenerator:
    """범용 AI Agent를 위한 응답 생성 클래스"""

    def __init__(self):
        self.required_info = {
            'recommendation': ['target', 'preference'],
            'information': ['subject', 'context'],
            'action': ['task', 'parameters'],
            'analysis': ['target', 'criteria'],
            'general': ['intent']
        }

        self.domain_patterns = {
            'tech': ['개발', '프로그래밍', 'AI', '기술', '코드'],
            'business': ['비즈니스', '마케팅', '전략', '기획'],
            'research': ['분석', '연구', '조사', '데이터'],
            'general': ['정보', '추천', '방법', '설명']
        }

    async def generate_response(self, query: str, analysis_result: Dict, context: Dict) -> str:
        """컨텍스트 기반 응답 생성"""
        try:
            # 도메인 및 의도 분석
            domain = self._analyze_domain(query, analysis_result)
            query_type = self._analyze_query_type(query, analysis_result)
            intent_info = self._analyze_intent(analysis_result.get('intent', {}))

            logger.info(f"Domain: {domain}, Query type: {query_type}, Intent: {intent_info}")

            # 컨텍스트 연관성 확인
            context_relation = self._analyze_context_relation(analysis_result, context)

            # 도메인별 특화 처리
            if domain_handler := self._get_domain_handler(domain):
                # 비동기 함수 호출 제거
                return domain_handler(query_type, analysis_result, context, context_relation)

            # 기본 응답 생성 로직
            missing_info = self._check_required_info(query_type, context, analysis_result)

            if missing_info:
                return self._generate_clarification_request(
                    query_type,
                    missing_info,
                    context,
                    analysis_result,
                    context_relation
                )

            if context_relation.get('related_activity'):
                return self._generate_activity_related_response(
                    query_type,
                    analysis_result,
                    context,
                    context_relation
                )

            return self._generate_standard_response(
                query_type,
                analysis_result,
                context
            )

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "응답 생성 중 오류가 발생했습니다."

    def _analyze_intent(self, intent: Union[Dict, str]) -> Dict:
        """의도 상세 분석"""
        try:
            if isinstance(intent, dict):
                intent_type = intent.get('유형', '')
                return {
                    'type': str(intent_type),  # 문자열로 변환
                    'subtype': str(intent.get('세부 유형', '')),  # 문자열로 변환
                    'context': str(intent.get('컨텍스트', '')),  # 딕셔너리를 문자열로 변환
                    'activity_related': '여가' in intent_type or '활동' in intent_type
                }
            return {
                'type': str(intent),
                'subtype': '',
                'context': '',
                'activity_related': '여가' in str(intent) or '활동' in str(intent)
            }
        except Exception as e:
            logger.error(f"Error analyzing intent: {str(e)}")
            return {'type': '', 'subtype': '', 'context': '', 'activity_related': False}

    def _analyze_context_relation(self, current: Dict, context: Dict) -> Dict:
        """컨텍스트 연관성 분석"""
        try:
            recent_topics = context.get('topic', {}).get('data', {}).get('recent_topics', [])
            recent_locations = context.get('location', {}).get('data', {}).get('recent_locations', [])
            recent_activities = context.get('topic', {}).get('data', {}).get('activities', [])

            # 활동 연관성 확인
            related_activity = None
            if '여가활동' in recent_topics or any('여가' in act for act in recent_activities):
                related_activity = {
                    'type': '여가활동',
                    'location': self._extract_location(recent_locations),
                    'details': str(context.get('topic', {}).get('data', {}).get('details', ''))  # 문자열로 변환
                }

            return {
                'related_activity': related_activity,
                'shared_location': bool(set(current.get('sub_topics', {}).get('spatial', [])) & set(recent_locations)),
                'temporal_overlap': bool(set(current.get('sub_topics', {}).get('temporal', [])) & set(context.get('temporal', {}).get('data', {}).get('recent_temporal', [])))
            }
        except Exception as e:
            logger.error(f"Error analyzing context relation: {str(e)}")
            return {}

    def _check_required_info(self, query_type: str, context: Dict, analysis_result: Dict) -> List[str]:
        """필수 정보 체크"""
        try:
            if query_type not in self.required_info:
                return []

            missing = []
            for info in self.required_info[query_type]:
                if not self._has_required_info(info, context, analysis_result):
                    missing.append(info)

            return missing

        except Exception as e:
            logger.error(f"Error checking required info: {str(e)}")
            return []

    def _has_required_info(self, info_type: str, context: Dict, analysis_result: Dict) -> bool:
        """필수 정보 존재 여부 확인"""
        try:
            if info_type == 'target':
                return bool(analysis_result.get('sub_topics', {}).get('target'))
            elif info_type == 'preference':
                return bool(analysis_result.get('sub_topics', {}).get('preferences'))
            elif info_type == 'subject':
                return bool(analysis_result.get('main_topic'))
            elif info_type == 'context':
                return bool(context.get('topic', {}).get('data', {}))
            elif info_type == 'task':
                return bool(analysis_result.get('sub_topics', {}).get('task'))
            elif info_type == 'parameters':
                return bool(analysis_result.get('sub_topics', {}).get('parameters'))
            elif info_type == 'criteria':
                return bool(analysis_result.get('sub_topics', {}).get('criteria'))
            return False
        except Exception as e:
            logger.error(f"Error checking required info existence: {str(e)}")
            return False

    def _generate_clarification_request(
        self,
        query_type: str,
        missing_info: List[str],
        context: Dict,
        analysis_result: Dict,
        context_relation: Dict
    ) -> str:
        """명확화 요청 생성"""
        try:
            if query_type == 'recommendation':
                if 'location' in missing_info:
                    # 분석 결과에서 위치 정보 확인
                    spatial_info = analysis_result.get('sub_topics', {}).get('spatial', [])
                    if spatial_info:
                        logger.info(f"spatial_info: {spatial_info}")
                        return f"{spatial_info[0]} 근처에서 찾아보시는 건가요? 아니면 다른 지역을 알려주시겠어요?"

                    # 컨텍스트에서 최근 위치 확인
                    recent_locations = context.get('location', {}).get('data', {}).get('recent_locations', [])
                    if recent_locations:
                        logger.info(f"recent_locations: {recent_locations}")
                        # 연관된 활동이 있는 경우
                        if context_relation.get('related_activity'):
                            activity = context_relation['related_activity']
                            logger.info(f"activity: {activity}")
                            return f"{recent_locations[0]} 근처에서 {activity['type']}과 관련하여 찾아보시는 건가요?"
                        return f"{recent_locations[0]} 근처에서 찾아보시는 건가요?"

                    return "어느 지역에서 찾아보시겠어요?"

            elif query_type == 'information':
                if 'time' in missing_info:
                    temporal_info = analysis_result.get('sub_topics', {}).get('temporal', [])
                    if temporal_info:
                        logger.info(f"temporal_info: {temporal_info}")
                        return f"{temporal_info[0]}를 기준으로 알려드릴까요?"

                    if context_relation.get('related_activity'):
                        activity = context_relation['related_activity']
                        logger.info(f"activity: {activity}")
                        temporal = activity.get('details', {}).get('temporal')
                        if temporal:
                            logger.info(f"temporal: {temporal}")
                            return f"{temporal[0]} 기준으로 알려드릴까요?"

                    return "언제를 기준으로 알려드릴까요?"

            return "더 자세한 정보를 알려주시겠어요?"

        except Exception as e:
            logger.error(f"Error generating clarification request: {str(e)}")
            return "죄송합니다. 질문을 더 자세히 해주시겠어요?"

    def _generate_business_recommendation(self, analysis: Dict, context: Dict) -> str:
        """비즈니스 추천 응답 생성"""
        try:
            target = analysis.get('sub_topics', {}).get('target', [''])[0]
            preferences = analysis.get('sub_topics', {}).get('preferences', [])

            if preferences:
                return f"{target}와 관련하여 {', '.join(preferences)} 특성을 고려한 추천을 제공하겠습니다."
            return f"{target}에 대한 비즈니스 추천을 제공하겠습니다."
        except Exception as e:
            logger.error(f"Error generating business recommendation: {str(e)}")
            return "비즈니스 추천 생성 중 오류가 발생했습니다."

    def _generate_research_recommendation(self, analysis: Dict, context: Dict) -> str:
        """연구 추천 응답 생성"""
        try:
            target = analysis.get('sub_topics', {}).get('target', [''])[0]
            preferences = analysis.get('sub_topics', {}).get('preferences', [])

            if preferences:
                return f"{target} 연구와 관련하여 {', '.join(preferences)} 방향의 추천을 제공하겠습니다."
            return f"{target}에 대한 연구 방향을 추천하겠습니다."
        except Exception as e:
            logger.error(f"Error generating research recommendation: {str(e)}")
            return "연구 추천 생성 중 오류가 발생했습니다."

    def _generate_tech_recommendation(self, analysis: Dict, context: Dict) -> str:
        """기술 추천 응답 생성"""
        try:
            target = analysis.get('sub_topics', {}).get('target', [''])[0]
            preferences = analysis.get('sub_topics', {}).get('preferences', [])

            if preferences:
                return f"{target} 기술과 관련하여 {', '.join(preferences)} 특성을 고려한 추천을 제공하겠습니다."
            return f"{target}에 대한 기술 추천을 제공하겠습니다."
        except Exception as e:
            logger.error(f"Error generating tech recommendation: {str(e)}")
            return "기술 추천 생성 중 오류가 발생했습니다."

    def _analyze_domain(self, query: str, analysis_result: Dict) -> str:
        """도메인 분석"""
        try:
            keywords = analysis_result.get('keywords', [])
            main_topic = analysis_result.get('main_topic', '')

            # 도메인 패턴 매칭
            for domain, patterns in self.domain_patterns.items():
                if any(pattern in query for pattern in patterns) or \
                any(pattern in main_topic for pattern in patterns) or \
                any(any(pattern in keyword for pattern in patterns) for keyword in keywords):
                    return domain

            return 'general'

        except Exception as e:
            logger.error(f"Error analyzing domain: {str(e)}")
            return 'general'

    def _extract_location(self, locations: List[str]) -> Optional[str]:
        """위치 정보 추출 및 정제"""
        try:
            for loc in locations:
                if '국내' in loc:
                    return loc.split('국내(')[1].rstrip(')')
            return None
        except Exception as e:
            logger.error(f"Error extracting location: {str(e)}")
            return None

    def _analyze_query_type(self, query: str, analysis_result: Dict) -> str:
        """쿼리 타입 분석"""
        try:
            # 키워드 기반 분석
            keywords = analysis_result.get('keywords', [])
            if '날씨' in keywords:
                return 'information'
            if '추천' in keywords:
                return 'recommendation'

            # 분석 결과의 의도를 확인
            intent = analysis_result.get('intent', '')
            if intent:
                if '추천' in intent:
                    return 'recommendation'
                elif '정보' in intent or '문의' in intent:
                    return 'information'
                elif '위치' in intent:
                    return 'location'

            # 쿼리 패턴 분석
            query_patterns = {
                'recommendation': ['추천', '알려줘', '좋은곳'],
                'information': ['어때', '알려줘', '어떻게'],
                'location': ['어디', '가는길', '위치']
            }

            for query_type, patterns in query_patterns.items():
                if any(pattern in query for pattern in patterns):
                    return query_type

            return 'general'

        except Exception as e:
            logger.error(f"Error analyzing query type: {str(e)}")
            return 'general'

    def _get_domain_handler(self, domain: str) -> Optional[Callable]:
        """도메인별 핸들러 반환"""
        try:
            domain_handlers = {
                'tech': self._handle_tech_domain,
                'business': self._handle_business_domain,
                'research': self._handle_research_domain
            }
            return domain_handlers.get(domain)
        except Exception as e:
            logger.error(f"Error getting domain handler: {str(e)}")
            return None

    def _generate_activity_related_response(
        self,
        query_type: str,
        analysis: Dict,
        context: Dict,
        relation: Dict
    ) -> str:
        """활동 연관 응답 생성"""
        try:
            # 위치 정보 추출
            location = self._extract_specific_location(analysis, context)

            # 활동 정보 추출
            activity = relation.get('related_activity', {})
            activity_type = activity.get('type', '')
            activity_details = activity.get('details', {})

            if query_type == 'information':
                # 날씨 관련 질의인 경우
                if '날씨' in analysis.get('keywords', []):
                    temporal_info = analysis.get('sub_topics', {}).get('temporal', [])
                    time_str = f"{temporal_info[0]} " if temporal_info else ""

                    return (
                        f"{location} 지역의 {time_str}날씨를 알려드리겠습니다. "
                        f"특히 {activity_type} 계획과 관련하여 "
                        f"활동 가능 여부도 함께 안내해드리겠습니다."
                    )

            elif query_type == 'recommendation':
                # 추천 관련 질의인 경우
                if activity_type:
                    return (
                        f"{location} 근처에서 {activity_type}과 관련된 "
                        f"추천 정보를 알려드리겠습니다."
                    )

            return self._generate_standard_response(query_type, analysis, context)

        except Exception as e:
            logger.error(f"Error generating activity related response: {str(e)}")
            return self._generate_standard_response(query_type, analysis, context)

    def _generate_standard_response(
        self,
        query_type: str,
        analysis: Dict,
        context: Dict
    ) -> str:
        """기본 응답 생성"""
        try:
            if query_type == 'recommendation':
                spatial_info = analysis.get('sub_topics', {}).get('spatial', [])
                location = spatial_info[0] if spatial_info else \
                        context.get('location', {}).get('data', {}).get('recent_locations', [''])[0]

                activities = analysis.get('sub_topics', {}).get('activities', [])
                activity_str = f"{', '.join(activities)} 관련한" if activities else ""

                return f"{location}의 {activity_str} 추천 정보를 알려드리겠습니다."

            elif query_type == 'information':
                main_topic = analysis.get('main_topic', '')
                temporal_info = analysis.get('sub_topics', {}).get('temporal', [])
                spatial_info = analysis.get('sub_topics', {}).get('spatial', [])

                location_str = f"{spatial_info[0]} 지역의 " if spatial_info else ""
                temporal_str = f"{temporal_info[0]} 기준" if temporal_info else ""

                return f"{location_str}{temporal_str} {main_topic} 정보를 알려드리겠습니다."

            return "알겠습니다. 도움이 필요하신가요?"

        except Exception as e:
            logger.error(f"Error generating standard response: {str(e)}")
            return "죄송합니다. 다시 한 번 말씀해 주시겠어요?"

    def _handle_tech_domain(
        self,
        query_type: str,
        analysis: Dict,
        context: Dict,
        context_relation: Dict
    ) -> str:
        """기술 도메인 처리"""
        try:
            if query_type == 'analysis':
                return self._generate_tech_analysis_response(analysis, context)
            elif query_type == 'recommendation':
                return self._generate_tech_recommendation(analysis, context)
            return self._generate_standard_response(query_type, analysis, context)
        except Exception as e:
            logger.error(f"Error handling tech domain: {str(e)}")
            return self._generate_standard_response(query_type, analysis, context)

    def _handle_business_domain(
        self,
        query_type: str,
        analysis: Dict,
        context: Dict,
        context_relation: Dict
    ) -> str:
        """비즈니스 도메인 처리"""
        try:
            if query_type == 'analysis':
                return self._generate_business_analysis_response(analysis, context)
            elif query_type == 'recommendation':
                return self._generate_business_recommendation(analysis, context)
            return self._generate_standard_response(query_type, analysis, context)
        except Exception as e:
            logger.error(f"Error handling business domain: {str(e)}")
            return self._generate_standard_response(query_type, analysis, context)

    def _handle_research_domain(
        self,
        query_type: str,
        analysis: Dict,
        context: Dict,
        context_relation: Dict
    ) -> str:
        """연구 도메인 처리"""
        try:
            if query_type == 'analysis':
                return self._generate_research_analysis_response(analysis, context)
            elif query_type == 'recommendation':
                return self._generate_research_recommendation(analysis, context)
            return self._generate_standard_response(query_type, analysis, context)
        except Exception as e:
            logger.error(f"Error handling research domain: {str(e)}")
            return self._generate_standard_response(query_type, analysis, context)

    def _generate_tech_analysis_response(self, analysis: Dict, context: Dict) -> str:
        """기술 분석 응답 생성"""
        try:
            target = analysis.get('sub_topics', {}).get('target', [''])[0]
            criteria = analysis.get('sub_topics', {}).get('criteria', [])
            tech_stack = analysis.get('sub_topics', {}).get('tech_stack', [])

            response = f"{target}에 대한 기술 분석을 진행하겠습니다.\n"
            if criteria:
                response += f"분석 기준: {', '.join(criteria)}\n"
            if tech_stack:
                response += f"관련 기술 스택: {', '.join(tech_stack)}"
            return response
        except Exception as e:
            logger.error(f"Error generating tech analysis response: {str(e)}")
            return "기술 분석 중 오류가 발생했습니다."

    def _generate_business_analysis_response(self, analysis: Dict, context: Dict) -> str:
        """비즈니스 분석 응답 생성"""
        try:
            target = analysis.get('sub_topics', {}).get('target', [''])[0]
            criteria = analysis.get('sub_topics', {}).get('criteria', [])
            return f"{target}에 대한 비즈니스 분석을 진행하겠습니다. " \
                f"분석 기준: {', '.join(criteria)}"
        except Exception as e:
            logger.error(f"Error generating business analysis response: {str(e)}")
            return "비즈니스 분석 중 오류가 발생했습니다."

    def _generate_research_analysis_response(self, analysis: Dict, context: Dict) -> str:
        """연구 분석 응답 생성"""
        try:
            target = analysis.get('sub_topics', {}).get('target', [''])[0]
            criteria = analysis.get('sub_topics', {}).get('criteria', [])
            methodology = analysis.get('sub_topics', {}).get('methodology', [])

            response = f"{target}에 대한 연구 분석을 진행하겠습니다.\n"
            if criteria:
                response += f"분석 기준: {', '.join(criteria)}\n"
            if methodology:
                response += f"연구 방법론: {', '.join(methodology)}"
            return response
        except Exception as e:
            logger.error(f"Error generating research analysis response: {str(e)}")
            return "연구 분석 중 오류가 발생했습니다."

    def _extract_specific_location(self, analysis: Dict, context: Dict) -> str:
        """구체적 위치 정보 추출"""
        try:
            # 현재 분석에서 구체적 위치 확인
            spatial_info = analysis.get('sub_topics', {}).get('spatial', [])
            for loc in spatial_info:
                if '국내(' in loc:
                    return loc.split('국내(')[1].rstrip(')')

            # 컨텍스트에서 구체적 위치 확인
            recent_locations = context.get('location', {}).get('data', {}).get('recent_locations', [])
            for loc in recent_locations:
                if '국내(' in loc:
                    return loc.split('국내(')[1].rstrip(')')

            # 일반적 위치 정보 반환
            return next(
                (loc for loc in spatial_info),
                next((loc for loc in recent_locations), '서울')
            )

        except Exception as e:
            logger.error(f"Error extracting specific location: {str(e)}")
            return '서울'
