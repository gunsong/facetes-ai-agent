from typing import Dict, List

from utils.logger import get_logger

logger = get_logger(__name__)

class PromptGenerator:
    """프롬프트 생성 클래스"""
    
    def __init__(self):
        """프롬프트 템플릿 초기화"""
        self.templates = {
            "enhanced": """
Current query: {current_input}

Reference conversations:
{reference_conversations}

Context information:
{context_data}

User Profile:
{user_profile}

Location Context:
{location_context}

Temporal Context:
{temporal_context}

## Role and Purpose
You are an AI Assistant specializing in contextual understanding and natural conversation. Your goal is to provide precise, contextually-aware responses that feel natural and helpful.

## Response Strategy
1. Context Analysis:
   - Identify query type and required context
   - Leverage user history and preferences
   - Consider temporal and spatial relevance
   - Apply contextual inference rules

2. Response Generation:
   - Start with the most relevant information
   - Incorporate context naturally
   - Add valuable insights when appropriate
   - Maintain conversation flow

3. Ambiguity Resolution:
   - Use most recent context first
   - Apply user preferences and patterns
   - Consider default assumptions last
   - Confirm critical assumptions naturally

## Language Guidelines
- Use natural, conversational Korean
- Maintain professional yet friendly tone
- Adapt formality to user's style
- Include English terms when necessary

## Response Requirements
1. Primary Information:
   - Direct answer to query
   - Context-based details
   - Relevant background info

2. Supplementary Elements:
   - Related insights
   - Helpful suggestions
   - Next steps if applicable

## Examples
Query: "날씨 어때?"
Bad: "날씨 정보입니다. 현재 기온은 20도입니다."
Good: "방콕은 현재 날씨가 맑고 기온이 30도네요. 여행하시기 좋은 날씨입니다. 특히 오후에는 기온이 더 올라갈 예정이라 실내 관광지를 추천드립니다."

Query: "맛집 추천해줘"
Bad: "맛집을 추천해드리겠습니다."
Good: "방콕 시내에서 현지식을 즐기실 수 있는 맛집을 추천드릴게요. 특히 짜뚜짝 시장 근처의 '쏨땀 누아' 레스토랑이 유명합니다."

## Success Criteria
- Accuracy: 정확한 정보 제공
- Relevance: 맥락에 맞는 응답
- Naturalness: 자연스러운 대화 흐름
- Helpfulness: 실질적인 도움 제공
""",
            "new_query": """
Current query: {current_input}

Reference conversations:
{reference_conversations}

Context information:
{context_data}

User Profile:
{user_profile}

Location Context:
{location_context}

Temporal Context:
{temporal_context}

## Response Generation Guidelines
1. Context-Aware Questions:
   - Focus on missing critical information
   - Consider user's recent interests
   - Reference previous conversations naturally
   - Maintain conversation flow

2. Question Types:
   - Clarification: 모호한 부분 명확화
   - Expansion: 관련 주제로 확장
   - Preference: 사용자 선호도 파악
   - Planning: 향후 계획 탐색

3. Question Format:
   - Use natural Korean language
   - Keep questions concise and clear
   - Avoid yes/no questions
   - Encourage detailed responses

## Examples
Bad: "다른 것은 필요하신가요?"
Good: "방콕에서 특별히 가보고 싶으신 지역이 있으신가요?"

Bad: "언제 여행 가시나요?"
Good: "12월 말에 방콕 여행 계획하신다고 하셨는데, 구체적인 일정이 정해지셨나요?"
"""
        }

    def create_enhanced_prompt(self, current: Dict, similar: List[Dict]) -> str:
        """컨텍스트 기반 향상된 프롬프트 생성"""
        try:
            logger.debug(f"Creating enhanced prompt for input: {current.get('input', '')}")
            user_profile = self._extract_user_profile(similar)
            location_context = self._extract_location_context(similar)
            temporal_context = self._extract_temporal_context(similar)

            return self.templates["enhanced"].format(
                current_input=current.get("input", ""),
                reference_conversations=self._format_reference_conversations(similar),
                context_data=self._format_context_data(similar),
                user_profile=user_profile,
                location_context=location_context,
                temporal_context=temporal_context
            )
        except Exception as e:
            logger.error(f"Error creating enhanced prompt: {str(e)}")
            return ""

    def create_new_query_prompt(self, current: Dict, similar: List[Dict]) -> str:
        """새로운 질의 생성 프롬프트"""
        try:
            logger.debug(f"Creating new query prompt for input: {current.get('input', '')}")
            user_profile = self._extract_user_profile(similar)
            location_context = self._extract_location_context(similar)
            temporal_context = self._extract_temporal_context(similar)
            
            return self.templates["new_query"].format(
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