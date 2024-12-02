import streamlit as st
import pandas as pd
import numpy as np
import json

# 여기에서 이전에 작성한 LearningRecommender 클래스를 포함합니다.
# 클래스 코드는 길기 때문에 이전 답변에서 복사하여 붙여넣으시면 됩니다.

# 예시 데이터를 불러옵니다.
data = {
    'User ID': [1207341]*15,
    'DateTime': [
        '2024-06-05T15:17:11.961Z', '2024-06-05T15:15:13.214Z',
        '2024-06-06T01:38:44.969Z', '2024-06-06T01:25:55.204Z',
        '2024-06-05T11:16:46.553Z', '2024-06-05T16:17:13.837Z',
        '2024-06-05T16:05:33.948Z', '2024-06-05T15:55:01.156Z',
        '2024-06-05T15:45:44.114Z', '2024-06-08T12:18:06.877Z',
        '2024-06-08T12:12:05.452Z', '2024-06-11T11:03:32.952Z',
        '2024-06-11T11:02:34.122Z', '2024-06-08T09:44:35.844Z',
        '2024-06-08T09:42:00.361Z'
    ],
    'Problem ID': [10880, 41271, 28255, 37703, 111680,
                   28202, 90811, 38415, 10883, 10959,
                   88251, 5204, 88012, 6929, 41405],
    'Subject': ['수학 I']*15,
    'Chapter': ['삼각함수']*9 + ['수열']*6,
    'Section': ['삼각함수의 뜻과 그래프']*9 + ['등차수열과 등비수열']*6,
    'Subsection': ['삼각함수의 활용']*9 + ['수열의 뜻, 등차수열의 일반항과 합']*6,
    'Difficulty': ['상']*15,
    'Correctness': ['O']*14 + ['X'],
    'Time Spent (sec)': [115, 221, 766, 7200, 8,
                         818, 629, 553, 465, 114,
                         353, 55, 515, 123, 968]
}

df = pd.DataFrame(data)
df['DateTime'] = pd.to_datetime(df['DateTime'])
df['Correctness'] = df['Correctness'].map({'O': 1, 'X': 0})

# LearningRecommender 클래스 초기화
recommender = LearningRecommender(df)

# Streamlit 앱 시작
st.set_page_config(
    page_title="학습 분석 및 추천 시스템",
    layout="wide"
)

st.title("📊 학습 분석 및 추천 시스템")
st.write("학생의 학습 데이터를 분석하여 맞춤형 학습 계획을 제공합니다.")

# 사용자 선택 (예시에서는 하나의 사용자만 존재)
user_id = st.selectbox("학생을 선택하세요:", df['User ID'].unique())

# 분석 결과 가져오기
recommendations = recommender.generate_daily_recommendation(user_id)

# 학습량 분석 표시
st.header("1️⃣ 학습량 분석")
study_volume = recommendations.get('학습량_분석', {})
if study_volume:
    col1, col2, col3 = st.columns(3)
    col1.metric("현재 일평균 문제 수", f"{study_volume.get('현재_일평균', 'N/A')} 문제")
    col2.metric("최소 문제 수", f"{study_volume.get('최소', 'N/A')} 문제")
    col3.metric("최대 문제 수", f"{study_volume.get('최대', 'N/A')} 문제")
    st.write(f"적정 여부: **{study_volume.get('적정여부', 'N/A')}**")
    st.write(f"권장 일일 문제 수: **{study_volume.get('권장_일일문제수', 'N/A')} 문제**")
else:
    st.warning("학습량 분석 데이터를 가져올 수 없습니다.")

# 난이도 분포 분석 표시
st.header("2️⃣ 난이도 분포 분석")
difficulty_analysis = recommendations.get('난이도_분석', {})
if difficulty_analysis:
    st.subheader("현재 난이도 분포")
    current_dist = pd.DataFrame.from_dict(difficulty_analysis.get('현재_분포', {}), orient='index', columns=['비율'])
    st.bar_chart(current_dist)

    st.subheader("권장 난이도 분포")
    recommended_dist = pd.DataFrame.from_dict(difficulty_analysis.get('권장_분포', {}), orient='index', columns=['비율'])
    st.bar_chart(recommended_dist)

    st.subheader("조정 필요 여부")
    adjustment = difficulty_analysis.get('조정필요', {})
    adjustment_df = pd.DataFrame(list(adjustment.items()), columns=['난이도', '조정 필요 여부'])
    st.table(adjustment_df)
else:
    st.warning("난이도 분포 분석 데이터를 가져올 수 없습니다.")

# 시간 관리 분석 표시
st.header("3️⃣ 시간 관리 분석")
time_analysis = recommendations.get('시간_분석', {})
if time_analysis:
    st.subheader("난이도별 시간 분석")
    time_difficulty = pd.DataFrame.from_dict(time_analysis.get('난이도별_시간', {}), orient='index')
    st.table(time_difficulty)

    st.subheader("시간대별 성과")
    time_performance = pd.DataFrame.from_dict(time_analysis.get('시간대별_성과', {}), orient='index')
    st.table(time_performance)

    st.subheader("개선 제안")
    suggestions = time_analysis.get('개선제안', [])
    if suggestions:
        for suggestion in suggestions:
            st.write(f"- 난이도 **{suggestion['난이도']}**: {suggestion['현상']} - {suggestion['제안']}")
    else:
        st.write("추가적인 개선 제안이 없습니다.")
else:
    st.warning("시간 관리 분석 데이터를 가져올 수 없습니다.")

# 권장 학습 계획 표시
st.header("4️⃣ 권장 학습 계획")
study_plan = recommendations.get('권장_계획', {})
if study_plan:
    st.subheader("일일 목표")
    daily_goal = study_plan.get('일일_목표', {})
    st.write(f"- 총 문제 수: **{daily_goal.get('총문제수', 'N/A')} 문제**")

    st.write("난이도별 분포:")
    daily_difficulty = pd.DataFrame.from_dict(daily_goal.get('난이도별_분포', {}), orient='index', columns=['권장 비율'])
    st.table(daily_difficulty)

    st.write("시간대별 권장 사항:")
    time_recommendation = daily_goal.get('시간대별_권장', {})
    st.write(f"- 추천 시간대: **{time_recommendation.get('추천_시간대', 'N/A')}**")
    st.write(f"- 예상 정답률: **{time_recommendation.get('예상_정답률', 'N/A')}**")
    st.write(f"- 평균 소요 시간: **{time_recommendation.get('평균_소요시간', 'N/A')}**")

    st.subheader("휴식 관리")
    rest_management = study_plan.get('휴식_관리', {})
    st.write(f"- 세션당 문제 수: **{rest_management.get('세션당_문제수', 'N/A')}**")
    st.write(f"- 쉬는 시간: **{rest_management.get('쉬는시간', 'N/A')}**")
    st.write(f"- 총 세션: **{rest_management.get('총_세션', 'N/A')}**")

    st.subheader("주간 계획")
    weekly_plan = study_plan.get('주간_계획', {})
    st.write(f"- 주간 목표 문제 수: **{weekly_plan.get('주간_목표문제수', 'N/A')} 문제**")
    st.write(f"- 중점 학습 영역: **{', '.join(weekly_plan.get('중점_학습영역', []))}**")
    st.write("분배 제안:")
    distribution = weekly_plan.get('분배_제안', {})
    for key, value in distribution.items():
        st.write(f"- {key}: {value}")
else:
    st.warning("권장 학습 계획 데이터를 가져올 수 없습니다.")
