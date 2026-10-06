import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="SK바이오사이언스 L HOUSE 원가관리 분석",
    page_icon="📊",
    layout="wide",
)

# -----------------------------
# Style
# -----------------------------
st.markdown(
    """
    <style>
    .main-title {font-size: 2.1rem; font-weight: 800; margin-bottom: 0.2rem;}
    .sub-title {color: #667085; margin-bottom: 1.4rem;}
    .section-title {font-size: 1.3rem; font-weight: 750; margin-top: 1.2rem; margin-bottom: 0.6rem;}
    .logic-box {
        border: 1px solid #d9e0e8; border-radius: 12px; padding: 18px 20px;
        background: #fafbfd; margin-bottom: 16px;
    }
    .framework {
        border-left: 4px solid #68778a; padding: 14px 18px;
        background: #f7f9fb; border-radius: 6px; line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">SK바이오사이언스 L HOUSE 원가관리 분석</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Management Accounting 관점 · 계획 → 실적 → 차이 → 원인 → 개선/의사결정</div>',
    unsafe_allow_html=True,
)

# -----------------------------
# Data
# -----------------------------
investment_2024 = pd.DataFrame(
    {
        "투자항목": ["백신 포트폴리오 확장", "인프라 투자", "추가 사업 확장"],
        "2024 투자금액(억원)": [998, 192, 226],
    }
)

investment_2025 = pd.DataFrame(
    {
        "투자항목": [
            "백신 포트폴리오 확장",
            "R&D/제조 Infra Upgrade",
            "SKYShield 실행",
            "Next Pandemic Preparedness",
            "New Bio 사업 확장",
        ],
        "2025 투자금액(억원)": [806, 390, 37, 13, 45],
    }
)

investment_2026_h1 = pd.DataFrame(
    {
        "투자항목": [
            "백신 포트폴리오 확장",
            "R&D/제조 Infra Upgrade",
            "SKYShield 실행",
            "Next Pandemic Preparedness",
            "New Bio 사업 확장",
        ],
        "2026 상반기 투자금액(억원)": [333, 235, 19, 8, 14],
    }
)

investment_trend = pd.DataFrame(
    {
        "기간": ["2024", "2025", "2026 상반기"],
        "백신 포트폴리오 확장": [998, 806, 333],
        "R&D/제조 인프라": [192, 390, 235],
    }
)

rd_2q26 = pd.DataFrame(
    {
        "구분": ["연구비 총액", "외부지원금 등", "판관비 반영 연구비"],
        "2Q26(억원)": [647, 485, 162],
    }
)

# -----------------------------
# Helpers
# -----------------------------
def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

def tab_intro(title, what, why, connection, method, limitation):
    st.markdown(
        f"""
        <div class="logic-box">
        <b>{title}</b><br><br>
        <b>① 무엇을 분석하는가</b><br>{what}<br><br>
        <b>② 왜 분석하는가</b><br>{why}<br><br>
        <b>③ Management Accounting과의 연결</b><br>{connection}<br><br>
        <b>④ 분석 방법</b><br>{method}<br><br>
        <b>⑤ 공개자료의 한계</b><br>{limitation}
        </div>
        """,
        unsafe_allow_html=True,
    )

def parse_optional_number(label, key, placeholder="숫자를 입력하세요"):
    raw = st.text_input(label, value="", placeholder=placeholder, key=key)
    if raw.strip() == "":
        return None
    try:
        return float(raw.replace(",", "").strip())
    except ValueError:
        st.warning(f"{label}: 숫자만 입력해 주세요.")
        return None


def format_value(value, unit):
    if value is None:
        return "미입력"
    if unit == "%":
        return f"{value:,.1f}%"
    return f"{value:,.2f} {unit}" if unit else f"{value:,.2f}"


def calc_plan_actual(plan, actual, unit, percentage_point=False):
    if plan is None or actual is None:
        return "계산 대기", "계산 대기"

    diff = actual - plan

    if percentage_point:
        diff_text = f"{diff:+,.1f}%p"
    else:
        diff_text = f"{diff:+,.2f} {unit}" if unit else f"{diff:+,.2f}"

    if plan == 0:
        rate_text = "계획값 0으로 증감률 계산 불가"
    else:
        rate = (actual - plan) / plan * 100
        rate_text = f"{rate:+,.1f}%"

    return diff_text, rate_text


def variance_label(value):
    if value > 0:
        return "불리(U)"
    elif value < 0:
        return "유리(F)"
    return "차이 없음"

def biggest_driver(df):
    if df.empty or df["차이금액"].abs().max() == 0:
        return "현재 입력값에서는 원가차이가 발생하지 않았습니다."
    temp = df.copy()
    idx = temp["차이금액"].abs().idxmax()
    row = temp.loc[idx]
    direction = "불리한" if row["차이금액"] > 0 else "유리한"
    return f"가장 큰 차이는 **{row['차이항목']}**이며, {abs(row['차이금액']):,.0f}원의 **{direction} 차이**입니다."

# -----------------------------
# Tabs: 최종 5개
# -----------------------------
tabs = st.tabs(
    [
        "1. 개요",
        "2. 연구개발 투자현황",
        "3. 계획 대비 실적",
        "4. 원가차이 분석",
        "5. 프로젝트 최종결론",
    ]
)

# =========================================================
# 1. 개요
# =========================================================
with tabs[0]:
    st.subheader("프로젝트 목적")

    st.markdown(
        """
        이 프로젝트는 SK바이오사이언스 안동 L HOUSE의 **Management Accounting 직무**를
        공개자료를 바탕으로 구조화한 프로젝트입니다.

        핵심은 단순히 원가를 집계하는 것이 아니라
        **「얼마가 발생했는가를 넘어 왜 발생했는가를 설명하는 것」**입니다.
        """
    )

    c1, c2, c3 = st.columns(3)
    c1.info("계획 대비 실적 관리")
    c2.info("연구개발 투자현황")
    c3.info("원가차이 분석")

    section("핵심 관리 논리")
    st.markdown(
        """
        <div class="framework">
        계획 → 실적 → 차이 → 원인 → 개선 및 다음 계획 반영
        </div>
        """,
        unsafe_allow_html=True,
    )

    section("데이터 원칙")
    st.warning(
        "공개되지 않은 숫자는 임의로 추정하지 않습니다. L HOUSE 총 제조원가, Batch당 제조원가, "
        "연구과제별 제조비, 계획원가는 공개자료에서 확인되지 않으면 N/A로 표시합니다."
    )
    st.markdown(
        """
        - SK바이오사이언스 매출원가를 L HOUSE 제조원가로 사용하지 않습니다.
        - 2026 상반기 R&D/제조 인프라 개선 235억원을 L HOUSE 제조원가로 해석하지 않습니다.
        - 백신 포트폴리오 확장 333억원은 **투자금액**이며 연구과제 실제 제조비가 아닙니다.
        - 333억원을 개별 파이프라인의 제조비로 임의 배분하지 않습니다.
        - 4번 탭의 원가차이 분석값은 사용자 입력값이며 SK바이오사이언스 실제 수치가 아닙니다.
        """
    )

# =========================================================
# 2. 연구개발 투자현황
# =========================================================
with tabs[1]:
    tab_intro(
        "연구개발 투자현황 | 분석 목적과 방법",
        "SK바이오사이언스의 공개자료에서 확인되는 연구개발 및 미래성장 투자현황을 정리합니다.",
        "회사가 어떤 백신 파이프라인과 연구개발 인프라에 자원을 투입하고 있는지 파악하기 위한 영역입니다.",
        "Management Accounting 관점에서는 투자 방향을 이해하되, 투자금액과 제조원가를 구분하는 것이 중요합니다.",
        "2024~2026 상반기 공개자료를 연도별로 구분하고, 백신 포트폴리오 확장과 R&D/제조 인프라 투자 추이를 비교합니다. 2Q26 연구비/R&D 비용은 별도로 제시합니다.",
        "투자항목의 명칭과 범위는 연도별로 달라질 수 있으며, 투자금액은 L HOUSE 제조원가 또는 개별 연구과제 제조비와 동일한 개념이 아닙니다.",
    )

    # A. 연도별 공개 투자현황
    section("연도별 R&D/미래성장 투자 현황")

    st.info(
        "연도별 공개자료를 선택해 미래성장 투자현황을 확인할 수 있습니다. "
        "동일·유사한 투자항목별 금액이 확인되는 2024년부터 2026년 상반기까지 비교합니다."
    )

    year_tabs = st.tabs(
        ["2024 현황 확인하기", "2025 현황 확인하기", "2026 상반기 현황 확인하기"]
    )

    with year_tabs[0]:
        st.markdown("#### 2024년 미래성장 투자 현황")
        st.dataframe(investment_2024, use_container_width=True, hide_index=True)
        st.info(
            "2024년 미래성장 투자 합계는 1,416억원입니다. "
            "백신 포트폴리오 확장 998억원, 인프라 투자 192억원, 추가 사업 확장 226억원으로 공개되었습니다."
        )
        with st.expander("백신 포트폴리오 확장 · 998억원"):
            st.markdown(
                """
                주요 추진내용
                - PCV21 / NextGen PCV 개발 및 상업화 준비
                - mRNA 플랫폼 및 파이프라인 개발
                - 차별화 플루, HPV9+ 등 신규 백신 발굴
                """
            )
        with st.expander("인프라 투자 · 192억원"):
            st.markdown(
                """
                주요 추진내용
                - 송도 R&PD 센터 건설 및 cGMP 시설 Upgrade
                - AI 활용 수율 개선 등
                """
            )
        with st.expander("추가 사업 확장 · 226억원"):
            st.markdown(
                """
                주요 추진내용
                - IDT 인수 및 PMI를 통한 CGT 사업 확장 검토
                - 태국 JV 설립 추진 등
                """
            )

    with year_tabs[1]:
        st.markdown("#### 2025년 미래성장 투자 현황")
        st.dataframe(investment_2025, use_container_width=True, hide_index=True)
        st.info(
            "2025년 미래성장 투자 합계는 1,291억원입니다. "
            "백신 포트폴리오 확장 806억원과 R&D/제조 Infra Upgrade 390억원이 주요 투자항목입니다."
        )
        with st.expander("백신 포트폴리오 확장 · 806억원"):
            st.markdown(
                """
                주요 추진내용
                - PCV21 글로벌 임상 3상 본격화
                - 차세대 백신 파이프라인 확대
                - PCV21 상업화 준비
                """
            )
        with st.expander("R&D/제조 Infra Upgrade · 390억원"):
            st.markdown(
                """
                주요 추진내용
                - 송도 글로벌 R&PD 센터 구축
                - 안동 L HOUSE G2+ 구축 및 PCV21 글로벌 상업생산 기반 확보
                - 연구·공정개발·품질 분석과 상업생산 인프라 고도화
                """
            )
        with st.expander("기타 미래성장 투자 · 95억원"):
            st.markdown(
                """
                - SKYShield 실행: 37억원
                - Next Pandemic Preparedness: 13억원
                - New Bio 사업 확장: 45억원
                """
            )

    with year_tabs[2]:
        st.markdown("#### 2026년 상반기 미래성장 투자 현황")
        st.dataframe(investment_2026_h1, use_container_width=True, hide_index=True)
        st.info(
            "2026년 상반기 미래성장 투자 합계는 609억원입니다. "
            "백신 포트폴리오 확장 333억원, R&D/제조 Infra Upgrade 235억원이 주요 투자항목입니다."
        )

        with st.expander("백신 포트폴리오 확장 · 333억원"):
            st.markdown(
                """
                주요 추진내용
                - PCV21 / NextGen PCV 개발
                - RSV 예방항체, 차세대 독감백신, 로타바이러스 백신 등 차기 파이프라인 확대
                - 글로벌 임상 및 상업화 준비
                """
            )

        with st.expander("R&D/제조 Infra Upgrade · 235억원"):
            st.markdown(
                """
                주요 추진내용
                - 글로벌 R&PD 센터
                - L HOUSE 생산시설 고도화
                - 생산수율 개선
                - cGMP 수준의 제조역량 고도화
                """
            )

        with st.expander("기타 미래성장 투자 · 41억원"):
            st.markdown(
                """
                - SKYShield 실행: 19억원
                - Next Pandemic Preparedness: 8억원
                - New Bio 사업 확장: 14억원
                """
            )

    section("주요 미래성장 투자 추이 | 2024~2026 상반기")

    trend_long = investment_trend.melt(
        id_vars="기간",
        var_name="투자항목",
        value_name="투자금액(억원)"
    )

    fig_investment_trend = px.bar(
        trend_long,
        x="기간",
        y="투자금액(억원)",
        color="투자항목",
        barmode="group",
        text="투자금액(억원)",
        title="백신 포트폴리오 확장 및 R&D/제조 인프라 투자 추이",
    )
    fig_investment_trend.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_investment_trend.update_layout(
        xaxis_title="기간",
        yaxis_title="투자금액(억원)",
        legend_title="투자항목",
        margin=dict(t=70, b=40),
    )
    st.plotly_chart(fig_investment_trend, use_container_width=True)

    st.caption(
        "※ 2023년은 이후 연도와 동일한 분류의 항목별 투자금액이 공개자료에서 확인되지 않아 그래프에서 금액을 표시하지 않았습니다. "
        "2024년의 '인프라 투자' 192억원을 2025년 이후의 'R&D/제조 Infra Upgrade'와 연결해 추이를 확인하되, 명칭과 세부 범위가 완전히 동일하다고 단정하지 않습니다. "
        "또한 2024·2025년은 연간 금액, 2026년은 상반기 누적 금액이므로 단순 증감률 비교에는 주의가 필요합니다."
    )

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(
            """
            그래프에서 확인할 점
            - 백신 포트폴리오 확장: 2024년 998억원 → 2025년 806억원 → 2026년 상반기 333억원
            - 인프라/R&D·제조 Infra: 2024년 192억원 → 2025년 390억원 → 2026년 상반기 235억원
            - 2026년은 상반기 누적치이므로 2024·2025 연간 금액과 직접적인 연간 증감률 비교는 하지 않습니다.
            """
        )
    with c2:
        st.info(
            "관리회계 관점에서는 투자금액 자체를 제조원가로 해석하지 않고, "
            "회사가 어떤 영역에 자원을 배분하고 있는지 파악하는 경영정보로 활용합니다."
        )

    section("연구비/R&D 비용 | 2Q26")
    st.dataframe(rd_2q26, use_container_width=True, hide_index=True)
    st.metric(
        "판관비 반영 연구비",
        "162억원",
        help=(
            "연구비 총액 중 회사 공시상 '외부지원금 등'을 차감한 후 판매비와관리비에 반영된 연구비입니다. "
            "'외부지원금 등'의 세부 구성은 공개자료만으로 모두 확인할 수 없으므로 전액을 순수 외부지원금으로 해석하지 않습니다."
        ),
    )

    st.info(
        "이 탭의 공개 투자금액은 연구개발·미래성장 투자현황을 보여주기 위한 자료입니다. "
        "원가차이 분석은 다음 탭에서 별도의 사용자 입력형 분석 도구로 구성했습니다."
    )

# =========================================================
# 3. 계획 대비 실적
# =========================================================
with tabs[2]:
    tab_intro(
        "계획 대비 실적 | 분석 목적과 방법",
        "L HOUSE의 계획값과 실제값을 같은 기준으로 입력·비교하고, 계획 대비 실적 차이를 자동 계산합니다.",
        "Management Accounting의 핵심은 실제 실적을 확인하는 데 그치지 않고 계획과 얼마나 차이가 발생했는지 파악하는 것이기 때문입니다.",
        "계획값을 입력하면 공개된 실제값과 자동 비교하고, 공개되지 않은 실제값도 추후 확인할 경우 직접 입력하여 차이와 증감률을 계산할 수 있습니다.",
        "계획·실제 생산능력, 생산실적, 총 제조원가를 입력하면 가동률과 Batch당 제조원가를 자동 계산하고 계획 대비 실제 차이를 비교합니다.",
        "입력 전에는 '미입력' 또는 '계산 대기'로 표시하며 공개되지 않은 숫자를 임의로 채우지 않습니다. 사용자 입력값을 바탕으로 파생지표만 자동 계산합니다.",
    )

    section("L HOUSE 계획·실제값 입력")
    st.info(
        "계획과 실제의 생산능력·생산실적·총 제조원가만 입력하면 "
        "가동률과 Batch당 제조원가는 자동으로 계산됩니다."
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 계획값")
        plan_capacity = parse_optional_number(
            "계획 생산능력 (batch)",
            key="plan_capacity",
            placeholder="예: 330"
        )
        plan_output = parse_optional_number(
            "계획 생산실적 (batch)",
            key="plan_output",
            placeholder="예: 200"
        )
        plan_total_cost = parse_optional_number(
            "계획 총 제조원가 (억원)",
            key="plan_total_cost",
            placeholder="예: 500"
        )

    with c2:
        st.markdown("#### 실제값")
        actual_capacity = parse_optional_number(
            "실제 생산능력 (batch)",
            key="actual_capacity",
            placeholder="예: 320"
        )
        actual_output = parse_optional_number(
            "실제 생산실적 (batch)",
            key="actual_output",
            placeholder="예: 137"
        )
        actual_total_cost = parse_optional_number(
            "실제 총 제조원가 (억원)",
            key="actual_total_cost",
            placeholder="예: 520"
        )

    # 자동 계산
    plan_utilization = (
        plan_output / plan_capacity * 100
        if plan_capacity is not None and plan_capacity > 0 and plan_output is not None
        else None
    )
    actual_utilization = (
        actual_output / actual_capacity * 100
        if actual_capacity is not None and actual_capacity > 0 and actual_output is not None
        else None
    )

    # 총 제조원가는 억원, Batch당 제조원가는 억원/Batch로 계산
    plan_unit_cost = (
        plan_total_cost / plan_output
        if plan_total_cost is not None and plan_output is not None and plan_output > 0
        else None
    )
    actual_unit_cost = (
        actual_total_cost / actual_output
        if actual_total_cost is not None and actual_output is not None and actual_output > 0
        else None
    )

    section("자동 계산 결과")
    a1, a2 = st.columns(2)
    with a1:
        st.markdown("#### 계획")
        st.metric(
            "계획 가동률",
            f"{plan_utilization:,.1f}%" if plan_utilization is not None else "계산 대기"
        )
        st.metric(
            "계획 Batch당 제조원가",
            f"{plan_unit_cost:,.2f}억원/Batch" if plan_unit_cost is not None else "계산 대기"
        )
    with a2:
        st.markdown("#### 실제")
        st.metric(
            "실제 가동률",
            f"{actual_utilization:,.1f}%" if actual_utilization is not None else "계산 대기"
        )
        st.metric(
            "실제 Batch당 제조원가",
            f"{actual_unit_cost:,.2f}억원/Batch" if actual_unit_cost is not None else "계산 대기"
        )

    st.caption(
        "가동률 = 생산실적 ÷ 생산능력 × 100 / "
        "Batch당 제조원가 = 총 제조원가 ÷ 생산실적. "
        "총 제조원가를 생산실적(Batch)로 나누어 억원/Batch로 표시합니다."
    )

    cap_diff, cap_rate = calc_plan_actual(plan_capacity, actual_capacity, "batch")
    out_diff, out_rate = calc_plan_actual(plan_output, actual_output, "batch")
    util_diff, util_rate = calc_plan_actual(
        plan_utilization,
        actual_utilization,
        "%",
        percentage_point=True
    )
    total_cost_diff, total_cost_rate = calc_plan_actual(
        plan_total_cost,
        actual_total_cost,
        "억원"
    )
    unit_cost_diff, unit_cost_rate = calc_plan_actual(
        plan_unit_cost,
        actual_unit_cost,
        "억원/Batch"
    )

    section("계획 대비 실제 자동 비교")

    comparison_df = pd.DataFrame(
        {
            "관리항목": [
                "생산능력",
                "생산실적",
                "가동률",
                "총 제조원가",
                "Batch당 제조원가",
            ],
            "계획": [
                format_value(plan_capacity, "batch"),
                format_value(plan_output, "batch"),
                format_value(plan_utilization, "%"),
                format_value(plan_total_cost, "억원"),
                format_value(plan_unit_cost, "억원/Batch"),
            ],
            "실제": [
                format_value(actual_capacity, "batch"),
                format_value(actual_output, "batch"),
                format_value(actual_utilization, "%"),
                format_value(actual_total_cost, "억원"),
                format_value(actual_unit_cost, "억원/Batch"),
            ],
            "차이(실제-계획)": [
                cap_diff,
                out_diff,
                util_diff,
                total_cost_diff,
                unit_cost_diff,
            ],
            "증감률": [
                cap_rate,
                out_rate,
                util_rate,
                total_cost_rate,
                unit_cost_rate,
            ],
            "값의 성격": [
                "사용자 입력",
                "사용자 입력",
                "자동 계산",
                "사용자 입력",
                "자동 계산",
            ],
        }
    )

    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    st.caption(
        "가동률 차이는 %p로 표시합니다. 증감률은 (실제 - 계획) ÷ 계획 × 100으로 계산합니다. "
        "가동률과 Batch당 제조원가는 입력한 생산능력·생산실적·총 제조원가를 바탕으로 자동 계산됩니다."
    )

    section("차이 해석")
    available_diffs = []

    if plan_capacity is not None and actual_capacity is not None:
        available_diffs.append(("생산능력", actual_capacity - plan_capacity, "batch"))
    if plan_output is not None and actual_output is not None:
        available_diffs.append(("생산실적", actual_output - plan_output, "batch"))
    if plan_utilization is not None and actual_utilization is not None:
        available_diffs.append(("가동률", actual_utilization - plan_utilization, "%p"))
    if plan_total_cost is not None and actual_total_cost is not None:
        available_diffs.append(("총 제조원가", actual_total_cost - plan_total_cost, "억원"))
    if plan_unit_cost is not None and actual_unit_cost is not None:
        available_diffs.append(("Batch당 제조원가", actual_unit_cost - plan_unit_cost, "억원/Batch"))

    if not available_diffs:
        st.info("계획값과 실제값을 입력하면 차이 해석이 자동으로 표시됩니다.")
    else:
        for item, diff, unit in available_diffs:
            if abs(diff) < 1e-12:
                st.write(f"- {item}: 계획과 실제가 동일합니다.")
            elif diff > 0:
                st.write(f"- {item}: 실제가 계획보다 {abs(diff):,.2f}{unit} 높습니다.")
            else:
                st.write(f"- {item}: 실제가 계획보다 {abs(diff):,.2f}{unit} 낮습니다.")

    st.caption(
        "차이의 크기만으로 유리·불리를 단정하지 않습니다. 생산능력·생산실적·가동률의 증가는 원가 감소를 의미하지 않으며, "
        "총 제조원가·Batch당 제조원가의 차이가 확인되면 4번 '원가차이 분석' 탭에서 세부 원가요소별 원인을 분석합니다."
    )

    section("내부 데이터가 있을 경우의 분석 흐름")
    st.markdown(
        """
        <div class="framework">
        계획값 입력 → 실제값 확인/입력 → 차이 자동계산
        → 직접재료원가 / 직접노무원가 / 제조간접원가
        → 원가차이 분석 → 원인 파악 → 개선 및 다음 계획 반영
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# 4. 원가차이 분석
# =========================================================
with tabs[3]:
    tab_intro(
        "원가차이 분석 | 분석 목적과 방법",
        "표준원가와 실제원가를 비교하여 직접재료원가·직접노무원가·제조간접원가에서 발생한 차이를 자동으로 계산합니다.",
        "Management Accounting에서는 원가가 계획과 달라졌다는 결과에서 끝나지 않고 가격·임률·능률 등 어떤 요인에서 차이가 발생했는지 파악해야 하기 때문입니다.",
        "직접재료원가는 가격차이와 능률차이, 직접노무원가는 임률차이와 능률차이, 제조간접원가는 변동·고정제조간접원가 차이로 구분해 분석합니다.",
        "사용자가 표준값과 실제값을 입력하면 차이금액과 유리(F)·불리(U) 여부를 자동 계산하고 가장 큰 차이항목을 보여줍니다.",
        "입력값은 분석 구조를 보여주기 위한 사용자 입력값이며 SK바이오사이언스 또는 특정 연구과제의 실제 수치가 아닙니다.",
    )

    section("원가차이 자동분석")

    st.warning(
        "아래 입력값은 분석 구조를 보여주기 위한 사용자 입력값입니다. "
        "SK바이오사이언스 또는 특정 연구과제의 실제 수치가 아닙니다."
    )

    st.markdown(
        """
        <div class="framework">
        표준원가 입력 → 실제원가 입력 → 원가차이 계산
        → 직접재료원가 / 직접노무원가 / 제조간접원가별 차이 분해
        → 가격·임률·능률 차이 확인 → 주요 원인 파악
        </div>
        """,
        unsafe_allow_html=True,
    )

    dm_tab, dl_tab, moh_tab = st.tabs(["직접재료원가", "직접노무원가", "제조간접원가"])

    # -------------------------
    # 직접재료원가
    # -------------------------
    with dm_tab:
        st.markdown("### 직접재료원가 차이분석")

        basis = st.radio(
            "가격차이 계산 기준",
            ["실제사용량 기준", "실제구입량 기준"],
            horizontal=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            dm_aq_used = st.number_input("실제사용량(AQ 사용)", min_value=0.0, value=0.0, step=1.0)
            dm_aq_purchased = st.number_input("실제구입량(AQ 구입)", min_value=0.0, value=0.0, step=1.0)
            dm_ap = st.number_input("실제가격(AP, 원/단위)", min_value=0.0, value=0.0, step=100.0)
        with c2:
            dm_sq = st.number_input(
                "표준허용량(SQ)",
                min_value=0.0,
                value=0.0,
                step=1.0,
                help="실제 생산량에 허용되는 표준 재료투입량",
            )
            dm_sp = st.number_input("표준가격(SP, 원/단위)", min_value=0.0, value=0.0, step=100.0)

        price_qty = dm_aq_used if basis == "실제사용량 기준" else dm_aq_purchased
        dm_price_var = price_qty * (dm_ap - dm_sp)
        dm_eff_var = dm_sp * (dm_aq_used - dm_sq)
        dm_total_var = dm_aq_used * dm_ap - dm_sq * dm_sp

        m1, m2, m3 = st.columns(3)
        m1.metric("가격차이", f"{abs(dm_price_var):,.0f}원", variance_label(dm_price_var))
        m2.metric("능률차이", f"{abs(dm_eff_var):,.0f}원", variance_label(dm_eff_var))
        m3.metric("사용기준 총원가차이", f"{abs(dm_total_var):,.0f}원", variance_label(dm_total_var))

        dm_result = pd.DataFrame(
            {
                "차이항목": ["직접재료 가격차이", "직접재료 능률차이"],
                "차이금액": [dm_price_var, dm_eff_var],
            }
        )
        st.info(biggest_driver(dm_result))

        st.markdown(
            """
            **계산식**
            - 가격차이 = 가격차이 기준수량 × (실제가격 - 표준가격)
            - 능률차이 = 표준가격 × (실제사용량 - 표준허용량)
            """
        )

        if basis == "실제구입량 기준" and dm_aq_purchased != dm_aq_used:
            st.warning(
                "가격차이를 실제구입량 기준으로 계산하면 실제구입량과 실제사용량이 다를 때 "
                "가격차이 + 능률차이가 사용기준 총원가차이와 일치하지 않을 수 있습니다."
            )

    # -------------------------
    # 직접노무원가
    # -------------------------
    with dl_tab:
        st.markdown("### 직접노무원가 차이분석")

        c1, c2 = st.columns(2)
        with c1:
            dl_ah = st.number_input("실제작업시간(AH)", min_value=0.0, value=0.0, step=1.0)
            dl_ar = st.number_input("실제임률(AR, 원/시간)", min_value=0.0, value=0.0, step=100.0)
        with c2:
            dl_sh = st.number_input(
                "표준허용시간(SH)",
                min_value=0.0,
                value=0.0,
                step=1.0,
                help="실제 생산량에 허용되는 표준 작업시간",
            )
            dl_sr = st.number_input("표준임률(SR, 원/시간)", min_value=0.0, value=0.0, step=100.0)

        dl_rate_var = dl_ah * (dl_ar - dl_sr)
        dl_eff_var = dl_sr * (dl_ah - dl_sh)
        dl_total_var = dl_ah * dl_ar - dl_sh * dl_sr

        m1, m2, m3 = st.columns(3)
        m1.metric("임률차이", f"{abs(dl_rate_var):,.0f}원", variance_label(dl_rate_var))
        m2.metric("능률차이", f"{abs(dl_eff_var):,.0f}원", variance_label(dl_eff_var))
        m3.metric("총 직접노무원가 차이", f"{abs(dl_total_var):,.0f}원", variance_label(dl_total_var))

        dl_result = pd.DataFrame(
            {
                "차이항목": ["직접노무 임률차이", "직접노무 능률차이"],
                "차이금액": [dl_rate_var, dl_eff_var],
            }
        )
        st.info(biggest_driver(dl_result))

        st.markdown(
            """
            **계산식**
            - 임률차이 = 실제작업시간 × (실제임률 - 표준임률)
            - 능률차이 = 표준임률 × (실제작업시간 - 표준허용시간)
            """
        )

    # -------------------------
    # 제조간접원가
    # -------------------------
    with moh_tab:
        st.markdown("### 제조간접원가 차이분석")
        st.caption("변동제조간접원가와 고정제조간접원가는 차이분석 방식이 달라 구분해서 계산합니다.")

        st.markdown("#### 1) 변동제조간접원가")
        c1, c2 = st.columns(2)
        with c1:
            voh_ah = st.number_input("실제조업도(AH)", min_value=0.0, value=0.0, step=1.0)
            voh_actual = st.number_input("실제 변동제조간접원가", min_value=0.0, value=0.0, step=1000.0)
        with c2:
            voh_sh = st.number_input("표준허용조업도(SH)", min_value=0.0, value=0.0, step=1.0)
            voh_sr = st.number_input("표준 변동제조간접원가 배부율", min_value=0.0, value=0.0, step=100.0)

        voh_spending = voh_actual - (voh_ah * voh_sr)
        voh_eff = voh_sr * (voh_ah - voh_sh)

        m1, m2 = st.columns(2)
        m1.metric("소비차이", f"{abs(voh_spending):,.0f}원", variance_label(voh_spending))
        m2.metric("능률차이", f"{abs(voh_eff):,.0f}원", variance_label(voh_eff))

        st.markdown(
            """
            **계산식**
            - 소비차이 = 실제 변동제조간접원가 - 실제조업도 × 표준배부율
            - 능률차이 = 표준배부율 × (실제조업도 - 표준허용조업도)
            """
        )

        st.markdown("#### 2) 고정제조간접원가")
        c1, c2 = st.columns(2)
        with c1:
            foh_actual = st.number_input("실제 고정제조간접원가", min_value=0.0, value=0.0, step=1000.0)
            foh_budget = st.number_input("예산 고정제조간접원가", min_value=0.0, value=0.0, step=1000.0)
        with c2:
            foh_denominator = st.number_input("기준조업도", min_value=0.0, value=0.0, step=1.0)
            foh_sh = st.number_input("표준허용조업도", min_value=0.0, value=0.0, step=1.0, key="foh_sh")

        foh_rate = foh_budget / foh_denominator if foh_denominator > 0 else 0.0
        foh_applied = foh_sh * foh_rate
        foh_budget_var = foh_actual - foh_budget
        foh_volume_var = foh_budget - foh_applied

        m1, m2 = st.columns(2)
        m1.metric("예산차이", f"{abs(foh_budget_var):,.0f}원", variance_label(foh_budget_var))
        m2.metric("조업도차이", f"{abs(foh_volume_var):,.0f}원", variance_label(foh_volume_var))

        st.markdown(
            """
            **계산식**
            - 표준배부율 = 예산 고정제조간접원가 ÷ 기준조업도
            - 예산차이 = 실제 고정제조간접원가 - 예산 고정제조간접원가
            - 조업도차이 = 예산 고정제조간접원가 - 배부 고정제조간접원가
            """
        )

    # -------------------------
    # 종합결과
    # -------------------------
    st.divider()
    section("C. 원가차이 종합결과")

    summary_df = pd.DataFrame(
        {
            "차이항목": [
                "직접재료 가격차이",
                "직접재료 능률차이",
                "직접노무 임률차이",
                "직접노무 능률차이",
                "변동제조간접원가 소비차이",
                "변동제조간접원가 능률차이",
                "고정제조간접원가 예산차이",
                "고정제조간접원가 조업도차이",
            ],
            "차이금액": [
                dm_price_var,
                dm_eff_var,
                dl_rate_var,
                dl_eff_var,
                voh_spending,
                voh_eff,
                foh_budget_var,
                foh_volume_var,
            ],
        }
    )
    summary_df["판정"] = summary_df["차이금액"].apply(variance_label)

    display_df = summary_df.copy()
    display_df["차이금액"] = display_df["차이금액"].map(lambda x: f"{abs(x):,.0f}원")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    fig2 = px.bar(summary_df, x="차이항목", y="차이금액", title="세부 원가차이")
    fig2.update_layout(xaxis_title="", yaxis_title="차이금액(원)")
    st.plotly_chart(fig2, use_container_width=True)

    st.info(biggest_driver(summary_df))
    st.caption("양수(+)는 불리한 차이(U), 음수(-)는 유리한 차이(F)입니다.")

# =========================================================
# 5. 프로젝트 최종결론
# =========================================================
with tabs[4]:
    st.subheader("프로젝트 최종결론")

    st.markdown(
        """
        공개자료만으로 L HOUSE의 실제 총 제조원가나 연구과제별 제조비를 계산할 수는 없습니다.
        따라서 공개되지 않은 숫자를 추정하는 대신, 공개자료에서 확인할 수 있는 연구개발·미래성장 투자 현황과
        실제 직무에서 활용 가능한 계획 대비 실적 및 원가차이 분석 구조를 분리했습니다.

        연구개발 투자현황에서는 333억원 등 미래성장 투자금액을 실제 제조비로 간주하지 않았습니다.
        대신 사내 데이터가 제공된다는 가정 아래 직접재료원가·직접노무원가·제조간접원가의
        표준값과 실제값을 입력해 가격차이·임률차이·능률차이 등을 자동 분석하도록 구성했습니다.

        이를 통해 Management Accounting을
        **「계획과 실제의 차이를 계산하고, 차이가 어떤 원가요소에서 발생했는지 파악해 다음 의사결정에 반영하는 업무」**
        로 표현하고자 했습니다.
        """
    )

    st.success("핵심: 계획 → 실적 → 원가차이 → 원인 파악 → 개선 및 다음 계획 반영")
