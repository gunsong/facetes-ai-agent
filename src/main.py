import argparse
import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import gradio as gr
from analyzers.conversation_analyzer import ConversationAnalyzer
from analyzers.similarity_analyzer import SimilarityAnalyzer
from generators.prompt_generator import PromptGenerator
from utils.logger import get_logger

logger = get_logger(__name__)

class UserSession:
    def __init__(self, email: str, name: str):
        self.session_id = str(uuid.uuid4())
        self.email = email
        self.name = name
        self.conversation_history = []
        self.last_activity = datetime.now()
        self.analyzer = None
        self.user_profile = None
        self.similarity_analyzer = None
        self.prompt_generator = None

    def initialize_components(self, openai_api_key: str, openai_base_url: str):
        """세션 컴포넌트 초기화"""
        self.analyzer = ConversationAnalyzer(
            openai_api_key=openai_api_key,
            openai_base_url=openai_base_url
        )
        self.user_profile = self.analyzer.user_profile
        self.similarity_analyzer = SimilarityAnalyzer(self.analyzer.client)
        self.prompt_generator = PromptGenerator(self.user_profile)

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
        self.cleanup_interval = 3600  # 1시간마다 정리
        self.last_cleanup = datetime.now()

    def create_session(self, email: str, name: str) -> UserSession:
        """새로운 세션 생성"""
        session = UserSession(email=email, name=name)
        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[UserSession]:
        """세션 ID로 세션 조회"""
        return self.sessions.get(session_id)

    def cleanup_inactive_sessions(self):
        """비활성 세션 정리"""
        current_time = datetime.now()
        if (current_time - self.last_cleanup).total_seconds() < self.cleanup_interval:
            return

        inactive_sessions = []
        for session_id, session in self.sessions.items():
            if (current_time - session.last_activity).total_seconds() > self.cleanup_interval:
                inactive_sessions.append(session_id)
                session.analyzer = None
                session.user_profile = None
                session.similarity_analyzer = None
                session.prompt_generator = None

        for session_id in inactive_sessions:
            del self.sessions[session_id]

        self.last_cleanup = current_time

