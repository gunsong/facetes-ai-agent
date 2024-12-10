from typing import Dict, List

from facets.user_profile import UserProfile
from utils.logger import get_logger

logger = get_logger(__name__)

class PromptGenerator:
    """프롬프트 생성 클래스"""

    def __init__(self, user_profile: UserProfile):
        self.user_profile = user_profile

        """프롬프트 템플릿 초기화"""
        self.templates = {
            "enhanced": """
You are analyzing a conversation in Korean. Review the following information carefully:

{context_info}

Your role is to act as a Korean conversation specialist. Generate responses that combine natural conversation flow with precise information delivery. Focus on providing contextually relevant and helpful information while maintaining a professional yet approachable tone.

When crafting your response:
First, analyze the historical context, giving it 30% consideration weight. Focus primarily on the current query (50% weight), while also anticipating potential future needs (20% weight).

Build your response by:
1. Starting with the most immediately relevant information
2. Naturally incorporating contextual details
3. Adding valuable insights when appropriate
4. Maintaining conversation flow
5. Using natural, conversational Korean

If you need to resolve ambiguity:
1. First check the most recent context
2. Then apply known user preferences
3. Consider standard assumptions only as a last resort
4. Confirm critical assumptions in a natural way

Remember to:
- Write in natural, conversational Korean
- Match the user's formality level
- Include English terms only when they add value
- Provide specific, actionable information

A good response should:
- Directly address the query
- Include relevant context
- Offer helpful insights
- Suggest next steps when appropriate

For example:
Instead of "The weather is 20 degrees" (too basic),
Say "It's sunny in Bangkok now, 30 degrees. Perfect for sightseeing, though you might want to visit indoor attractions in the afternoon when it gets hotter."

Your response will be evaluated on:
- Accuracy of information
- Contextual relevance
- Natural conversation flow
- Practical value to the user
""",
            "suggestion_query": """
You are generating follow-up questions for a Korean conversation. Review the provided context:

Current Query: {current_input}

Previous Interactions:
{reference_conversations}

Available Context:
{context_data}

User Information:
Consider their profile ({user_profile}), location ({location_context}), and temporal context ({temporal_context})

Your task is to generate natural follow-up questions that deepen the conversation. Create two types of questions:

For immediate clarification:
1. Focus directly on the current topic
2. Address missing but important details
3. Help understand specific preferences
4. Consider time and location context

For exploration:
1. Connect with previous conversation topics
2. Explore related interests
3. Consider user's demonstrated patterns
4. Maintain natural flow

When creating questions:
- Use open-ended formats that encourage detailed responses
- Keep questions relevant to both current and previous context
- Avoid simple yes/no questions
- Make each question focused and specific

Craft your questions in natural Korean, matching the user's style and formality level. Consider domain-specific aspects:
- For technical topics, focus on environment and specifications
- For business queries, consider scale and participation
- For research topics, explore methodology and objectives

Structure follow-up questions to:
1. Clarify core information
2. Explore related topics
3. Verify understanding
4. Plan next steps

Remember: Good questions lead to meaningful responses that help better understand the user's needs.
"""
        }

    def create_enhanced_prompt(self, current: Dict, similar: List[Dict]) -> str:
        """컨텍스트 기반 향상된 프롬프트 생성"""
        try:
            logger.debug(f"Creating enhanced prompt for input: {current.get('input', '')}")

            # 컨텍스트 정보 추출 및 구조화
            context_info = self._build_context_information(current, similar)
            logger.info(f"Generated context information: {context_info}")

            return self.templates["enhanced"].format(
                current_input=current.get("input", ""),
                context_info=context_info
            )
        except Exception as e:
            logger.error(f"Error creating enhanced prompt: {str(e)}")
            return ""

    def _build_context_information(self, current: Dict, similar: List[Dict]) -> str:
        """컨텍스트 정보 구조화"""
        try:
            personal_context = self._get_personal_info_context()

            return f"""
The user has just asked: {current.get("input", "")}

User Profile Information:
{personal_context}

Examine the conversation history to understand context:
{self._format_reference_conversations(similar)}

Consider these contextual elements:
{self._format_context_data(similar)}

Understand the user's background:
Their interests include {self._extract_user_interests(similar)}
Their typical behavior patterns show {self._extract_user_patterns(similar)}

Let's look at their spatial context:
They have recently visited {self._extract_location_context(similar)}
I notice they frequently spend time in {self._extract_frequent_locations(similar)}

Regarding temporal patterns:
At this moment, {self._extract_current_temporal(similar)}
Looking at their history, {self._extract_temporal_patterns(similar)}
"""
        except Exception as e:
            logger.error(f"Error building context information: {str(e)}")
            return ""

    def create_suggestion_query_prompt(self, current: Dict, similar: List[Dict]) -> str:
        """새로운 질의 생성 프롬프트"""
        try:
            logger.debug(f"Creating new query prompt for input: {current.get('input', '')}")
            user_profile = self._extract_user_profile(similar)
            location_context = self._extract_location_context(similar)
            temporal_context = self._extract_temporal_context(similar)

            return self.templates["suggestion_query"].format(
                current_input=current.get("input", ""),
                reference_conversations=self._format_reference_conversations(similar),
                context_data=self._format_context_data(similar),
                user_profile=user_profile,
                location_context=location_context,
                temporal_context=temporal_context
            )
        except Exception as e:
            logger.error(f"Error creating new query prompt: {str(e)}")
            return ""

    def _format_reference_conversations(self, conversations: List[Dict]) -> str:
        """참조 대화 포맷팅"""
        try:
            formatted_convs = []
            for conv in conversations:
                timestamp = conv.get("timestamp", "")
                user_input = conv.get("input", "")
                if timestamp and user_input:
                    formatted_convs.append(f"- {timestamp}: {user_input}")
            return "\n".join(formatted_convs)
        except Exception as e:
            logger.error(f"Error formatting reference conversations: {str(e)}")
            return ""

    def _format_context_data(self, conversations: List[Dict]) -> str:
        """컨텍스트 데이터 포맷팅"""
        try:
            context_data = []
            for conv in conversations:
                analysis = conv.get("analysis", {})
                if not analysis:
                    continue

                context_entry = [f"- Topic: {analysis.get('main_topic', 'unknown')}"]

                if "keywords" in analysis:
                    context_entry.append(f"  Keywords: {', '.join(analysis['keywords'])}")

                intent = analysis.get("intent", {})
                if isinstance(intent, dict):
                    intent_str = intent.get("유형", str(intent))
                else:
                    intent_str = str(intent)
                context_entry.append(f"  Intent: {intent_str}")

                context_data.append("\n".join(context_entry))

            return "\n".join(context_data)
        except Exception as e:
            logger.error(f"Error formatting context data: {str(e)}")
            return ""

    def _extract_user_profile(self, conversations: List[Dict]) -> str:
        """사용자 프로필 정보 추출"""
        try:
            interests = []
            patterns = []

            for conv in conversations:
                analysis = conv.get("analysis", {})
                if "main_topic" in analysis:
                    interests.append(analysis["main_topic"])
                if "sub_topics" in analysis:
                    patterns.extend(analysis["sub_topics"].get("patterns", []))

            return f"Interests: {', '.join(set(interests))}\nPatterns: {', '.join(set(patterns))}"
        except Exception as e:
            logger.error(f"Error extracting user profile: {str(e)}")
            return ""

    def _extract_location_context(self, conversations: List[Dict]) -> str:
        """위치 컨텍스트 추출"""
        try:
            locations = []
            for conv in conversations:
                analysis = conv.get("analysis", {})
                if "sub_topics" in analysis and "spatial" in analysis["sub_topics"]:
                    locations.extend(analysis["sub_topics"]["spatial"])

            return f"Recent Locations: {', '.join(set(locations))}"
        except Exception as e:
            logger.error(f"Error extracting location context: {str(e)}")
            return ""

    def _extract_temporal_context(self, conversations: List[Dict]) -> str:
        """시간 컨텍스트 추출"""
        try:
            temporal_info = []
            for conv in conversations:
                analysis = conv.get("analysis", {})
                if "sub_topics" in analysis and "temporal" in analysis["sub_topics"]:
                    temporal_info.extend(analysis["sub_topics"]["temporal"])

            return f"Temporal References: {', '.join(set(temporal_info))}"
        except Exception as e:
            logger.error(f"Error extracting temporal context: {str(e)}")
            return ""

    def _extract_user_interests(self, conversations: List[Dict]) -> str:
        """사용자 관심사 추출"""
        try:
            interests = set()
            for conv in conversations:
                if "main_topic" in conv.get("analysis", {}):
                    interests.add(conv["analysis"]["main_topic"])
            return ", ".join(interests) if interests else "Not enough data"
        except Exception as e:
            logger.error(f"Error extracting user interests: {str(e)}")
            return "Error extracting interests"

    def _extract_user_patterns(self, conversations: List[Dict]) -> str:
        """사용자 패턴 추출"""
        try:
            patterns = []
            for conv in conversations:
                if "sub_topics" in conv.get("analysis", {}):
                    if activities := conv["analysis"]["sub_topics"].get("activities"):
                        patterns.extend(activities)
            return ", ".join(set(patterns)) if patterns else "No clear patterns"
        except Exception as e:
            logger.error(f"Error extracting user patterns: {str(e)}")
            return "Error extracting patterns"

    def _extract_frequent_locations(self, conversations: List[Dict]) -> str:
        """자주 방문하는 위치 추출"""
        try:
            locations = []
            for conv in conversations:
                if spatial := conv.get("analysis", {}).get("sub_topics", {}).get("spatial"):
                    locations.extend(spatial)
            return ", ".join(set(locations)) if locations else "No location data"
        except Exception as e:
            logger.error(f"Error extracting frequent locations: {str(e)}")
            return "Error extracting locations"

    def _extract_current_temporal(self, conversations: List[Dict]) -> str:
        """현재 시간 컨텍스트 추출"""
        try:
            current_temporal = []
            if conversations:
                latest_conv = conversations[-1]
                if 'analysis' in latest_conv:
                    temporal_info = latest_conv['analysis'].get('sub_topics', {}).get('temporal', [])
                    current_temporal.extend(
                        info for info in temporal_info 
                        if any(t in info for t in ['현재', '오늘', '지금'])
                    )
            return ', '.join(current_temporal) if current_temporal else '현재 시점'
        except Exception as e:
            logger.error(f"Error extracting current temporal: {str(e)}")
            return '현재 시점'

    def _extract_temporal_patterns(self, conversations: List[Dict]) -> str:
        """시간 패턴 분석"""
        try:
            patterns = {
                'time_of_day': [],
                'day_of_week': [],
                'period': []
            }

            for conv in conversations:
                if 'analysis' not in conv:
                    continue

                temporal_info = conv['analysis'].get('sub_topics', {}).get('temporal', [])

                for info in temporal_info:
                    # 시간대 분석
                    if any(t in info for t in ['아침', '오전', '오후', '저녁', '밤']):
                        patterns['time_of_day'].append(info)
                    # 요일 분석
                    elif any(d in info for d in ['평일', '주말', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']):
                        patterns['day_of_week'].append(info)
                    # 기간 분석
                    elif any(p in info for p in ['단기', '중기', '장기']):
                        patterns['period'].append(info)

            # 패턴 요약
            summary = []
            for category, items in patterns.items():
                if items:
                    summary.append(f"{category}: {', '.join(set(items))}")

            return '; '.join(summary) if summary else '패턴 없음'

        except Exception as e:
            logger.error(f"Error extracting temporal patterns: {str(e)}")
            return '패턴 분석 실패'

    def _get_personal_info_context(self) -> str:
        """개인 정보 컨텍스트 생성"""
        try:
            profile = self.user_profile.get_profile()["user_profile"]
            context_parts = []

            # 기본 개인정보 처리
            personal_info = profile.get("personal_info", {})
            if personal_info:
                basic_info = []
                if personal_info.get("name"):
                    basic_info.append(f"이름: {personal_info['name']}")
                if personal_info.get("email"):
                    basic_info.append(f"이메일: {personal_info['email']}")
                if personal_info.get("address"):
                    basic_info.append(f"주소: {personal_info['address']}")
                if personal_info.get("age"):
                    basic_info.append(f"나이: {personal_info['age']}")
                if personal_info.get("language"):
                    basic_info.append(f"선호 언어: {personal_info['language']}")

                if basic_info:
                    context_parts.append("기본 정보:\n- " + "\n- ".join(basic_info))

            # 가족 정보 처리
            family_info = profile.get("family_info", {})
            if family_info:
                family_details = []
                if family_info.get("household_size"):
                    family_details.append(f"가구 구성원 수: {family_info['household_size']}")
                if family_info.get("living_arrangement"):
                    family_details.append(f"거주 형태: {family_info['living_arrangement']}")
                if family_info.get("family_members"):
                    members = [f"{m['relation']}({m['age']}세)" for m in family_info['family_members'] if 'relation' in m and 'age' in m]
                    if members:
                        family_details.append(f"가족 구성원: {', '.join(members)}")

                if family_details:
                    context_parts.append("가족 정보:\n- " + "\n- ".join(family_details))

            # 직업 정보 처리
            prof_info = profile.get("professional_info", {})
            if prof_info:
                work_info = []
                if prof_info.get("occupation"):
                    work_info.append(f"직업: {prof_info['occupation']}")
                if prof_info.get("company_name"):
                    work_info.append(f"회사: {prof_info['company_name']}")
                if prof_info.get("position"):
                    work_info.append(f"직위: {prof_info['position']}")
                if prof_info.get("industry"):
                    work_info.append(f"업종: {prof_info['industry']}")

                if work_info:
                    context_parts.append("직업 정보:\n- " + "\n- ".join(work_info))

            # 거주 정보 처리
            residence_info = profile.get("residence_info", {})
            if residence_info:
                home_info = []
                if residence_info.get("housing_type"):
                    home_info.append(f"주거형태: {residence_info['housing_type']}")
                if residence_info.get("neighborhood"):
                    home_info.append(f"동네: {residence_info['neighborhood']}")
                if residence_info.get("residence_period"):
                    home_info.append(f"거주기간: {residence_info['residence_period']}")

                if home_info:
                    context_parts.append("거주 정보:\n- " + "\n- ".join(home_info))

            # 컨텍스트 조합
            if context_parts:
                return "\n\n".join(context_parts)
            return ""  # 충분한 정보가 없는 경우 빈 문자열 반환
        except Exception as e:
            logger.error(f"Error building personal info context: {str(e)}")
            return ""
