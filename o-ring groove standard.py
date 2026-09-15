import streamlit as st
import pandas as pd
import os

# 💡 분리된 database.py 파일에서 데이터를 그대로 끌어옵니다! (데이터 훼손 방지)
from database import P_DATA, G_DATA, S_DATA

st.set_page_config(page_title="UNIT R&D - O-Ring Guide", layout="wide", page_icon="⚙️")

# 데이터프레임 구성
df_p = pd.DataFrame(P_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'D', 'H'])
df_g = pd.DataFrame(G_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'D', 'H'])
df_s = pd.DataFrame(S_DATA, columns=['호칭', 'W', 'ID', 'OD', 'd', 'D1', 'G', 'H'])

# 검색을 위해 수치형 변환
for col in ['d', 'D', 'H']:
    df_p[col + '_num'] = pd.to_numeric(df_p[col], errors='coerce')
    df_g[col + '_num'] = pd.to_numeric(df_g[col], errors='coerce')
for col in ['d', 'D1', 'G', 'H']:
    df_s[col + '_num'] = pd.to_numeric(df_s[col], errors='coerce')

# =========================================================
# UI 구성
# =========================================================
# 로고 및 타이틀 배치
col_logo, col_title = st.columns([1, 8])
with col_logo:
    if os.path.exists("로고.png"):
        st.image("로고.png", width=120)
with col_title:
    st.title("UNIT R&D - O-Ring Specification Guide")

st.markdown("---")

# ---------------------------------------------------------
# 이미지 4개 나란히 배치
# ---------------------------------------------------------
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
            st.info(f"[{img_path}] 파일이 없습니다.")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📌 1. 오링 규격 선택 및 상세 제원", "🔍 2. 규격 통합 검색", "📊 3. 계열별 전체 규격 표"])

# ---------------------------------------------------------
# Tab 1: 오링 규격 선택
# ---------------------------------------------------------
with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("규격 선택")
        series = st.selectbox("계열 선택", ["P 계열", "G 계열", "S 계열"])
        
        if series == "P 계열":
            df_target = df_p
        elif series == "G 계열":
            df_target = df_g
        else:
            df_target = df_s
            
        name = st.selectbox("호칭 선택", df_target['호칭'])
        
    with col2:
        st.subheader(f"[{name}] 상세 제원")
        
        row = df_target[df_target['호칭'] == name].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### ■ 오링(O-RING) 기본 치수")
            st.write(f"- **선경 (W)** : `{row['W']}` mm")
            st.write(f"- **내경 (ID)** : `{row['ID']}` mm")
            st.write(f"- **외경 (OD)** : `{row['OD']}` mm")
            
        with c2:
            st.markdown("##### ■ 적용 홈 권장 치수")
            if series in ["P 계열", "G 계열"]:
                st.write(f"- **홈 깊이 (H)** : `{row['H']}` mm")
                st.write(f"- **축 외경 (D)** : `{row['D']}` mm")
                st.write(f"- **하우징 내경 (d)** : `{row['d']}` mm")
            else:
                st.write(f"- **홈 깊이 (H)** : `{row['H']}` mm")
                st.write(f"- **축 외경 (d)** : `{row['d']}` mm")
                st.write(f"- **하우징 내경 (D1)** : `{row['D1']}` mm")
                st.write(f"- **홈 폭 (G)** : `{row['G']}` mm")
                
# ---------------------------------------------------------
# Tab 2: 규격 통합 검색
# ---------------------------------------------------------
with tab2:
    st.info("💡 **D, d, H 중 하나만 입력해도 즉시 매칭됩니다.** (오차 범위 ±0.15~0.25 자동 적용)")
    
    sc1, sc2, sc3 = st.columns(3)
    val_D = sc1.number_input("축 외경(D) / S계열은 d", value=None, step=0.1, format="%.2f")
    val_d = sc2.number_input("하우징 내경(d) / S계열은 D1", value=None, step=0.1, format="%.2f")
    val_H = sc3.number_input("홈 깊이(H)", value=None, step=0.1, format="%.2f")
    
    def filter_dataframe(df, d_val, D_val, H_val, is_s=False):
        res = df.copy()
        
        col_d = 'd_num'
        col_D = 'D1_num' if is_s else 'D_num'
        col_H = 'H_num'
        
        if d_val is not None:
            res = res[abs(res[col_d] - d_val) <= 0.15]
        if D_val is not None:
            res = res[abs(res[col_D] - D_val) <= 0.15]
        if H_val is not None:
            res = res[abs(res[col_H] - H_val) <= 0.25]
            
        return res
        
    res_p = filter_dataframe(df_p, val_d, val_D, val_H)
    res_g = filter_dataframe(df_g, val_d, val_D, val_H)
    res_s = filter_dataframe(df_s, val_d, val_D, val_H, is_s=True)
    
    total = len(res_p) + len(res_g) + len(res_s)
    
    if (val_d is not None) or (val_D is not None) or (val_H is not None):
        if total > 0:
            st.success(f"✅ 총 {total}개의 규격이 검색되었습니다. ( P: {len(res_p)} | G: {len(res_g)} | S: {len(res_s)} )")
            
            if not res_p.empty:
                st.markdown("#### P 계열 검색 결과")
                st.dataframe(res_p.drop(columns=['d_num', 'D_num', 'H_num']), use_container_width=True)
            if not res_g.empty:
                st.markdown("#### G 계열 검색 결과")
                st.dataframe(res_g.drop(columns=['d_num', 'D_num', 'H_num']), use_container_width=True)
            if not res_s.empty:
                st.markdown("#### S 계열 검색 결과")
                st.dataframe(res_s.drop(columns=['d_num', 'D1_num', 'G_num', 'H_num']), use_container_width=True)
        else:
            st.error("❌ 조건을 만족하는 표준 오링이 없습니다.")

# ---------------------------------------------------------
# Tab 3: 전체 규격 표
# ---------------------------------------------------------
with tab3:
    st.subheader("P 계열 전체 규격")
    st.dataframe(df_p.drop(columns=['d_num', 'D_num', 'H_num']), use_container_width=True)
    
    st.subheader("G 계열 전체 규격")
    st.dataframe(df_g.drop(columns=['d_num', 'D_num', 'H_num']), use_container_width=True)
    
    st.subheader("S 계열 전체 규격")
    st.dataframe(df_s.drop(columns=['d_num', 'D1_num', 'G_num', 'H_num']), use_container_width=True)
