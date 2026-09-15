import streamlit as st
import pandas as pd
import os

# 💡 분리된 oring_db.py 파일 연동
from oring_db import P_DATA, G_DATA, S_DATA

st.set_page_config(page_title="UNIT R&D - O-Ring Guide", layout="wide", page_icon="⚙️")

# =========================================================
# 💡 디자인/여백 CSS
# =========================================================
st.markdown("""
<style>
    /* 전체 여백 대폭 축소 */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; max-width: 98%; }
    hr { margin: 0.8em 0px !important; }

    /* 헤더 로고 텍스트 정렬 */
    .header-title { font-size: 26px; font-weight: bold; color: #1e3a8a; margin-top: 10px; margin-left: 10px; }

    /* 상단 이미지 4개 구역 컨테이너 스타일 */
    .img-box-header { 
        background-color: #1E293B; 
        color: #ffffff; 
        font-weight: bold; 
        font-size: 14px; 
        text-align: center; 
        padding: 5px 0; 
        margin-bottom: 5px;
    }

    /* 상세 제원 텍스트 박스 */
    .detail-container { font-size: 15px; line-height: 1.8; color: #000000; }
    .detail-title { font-size: 16px; font-weight: bold; color: #2563EB; margin-bottom: 15px; }
    .sub-title { font-weight: bold; color: #000000; margin-bottom: 8px; font-size: 15px; }
    
    /* 공차 스택 디자인 (도면 치수 스타일) */
    .tol-stack { 
        display: inline-flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: flex-start; 
        font-size: 11px; 
        line-height: 1.1; 
        margin-left: 4px; 
        vertical-align: middle; 
    }

    /* 우측 아코디언 메뉴 스타일 */
    [data-testid="stExpander"] { 
        background-color: #0F172A !important; 
        border: 1px solid #1E293B !important; 
    }
    [data-testid="stExpander"] summary p, [data-testid="stExpander"] summary svg { 
        color: #ffffff !important; 
        font-weight: bold !important; 
        font-size: 15px !important; 
    }
    [data-testid="stExpanderDetails"] { 
        background-color: #ffffff !important; 
        padding: 0 !important; 
    }
    
    /* 섹션 제목 ( [ 1. ... ] ) */
    .section-title { font-size: 16px; font-weight: bold; color: #000000; margin-top: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 데이터 준비 및 공차 병합 로직
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

# 💡 S계열 축 외경(D), 하우징 내경(d) 라벨 매핑 완벽 반영
disp_s['하우징내경(d)'] = disp_s.apply(lambda r: merge_tol(r['d'], r['d공차']), axis=1)
disp_s['축외경(D)'] = disp_s.apply(lambda r: merge_tol(r['D1'], r['D1공차']), axis=1)
disp_s['홈깊이(H)'] = disp_s.apply(lambda r: merge_tol(r['H'], r['H공차']), axis=1)

disp_p = disp_p[['호칭', 'W', 'ID', 'OD', '하우징내경(d)', '축외경(D)', '홈깊이(H)', 'R']]
disp_g = disp_g[['호칭', 'W', 'ID', 'OD', '하우징내경(d)', '축외경(D)', '홈깊이(H)', 'R']]
disp_s = disp_s[['호칭', 'W', 'ID', 'OD', '하우징내경(d)', '축외경(D)', 'G', '홈깊이(H)', 'R']]

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

# ---------------------------------------------------------
# 상단 이미지 4개 구역 (스트림릿 고유 기능으로 복구하여 짤림 방지)
# ---------------------------------------------------------
img_cols = st.columns(4, gap="small")
images = [("오링 치수 및 형상", "오링 치수 및 형상.png"), ("오링 홈 치수 및 형상", "오링 홈 치수 및 형상.png"), 
          ("외부 가스켓 형태", "외부 가스켓 형태.png"), ("내부 가스켓 형태", "내부 가스켓 형태.png")]

for i, (title, path) in enumerate(images):
    with img_cols[i]:
        with st.container(border=True):
            st.markdown(f"<div class='img-box-header'>{title}</div>", unsafe_allow_html=True)
            if os.path.exists(path): 
                st.image(path, use_container_width=True) # 자동으로 박스 크기에 꽉 차게 렌더링
            else: 
                st.info("이미지 없음")

st.markdown("<hr>", unsafe_allow_html=True)

# 💡 피드백 반영: 우측 규격집(데이터테이블)을 화면의 약 35% 이상 차지하도록 넓게 수정
left_col, right_col = st.columns([6.2, 3.8], gap="large")

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
            st.markdown("<br><div style='text-align:center; font-weight:bold; font-size:14px;'>• 호칭 선택:</div>", unsafe_allow_html=True)
            name = st.selectbox("호칭", target_df['호칭'], label_visibility="collapsed")
            st.markdown("<br><br>", unsafe_allow_html=True)
            
    with sel_2:
        r = target_df[target_df['호칭'] == name].iloc[0]
        
        # S계열도 P/G와 동일한 D(축외경), d(하우징) 라벨 사용
        if s_type in ["P 계열", "G 계열"]:
            detail_html = f"""
            <div style="border: 1px solid #cbd5e1; padding: 18px; border-radius: 8px; height: 100%;">
                <div class='detail-title'>[ {s_type} 호칭: {name} ]</div>
                <div style='display:flex; justify-content: space-between;' class='detail-container'>
                    <div style="flex:1;">
                        <div class='sub-title'>■ 오링(O-RING) 기본 치수</div>
                        • 선경(W) &nbsp;&nbsp;&nbsp;: {r['W']}<br>
                        • 내경(ID) &nbsp;&nbsp;&nbsp;: {r['ID']}<br>
                        • 외경(OD) &nbsp;&nbsp;: {r['OD']}
                    </div>
                    <div style="flex:1;">
                        <div class='sub-title'>■ 적용 홈 권장 치수</div>
                        • 홈 깊이(H) &nbsp;&nbsp;: {get_html_tol(r['H'], r['H공차'])}<br>
                        • 축 외경(D) &nbsp;&nbsp;: {get_html_tol(r['D'], r['D공차'])}<br>
                        • 하우징 내경(d): {get_html_tol(r['d'], r['d공차'])}<br>
                        • 코너 R &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {r['R']}
                    </div>
                </div>
            </div>
            """
        else: # S 계열
            detail_html = f"""
            <div style="border: 1px solid #cbd5e1; padding: 18px; border-radius: 8px; height: 100%;">
                <div class='detail-title'>[ {s_type} 호칭: {name} ]</div>
                <div style='display:flex; justify-content: space-between;' class='detail-container'>
                    <div style="flex:1;">
                        <div class='sub-title'>■ 오링(O-RING) 기본 치수</div>
                        • 선경(W) &nbsp;&nbsp;&nbsp;: {r['W']}<br>
                        • 내경(ID) &nbsp;&nbsp;&nbsp;: {r['ID']}<br>
                        • 외경(OD) &nbsp;&nbsp;: {r['OD']}<br>
                        • 홈 폭(G) &nbsp;&nbsp;&nbsp;&nbsp;: {r['G']}
                    </div>
                    <div style="flex:1;">
                        <div class='sub-title'>■ 적용 홈 권장 치수</div>
                        • 홈 깊이(H) &nbsp;&nbsp;: {get_html_tol(r['H'], r['H공차'])}<br>
                        • 축 외경(D) &nbsp;&nbsp;: {get_html_tol(r['D1'], r['D1공차'])}<br>
                        • 하우징 내경(d): {get_html_tol(r['d'], r['d공차'])}<br>
                        • 코너 R &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {r['R']}
                    </div>
                </div>
            </div>
            """
        st.markdown(detail_html, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # [ 2. 통합 검색 ]
    # ---------------------------------------------------------
    st.markdown("<div class='section-title'>[ 2. 규격 통합 검색 ]</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:13px; color:#64748b; margin-bottom:10px;'>D, d, H 중 하나만 입력/선택해도 매칭됩니다.</div>", unsafe_allow_html=True)
    
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
    
    sch_4.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    sch_4.button("🔍 검색 실행")
    
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
# 우측: 아코디언 메뉴 (검은 빈 상자 버그 해결)
# ---------------------------------------------------------
with right_col:
    # 💡 HTML <div>로 감싸지 않고 순수 Streamlit expander 사용
    st.markdown("<div class='section-title'>[ 규격 데이터베이스 ]</div>", unsafe_allow_html=True)
    with st.expander("▶ P 계열 전체 규격 표", expanded=True):
        st.dataframe(disp_p, use_container_width=True, hide_index=True, height=500)
    with st.expander("▶ G 계열 전체 규격 표", expanded=False):
        st.dataframe(disp_g, use_container_width=True, hide_index=True, height=500)
    with st.expander("▶ S 계열 전체 규격 표", expanded=False):
        st.dataframe(disp_s, use_container_width=True, hide_index=True, height=500)