class ConversationInsightUI:
    def __init__(self, openai_api_key: str, openai_base_url: str):
        """WebUI 초기화"""
        self.session_manager = SessionManager()
        self.openai_api_key = openai_api_key
        self.openai_base_url = openai_base_url

    def format_analysis_result(self, result: Dict) -> str:
        """분석 결과 포맷팅"""
        # analysis_result 키가 있는 경우 해당 값을 사용
        if 'analysis_result' in result:
            result = result['analysis_result']

        html = "<div style='padding: 20px; background-color: white; border: 1px solid #ddd; border-radius: 8px; color: black;'>"
        html += "<h3 style='color: #1a73e8;'>🔍 분석 결과</h3>"

        # 메인 주제
        if result.get('main_topic'):
            html += f"<div style='margin: 10px 0;'><b style='color: black;'>주요 주제:</b> <span style='color: black;'>{result['main_topic']}</span></div>"

        # 의도 분석
        if result.get('intent'):
            html += f"<div style='margin: 10px 0;'><b style='color: black;'>의도:</b> <span style='color: black;'>{result['intent']}</span></div>"

        # 키워드
        if result.get('keywords'):
            html += "<div style='margin: 10px 0;'><b style='color: black;'>키워드:</b> "
            html += ", ".join([f"<span style='background-color: #e8f0fe; padding: 2px 6px; border-radius: 4px; margin: 0 2px; color: black;'>{k}</span>" 
                            for k in result['keywords']])
            html += "</div>"

        # 세부 주제
        if 'sub_topics' in result:
            html += "<div style='margin: 10px 0;'><b style='color: black;'>세부 정보:</b></div>"
            html += "<table style='width:100%; border-collapse: collapse; margin-top: 10px;'>"

            for key, value in result['sub_topics'].items():
                if value:  # 값이 있는 경우만 표시
                    html += "<tr style='border-bottom: 1px solid #dee2e6;'>"
                    html += f"<td style='padding:8px; width:30%; background-color: #f1f3f4; color: black;'><b style='color: black;'>{key}</b></td>"
                    html += f"<td style='padding:8px; color: black;'>{', '.join(value)}</td></tr>"
            html += "</table>"

        # 신뢰도 및 감정 상태
        if result.get('reliability_score'):
            html += f"<div style='margin: 10px 0;'><b style='color: black;'>신뢰도:</b> <span style='color: black;'>{result['reliability_score']}%</span></div>"

        if result.get('sentiment'):
            sentiment = result['sentiment']
            html += "<div style='margin: 10px 0; padding: 10px; background-color: #e8f0fe; border-radius: 4px;'>"
            html += "<b style='color: black;'>감정 분석:</b><br>"
            html += f"<span style='color: black;'>유형: {sentiment.get('type', '')}</span><br>"
            html += f"<span style='color: black;'>강도: {sentiment.get('intensity', '')}%</span><br>"
            html += f"<span style='color: black;'>세부: {sentiment.get('detail', '')}</span>"
            html += "</div>"

        html += "</div>"
        return html

    def format_user_profile(self, profile: Dict) -> str:
        """사용자 프로필 포맷팅"""
        html = "<div style='padding: 20px; background-color: white; border: 1px solid #ddd; border-radius: 8px; color: black;'>"
        html += "<h3 style='color: #2c3e50;'>👤 사용자 프로필</h3>"

        # 통합된 관심사 분석
        html += "<div class='pattern-section'>"
        html += "<h4 style='color: #34495e; margin: 15px 0 10px 0;'>🎯 관심사 및 활동 분석</h4>"
        html += "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 4px; color: black;'>"

        if 'user_interests' in profile:
            interests = profile['user_interests']
            combined_interests = {}

            # 모든 관심사 통합
            if interests.get('top_topics'):
                for topic, count in interests['top_topics']:
                    combined_interests[topic] = {'count': count, 'types': ['주요 관심사']}

            if interests.get('preferences'):
                for pref_type, items in interests['preferences'].items():
                    for item, count in items:
                        if item in combined_interests:
                            combined_interests[item]['count'] += count
                            combined_interests[item]['types'].append(pref_type)
                        else:
                            combined_interests[item] = {'count': count, 'types': [pref_type]}

            # 통합된 결과 출력
            if combined_interests:
                for item, data in sorted(combined_interests.items(), key=lambda x: x[1]['count'], reverse=True):
                    types_str = ', '.join(data['types'])
                    html += f"<div style='margin: 5px 0 5px 15px; color: black;'>- {item}: {data['count']}회 ({types_str})</div>"

        html += "</div></div>"

        # 행동 패턴
        if 'behavior_patterns' in profile:
            patterns = profile['behavior_patterns']

            # 시간적 패턴
            html += "<div class='pattern-section'>"
            html += "<h4 style='color: #34495e; margin: 15px 0 10px 0;'>⏰ 시간적 패턴</h4>"
            html += "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 4px; color: black;'>"
            for period, items in patterns.get('temporal', {}).items():
                if items:
                    html += f"<div style='margin: 5px 0; color: black;'><b style='color: black;'>{period}:</b> {json.dumps(items, ensure_ascii=False)}</div>"
            html += "</div></div>"

            # 공간적 패턴
            html += "<div class='pattern-section'>"
            html += "<h4 style='color: #34495e; margin: 15px 0 10px 0;'>📍 공간적 패턴</h4>"
            html += "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 4px; color: black;'>"
            for loc_type, items in patterns.get('spatial', {}).items():
                if items:
                    formatted_items = [f"{item}: {count}회" for item, count in items]
                    html += f"<div style='margin: 5px 0; color: black;'><b style='color: black;'>{loc_type}:</b> {', '.join(formatted_items)}</div>"
            html += "</div></div>"

            # 사회적 패턴
            html += "<div class='pattern-section'>"
            html += "<h4 style='color: #34495e; margin: 15px 0 10px 0;'>👥 사회적 패턴</h4>"
            html += "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 4px; color: black;'>"
            for social_type, items in patterns.get('social', {}).items():
                if items:
                    formatted_items = [f"{item}: {count}회" for item, count in items]
                    html += f"<div style='margin: 5px 0; color: black;'><b style='color: black;'>{social_type}:</b> {', '.join(formatted_items)}</div>"
            html += "</div></div>"

        # 활동 통계
        if 'activities' in profile and 'activity_stats' in profile['activities']:
            html += "<div class='pattern-section'>"
            html += "<h4 style='color: #34495e; margin: 15px 0 10px 0;'>📊 활동 통계</h4>"
            html += "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 4px; color: black;'>"
            stats = profile['activities']['activity_stats']
            html += f"<div style='margin: 5px 0; color: black;'><b style='color: black;'>총 활동:</b> {stats['total_activities']}회</div>"
            html += f"<div style='margin: 5px 0; color: black;'><b style='color: black;'>완료된 활동:</b> {stats['completed_activities']}회</div>"
            html += f"<div style='margin: 5px 0; color: black;'><b style='color: black;'>예정된 활동:</b> {stats['planned_activities']}회</div>"
            html += "</div></div>"

        # 상호작용 지표
        if 'interaction_metrics' in profile:
            html += "<div class='pattern-section'>"
            html += "<h4 style='color: #34495e; margin: 15px 0 10px 0;'>💭 상호작용 지표</h4>"
            html += "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 4px; color: black;'>"
            metrics = profile['interaction_metrics']
            if 'interaction_counts' in metrics:
                counts = metrics['interaction_counts']
                html += f"<div style='margin: 5px 0; color: black;'><b style='color: black;'>총 상호작용:</b> {counts['total']}회</div>"
                if counts.get('by_type'):
                    html += "<div style='margin: 5px 0;'><b style='color: black;'>유형별:</b></div>"
                    for type_, count in counts['by_type'].items():
                        html += f"<div style='margin: 5px 0 5px 15px; color: black;'>- {type_}: {count}회</div>"
            html += "</div></div>"

        html += "</div>"
        return html

    def format_conversation_history(self, history: List[Dict]) -> str:
        """대화 히스토리 포맷팅"""
        html = "<div style='padding: 20px; background-color: white; border: 1px solid #ddd; border-radius: 8px; color: black;'>"
        html += "<h3 style='color: #2c3e50;'>💬 대화 히스토리</h3>"

        html += "<div style='max-height: 400px; overflow-y: auto;'>"
        for entry in history:
            html += "<div style='margin: 10px 0; padding: 15px; background-color: white; border: 1px solid #eee; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); color: black;'>"
            html += f"<div style='color: #666; font-size: 0.9em;'>{entry.get('timestamp', '')}</div>"

            # 입력 텍스트 스타일 수정
            html += "<div style='margin: 8px 0;'>"
            html += "<b style='color: black;'>입력:</b> "
            html += f"<span style='color: black;'>{entry.get('input', '')}</span>"
            html += "</div>"

            if 'analysis' in entry:
                analysis = entry['analysis']
                # 주제 텍스트 스타일 수정
                html += "<div style='margin: 8px 0;'>"
                html += "<b style='color: black;'>주제:</b> "
                html += f"<span style='color: black;'>{analysis.get('main_topic', '')}</span>"
                html += "</div>"

                # 의도 텍스트 스타일 수정
                html += "<div style='margin: 8px 0;'>"
                html += "<b style='color: black;'>의도:</b> "
                html += f"<span style='color: black;'>{analysis.get('intent', '')}</span>"
                html += "</div>"

                # 키워드 텍스트 스타일 수정
                if analysis.get('keywords'):
                    html += "<div style='margin: 8px 0;'>"
                    html += "<b style='color: black;'>키워드:</b> "
                    html += ", ".join([
                        f"<span style='background-color: #e8f0fe; padding: 2px 6px; border-radius: 4px; margin: 0 2px; color: black;'>{k}</span>"
                        for k in analysis.get('keywords', [])
                    ])
                    html += "</div>"

            html += "</div>"
        html += "</div></div>"
        return html

    def create_ui(self) -> gr.Interface:
        """Gradio UI 생성"""
        with gr.Blocks(css=custom_css) as interface:  # css 파라미터를 여기로 이동
            session_id = gr.State(None)

            # 로그인 팝업
            with gr.Row(visible=True) as login_row:
                with gr.Column():
                    with gr.Box(elem_classes="login-popup"):
                        gr.Markdown("## 로그인")
                        email_input = gr.Textbox(
                            label="이메일 (ID)",
                            placeholder="이메일을 입력하세요"
                        )
                        name_input = gr.Textbox(
                            label="이름",
                            placeholder="이름을 입력하세요"
                        )
                        password_input = gr.Textbox(
                            label="패스워드",
                            placeholder="패스워드를 입력하세요",
                            type="password"
                        )
                        login_btn = gr.Button("로그인", variant="primary")
                        login_status = gr.Markdown("")

            # 메인 인터페이스
            with gr.Row(visible=False) as main_interface:
                with gr.Column():
                    input_text = gr.Textbox(
                        label="사용자 입력",
                        placeholder="대화 내용을 입력하세요...",
                        lines=3
                    )
                    analyze_btn = gr.Button("분석 실행", variant="primary")

                    enhanced_prompt = gr.Textbox(
                        label="Enhanced Prompt",
                        interactive=False
                    )
                    enhanced_result = gr.Markdown(label="Enhanced Prompt 분석 결과")
                    run_enhanced_btn = gr.Button("Enhanced Prompt 실행")

                    suggestion_query_prompt = gr.Textbox(
                        label="Suggestion Query Prompt",
                        interactive=False
                    )
                    suggestion_query_result = gr.Markdown(label="Suggestion Query Prompt 분석 결과")
                    run_suggestion_query_btn = gr.Button("Suggestion Query Prompt 실행")

                with gr.Column():
                    analysis_result = gr.HTML(label="분석 결과")
                    user_profile = gr.HTML(label="사용자 프로필")
                    conversation_history = gr.HTML(label="대화 히스토리")

            async def run_enhanced_analysis(prompt: str, session_id: str) -> str:
                """Enhanced Prompt 분석 실행"""
                try:
                    if not prompt:
                        return "프롬프트가 비어있습니다."

                    session = self.session_manager.get_session(session_id)
                    if not session:
                        return "세션이 만료되었습니다. 다시 로그인해주세요."

                    response = await session.analyzer.client.chat.completions.create(
                        model="openai/gpt-4o-mini-2024-07-18",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    output = response.choices[0].message.content
                    logger.info(f"Enhanced Output from LLM: {output}")
                    return output
                except Exception as e:
                    logger.error(f"Error in enhanced analysis: {str(e)}")
                    return f"분석 중 오류가 발생했습니다: {str(e)}"

            async def run_suggestion_query_analysis(prompt: str, session_id: str) -> str:
                """Suggestion Query Prompt 분석 실행"""
                try:
                    if not prompt:
                        return "프롬프트가 비어있습니다."

                    session = self.session_manager.get_session(session_id)
                    if not session:
                        return "세션이 만료되었습니다. 다시 로그인해주세요."

                    response = await session.analyzer.client.chat.completions.create(
                        model="openai/gpt-4o-mini-2024-07-18",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    output = response.choices[0].message.content
                    logger.info(f"Suggestion Output from LLM: {output}")
                    return output
                except Exception as e:
                    logger.error(f"Error in Suggestion Query analysis: {str(e)}")
                    return f"분석 중 오류가 발생했습니다: {str(e)}"

            async def handle_login(email: str, name: str, password: str) -> tuple:
                """로그인 처리 및 개인정보 저장"""
                if not email or not name:
                    return None, "이메일과 이름을 모두 입력해주세요.", gr.Row(visible=True), gr.Row(visible=False)

                # 패스워드 검증
                if password != "1209":
                    return None, "패스워드가 올바르지 않습니다.", gr.Row(visible=True), gr.Row(visible=False)

                # 기존 세션 강제 종료
                for session_id, session in list(self.session_manager.sessions.items()):
                    if session.email == email:
                        session.analyzer = None
                        session.user_profile = None
                        session.similarity_analyzer = None
                        session.prompt_generator = None
                        del self.session_manager.sessions[session_id]
                        break

                # 새 세션 생성 및 초기화
                session = self.session_manager.create_session(email, name)
                session.initialize_components(
                    openai_api_key=self.openai_api_key,
                    openai_base_url=self.openai_base_url
                )

                # 사용자 정보 저장
                session.user_profile.update_default_personal_info(
                    name=name,
                    email=email
                )

                return (
                    session.session_id,
                    f"환영합니다, {name}님!",
                    gr.Row(visible=False),
                    gr.Row(visible=True)
                )

            async def process_message(message: str, session_id: str) -> tuple:
                """세션별 메시지 처리"""
                if not session_id:
                    return "로그인이 필요합니다.", "", "", "", ""

                session = self.session_manager.get_session(session_id)
                if not session:
                    return "세션이 만료되었습니다. 다시 로그인해주세요.", "", "", "", ""

                session.last_activity = datetime.now()

                try:
                    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # 기본 분석 수행
                    result = await session.analyzer.analyze_conversation(
                        user_input=message,
                        current_date=current_date
                    )
                    logger.debug(f"analysis_result: {result}")

                    # 사용자 프로필 조회
                    user_profile = session.user_profile.get_profile()
                    logger.debug(f"user_profile: {user_profile}")

                    # 내부 대화 내용 저장
                    conversation_record = {
                        "timestamp": current_date,
                        "input": message,
                        "analysis": result
                    }
                    session.conversation_history.append(conversation_record)
                    logger.info(f"대화 내용 저장 완료. 현재 히스토리 크기: {len(session.conversation_history)}")

                    # 대화 히스토리 조회
                    conversation_history = session.analyzer.get_conversation_history()
                    logger.debug(f"conversation_history({len(conversation_history)}): {conversation_history}")

                    # 유사 대화 검색 (대화 히스토리가 2개 이상인 경우)
                    enhanced_prompt = ""
                    suggestion_query_prompt = ""
                    if len(conversation_history) >= 2:
                        similar_conversations = await session.similarity_analyzer.find_similar_conversations(
                            result,
                            conversation_history[:-1]  # 현재 대화를 제외한 이전 대화들만 비교
                        )
                        logger.info(f"similar_conversations: {similar_conversations}")

                        # 프롬프트 생성 (유사 대화가 있는 경우)
                        if similar_conversations:
                            enhanced_prompt = session.prompt_generator.create_enhanced_prompt(
                                result,
                                similar_conversations
                            )
                            suggestion_query_prompt = session.prompt_generator.create_suggestion_query_prompt(
                                result,
                                similar_conversations
                            )
                            logger.info(f"enhanced_prompt: {enhanced_prompt}")
                            logger.info(f"suggestion_query_prompt: {suggestion_query_prompt}")

                    return (
                        self.format_analysis_result(result),
                        self.format_user_profile(user_profile),
                        self.format_conversation_history(conversation_history),
                        enhanced_prompt,
                        suggestion_query_prompt
                    )
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    return "처리 중 오류가 발생했습니다.", "", "", "", ""

            # 이벤트 핸들러 연결
            login_btn.click(
                fn=handle_login,
                inputs=[email_input, name_input, password_input],
                outputs=[
                    session_id,
                    login_status,
                    login_row,
                    main_interface
                ]
            )

            analyze_btn.click(
                fn=process_message,
                inputs=[input_text, session_id],
                outputs=[
                    analysis_result,
                    user_profile,
                    conversation_history,
                    enhanced_prompt,
                    suggestion_query_prompt
                ]
            )

            run_enhanced_btn.click(
                fn=run_enhanced_analysis,
                inputs=[enhanced_prompt, session_id],
                outputs=[enhanced_result]
            )

            run_suggestion_query_btn.click(
                fn=run_suggestion_query_analysis,
                inputs=[suggestion_query_prompt, session_id],
                outputs=[suggestion_query_result]
            )

            return interface

    def _validate_email(self, email: str) -> bool:
        """이메일 형식 검증"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

# CSS 스타일 추가
custom_css = """
.login-popup {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    min-width: 300px;
    max-width: 400px;
}

.login-popup input {
    width: 100%;
    margin-bottom: 1rem;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.login-popup button {
    width: 100%;
    padding: 0.5rem;
    background-color: #2196F3;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.login-popup button:hover {
    background-color: #1976D2;
}
"""

def launch_app():
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        openai_base_url = os.getenv("OPENAI_BASE_URL", "")

        app = ConversationInsightUI(
            openai_api_key=openai_api_key,
            openai_base_url=openai_base_url
        )

        ui = app.create_ui()
        ui.launch(
            server_name="0.0.0.0",
            server_port=8760
            # css 파라미터 제거
        )
    except Exception as e:
        logger.error(f"Error launching app: {str(e)}")
        raise

async def main():
    parser = argparse.ArgumentParser(description='Conversation Analyzer')
    parser.add_argument('prompts', type=str, nargs='+', help='One or more prompts for conversation analysis')

    # 날짜 인자 추가 (선택적)
    parser.add_argument('--date', type=str,
                       default=datetime.now().strftime("%Y-%m-%d"),
                       help='Analysis date (YYYY-MM-DD format)')
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "")

    analyzer = ConversationAnalyzer(
        openai_api_key=api_key,
        openai_base_url=base_url
    )

    try:
        # 첫 번째 프롬프트 분석
        logger.info("=== 대화 분석 시작 (1/%d) ===", len(args.prompts))
        result = await analyzer.analyze_conversation(
            user_input=args.prompts[0],
            current_date=args.date
        )

        # 로그 출력 개선
        logger.debug("첫 번째 대화 분석 결과:\n%s", 
            json.dumps(result, indent=2, ensure_ascii=False))

        # 두 번째 이후의 프롬프트가 있다면 연속 분석 수행
        for i, prompt in enumerate(args.prompts[1:], start=2):
            logger.info("=== 대화 분석 진행 (%d/%d) ===", i, len(args.prompts))
            result = await analyzer.analyze_conversation(
                user_input=prompt,
                current_date=args.date,
                context=result["analysis_result"]
            )

            # 로그 출력 개선
            logger.debug("대화 분석 결과 #%d:\n%s", i,
                json.dumps(result, indent=2, ensure_ascii=False))

        # 최종 결과 출력 개선
        logger.info("\n=== 분석 결과 요약 ===")
        logger.info("총 처리된 대화: %d개", len(args.prompts))

        # 사용자 프로필 출력 개선
        user_profile = analyzer.get_user_profile()
        logger.info("사용자 프로필:\n%s",
            json.dumps(user_profile, ensure_ascii=False))

        # 대화 히스토리 출력 개선
        conversation_history = analyzer.get_conversation_history()
        logger.info("대화 히스토리:\n%s",
            json.dumps(conversation_history, indent=2, ensure_ascii=False))

        return result

    except Exception as e:
        logger.error("Error in main: %s", str(e))
        raise

if __name__ == "__main__":
    # import asyncio
    # asyncio.run(main())

    launch_app()
