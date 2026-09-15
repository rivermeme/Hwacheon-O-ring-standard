import streamlit as st
import pandas as pd
import os

# 💡 분리된 database 파일 연동
from oring_db import P_DATA, G_DATA, S_DATA

st.set_page_config(page_title="UNIT R&D - O-Ring Guide", layout="wide", page_icon="⚙️")

# =========================================================
# 💡 디자인 CSS (Tkinter 군청색 테마 복구)
# =========================================================
st.markdown("""
<style>
    /* 전체 여백 압축 */
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; max-width: 95%; }
    hr { margin: 0.5em 0px !important; }

    /* 상단 이미지 4개 구역: 군청색 헤더 스타일 */
    .img-box {
        border: 1px solid #cbd5e1;
        background-color: white;
        text-align: center;
        margin-bottom: 10px;
    }
    .img-header {
        background-color: #1E293B; /* 군청색 */
        color: white;
        font-weight: bold;
        padding: 5px 0;
        font-size: 14px;
    }
    .img-content {
        padding: 5px;
    }
    .img-content img {
        height: 120px !important;
        width: auto !important;
        max-width: 100% !important;
        object-fit: contain !important;
        margin: 0 auto;
        display: block;
    }

    /* 우측 아코디언(전체 규격표) 군청색 배경 */
    [data-testid="stExpander"] {
        background-color: #0F172A !important;
        border: none !important;
    }
    [data-testid="stExpander"] summary p {
        color: white !important;
        font-weight: bold !important;
    }
    [data-testid="stExpander"] summary svg {
        color: white !important;
    }
    /* 아코디언 내부 표 배경은 밝게 유지 */
    [data-testid="stExpanderDetails"] {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 데이터 전처리
# =========================================================
df_p = pd.DataFrame(P_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D', 'D공차', 'H', 'H공차', 'R'])
df_g = pd.DataFrame(G_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D', 'D공차', 'H', 'H공차', 'R'])
# 💡 S계열 컬럼 순서 및 매핑 오류 수정 (d, D1, G, H 제대로 매칭)
df_s = pd.DataFrame(S_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D1', 'D1공차', 'G', 'H', 'H공차', 'R'])

def merge_tol(val, tol):
    if pd.isna(tol) or not str(tol).strip(): return val
    if '±' in tol: return f"{val} {tol}"
    tols = [t.strip() for t in tol.split(',')]
    if len(tols) == 2: return f"{val} ({tols[0]} / {tols[1]})"
    return f"{val} ({tol})"

# 표출용 데이터프레임
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

# 💡 S계열 표출용 컬럼 오류 수정
disp_s = df_s[['호칭', 'W', 'ID', 'OD']].copy()
disp_s['축외경(d)'] = df_s.apply(lambda r: merge_tol(r['d'], r['d공차']), axis=1)
disp_s['하우징내경(D1)'] = df_s.apply(lambda r: merge_tol(r['D1'], r['D1공차']), axis=1)
disp_s['홈폭(G)'] = df_s['G']
disp_s['홈깊이(H)'] = df_s.apply(lambda r: merge_tol(r['H'], r['H공차']), axis=1)
disp_s['R'] = df_s['R']

# 검색 연산용 변환
for col in ['d', 'D', 'H']:
    df_p[col + '_num'] = pd.to_numeric(df_p[col], errors='coerce')
    df_g[col + '_num'] = pd.to_numeric(df_g[col], errors='coerce')
for col in ['d', 'D1', 'H']:
    df_s[col + '_num'] = pd.to_numeric(df_s[col], errors='coerce')

# HTML 공차 스택
def html_tol(val, tol):
    if tol == '0, -0.05': t_up, t_dn = '0', '-0.05'
    elif tol == '+0.05, 0': t_up, t_dn = '+0.05', '0'
    elif tol == '0, -0.1': t_up, t_dn = '0', '-0.1'
    elif tol == '+0.1, 0': t_up, t_dn = '+0.1', '0'
    elif '±' in tol: return f"{val} {tol}"
    else: return f"{val} ({tol})"
    return f"{val}<span style='display: inline-flex; flex-direction: column; justify-content: center; vertical-align: middle; text-align: left; font-size: 0.75em; line-height: 1.1; margin-left: 3px;'><span>{t_up}</span><span>{t_dn}</span></span>"

# =========================================================
# UI 렌더링 시작
# =========================================================
col_logo, col_title = st.columns([1, 15])
with col_logo:
    if os.path.exists("로고.png"): st.image("로고.png", width=110)
with col_title:
    st.markdown("<div style='font-size: 24px; font-weight: bold; margin-top: 5px; color: #1e3a8a;'>UNIT R&D - O-Ring Specification Guide</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# 상단 이미지 4개 구역 (군청색 헤더 적용)
img_cols = st.columns(4)
images_to_show = [
    ("오링 치수 및 형상", "오링 치수 및 형상.png"),
    ("오링 홈 치수 및 형상", "오링 홈 치수 및 형상.png"),
    ("외부 가스켓 형태", "외부 가스켓 형태.png"),
    ("내부 가스켓 형태", "내부 가스켓 형태.png")
]
for i, (img_title, img_path) in enumerate(images_to_show):
    with img_cols[i]:
        html_str = f"""
        <div class="img-box">
            <div class="img-header">{img_title}</div>
            <div class="img-content">
        """
        st.markdown(html_str, unsafe_allow_html=True)
        if os.path.exists(img_path): st.image(img_path)
        else: st.info("이미지 누락")
        st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

left_col, right_col = st.columns([6, 4], gap="small")

with left_col:
    # ---------------------------------------------------------
    # [ 1. 오링 규격 선택 ]
    # ---------------------------------------------------------
    st.markdown("<b style='font-size: 16px;'>[ 1. 오링 규격 선택 및 상세 제원 ]</b>", unsafe_allow_html=True)
    sel_col1, sel_col2 = st.columns([1.5, 3])
    with sel_col1:
        with st.container(border=True):
            series_tab = st.radio("계열 선택", ["P 계열", "G 계열", "S 계열"], horizontal=True, label_visibility="collapsed")
            if series_tab == "P 계열": df_target = df_p
            elif series_tab == "G 계열": df_target = df_g
            else: df_target = df_s
            name = st.selectbox("• 호칭 선택:", df_target['호칭'])
            
    with sel_col2:
        with st.container(border=True):
            row = df_target[df_target['호칭'] == name].iloc[0]
            # 💡 S계열 치수 표시 매핑 오류 수정 완료
            if series_tab in ["P 계열", "G 계열"]:
                detail_html = f"""
                <div style='color:#2563EB; font-weight:bold; font-size:16px; margin-bottom:8px;'>[ {series_tab} 호칭: {name} ]</div>
                <div style='display:flex; justify-content: space-between; font-size: 15px; line-height: 1.8;'>
                    <div>
                        <b>■ 오링 기본 치수</b><br>
                        • 선경(W) : {row['W']}<br>
                        • 내경(ID) : {row['ID']}<br>
                        • 외경(OD) : {row['OD']}
                    </div>
                    <div>
                        <b>■ 홈 권장 치수</b><br>
                        • 홈 깊이(H) : {html_tol(row['H'], row['H공차'])}<br>
                        • 축 외경(D) : {html_tol(row['D'], row['D공차'])}<br>
                        • 하우징(d) : {html_tol(row['d'], row['d공차'])}<br>
                        • 코너 R : {row['R']}
                    </div>
                </div>
                """
            else:
                detail_html = f"""
                <div style='color:#2563EB; font-weight:bold; font-size:16px; margin-bottom:8px;'>[ {series_tab} 호칭: {name} ]</div>
                <div style='display:flex; justify-content: space-between; font-size: 15px; line-height: 1.8;'>
                    <div>
                        <b>■ 오링 기본 치수</b><br>
                        • 선경(W) : {row['W']}<br>
                        • 내경(ID) : {row['ID']}<br>
                        • 외경(OD) : {row['OD']}<br>
                        • 홈 폭(G) : {row['G']}
                    </div>
                    <div>
                        <b>■ 홈 권장 치수</b><br>
                        • 홈 깊이(H) : {html_tol(row['H'], row['H공차'])}<br>
                        • 축 외경(d) : {html_tol(row['d'], row['d공차'])}<br>
                        • 하우징(D1) : {html_tol(row['D1'], row['D1공차'])}<br>
                        • 코너 R : {row['R']}
                    </div>
                </div>
                """
            st.markdown(detail_html, unsafe_allow_html=True)
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # [ 2. 검색 ]
    # ---------------------------------------------------------
    st.markdown("<b style='font-size: 16px;'>[ 2. 규격 통합 검색 ]</b>", unsafe_allow_html=True)
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
    
    valid_H = set(res_p_pre['H_num'].dropna().unique()) | set(res_g_pre['H_num'].dropna().unique()) | set(res_s_pre['H_num'].dropna().unique())
    h_options = ["전체"] + [f"{x:g}" for x in sorted(list(valid_H))]
    
    val_H_str = sch_col3.selectbox("홈 깊이(H)", options=h_options)
    val_H = float(val_H_str) if val_H_str != "전체" else None
    
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
# 우측: 군청색 아코디언 메뉴
# ---------------------------------------------------------
with right_col:
    with st.expander("▶ P 계열 전체 규격 표", expanded=True):
        st.dataframe(disp_p, use_container_width=True, hide_index=True, height=280)
    with st.expander("▶ G 계열 전체 규격 표"):
        st.dataframe(disp_g, use_container_width=True, hide_index=True, height=280)
    with st.expander("▶ S 계열 전체 규격 표"):
        st.dataframe(disp_s, use_container_width=True, hide_index=True, height=280)
