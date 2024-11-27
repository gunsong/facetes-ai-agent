from datetime import datetime, timedelta
from typing import Dict, List, Optional

from openai import AsyncOpenAI
from utils.logger import get_logger

logger = get_logger(__name__)

class SimilarityAnalyzer:
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.time_window = timedelta(hours=1)
        logger.info("SimilarityAnalyzer initialized with time window: 1 hour")

    async def find_similar_conversations(
        self,
        current_conversation: Dict,
        history: List[Dict],
        max_results: int = 2
    ) -> List[Dict]:
        """유사 대화 검색"""
        try:
            logger.info(f"Finding similar conversations for input: {current_conversation.get('input', '')}")
            logger.debug(f"History size: {len(history)} conversations")

            # 1단계: 키워드 기반 필터링
            keyword_candidates = await self._filter_by_keywords(current_conversation, history)
            logger.info(f"Keyword filtering found {len(keyword_candidates)} candidates")

            # 2단계: 시간 기반 필터링 
            time_candidates = self._filter_by_time(current_conversation, history)
            logger.info(f"Time filtering found {len(time_candidates)} candidates")

            # 중복 제거된 후보군 생성
            candidates = list({
                conv["timestamp"]: conv 
                for conv in (keyword_candidates + time_candidates)
            }.values())
            logger.info(f"Total unique candidates after deduplication: {len(candidates)}")

            if not candidates:
                logger.info("No similar conversations found")
                return []

            # 3단계: LLM 기반 유사도 측정
            similarities = await self._calculate_llm_similarities(current_conversation, candidates)
            logger.debug(f"Similarity scores: {similarities}")

            # 유사도 기준 정렬 및 상위 결과 반환
            sorted_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
            logger.info(f"Selected top {max_results} similar conversations")

            result = [candidates[idx] for idx, score in sorted_results[:max_results]]
            logger.debug(f"Final selected conversations: {[r.get('input', '') for r in result]}")
            return result

        except Exception as e:
            logger.error(f"Error finding similar conversations: {str(e)}")
            return []

    async def _filter_by_keywords(
        self,
        current: Dict,
        history: List[Dict],
        max_results: int = 2
    ) -> List[Dict]:
        """키워드 기반 유사도 필터링"""
        try:
            # current의 키워드 추출
            current_keywords = set(current.get("analysis", {}).get("keywords", []))
            logger.debug(f"Current keywords: {current_keywords}")

            if not current_keywords:
                logger.warning("No keywords found in current conversation")
                return []

            scored_convs = []
            for conv in history:
                # history의 각 항목에서 키워드 추출
                hist_keywords = set(conv.get("analysis", {}).get("keywords", []))
                if not hist_keywords:
                    continue
                
                similarity = len(current_keywords & hist_keywords) / len(current_keywords | hist_keywords)
                logger.debug(f"Keyword similarity with '{conv.get('input', '')}': {similarity:.2f}")

                if similarity >= 0.3:  # 키워드 유사도 임계값
                    scored_convs.append((conv, similarity))
                    logger.debug(f"Added to candidates with similarity score: {similarity:.2f}")

            result = [conv for conv, score in sorted(scored_convs, key=lambda x: x[1], reverse=True)[:max_results]]
            logger.info(f"Keyword filtering selected {len(result)} conversations")
            return result

        except Exception as e:
            logger.error(f"Error in keyword filtering: {str(e)}")
            return []

    def _filter_by_time(
        self,
        current: Dict,
        history: List[Dict],
        max_results: int = 2
    ) -> List[Dict]:
        """시간 기반 필터링"""
        try:
            # 현재 대화의 타임스탬프가 없거나 빈 문자열인 경우 처리
            current_timestamp = current.get("timestamp")
            if not current_timestamp:
                logger.warning("Current conversation has no timestamp")
                return []
                
            current_time = datetime.strptime(current_timestamp, "%Y-%m-%d %H:%M:%S")
            logger.debug(f"Current timestamp: {current_time}")
            
            # 시간 범위 내 대화 필터링
            time_filtered = []
            for conv in history:
                # 히스토리의 타임스탬프가 없거나 빈 문자열인 경우 스킵
                conv_timestamp = conv.get("timestamp")
                if not conv_timestamp:
                    logger.debug(f"Skipping conversation with no timestamp: {conv.get('input', '')}")
                    continue
                    
                try:
                    conv_time = datetime.strptime(conv_timestamp, "%Y-%m-%d %H:%M:%S")
                    time_diff = current_time - conv_time
                    logger.debug(f"Time difference with '{conv.get('input', '')}': {time_diff}")

                    if time_diff <= self.time_window:
                        time_filtered.append(conv)
                        logger.debug(f"Added to time-filtered candidates: {conv.get('input', '')}")
                except ValueError as e:
                    logger.warning(f"Invalid timestamp format in history: {conv_timestamp}")
                    continue
            
            # 최근 순으로 정렬
            result = sorted(time_filtered, key=lambda x: x.get("timestamp", ""), reverse=True)[:max_results]
            logger.info(f"Time filtering selected {len(result)} conversations")
            return result
            
        except Exception as e:
            logger.error(f"Error in time filtering: {str(e)}")
            return []

    async def _calculate_llm_similarities(
        self,
        current: Dict,
        candidates: List[Dict]
    ) -> Dict[int, float]:
        """LLM 기반 유사도 계산"""
        try:
            logger.info(f"Calculating LLM similarities for {len(candidates)} candidates")
            similarities = {}
            
            for idx, candidate in enumerate(candidates):
                logger.debug(f"Processing candidate {idx + 1}/{len(candidates)}")
                prompt = self._create_similarity_prompt(current["input"], candidate["input"])
                
                response = await self.client.chat.completions.create(
                    model="openai/gpt-4o-mini-2024-07-18",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI that measures the semantic similarity between two conversations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=100
                )
                
                raw_score = response.choices[0].message.content
                logger.debug(f"Raw similarity score from LLM: {raw_score}")

                similarity_score = self._parse_similarity_score(raw_score)
                logger.debug(f"Parsed similarity score: {similarity_score:.2f}")
                similarities[idx] = similarity_score
                
            logger.info(f"Completed similarity calculations for all candidates")
            return similarities
            
        except Exception as e:
            logger.error(f"Error calculating LLM similarities: {str(e)}")
            return {}

    def _create_similarity_prompt(self, text1: str, text2: str) -> str:
        """유사도 측정용 프롬프트 생성"""
        return f"""
Compare the semantic similarity of these two conversations and rate from 0 to 100:

Conversation 1: {text1}
Conversation 2: {text2}

Provide only the numerical score (0-100) as response.
"""

    def _parse_similarity_score(self, response: str) -> float:
        """LLM 응답에서 유사도 점수 추출"""
        try:
            score = float(response.strip())
            return max(0.0, min(100.0, score)) / 100.0
        except:
            return 0.0