import streamlit as st
import pandas as pd
import os

from oring_db import P_DATA, G_DATA, S_DATA

st.set_page_config(page_title="UNIT R&D - O-Ring Guide", layout="wide", page_icon="⚙️")

# =========================================================
# 💡 핵심 CSS: 디자인 붕괴 방지 & 폰트/여백 정밀 조정
# =========================================================
st.markdown("""
<style>
    /* 전체 여백 조정 */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 96%; }
    hr { margin: 0.8em 0px !important; }

    /* 로고 & 타이틀 라인 정렬 */
    .header-title { font-size: 26px; font-weight: bold; color: #1e3a8a; margin-top: 5px; }

    /* 상단 이미지 4개 구역 (제목 안 짤리고 이미지 비율 유지) */
    .img-box { border: 1px solid #cbd5e1; background-color: #ffffff; text-align: center; }
    .img-header { background-color: #1E293B; color: #ffffff; font-weight: bold; font-size: 14px; padding: 6px 0; }
    .img-content { padding: 8px; display: flex; justify-content: center; align-items: center; height: 160px; }
    .img-content img { max-height: 100%; max-width: 100%; object-fit: contain; }

    /* 상세 제원 텍스트 박스 간격/폰트 통일 */
    .detail-container { font-size: 15px; line-height: 2.0; color: #0f172a; }
    .detail-title { font-size: 16px; font-weight: bold; color: #1e3a8a; margin-bottom: 10px; }
    
    /* 공차 스택 디자인 (깔끔한 상하 정렬) */
    .tol-stack { display: inline-flex; flex-direction: column; vertical-align: middle; font-size: 0.7em; line-height: 1.1; margin-left: 2px; }

    /* 우측 아코디언 메뉴 색상 복구 */
    [data-testid="stExpander"] { background-color: #0F172A !important; border: 1px solid #1E293B !important; }
    [data-testid="stExpander"] summary p, [data-testid="stExpander"] summary svg { color: #ffffff !important; font-weight: bold !important; }
    [data-testid="stExpanderDetails"] { background-color: #ffffff !important; padding: 0 !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 데이터 준비 및 공차 렌더링 함수
# =========================================================
df_p = pd.DataFrame(P_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D', 'D공차', 'H', 'H공차', 'R'])
df_g = pd.DataFrame(G_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D', 'D공차', 'H', 'H공차', 'R'])
df_s = pd.DataFrame(S_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D1', 'D1공차', 'G', 'H', 'H공차', 'R'])

# 숫자 검색용 변환
for col in ['d', 'D', 'H']:
    df_p[col + '_num'] = pd.to_numeric(df_p[col], errors='coerce')
    df_g[col + '_num'] = pd.to_numeric(df_g[col], errors='coerce')
for col in ['d', 'D1', 'H']:
    df_s[col + '_num'] = pd.to_numeric(df_s[col], errors='coerce')

# 테이블용 1줄짜리 공차 병합
def merge_tol(val, tol):
    if pd.isna(tol) or not str(tol).strip(): return val
    if '±' in tol: return f"{val} {tol}"
    tols = [t.strip() for t in tol.split(',')]
    if len(tols) == 2: return f"{val} ({tols[0]}/{tols[1]})"
    return f"{val} ({tol})"

# 디스플레이용 데이터프레임
disp_p, disp_g, disp_s = df_p.copy(), df_g.copy(), df_s.copy()
for df in (disp_p, disp_g):
    df['하우징내경(d)'] = df.apply(lambda r: merge_tol(r['d'], r['d공차']), axis=1)
    df['축외경(D)'] = df.apply(lambda r: merge_tol(r['D'], r['D공차']), axis=1)
    df['홈깊이(H)'] = df.apply(lambda r: merge_tol(r['H'], r['H공차']), axis=1)
disp_s['축외경(d)'] = disp_s.apply(lambda r: merge_tol(r['d'], r['d공차']), axis=1)
disp_s['하우징내경(D1)'] = disp_s.apply(lambda r: merge_tol(r['D1'], r['D1공차']), axis=1)
disp_s['홈깊이(H)'] = disp_s.apply(lambda r: merge_tol(r['H'], r['H공차']), axis=1)

disp_p = disp_p[['호칭', 'W', 'ID', 'OD', '하우징내경(d)', '축외경(D)', '홈깊이(H)', 'R']]
disp_g = disp_g[['호칭', 'W', 'ID', 'OD', '하우징내경(d)', '축외경(D)', '홈깊이(H)', 'R']]
disp_s = disp_s[['호칭', 'W', 'ID', 'OD', '축외경(d)', '하우징내경(D1)', 'G', '홈깊이(H)', 'R']]

# 💡 HTML 스택 공차 렌더링 (±는 옆으로, 나머지는 위아래로)
def get_html_tol(val, tol):
    if tol == '0, -0.05': tup, tdn = '0', '-0.05'
    elif tol == '+0.05, 0': tup, tdn = '+0.05', '0'
    elif tol == '0, -0.1': tup, tdn = '0', '-0.1'
    elif tol == '+0.1, 0': tup, tdn = '+0.1', '0'
    elif '±' in tol: return f"{val} {tol}"
    else: return f"{val} ({tol})"
    return f"{val}<span class='tol-stack'><span>{tup}</span><span>{tdn}</span></span>"


# =========================================================
# 화면 그리기 시작
# =========================================================

# 상단 로고 & 타이틀
col_logo, col_title = st.columns([1, 15])
with col_logo:
    if os.path.exists("로고.png"): st.image("로고.png", width=120)
with col_title:
    st.markdown("<div class='header-title'>UNIT R&D - O-Ring Specification Guide</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# 💡 1번, 5번 피드백: 이미지 크기 강제 고정, 제목 잘림 방지 CSS 적용 완
img_cols = st.columns(4)
images = [("오링 치수 및 형상", "오링 치수 및 형상.png"), ("오링 홈 치수 및 형상", "오링 홈 치수 및 형상.png"), 
          ("외부 가스켓 형태", "외부 가스켓 형태.png"), ("내부 가스켓 형태", "내부 가스켓 형태.png")]

for i, (title, path) in enumerate(images):
    with img_cols[i]:
        html = f"""<div class='img-box'><div class='img-header'>{title}</div><div class='img-content'>"""
        st.markdown(html, unsafe_allow_html=True)
        if os.path.exists(path): st.image(path)
        else: st.info("이미지 없음")
        st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# 메인 좌우 분할
left_col, right_col = st.columns([6, 4], gap="medium")

with left_col:
    # ---------------------------------------------------------
    # [ 1. 상세 제원 ]
    # ---------------------------------------------------------
    st.markdown("**[ 1. 오링 규격 선택 및 상세 제원 ]**")
    sel_1, sel_2 = st.columns([2, 5])
    
    with sel_1:
        with st.container(border=True):
            s_type = st.radio("계열 선택", ["P 계열", "G 계열", "S 계열"], horizontal=True, label_visibility="collapsed")
            target_df = df_p if s_type == "P 계열" else df_g if s_type == "G 계열" else df_s
            name = st.selectbox("• 호칭 선택:", target_df['호칭'])
            
    with sel_2:
        with st.container(border=True):
            r = target_df[target_df['호칭'] == name].iloc[0]
            
            # 💡 3, 4, 7번 피드백: 폰트 사이즈/간격 통일, S계열 변수 매핑(d, D1) 완전 수정
            st.markdown(f"<div class='detail-title'>[ {s_type} 호칭: {name} ]</div>", unsafe_allow_html=True)
            
            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown("<div class='detail-container'>", unsafe_allow_html=True)
                st.markdown("**■ 오링 기본 치수**")
                st.markdown(f"• 선경(W) : {r['W']}")
                st.markdown(f"• 내경(ID) : {r['ID']}")
                st.markdown(f"• 외경(OD) : {r['OD']}")
                if s_type == "S 계열":
                    st.markdown(f"• 홈 폭(G) : {r['G']}")
                st.markdown("</div>", unsafe_allow_html=True)

            with c_right:
                st.markdown("<div class='detail-container'>", unsafe_allow_html=True)
                st.markdown("**■ 홈 권장 치수**")
                st.markdown(f"• 홈 깊이(H) : {get_html_tol(r['H'], r['H공차'])}", unsafe_allow_html=True)
                if s_type in ["P 계열", "G 계열"]:
                    st.markdown(f"• 축 외경(D) : {get_html_tol(r['D'], r['D공차'])}", unsafe_allow_html=True)
                    st.markdown(f"• 하우징(d) : {get_html_tol(r['d'], r['d공차'])}", unsafe_allow_html=True)
                else: # S 계열
                    st.markdown(f"• 축 외경(d) : {get_html_tol(r['d'], r['d공차'])}", unsafe_allow_html=True)
                    st.markdown(f"• 하우징(D1) : {get_html_tol(r['D1'], r['D1공차'])}", unsafe_allow_html=True)
                st.markdown(f"• 코너 R : {r['R']}")
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # [ 2. 통합 검색 ]
    # ---------------------------------------------------------
    st.markdown("**[ 2. 규격 통합 검색 ]**")
    
    sch_1, sch_2, sch_3 = st.columns(3)
    val_D = sch_1.number_input("축 외경(D) / S계열은 d", value=None, step=0.1, format="%.2f")
    val_d = sch_2.number_input("하우징 내경(d) / S계열은 D1", value=None, step=0.1, format="%.2f")
    
    def do_filter(df, vd, vD, is_s=False):
        res = df.copy()
        c_d = 'd_num'
        c_D = 'D1_num' if is_s else 'D_num'
        if vd is not None: res = res[abs(res[c_d] - vd) <= 0.15]
        if vD is not None: res = res[abs(res[c_D] - vD) <= 0.15]
        return res
        
    rp_pre = do_filter(df_p, val_d, val_D)
    rg_pre = do_filter(df_g, val_d, val_D)
    rs_pre = do_filter(df_s, val_d, val_D, is_s=True)
    
    valid_H = sorted(list(set(rp_pre['H_num'].dropna()) | set(rg_pre['H_num'].dropna()) | set(rs_pre['H_num'].dropna())))
    h_str = sch_3.selectbox("홈 깊이(H)", options=["전체"] + [f"{x:g}" for x in valid_H])
    val_H = float(h_str) if h_str != "전체" else None
    
    if val_H is not None:
        rp = rp_pre[abs(rp_pre['H_num'] - val_H) <= 0.25]
        rg = rg_pre[abs(rg_pre['H_num'] - val_H) <= 0.25]
        rs = rs_pre[abs(rs_pre['H_num'] - val_H) <= 0.25]
    else:
        rp, rg, rs = rp_pre, rg_pre, rs_pre

    total = len(rp) + len(rg) + len(rs)
    
    if (val_d is not None) or (val_D is not None) or (val_H is not None):
        if total > 0:
            st.success(f"매칭 {total}건 (P:{len(rp)}, G:{len(rg)}, S:{len(rs)})")
            t1, t2, t3 = st.tabs(["P 계열", "G 계열", "S 계열"])
            with t1: st.dataframe(disp_p[disp_p['호칭'].isin(rp['호칭'])], use_container_width=True, hide_index=True)
            with t2: st.dataframe(disp_g[disp_g['호칭'].isin(rg['호칭'])], use_container_width=True, hide_index=True)
            with t3: st.dataframe(disp_s[disp_s['호칭'].isin(rs['호칭'])], use_container_width=True, hide_index=True)
        else:
            st.error("조건을 만족하는 규격이 없습니다.")

# ---------------------------------------------------------
# 우측: 아코디언 메뉴
# ---------------------------------------------------------
with right_col:
    with st.expander("▶ P 계열 전체 규격 표", expanded=True):
        st.dataframe(disp_p, use_container_width=True, hide_index=True, height=280)
    with st.expander("▶ G 계열 전체 규격 표"):
        st.dataframe(disp_g, use_container_width=True, hide_index=True, height=280)
    with st.expander("▶ S 계열 전체 규격 표"):
        st.dataframe(disp_s, use_container_width=True, hide_index=True, height=280)
