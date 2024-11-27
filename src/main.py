import argparse
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List

import gradio as gr
from analyzers.conversation_analyzer import ConversationAnalyzer
from analyzers.similarity_analyzer import SimilarityAnalyzer
from generators.prompt_generator import PromptGenerator
from utils.logger import get_logger

logger = get_logger(__name__)

class ConversationInsightUI:
    def __init__(self, openai_api_key: str, openai_base_url: str):
        """WebUI 초기화"""
        self.analyzer = ConversationAnalyzer(
            openai_api_key=openai_api_key,
            openai_base_url=openai_base_url
        )
        self.similarity_analyzer = SimilarityAnalyzer(self.analyzer.client)
        self.prompt_generator = PromptGenerator()

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
        
        # 관심사 분석
        html += "<div class='pattern-section'>"
        html += "<h4 style='color: #34495e; margin: 15px 0 10px 0;'>🎯 관심사 분석</h4>"
        html += "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 4px; color: black;'>"
        if 'user_interests' in profile:
            interests = profile['user_interests']
            if interests.get('top_topics'):
                html += "<div style='margin: 5px 0;'><b style='color: black;'>주요 관심사:</b></div>"
                for topic, count in interests['top_topics']:
                    html += f"<div style='margin: 5px 0 5px 15px; color: black;'>- {topic}: {count}회</div>"
            
            if interests.get('preferences'):
                prefs = interests['preferences']
                for pref_type, items in prefs.items():
                    if items:
                        html += f"<div style='margin: 10px 0;'><b style='color: black;'>{pref_type}:</b></div>"
                        for item, count in items:
                            html += f"<div style='margin: 5px 0 5px 15px; color: black;'>- {item}: {count}회</div>"
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

    async def process_input(self, user_input: str) -> tuple:
        """사용자 입력 처리"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 기본 분석 수행
            analysis_result = await self.analyzer.analyze_conversation(
                user_input=user_input,
                current_date=current_date
            )
            logger.debug(f"analysis_result: {analysis_result}")

            # 사용자 프로필 조회
            user_profile = self.analyzer.get_user_profile()
            logger.debug(f"user_profile: {user_profile}")

            # 대화 히스토리 조회
            conversation_history = self.analyzer.get_conversation_history()
            logger.debug(f"conversation_history: {conversation_history}")

            # 유사 대화 검색 (대화 히스토리가 2개 이상인 경우)
            similar_conversations = []
            if len(conversation_history) >= 2:
                similar_conversations = await self.similarity_analyzer.find_similar_conversations(
                    analysis_result,
                    conversation_history[:-1]  # 현재 대화를 제외한 이전 대화들만 비교
                )
                logger.info(f"similar_conversations: {similar_conversations}")

            # 프롬프트 생성 (유사 대화가 있는 경우)
            enhanced_prompt = ""
            new_query_prompt = ""
            if similar_conversations:
                enhanced_prompt = self.prompt_generator.create_enhanced_prompt(
                    analysis_result,
                    similar_conversations
                )
                new_query_prompt = self.prompt_generator.create_new_query_prompt(
                    analysis_result,
                    similar_conversations
                )
                logger.info(f"enhanced_prompt: {enhanced_prompt}")
                logger.info(f"new_query_prompt: {new_query_prompt}")

            # 결과 포맷팅 및 반환
            return (
                self.format_analysis_result(analysis_result),
                self.format_user_profile(user_profile),
                self.format_conversation_history(conversation_history),
                enhanced_prompt,
                new_query_prompt
            )
            
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return ("Error occurred", "Error occurred", "Error occurred", "", "")

    def create_ui(self) -> gr.Interface:
        """Gradio UI 생성"""
        with gr.Blocks() as interface:
            with gr.Row():
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

                    new_query_prompt = gr.Textbox(
                        label="New Query Prompt",
                        interactive=False
                    )
                    new_query_result = gr.Markdown(label="New Query Prompt 분석 결과")
                    run_new_query_btn = gr.Button("New Query Prompt 실행")

                with gr.Column():
                    analysis_result = gr.HTML(label="분석 결과")
                    user_profile = gr.HTML(label="사용자 프로필")
                    conversation_history = gr.HTML(label="대화 히스토리")
            
            async def run_enhanced_analysis(prompt: str) -> str:
                try:
                    if not prompt:
                        return "프롬프트가 비어있습니다."

                    response = await self.analyzer.client.chat.completions.create(
                        model="openai/gpt-4o-mini-2024-07-18",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    logger.error(f"Error in enhanced analysis: {str(e)}")
                    return f"분석 중 오류가 발생했습니다: {str(e)}"

            async def run_new_query_analysis(prompt: str) -> str:
                try:
                    if not prompt:
                        return "프롬프트가 비어있습니다."

                    response = await self.analyzer.client.chat.completions.create(
                        model="openai/gpt-4o-mini-2024-07-18",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    logger.error(f"Error in new query analysis: {str(e)}")
                    return f"분석 중 오류가 발생했습니다: {str(e)}"

            analyze_btn.click(
                fn=self.process_input,
                inputs=[input_text],
                outputs=[
                    analysis_result,
                    user_profile,
                    conversation_history,
                    enhanced_prompt,
                    new_query_prompt
                ]
            )

            run_enhanced_btn.click(
                fn=run_enhanced_analysis,
                inputs=[enhanced_prompt],
                outputs=[enhanced_result]
            )

            run_new_query_btn.click(
                fn=run_new_query_analysis,
                inputs=[new_query_prompt],
                outputs=[new_query_result]
            )

            return interface

def launch_app():
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        openai_base_url = os.getenv("OPENAI_BASE_URL", "https://dev-api.platform.a15t.com/v1")

        # UI 인스턴스 생성
        app = ConversationInsightUI(
            openai_api_key=openai_api_key,
            openai_base_url=openai_base_url
        )

        # Gradio 인터페이스 실행
        ui = app.create_ui()
        ui.launch(server_name="0.0.0.0", server_port=8760)
        
    except Exception as e:
        logger.error(f"Error launching app: {str(e)}")
        raise

async def main():
    parser = argparse.ArgumentParser(description='Conversation Analyzer')
    
    # 여러 개의 프롬프트를 받을 수 있도록 수정
    parser.add_argument('prompts', type=str, nargs='+',
                       help='One or more prompts for conversation analysis')
    
    # 날짜 인자 추가 (선택적)
    parser.add_argument('--date', type=str,
                       default=datetime.now().strftime("%Y-%m-%d"),
                       help='Analysis date (YYYY-MM-DD format)')

    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "https://dev-api.platform.a15t.com/v1")

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
