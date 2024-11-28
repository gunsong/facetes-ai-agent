from datetime import datetime
from typing import Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)

class ConversationFlowManager:
    """대화 흐름 관리 클래스"""

    def __init__(self):
        self.conversation_state = {
            'current_topic': None,
            'current_intent': None,
            'pending_clarification': False,
            'last_query': None,
            'last_response': None,
            'context_stack': []
        }

    def update_state(
        self, 
        query: str, 
        analysis_result: Dict,
        response: str
    ) -> None:
        """대화 상태 업데이트"""
        try:
            # 기본 상태 업데이트
            self.conversation_state.update({
                'last_query': query,
                'last_response': response,
                'current_topic': analysis_result.get('main_topic'),
                'current_intent': analysis_result.get('intent'),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # 명확화 필요 여부 확인
            self.conversation_state['pending_clarification'] = \
                self._needs_clarification(analysis_result)

            # 컨텍스트 스택 관리
            self._update_context_stack(analysis_result)

            logger.info("Conversation state updated successfully")

        except Exception as e:
            logger.error(f"Error updating conversation state: {str(e)}")

    def _needs_clarification(self, analysis_result: Dict) -> bool:
        """명확화 필요 여부 확인"""
        try:
            # 필수 정보가 이미 충분한 경우
            if analysis_result.get('sub_topics', {}).get('spatial') and \
               analysis_result.get('sub_topics', {}).get('temporal') and \
               analysis_result.get('sub_topics', {}).get('activities'):
                return False

            # 필수 정보 누락 체크
            required_info = self._get_required_info(analysis_result.get('intent'))
            available_info = self._get_available_info(analysis_result)

            return not all(info in available_info for info in required_info)

        except Exception as e:
            logger.error(f"Error checking clarification need: {str(e)}")
            return False

    def _get_required_info(self, intent: Union[str, Dict]) -> List[str]:
        """의도별 필수 정보 정의"""
        try:
            # intent가 딕셔너리인 경우 처리
            if isinstance(intent, dict):
                intent_type = intent.get('유형', '')
                if not intent_type:
                    return []

                required_info_map = {
                    '위치문의': ['location'],
                    '시간문의': ['temporal'],
                    '추천요청': ['location', 'preference'],
                    '정보 요청': ['subject', 'temporal']
                }
                return required_info_map.get(intent_type, [])

            # intent가 문자열인 경우 처리
            required_info_map = {
                '위치문의': ['location'],
                '시간문의': ['temporal'],
                '추천요청': ['location', 'preference'],
                '정보요청': ['subject', 'temporal']
            }
            return required_info_map.get(intent, [])

        except Exception as e:
            logger.error(f"Error getting required info: {str(e)}")
            return []

    def _get_available_info(self, analysis_result: Dict) -> List[str]:
        """사용 가능한 정보 추출"""
        try:
            available_info = []
            sub_topics = analysis_result.get('sub_topics', {})

            if sub_topics.get('spatial'):
                available_info.append('location')
            if sub_topics.get('temporal'):
                available_info.append('temporal')
            if analysis_result.get('keywords'):
                available_info.append('subject')
            if sub_topics.get('activities'):
                available_info.append('preference')

            return available_info

        except Exception as e:
            logger.error(f"Error getting available info: {str(e)}")
            return []

    def _update_context_stack(self, analysis_result: Dict) -> None:
        """컨텍스트 스택 업데이트"""
        try:
            # 새로운 컨텍스트 추가
            self.conversation_state['context_stack'].append({
                'topic': analysis_result.get('main_topic'),
                'intent': analysis_result.get('intent'),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # 스택 크기 제한 (최근 5개만 유지)
            if len(self.conversation_state['context_stack']) > 5:
                self.conversation_state['context_stack'].pop(0)

        except Exception as e:
            logger.error(f"Error updating context stack: {str(e)}")

    def get_current_state(self) -> Dict:
        """현재 대화 상태 반환"""
        return self.conversation_state

    def get_active_context(self) -> Optional[Dict]:
        """현재 활성 컨텍스트 반환"""
        try:
            if self.conversation_state['context_stack']:
                return self.conversation_state['context_stack'][-1]
            return None

        except Exception as e:
            logger.error(f"Error getting active context: {str(e)}")
            return None