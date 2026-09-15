import streamlit as st
import pandas as pd
import os
import base64

# 💡 분리된 oring_db.py 파일에서 데이터를 그대로 끌어옵니다!
from oring_db import P_DATA, G_DATA, S_DATA

st.set_page_config(page_title="UNIT R&D - O-Ring Guide", layout="wide", page_icon="⚙️")

# =========================================================
# 💡 완벽 복제 CSS 및 이미지 인코딩
# =========================================================
st.markdown("""
<style>
    /* 전체 여백 대폭 축소 (Tkinter 느낌) */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
    hr { margin: 0.5em 0px !important; }

    /* 헤더 (로고 & 제목) */
    .header-title { font-size: 26px; font-weight: bold; color: #1e3a8a; margin-top: 10px; margin-left: 10px; }

    /* 상단 이미지 4개 구역 (강제 고정으로 짤림/여백 완벽 해결) */
    .img-box { border: 1px solid #1E293B; background-color: #ffffff; text-align: center; height: 100%; display: flex; flex-direction: column; }
    .img-header { background-color: #1E293B; color: #ffffff; font-weight: bold; font-size: 14px; padding: 4px 0; border-bottom: 1px solid #1E293B; }
    .img-content { padding: 5px; flex-grow: 1; display: flex; align-items: center; justify-content: center; height: 140px; }
    .img-content img { max-height: 100%; max-width: 100%; object-fit: contain; }

    /* 상세 제원 텍스트 박스 */
    .detail-container { font-size: 14px; line-height: 1.8; color: #000000; }
    .detail-title { font-size: 15px; font-weight: bold; color: #2563EB; margin-bottom: 10px; }
    .sub-title { font-weight: bold; color: #000000; margin-bottom: 5px; font-size: 14px; }
    
    /* 공차 스택 디자인 (도면 치수 스타일) */
    .tol-stack { display: inline-flex; flex-direction: column; vertical-align: middle; font-size: 0.7em; line-height: 1.1; margin-left: 2px; text-align: left; }

    /* 우측 전체 규격 표 (검은색 배경 아코디언) */
    [data-testid="stExpander"] { background-color: #0F172A !important; border: none !important; border-bottom: 1px solid #1E293B !important; border-radius: 0 !important; }
    [data-testid="stExpander"] summary { padding: 10px 15px !important; }
    [data-testid="stExpander"] summary p, [data-testid="stExpander"] summary svg { color: #ffffff !important; font-weight: bold !important; font-size: 14px !important; }
    [data-testid="stExpanderDetails"] { background-color: #ffffff !important; padding: 0 !important; }
    
    /* 섹션 제목 ( [ 1. ... ] ) */
    .section-title { font-size: 15px; font-weight: bold; color: #000000; margin-top: 10px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# 💡 이미지를 HTML 안에 직접 때려 박아서 레이아웃 붕괴를 원천 차단하는 함수
def get_img_html(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{data}"
    return ""

# =========================================================
# 데이터 준비 및 공차 렌더링 함수
# =========================================================
df_p = pd.DataFrame(P_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D', 'D공차', 'H', 'H공차', 'R'])
df_g = pd.DataFrame(G_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D', 'D공차', 'H', 'H공차', 'R'])
df_s = pd.DataFrame(S_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'd공차', 'D1', 'D1공차', 'G', 'H', 'H공차', 'R'])

for col in ['d', 'D', 'H']:
    df_p[col + '_num'] = pd.to_numeric(df_p[col], errors='coerce')
    df_g[col + '_num'] = pd.to_numeric(df_g[col], errors='coerce')
for col in ['d', 'D1', 'H']:
    df_s[col + '_num'] = pd.to_numeric(df_s[col], errors='coerce')

def merge_tol(val, tol):
    if pd.isna(tol) or not str(tol).strip(): return val
    if '±' in tol: return f"{val} {tol}"
    tols = [t.strip() for t in tol.split(',')]
    if len(tols) == 2: return f"{val} ({tols[0]}/{tols[1]})"
    return f"{val} ({tol})"

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
    if os.path.exists("로고.png"): st.image("로고.png", width=140)
with col_title:
    st.markdown("<div class='header-title'>UNIT R&D - O-Ring Specification Guide</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# 💡 [핵심 수정 부분] 상단 이미지 4개 구역 (스트림릿 레이아웃 붕괴 완벽 차단)
img_cols = st.columns(4, gap="small")
images = [("오링 치수 및 형상", "오링 치수 및 형상.png"), ("오링 홈 치수 및 형상", "오링 홈 치수 및 형상.png"), 
          ("외부 가스켓 형태", "외부 가스켓 형태.png"), ("내부 가스켓 형태", "내부 가스켓 형태.png")]

for i, (title, path) in enumerate(images):
    with img_cols[i]:
        img_src = get_img_html(path)
        if img_src:
            html = f"""
            <div class='img-box'>
                <div class='img-header'>{title}</div>
                <div class='img-content'><img src='{img_src}'></div>
            </div>
            """
        else:
            html = f"<div class='img-box'><div class='img-header'>{title}</div><div class='img-content'>이미지 없음</div></div>"
        st.markdown(html, unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 15px !important;'>", unsafe_allow_html=True)

# 메인 레이아웃: 좌측(컨트롤/상세) / 우측(검은색 사이드바)
left_col, right_col = st.columns([7, 3], gap="medium")

with left_col:
    # ---------------------------------------------------------
    # [ 1. 상세 제원 ]
    # ---------------------------------------------------------
    st.markdown("<div class='section-title'>[ 1. 오링 규격 선택 및 상세 제원 ]</div>", unsafe_allow_html=True)
    sel_1, sel_2 = st.columns([2, 5])
    
    with sel_1:
        with st.container(border=True):
            st.markdown("<div style='background-color:#E2E8F0; padding:5px; margin:-17px -17px 10px -17px; border-bottom:1px solid #cbd5e1; text-align:center;'>", unsafe_allow_html=True)
            s_type = st.radio("계열 선택", ["P 계열", "G 계열", "S 계열"], horizontal=True, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
            target_df = df_p if s_type == "P 계열" else df_g if s_type == "G 계열" else df_s
            st.markdown("<br><div style='text-align:center; font-weight:bold;'>• 호칭 선택:</div>", unsafe_allow_html=True)
            name = st.selectbox("호칭", target_df['호칭'], label_visibility="collapsed")
            st.markdown("<br><br>", unsafe_allow_html=True)
            
    with sel_2:
        with st.container(border=True):
            r = target_df[target_df['호칭'] == name].iloc[0]
            
            st.markdown(f"<div class='detail-title'>[ {s_type} 호칭: {name} ]</div>", unsafe_allow_html=True)
            
            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown("<div class='detail-container'>", unsafe_allow_html=True)
                st.markdown("<div class='sub-title'>■ 오링(O-RING) 기본 치수</div>", unsafe_allow_html=True)
                st.markdown(f"• 선경(W)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {r['W']}")
                st.markdown(f"• 내경(ID)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {r['ID']}")
                st.markdown(f"• 외경(OD)&nbsp;&nbsp;&nbsp;&nbsp;: {r['OD']}")
                if s_type == "S 계열":
                    st.markdown(f"• 홈 폭(G)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {r['G']}")
                st.markdown("</div>", unsafe_allow_html=True)

            with c_right:
                st.markdown("<div class='detail-container'>", unsafe_allow_html=True)
                st.markdown("<div class='sub-title'>■ 적용 홈 권장 치수</div>", unsafe_allow_html=True)
                st.markdown(f"• 홈 깊이(H)&nbsp;&nbsp;&nbsp;&nbsp;: {get_html_tol(r['H'], r['H공차'])}", unsafe_allow_html=True)
                if s_type in ["P 계열", "G 계열"]:
                    st.markdown(f"• 축 외경(D)&nbsp;&nbsp;&nbsp;&nbsp;: {get_html_tol(r['D'], r['D공차'])}", unsafe_allow_html=True)
                    st.markdown(f"• 하우징 내경(d) : {get_html_tol(r['d'], r['d공차'])}", unsafe_allow_html=True)
                else:
                    st.markdown(f"• 축 외경(d)&nbsp;&nbsp;&nbsp;&nbsp;: {get_html_tol(r['d'], r['d공차'])}", unsafe_allow_html=True)
                    st.markdown(f"• 하우징 내경(D1): {get_html_tol(r['D1'], r['D1공차'])}", unsafe_allow_html=True)
                st.markdown(f"• 코너 R&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {r['R']}")
                st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # [ 2. 통합 검색 ]
    # ---------------------------------------------------------
    st.markdown("<div class='section-title'>[ 2. 규격 통합 검색 ]</div>", unsafe_allow_html=True)
    st.caption("D, d, H 중 하나만 입력/선택해도 매칭됩니다.")
    
    sch_1, sch_2, sch_3, sch_4 = st.columns([2, 2, 2, 1])
    val_D = sch_1.number_input("축 외경(D)", value=None, step=0.1, format="%.2f")
    val_d = sch_2.number_input("하우징 내경(d)", value=None, step=0.1, format="%.2f")
    
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
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # [ 3. 검색 결과 ]
    # ---------------------------------------------------------
    st.markdown("<div class='section-title'>[ 3. 검색 결과 ]</div>", unsafe_allow_html=True)
    
    with st.container(border=True):
        if (val_d is not None) or (val_D is not None) or (val_H is not None):
            if total > 0:
                st.markdown(f"<div style='color:#2563EB; font-weight:bold; margin-bottom:10px;'>✅ 조건 매칭 완료 - 총 {total}개</div>", unsafe_allow_html=True)
                t1, t2, t3 = st.tabs(["P 계열", "G 계열", "S 계열"])
                with t1: st.dataframe(disp_p[disp_p['호칭'].isin(rp['호칭'])], use_container_width=True, hide_index=True)
                with t2: st.dataframe(disp_g[disp_g['호칭'].isin(rg['호칭'])], use_container_width=True, hide_index=True)
                with t3: st.dataframe(disp_s[disp_s['호칭'].isin(rs['호칭'])], use_container_width=True, hide_index=True)
            else:
                st.markdown("<div style='color:#EF4444; font-weight:bold; margin-bottom:10px;'>❌ 조건을 만족하는 표준 오링이 없습니다.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#1E3A8A; font-weight:bold; margin-bottom:10px;'>조건을 입력하면 검색 결과가 표시됩니다.</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 우측: 아코디언 메뉴 (검은색 배경 컨테이너)
# ---------------------------------------------------------
with right_col:
    st.markdown("<div style='background-color:#0F172A; height:100%; min-height:800px; padding-top:10px;'>", unsafe_allow_html=True)
    
    with st.expander("▶ P 계열 전체 규격 표", expanded=False):
        st.dataframe(disp_p, use_container_width=True, hide_index=True, height=500)
    with st.expander("▶ G 계열 전체 규격 표", expanded=False):
        st.dataframe(disp_g, use_container_width=True, hide_index=True, height=500)
    with st.expander("▶ S 계열 전체 규격 표", expanded=False):
        st.dataframe(disp_s, use_container_width=True, hide_index=True, height=500)
        
    st.markdown("</div>", unsafe_allow_html=True)
