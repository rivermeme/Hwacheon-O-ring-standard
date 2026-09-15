import streamlit as st
import pandas as pd
import os

# 💡 분리된 oring_db.py 파일에서 데이터를 끌어옵니다.
from oring_db import P_DATA, G_DATA, S_DATA

st.set_page_config(page_title="UNIT R&D - O-Ring Guide", layout="wide", page_icon="⚙️")

# 💡 1, 5, 6번 피드백 반영: CSS를 통한 전체 여백 축소, 제목 크기 축소, 이미지 고정 사이즈 처리
st.markdown("""
<style>
    /* 화면 좌우/상하 여백 대폭 축소 */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
    
    /* 요소 간격 조절 */
    .stMarkdown p { margin-bottom: 0.2rem; }
    
    /* 모든 이미지 사이즈(높이) 강제 통일 및 중앙 정렬 */
    [data-testid="stImage"] img {
        height: 140px !important;
        width: auto !important;
        max-width: 100% !important;
        object-fit: contain !important;
        border: 1px solid #cbd5e1;
        margin: 0 auto;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 데이터 전처리 (3번 피드백: 규격표 공차 깔끔하게 합치기)
# =========================================================
df_p = pd.DataFrame(P_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D', 'D공차', 'H', 'H공차', 'R'])
df_g = pd.DataFrame(G_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D', 'D공차', 'H', 'H공차', 'R'])
df_s = pd.DataFrame(S_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D1', 'D1공차', 'G', 'H', 'H공차', 'R'])

def merge_tol(val, tol):
    if pd.isna(tol) or not str(tol).strip(): return val
    if '±' in tol: return f"{val} {tol}"
    tols = [t.strip() for t in tol.split(',')]
    if len(tols) == 2: return f"{val} ({tols[0]} / {tols[1]})"
    return f"{val} ({tol})"

# 표출용 데이터프레임 (공차 병합)
disp_p = df_p[['호칭', 'W', 'ID', 'OD']].copy()
disp_p['하우징내경(d)'] = df_p.apply(lambda r: merge_tol(r['d'], r['d공차']), axis=1)
disp_p['축외경(D)'] = df_p.apply(lambda r: merge_tol(r['D'], r['D공차']), axis=1)
disp_p['홈깊이(H)'] = df_p.apply(lambda r: merge_tol(r['H'], r['H공차']), axis=1)
disp_p['R'] = df_p['R']

disp_g = df_g[['호칭', 'W', 'ID', 'OD']].copy()
disp_g['하우징내경(d)'] = df_g.apply(lambda r: merge_tol(r['d'], r['d공차']), axis=1)
disp_g['축외경(D)'] = df_g.apply(lambda r: merge_tol(r['D'], r['D공차']), axis=1)
disp_g['홈깊이(H)'] = df_g.apply(lambda r: merge_tol(r['H'], r['H공차']), axis=1)
disp_g['R'] = df_g['R']

disp_s = df_s[['호칭', 'W', 'ID', 'OD']].copy()
disp_s['축외경(d)'] = df_s.apply(lambda r: merge_tol(r['d'], r['d공차']), axis=1)
disp_s['하우징내경(D1)'] = df_s.apply(lambda r: merge_tol(r['D1'], r['D1공차']), axis=1)
disp_s['홈폭(G)'] = df_s['G']
disp_s['홈깊이(H)'] = df_s.apply(lambda r: merge_tol(r['H'], r['H공차']), axis=1)
disp_s['R'] = df_s['R']

# 검색 연산을 위한 수치형 컬럼
for col in ['d', 'D', 'H']:
    df_p[col + '_num'] = pd.to_numeric(df_p[col], errors='coerce')
    df_g[col + '_num'] = pd.to_numeric(df_g[col], errors='coerce')
for col in ['d', 'D1', 'H']:
    df_s[col + '_num'] = pd.to_numeric(df_s[col], errors='coerce')

# 💡 2번 피드백: 도면 치수처럼 우측 상하단에 공차 스택(Stack) 배치
def latex_tol(val, tol):
    if tol == '0, -0.05': return f"${val}_{{-0.05}}^{{0}}$"
    if tol == '+0.05, 0': return f"${val}_{{0}}^{{+0.05}}$"
    if tol == '0, -0.1': return f"${val}_{{-0.1}}^{{0}}$"
    if tol == '+0.1, 0': return f"${val}_{{0}}^{{+0.1}}$"
    if tol == '±0.05': return f"${val} \pm 0.05$"
    if tol == '±0.1': return f"${val} \pm 0.1$"
    return f"{val} ({tol})"

# =========================================================
# UI 레이아웃
# =========================================================
col_logo, col_title = st.columns([1, 10])
with col_logo:
    if os.path.exists("로고.png"): st.image("로고.png", width=120)
with col_title:
    st.markdown("<h4 style='margin-top: 15px;'>UNIT R&D - O-Ring Specification Guide</h4>", unsafe_allow_html=True)

st.divider() # 가로줄 컴팩트하게

# 상단 이미지 4개 구역
img_cols = st.columns(4)
images_to_show = [
    ("오링 치수 및 형상", "오링 치수 및 형상.png"),
    ("오링 홈 치수 및 형상", "오링 홈 치수 및 형상.png"),
    ("외부 가스켓 형태", "외부 가스켓 형태.png"),
    ("내부 가스켓 형태", "내부 가스켓 형태.png")
]
for i, (img_title, img_path) in enumerate(images_to_show):
    with img_cols[i]:
        st.markdown(f"**{img_title}**")
        if os.path.exists(img_path): st.image(img_path)
        else: st.info(f"이미지 없음")

st.divider()

left_col, right_col = st.columns([6, 4], gap="small")

with left_col:
    # ---------------------------------------------------------
    # [ 1. 오링 규격 선택 및 상세 제원 ]
    # ---------------------------------------------------------
    st.markdown("**[ 1. 오링 규격 선택 및 상세 제원 ]**")
    
    sel_col1, sel_col2 = st.columns([2, 3])
    with sel_col1:
        with st.container(border=True):
            series_tab = st.radio("계열 선택", ["P 계열", "G 계열", "S 계열"], horizontal=True, label_visibility="collapsed")
            if series_tab == "P 계열": df_target = df_p
            elif series_tab == "G 계열": df_target = df_g
            else: df_target = df_s
            name = st.selectbox("• 호칭 선택:", df_target['호칭'])
            
    with sel_col2:
        with st.container(border=True):
            st.markdown(f"<span style='color:#2563EB; font-weight:bold;'>[ {series_tab} 호칭: {name} ]</span>", unsafe_allow_html=True)
            row = df_target[df_target['호칭'] == name].iloc[0]
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**■ 오링 기본 치수**")
                st.write(f"- 선경(W) : `{row['W']}`")
                st.write(f"- 내경(ID) : `{row['ID']}`")
                st.write(f"- 외경(OD) : `{row['OD']}`")
                
            with c2:
                st.markdown("**■ 홈 권장 치수**")
                if series_tab in ["P 계열", "G 계열"]:
                    st.write(f"- 홈 깊이(H) : {latex_tol(row['H'], row['H공차'])}")
                    st.write(f"- 축 외경(D) : {latex_tol(row['D'], row['D공차'])}")
                    st.write(f"- 하우징(d) : {latex_tol(row['d'], row['d공차'])}")
                    st.write(f"- 코너 R : `{row['R']}`")
                else:
                    st.write(f"- 홈 깊이(H) : {latex_tol(row['H'], row['H공차'])}")
                    st.write(f"- 축 외경(d) : {latex_tol(row['d'], row['d공차'])}")
                    st.write(f"- 하우징(D1) : {latex_tol(row['D1'], row['D1공차'])}")
                    st.write(f"- 홈 폭(G) : `{row['G']}`")
                    st.write(f"- 코너 R : `{row['R']}`")

    # ---------------------------------------------------------
    # [ 2. 규격 통합 검색 ]
    # ---------------------------------------------------------
    st.markdown("**[ 2. 규격 통합 검색 ]**")
    
    # 💡 4번 피드백 반영: D, d는 숫자 입력, H는 선택식(Selectbox)으로 변경
    sch_col1, sch_col2, sch_col3 = st.columns(3)
    val_D = sch_col1.number_input("축 외경(D) / S계열은 d", value=None, step=0.1, format="%.2f")
    val_d = sch_col2.number_input("하우징 내경(d) / S계열은 D1", value=None, step=0.1, format="%.2f")
    
    def filter_data(df, val_d, val_D, is_s=False):
        res = df.copy()
        col_d = 'd_num'
        col_D = 'D1_num' if is_s else 'D_num'
        if val_d is not None: res = res[abs(res[col_d] - val_d) <= 0.15]
        if val_D is not None: res = res[abs(res[col_D] - val_D) <= 0.15]
        return res
        
    res_p_pre = filter_data(df_p, val_d, val_D)
    res_g_pre = filter_data(df_g, val_d, val_D)
    res_s_pre = filter_data(df_s, val_d, val_D, is_s=True)
    
    # D, d 입력값에 따라 선택 가능한 H값 리스트 동적 생성
    valid_H = set(res_p_pre['H_num'].dropna().unique()) | set(res_g_pre['H_num'].dropna().unique()) | set(res_s_pre['H_num'].dropna().unique())
    h_options = ["전체"] + [f"{x:g}" for x in sorted(list(valid_H))]
    
    val_H_str = sch_col3.selectbox("홈 깊이(H)", options=h_options)
    val_H = float(val_H_str) if val_H_str != "전체" else None
    
    # 최종 H값 필터링
    if val_H is not None:
        res_p = res_p_pre[abs(res_p_pre['H_num'] - val_H) <= 0.25]
        res_g = res_g_pre[abs(res_g_pre['H_num'] - val_H) <= 0.25]
        res_s = res_s_pre[abs(res_s_pre['H_num'] - val_H) <= 0.25]
    else:
        res_p, res_g, res_s = res_p_pre, res_g_pre, res_s_pre

    total = len(res_p) + len(res_g) + len(res_s)
    
    if (val_d is not None) or (val_D is not None) or (val_H is not None):
        if total > 0:
            st.success(f"매칭 {total}건 (P:{len(res_p)}, G:{len(res_g)}, S:{len(res_s)})")
            r1, r2, r3 = st.tabs(["P 계열", "G 계열", "S 계열"])
            with r1: st.dataframe(disp_p[disp_p['호칭'].isin(res_p['호칭'])], use_container_width=True, hide_index=True)
            with r2: st.dataframe(disp_g[disp_g['호칭'].isin(res_g['호칭'])], use_container_width=True, hide_index=True)
            with r3: st.dataframe(disp_s[disp_s['호칭'].isin(res_s['호칭'])], use_container_width=True, hide_index=True)
        else:
            st.error("조건을 만족하는 규격이 없습니다.")

# ---------------------------------------------------------
# 우측 사이드바: 아코디언 전체 규격표 (Tkinter Treeview 느낌)
# ---------------------------------------------------------
with right_col:
    st.markdown("**[ 규격 데이터베이스 ]**")
    
    with st.expander("▶ P 계열 전체 규격 표", expanded=True):
        st.dataframe(disp_p, use_container_width=True, hide_index=True, height=250)
    with st.expander("▶ G 계열 전체 규격 표"):
        st.dataframe(disp_g, use_container_width=True, hide_index=True, height=250)
    with st.expander("▶ S 계열 전체 규격 표"):
        st.dataframe(disp_s, use_container_width=True, hide_index=True, height=250)
