from typing import Dict, List

from utils.logger import get_logger

logger = get_logger(__name__)

class PromptGenerator:
    """프롬프트 생성 클래스"""

    def __init__(self):
        """프롬프트 템플릿 초기화"""
        self.templates = {
            "enhanced": """
You are analyzing a conversation in Korean. Review the following information carefully:

Current User Query: {current_input}

Examine the conversation history to understand context:
{reference_conversations}

Consider these contextual elements:
{context_data}

Understand the user's background:
The user profile shows {user_profile}
Their location context indicates {location_context}
The temporal context suggests {temporal_context}

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
            "new_query": """
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