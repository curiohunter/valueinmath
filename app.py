# app.py

import streamlit as st
import pandas as pd
import numpy as np
import json

# LearningRecommender 클래스 정의
class LearningRecommender:
    def __init__(self, data):
        self.data = data
        # 최적 학습량 기준
        self.optimal_daily_problems = {
            'min': 15,  # 최소 문제 수
            'max': 25,  # 최대 문제 수
            'difficulty_ratio': {  # 난이도별 권장 비율
                '상': 0.4,
                '중': 0.4,
                '하': 0.2
            }
        }
        
    def generate_daily_recommendation(self, user_id):
        """일일 학습 권장사항 생성"""
        student_data = self.data[self.data['User ID'] == user_id].copy()
        if len(student_data) == 0:
            return "학생 데이터가 없습니다."
        
        # 최근 7일 데이터 분석
        recent_data = self._get_recent_pattern(student_data)
        
        # 권장사항 생성
        recommendations = {
            '학습량_분석': self._analyze_study_volume(recent_data),
            '난이도_분포_분석': self._analyze_difficulty_distribution(recent_data),
            '시간_관리_분석': self._analyze_time_management(recent_data),
            '권장_학습_계획': self._create_study_plan(recent_data)
        }
        
        return recommendations

    def _get_recent_pattern(self, data):
        """최근 7일 학습 패턴 분석"""
        try:
            last_date = data['DateTime'].max()
            recent_data = data[
                data['DateTime'] >= last_date - pd.Timedelta(days=7)
            ].copy()
            return recent_data
        except Exception as e:
            print(f"최근 데이터 분석 중 오류 발생: {str(e)}")
            return data

    def _analyze_study_volume(self, data):
        """학습량 분석"""
        try:
            daily_problems = data.groupby(
                data['DateTime'].dt.date
            ).size()
            mean_daily = daily_problems.mean()
            return {
                '현재_일평균': round(mean_daily, 1),
                '최소': int(daily_problems.min()),
                '최대': int(daily_problems.max()),
                '적정여부': '적정' if self.optimal_daily_problems['min'] <= mean_daily <= self.optimal_daily_problems['max'] else '조정필요',
                '권장_일일문제수': self._suggest_daily_volume(mean_daily)
            }
        except Exception as e:
            print(f"학습량 분석 중 오류 발생: {str(e)}")
            return {}

    def _suggest_daily_volume(self, mean_daily):
        """일일 권장 문제 수 제안"""
        if mean_daily < self.optimal_daily_problems['min']:
            return self.optimal_daily_problems['min']
        elif mean_daily > self.optimal_daily_problems['max']:
            return self.optimal_daily_problems['max']
        return round(mean_daily)

    def _analyze_difficulty_distribution(self, data):
        """난이도 분포 분석"""
        try:
            if len(data) == 0:
                return {}
            current_dist = data['Difficulty'].value_counts(normalize=True)
            current_ratio = current_dist.to_dict()
            recommended_ratio = self.optimal_daily_problems['difficulty_ratio']
            adjustment_needed = self._get_distribution_adjustment(current_ratio)
            return {
                '현재_분포': {
                    level: f"{ratio*100:.1f}%" 
                    for level, ratio in current_ratio.items()
                },
                '권장_분포': {
                    level: f"{ratio*100:.1f}%" 
                    for level, ratio in recommended_ratio.items()
                },
                '조정필요': adjustment_needed
            }
        except Exception as e:
            print(f"난이도 분포 분석 중 오류 발생: {str(e)}")
            return {}

    def _get_distribution_adjustment(self, current_ratio):
        """난이도 분포 조정 필요 여부"""
        adjustments = {}
        recommended_ratio = self.optimal_daily_problems['difficulty_ratio']
        for level in recommended_ratio.keys():
            current = current_ratio.get(level, 0)
            recommended = recommended_ratio[level]
            if abs(current - recommended) > 0.1:
                adjustments[level] = '조정 필요'
            else:
                adjustments[level] = '적정'
        return adjustments

    def _analyze_time_management(self, data):
        """시간 관리 분석"""
        try:
            if len(data) == 0:
                return {}
            # 난이도별 평균 및 표준편차 계산
            time_stats = data.groupby('Difficulty')['Time Spent (sec)'].agg(['mean', 'std'])
            time_analysis = {}
            consistency_threshold = 0.5  # 일관성 판단 기준
            for diff in time_stats.index:
                mean_time = time_stats.loc[diff, 'mean']
                std_time = time_stats.loc[diff, 'std']
                if np.isnan(std_time):  # 표준편차가 NaN인 경우 처리
                    std_time = 0
                time_analysis[diff] = {
                    '평균시간': f"{mean_time:.1f}초",
                    '표준편차': f"{std_time:.1f}초",
                    '일관성': '안정' if (std_time / mean_time if mean_time != 0 else 0) < consistency_threshold else '불안정'
                }
            # 시간대별 성과 분석 추가
            time_of_day = self._analyze_time_of_day_performance(data)
            return {
                '난이도별_시간': time_analysis,
                '시간대별_성과': time_of_day,
                '개선제안': self._generate_time_suggestions(time_stats)
            }
        except Exception as e:
            print(f"시간 관리 분석 중 오류 발생: {str(e)}")
            return {}

    def _analyze_time_of_day_performance(self, data):
        """시간대별 성과 분석"""
        try:
            data['Hour'] = data['DateTime'].dt.hour
            time_slots = {
                '오전(06-12시)': (6, 12),
                '오후(12-18시)': (12, 18),
                '저녁(18-24시)': (18, 24),
                '새벽(00-06시)': (0, 6)
            }
            performance = {}
            for slot_name, (start, end) in time_slots.items():
                slot_data = data[(data['Hour'] >= start) & (data['Hour'] < end)]
                if len(slot_data) > 0:
                    performance[slot_name] = {
                        '문제수': len(slot_data),
                        '정답률': f"{(slot_data['Correctness'].mean() * 100):.1f}%",
                        '평균시간': f"{slot_data['Time Spent (sec)'].mean():.1f}초"
                    }
            return performance
        except Exception as e:
            print(f"시간대별 분석 중 오류 발생: {str(e)}")
            return {}

    def _generate_time_suggestions(self, time_stats):
        """시간 관리 개선 제안"""
        try:
            suggestions = []
            for diff in time_stats.index:
                mean_time = time_stats.loc[diff, 'mean']
                std_time = time_stats.loc[diff, 'std']
                if np.isnan(std_time):  # 표준편차가 NaN인 경우 처리
                    std_time = 0
                if mean_time == 0:
                    continue
                if std_time / mean_time > 0.5:
                    suggestions.append({
                        '난이도': diff,
                        '현상': '풀이시간 편차가 큽니다',
                        '제안': '일관된 풀이 전략이 필요합니다'
                    })
                if mean_time > self._get_recommended_time(diff):
                    suggestions.append({
                        '난이도': diff,
                        '현상': '평균 풀이시간이 깁니다',
                        '제안': '기본 개념 복습이 필요합니다'
                    })
            return suggestions
        except Exception as e:
            print(f"개선 제안 생성 중 오류 발생: {str(e)}")
            return []

    def _get_recommended_time(self, difficulty):
        """난이도별 권장 풀이시간"""
        recommended_times = {
            '하': 120,  # 2분
            '중': 180,  # 3분
            '상': 300   # 5분
        }
        return recommended_times.get(difficulty, 180)

    def _create_study_plan(self, data):
        """학습 계획 생성"""
        try:
            # 현재 성과 분석
            performance = data.groupby('Difficulty')['Correctness'].mean()
            # 학습 계획 생성
            plan = {
                '일일_목표': {
                    '총문제수': int(self._suggest_daily_volume(len(data))),
                    '난이도별_분포': self._get_recommended_distribution(performance),
                    '시간대별_권장': self._get_time_recommendations(data)
                },
                '휴식_관리': {
                    '세션당_문제수': '5-7문제',
                    '쉬는시간': '15-20분',
                    '총_세션': '3-4회'
                },
                '주간_계획': self._create_weekly_plan(performance)
            }
            return plan
        except Exception as e:
            print(f"학습 계획 생성 중 오류 발생: {str(e)}")
            return {}

    def _get_recommended_distribution(self, performance):
        """난이도 분포 추천"""
        try:
            base_dist = self.optimal_daily_problems['difficulty_ratio'].copy()
            # 성취도에 따른 조정
            for diff in base_dist:
                if diff in performance:
                    if performance[diff] < 0.7:  # 70% 미만 성취도
                        base_dist[diff] += 0.1
                    elif performance[diff] > 0.9:  # 90% 이상 성취도
                        base_dist[diff] -= 0.1
            # 비율 정규화
            total = sum(base_dist.values())
            return {
                level: f"{(ratio/total)*100:.1f}%"
                for level, ratio in base_dist.items()
            }
        except Exception as e:
            print(f"분포 추천 중 오류 발생: {str(e)}")
            return {
                l
