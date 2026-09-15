import streamlit as st
import pandas as pd
import os

# 💡 분리된 oring_db.py 파일에서 데이터를 그대로 끌어옵니다!
from oring_db import P_DATA, G_DATA, S_DATA

# 웹 페이지 넓게 쓰기 설정
st.set_page_config(page_title="UNIT R&D - O-Ring Guide", layout="wide", page_icon="⚙️")

# 커스텀 CSS (UI를 좀 더 Tkinter 버전처럼 타이트하게 조절)
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stImage > img { border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)

# 데이터프레임 구성
df_p = pd.DataFrame(P_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D', 'D공차', 'H', 'H공차', 'R'])
df_g = pd.DataFrame(G_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D', 'D공차', 'H', 'H공차', 'R'])
df_s = pd.DataFrame(S_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D1', 'D1공차', 'G', 'H', 'H공차', 'R'])

for col in ['d', 'D', 'H']:
    df_p[col + '_num'] = pd.to_numeric(df_p[col], errors='coerce')
    df_g[col + '_num'] = pd.to_numeric(df_g[col], errors='coerce')
for col in ['d', 'D1', 'G', 'H']:
    df_s[col + '_num'] = pd.to_numeric(df_s[col], errors='coerce')

# 공차 스택 렌더링 함수
def format_tol(tol_str):
    if tol_str == '0, -0.05': return r'$^{0}_{-0.05}$'
    if tol_str == '+0.05, 0': return r'$^{+0.05}_{0}$'
    if tol_str == '0, -0.1': return r'$^{0}_{-0.1}$'
    if tol_str == '+0.1, 0': return r'$^{+0.1}_{0}$'
    if tol_str == '±0.05': return r'$\pm0.05$'
    if tol_str == '±0.1': return r'$\pm0.1$'
    return f" ({tol_str})"

# =========================================================
# 상단 타이틀
# =========================================================
col_logo, col_title = st.columns([1, 10])
with col_logo:
    if os.path.exists("로고.png"):
        st.image("로고.png", width=150)
with col_title:
    st.markdown("### UNIT R&D - O-Ring Specification Guide")

st.markdown("---")

# =========================================================
# 1. 상단 이미지 4개 구역
# =========================================================
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
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.info(f"이미지 누락")

st.markdown("---")

# =========================================================
# 메인 레이아웃 분할 (좌측: 컨트롤 & 검색 / 우측: 전체 규격표)
# =========================================================
left_col, right_col = st.columns([7, 3], gap="large")

with left_col:
    # ---------------------------------------------------------
    # [ 1. 오링 규격 선택 및 상세 제원 ]
    # ---------------------------------------------------------
    st.markdown("#### [ 1. 오링 규격 선택 및 상세 제원 ]")
    
    sel_col1, sel_col2 = st.columns([1, 2])
    
    with sel_col1:
        st.container(border=True)
        series_tab = st.radio("계열 선택", ["P 계열", "G 계열", "S 계열"], horizontal=True)
        
        if series_tab == "P 계열": df_target = df_p
        elif series_tab == "G 계열": df_target = df_g
        else: df_target = df_s
            
        name = st.selectbox("• 호칭 선택:", df_target['호칭'])
        
    with sel_col2:
        st.container(border=True)
        st.markdown(f"**[ {series_tab} 호칭: {name} ]**", unsafe_allow_html=True)
        row = df_target[df_target['호칭'] == name].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### ■ 오링 기본 치수")
            st.write(f"- **선경(W)** : `{row['W']}` mm")
            st.write(f"- **내경(ID)** : `{row['ID']}` mm")
            st.write(f"- **외경(OD)** : `{row['OD']}` mm")
            
        with c2:
            st.markdown("##### ■ 적용 홈 권장 치수")
            if series_tab in ["P 계열", "G 계열"]:
                st.markdown(f"- **홈 깊이(H)** : {row['H']} {format_tol(row['H공차'])} mm")
                st.markdown(f"- **축 외경(D)** : {row['D']} {format_tol(row['D공차'])} mm")
                st.markdown(f"- **하우징 내경(d)**: {row['d']} {format_tol(row['d공차'])} mm")
                st.markdown(f"- **코너 반경(R)** : `{row['R']}` mm")
            else:
                st.markdown(f"- **홈 깊이(H)** : {row['H']} {format_tol(row['H공차'])} mm")
                st.markdown(f"- **축 외경(d)** : {row['d']} {format_tol(row['d공차'])} mm")
                st.markdown(f"- **하우징 내경(D1)**: {row['D1']} {format_tol(row['D1공차'])} mm")
                st.markdown(f"- **홈 폭(G)** : `{row['G']}` mm")
                st.markdown(f"- **코너 반경(R)** : `{row['R']}` mm")
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # [ 2. 규격 통합 검색 ]
    # ---------------------------------------------------------
    st.markdown("#### [ 2. 규격 통합 검색 ]")
    st.caption("D, d, H 중 하나만 입력해도 매칭됩니다. (실시간 검색)")
    
    sch_col1, sch_col2, sch_col3 = st.columns(3)
    val_D = sch_col1.number_input("축 외경(D) / S계열은 d", value=None, step=0.1, format="%.2f")
    val_d = sch_col2.number_input("하우징 내경(d) / S계열은 D1", value=None, step=0.1, format="%.2f")
    val_H = sch_col3.number_input("홈 깊이(H)", value=None, step=0.1, format="%.2f")

    # ---------------------------------------------------------
    # [ 3. 검색 결과 ]
    # ---------------------------------------------------------
    st.markdown("#### [ 3. 검색 결과 ]")
    
    def filter_dataframe(df, d_val, D_val, H_val, is_s=False):
        res = df.copy()
        col_d = 'd_num'
        col_D = 'D1_num' if is_s else 'D_num'
        col_H = 'H_num'
        
        if d_val is not None: res = res[abs(res[col_d] - d_val) <= 0.15]
        if D_val is not None: res = res[abs(res[col_D] - D_val) <= 0.15]
        if H_val is not None: res = res[abs(res[col_H] - H_val) <= 0.25]
        return res
        
    res_p = filter_dataframe(df_p, val_d, val_D, val_H)
    res_g = filter_dataframe(df_g, val_d, val_D, val_H)
    res_s = filter_dataframe(df_s, val_d, val_D, val_H, is_s=True)
    
    total = len(res_p) + len(res_g) + len(res_s)
    
    if (val_d is not None) or (val_D is not None) or (val_H is not None):
        if total > 0:
            st.success(f"조건 매칭 완료 - 총 {total}개 (P:{len(res_p)}, G:{len(res_g)}, S:{len(res_s)})")
            res_tab1, res_tab2, res_tab3 = st.tabs(["P 계열", "G 계열", "S 계열"])
            with res_tab1: st.dataframe(res_p.drop(columns=['d_num', 'D_num', 'H_num', 'd공차', 'D공차', 'H공차', 'R']), use_container_width=True)
            with res_tab2: st.dataframe(res_g.drop(columns=['d_num', 'D_num', 'H_num', 'd공차', 'D공차', 'H공차', 'R']), use_container_width=True)
            with res_tab3: st.dataframe(res_s.drop(columns=['d_num', 'D1_num', 'G_num', 'H_num', 'd공차', 'D1공차', 'H공차', 'R']), use_container_width=True)
        else:
            st.error("조건을 만족하는 표준 오링이 없습니다.")
    else:
        st.info("조건을 입력하면 검색 결과가 표시됩니다.")

# ---------------------------------------------------------
# 우측 사이드바: 아코디언 전체 규격표
# ---------------------------------------------------------
with right_col:
    st.markdown("#### 규격 데이터베이스")
    
    with st.expander("▶ P 계열 전체 규격 표", expanded=True):
        st.dataframe(df_p.drop(columns=['d_num', 'D_num', 'H_num']), use_container_width=True)
    
    with st.expander("▶ G 계열 전체 규격 표"):
        st.dataframe(df_g.drop(columns=['d_num', 'D_num', 'H_num']), use_container_width=True)
    
    with st.expander("▶ S 계열 전체 규격 표"):
        st.dataframe(df_s.drop(columns=['d_num', 'D1_num', 'G_num', 'H_num']), use_container_width=True)
