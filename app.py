import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
from fpdf import FPDF
from io import BytesIO
import base64
from datetime import datetime

# ─── Page Config ───
st.set_page_config(
    page_title="MobilityAI Navigator",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #1a365d 0%, #2d5a8e 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 { color: white; margin: 0; font-size: 2rem; font-weight: 700; }
    .main-header p { color: #b8d4f0; margin: 0.5rem 0 0 0; font-size: 1.05rem; }
    
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .metric-card h3 { color: #1a365d; font-size: 2rem; margin: 0; }
    .metric-card p { color: #64748b; font-size: 0.9rem; margin: 0.25rem 0 0 0; }
    
    .maturity-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1.1rem;
        color: white;
    }
    .maturity-1 { background: #ef4444; }
    .maturity-2 { background: #f97316; }
    .maturity-3 { background: #eab308; color: #1a1a1a; }
    .maturity-4 { background: #22c55e; }
    .maturity-5 { background: #1a365d; }
    
    .use-case-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .use-case-card h4 { color: #1a365d; margin: 0 0 0.5rem 0; }
    
    .pillar-tag {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 15px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.4rem;
    }
    .pillar-punctuality { background: #dbeafe; color: #1e40af; }
    .pillar-reliability { background: #dcfce7; color: #166534; }
    .pillar-efficiency { background: #fef3c7; color: #92400e; }
    .pillar-sustainability { background: #d1fae5; color: #065f46; }
    
    div[data-testid="stSidebar"] { background: #f8fafc; }
    .stRadio > div { gap: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ─── Translations ───
T = {
    "en": {
        "title": "MobilityAI Navigator",
        "subtitle": "AI Readiness Assessment, Use Case Recommender & Adoption Playbook for Rail & Mobility",
        "nav_home": "Home",
        "nav_assess": "AI Readiness Assessment",
        "nav_usecases": "Use Case Recommender",
        "nav_community": "Community Playbook",
        "nav_report": "Download Report",
        "home_welcome": "Welcome",
        "home_desc": "This tool helps digitalization consulting teams assess AI readiness, discover relevant use cases, and design adoption strategies — specifically calibrated for rail and mobility organizations.",
        "home_m1": "Readiness Assessment",
        "home_m1_desc": "Evaluate AI maturity across 8 dimensions adapted for rail & mobility",
        "home_m2": "Use Case Recommender",
        "home_m2_desc": "Discover 40+ real AI implementations from global rail operators",
        "home_m3": "Community Playbook",
        "home_m3_desc": "Generate tailored AI adoption and community-building strategies",
        "assess_title": "AI Readiness Assessment",
        "assess_desc": "Answer the following questions to evaluate your organization's AI maturity. Each dimension is scored 1-5.",
        "assess_btn": "Calculate Readiness Score",
        "results_title": "Assessment Results",
        "maturity_levels": {
            1: "Exploring",
            2: "Planning", 
            3: "Implementing",
            4: "Scaling",
            5: "Transforming"
        },
        "maturity_descriptions": {
            1: "The organization is beginning to explore AI opportunities. Focus on building awareness and foundational data capabilities.",
            2: "Initial AI strategy is taking shape. Focus on data quality, pilot selection, and governance frameworks.",
            3: "AI pilots are underway with measurable results. Focus on standardization, scaling infrastructure, and change management.",
            4: "AI is integrated into multiple business processes. Focus on cross-functional scaling, community building, and ROI optimization.",
            5: "AI is a core part of organizational strategy and culture. Focus on innovation leadership and ecosystem development."
        },
        "strengths": "Key Strengths",
        "gaps": "Critical Gaps",
        "uc_title": "Use Case Recommender",
        "uc_desc": "Based on your readiness profile, here are the most relevant AI use cases for your organization.",
        "uc_filter_pillar": "Filter by S3 Pillar",
        "uc_filter_cat": "Filter by Category",
        "uc_filter_complexity": "Filter by Complexity",
        "uc_all": "All",
        "uc_no_assessment": "Complete the Readiness Assessment first to get personalized recommendations, or browse all use cases below.",
        "community_title": "Community Adoption Playbook",
        "community_desc": "AI adoption fails 88% of the time — almost always for organizational, not technical reasons. This playbook helps you build the community infrastructure needed for success.",
        "report_title": "Download Report",
        "report_desc": "Generate a consulting-quality PDF report with your assessment results, recommended use cases, and adoption playbook.",
        "report_btn": "Generate PDF Report",
        "report_no_data": "Please complete the Readiness Assessment first to generate a report.",
        "dimensions": {
            "strategy": "Strategy & Leadership",
            "data": "Data Readiness",
            "technology": "Technology & Infrastructure",
            "talent": "Talent & Skills",
            "governance": "Governance & Ethics",
            "culture": "Culture & Change Readiness",
            "safety": "Safety & Regulatory",
            "collaboration": "Cross-Org Collaboration"
        },
        "questions": {
            "strategy": [
                "AI is part of our organization's strategic roadmap",
                "Leadership actively sponsors and champions AI initiatives",
                "We have allocated dedicated budget for AI projects"
            ],
            "data": [
                "Our core operational data is digitized and accessible",
                "We have established data quality standards and processes",
                "Data is shared effectively across departments and teams"
            ],
            "technology": [
                "We have cloud infrastructure or platforms to support AI workloads",
                "We use BI/analytics tools (Power BI, Tableau, etc.) regularly",
                "We have development environments for prototyping AI solutions"
            ],
            "talent": [
                "We have staff with data science or AI skills",
                "Employees receive training on digital tools and AI concepts",
                "We can attract or access AI talent when needed"
            ],
            "governance": [
                "We have clear policies for AI ethics and responsible use",
                "Data privacy and GDPR compliance processes are established",
                "There are defined approval processes for new AI deployments"
            ],
            "culture": [
                "Employees are open to adopting new digital tools",
                "There is a culture of experimentation and learning from failure",
                "Change management support is available for new technology rollouts"
            ],
            "safety": [
                "AI deployments consider rail safety certification requirements",
                "Works council / employee representatives are involved in AI decisions",
                "Regulatory compliance (e.g., CENELEC, EN 5012x) is integrated into AI planning"
            ],
            "collaboration": [
                "We actively share knowledge and solutions with other departments or subsidiaries",
                "There are established channels for cross-team collaboration on digital projects",
                "We reuse solutions from other parts of the organization rather than building from scratch"
            ]
        },
        "scale_labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
        "complexity": {"Low": "Low", "Medium": "Medium", "High": "High"},
        "impact_vs_feasibility": "Impact vs. Feasibility Matrix",
        "recommended_for_you": "Recommended for Your Maturity Level",
        "all_use_cases": "All Use Cases",
        "operator": "Operator",
        "impact": "Impact",
        "time_to_value": "Time to Value",
        "maturity_req": "Min. Maturity Required",
        "s3_pillar": "S3 Pillar",
        "sustainability": "Sustainability Impact"
    },
    "de": {
        "title": "MobilityAI Navigator",
        "subtitle": "KI-Reifegradanalyse, Use-Case-Empfehlung & Adoptions-Playbook für Schiene & Mobilität",
        "nav_home": "Startseite",
        "nav_assess": "KI-Reifegradanalyse",
        "nav_usecases": "Use-Case-Empfehlung",
        "nav_community": "Community-Playbook",
        "nav_report": "Bericht herunterladen",
        "home_welcome": "Willkommen",
        "home_desc": "Dieses Tool hilft Digitalisierungs-Beratungsteams bei der Bewertung der KI-Reife, der Entdeckung relevanter Use Cases und der Gestaltung von Adoptionsstrategien — speziell kalibriert für Schiene und Mobilität.",
        "home_m1": "Reifegradanalyse",
        "home_m1_desc": "KI-Reifegrad über 8 Dimensionen bewerten, angepasst an Schiene & Mobilität",
        "home_m2": "Use-Case-Empfehlung",
        "home_m2_desc": "Über 40 reale KI-Implementierungen von internationalen Bahnbetreibern entdecken",
        "home_m3": "Community-Playbook",
        "home_m3_desc": "Maßgeschneiderte KI-Adoptions- und Community-Building-Strategien generieren",
        "assess_title": "KI-Reifegradanalyse",
        "assess_desc": "Beantworten Sie die folgenden Fragen zur Bewertung der KI-Reife Ihrer Organisation. Jede Dimension wird von 1-5 bewertet.",
        "assess_btn": "Reifegrad berechnen",
        "results_title": "Analyseergebnisse",
        "maturity_levels": {
            1: "Erkundend",
            2: "Planend",
            3: "Implementierend",
            4: "Skalierend",
            5: "Transformierend"
        },
        "maturity_descriptions": {
            1: "Die Organisation beginnt, KI-Möglichkeiten zu erkunden. Fokus auf Bewusstseinsbildung und grundlegende Datenfähigkeiten.",
            2: "Eine erste KI-Strategie nimmt Gestalt an. Fokus auf Datenqualität, Pilotauswahl und Governance-Frameworks.",
            3: "KI-Piloten laufen mit messbaren Ergebnissen. Fokus auf Standardisierung, Skalierungsinfrastruktur und Change Management.",
            4: "KI ist in mehrere Geschäftsprozesse integriert. Fokus auf funktionsübergreifende Skalierung und Community-Building.",
            5: "KI ist ein Kernbestandteil der Organisationsstrategie und -kultur. Fokus auf Innovationsführerschaft."
        },
        "strengths": "Stärken",
        "gaps": "Kritische Lücken",
        "uc_title": "Use-Case-Empfehlung",
        "uc_desc": "Basierend auf Ihrem Reifegradprofil sind hier die relevantesten KI-Use-Cases für Ihre Organisation.",
        "uc_filter_pillar": "Nach S3-Säule filtern",
        "uc_filter_cat": "Nach Kategorie filtern",
        "uc_filter_complexity": "Nach Komplexität filtern",
        "uc_all": "Alle",
        "uc_no_assessment": "Führen Sie zuerst die Reifegradanalyse durch, um personalisierte Empfehlungen zu erhalten, oder durchsuchen Sie alle Use Cases unten.",
        "community_title": "Community-Adoptions-Playbook",
        "community_desc": "88% der KI-Piloten scheitern — fast immer aus organisatorischen, nicht technischen Gründen. Dieses Playbook hilft Ihnen, die nötige Community-Infrastruktur aufzubauen.",
        "report_title": "Bericht herunterladen",
        "report_desc": "Erstellen Sie einen beratungsqualitätsgemäßen PDF-Bericht mit Ihren Analyseergebnissen, empfohlenen Use Cases und Adoptions-Playbook.",
        "report_btn": "PDF-Bericht erstellen",
        "report_no_data": "Bitte führen Sie zuerst die Reifegradanalyse durch.",
        "dimensions": {
            "strategy": "Strategie & Führung",
            "data": "Datenbereitschaft",
            "technology": "Technologie & Infrastruktur",
            "talent": "Talent & Kompetenzen",
            "governance": "Governance & Ethik",
            "culture": "Kultur & Veränderungsbereitschaft",
            "safety": "Sicherheit & Regulierung",
            "collaboration": "Organisationsübergreifende Zusammenarbeit"
        },
        "questions": {
            "strategy": [
                "KI ist Teil der strategischen Roadmap unserer Organisation",
                "Die Führungsebene sponsert und fördert KI-Initiativen aktiv",
                "Wir haben ein dediziertes Budget für KI-Projekte zugewiesen"
            ],
            "data": [
                "Unsere Kernbetriebsdaten sind digitalisiert und zugänglich",
                "Wir haben Datenqualitätsstandards und -prozesse etabliert",
                "Daten werden effektiv über Abteilungen hinweg geteilt"
            ],
            "technology": [
                "Wir haben Cloud-Infrastruktur zur Unterstützung von KI-Workloads",
                "Wir nutzen BI-/Analytics-Tools (Power BI, Tableau, etc.) regelmäßig",
                "Wir haben Entwicklungsumgebungen zum Prototyping von KI-Lösungen"
            ],
            "talent": [
                "Wir haben Mitarbeitende mit Data-Science- oder KI-Kompetenzen",
                "Mitarbeitende erhalten Schulungen zu digitalen Tools und KI-Konzepten",
                "Wir können bei Bedarf KI-Talente gewinnen oder darauf zugreifen"
            ],
            "governance": [
                "Wir haben klare Richtlinien für KI-Ethik und verantwortungsvolle Nutzung",
                "Datenschutz- und DSGVO-Compliance-Prozesse sind etabliert",
                "Es gibt definierte Genehmigungsprozesse für neue KI-Deployments"
            ],
            "culture": [
                "Mitarbeitende sind offen für die Einführung neuer digitaler Tools",
                "Es gibt eine Kultur des Experimentierens und Lernens aus Fehlern",
                "Change-Management-Unterstützung ist für neue Technologie-Rollouts verfügbar"
            ],
            "safety": [
                "KI-Deployments berücksichtigen Eisenbahn-Sicherheitszertifizierungen",
                "Der Betriebsrat ist in KI-Entscheidungen eingebunden",
                "Regulatorische Compliance (z.B. CENELEC, EN 5012x) ist in die KI-Planung integriert"
            ],
            "collaboration": [
                "Wir teilen aktiv Wissen und Lösungen mit anderen Abteilungen oder Tochtergesellschaften",
                "Es gibt etablierte Kanäle für teamübergreifende Zusammenarbeit bei Digitalprojekten",
                "Wir nutzen Lösungen aus anderen Teilen der Organisation wieder, statt neu zu entwickeln"
            ]
        },
        "scale_labels": ["Stimme gar nicht zu", "Stimme nicht zu", "Neutral", "Stimme zu", "Stimme voll zu"],
        "complexity": {"Low": "Niedrig", "Medium": "Mittel", "High": "Hoch"},
        "impact_vs_feasibility": "Wirkung vs. Machbarkeit",
        "recommended_for_you": "Empfohlen für Ihren Reifegrad",
        "all_use_cases": "Alle Use Cases",
        "operator": "Betreiber",
        "impact": "Wirkung",
        "time_to_value": "Time-to-Value",
        "maturity_req": "Min. Reifegrad erforderlich",
        "s3_pillar": "S3-Säule",
        "sustainability": "Nachhaltigkeitswirkung"
    }
}

# ─── Session State Init ───
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "scores" not in st.session_state:
    st.session_state.scores = None
if "maturity_level" not in st.session_state:
    st.session_state.maturity_level = None
if "dimension_scores" not in st.session_state:
    st.session_state.dimension_scores = {}

def t(key):
    """Get translation for current language."""
    keys = key.split(".")
    val = T[st.session_state.lang]
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k, key)
        else:
            return key
    return val

# ─── Load Use Cases ───
@st.cache_data
def load_use_cases():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "use_cases.json"), "r", encoding="utf-8") as f:
        return json.load(f)

use_cases = load_use_cases()

# ─── Sidebar ───
with st.sidebar:
    st.markdown("### 🌐 Language / Sprache")
    lang_choice = st.radio("", ["English", "Deutsch"], 
                           index=0 if st.session_state.lang == "en" else 1,
                           label_visibility="collapsed")
    st.session_state.lang = "en" if lang_choice == "English" else "de"
    
    st.markdown("---")
    st.markdown(f"### 🧭 Navigation")
    
    pages = {
        t("nav_home"): "home",
        t("nav_assess"): "assess", 
        t("nav_usecases"): "usecases",
        t("nav_community"): "community",
        t("nav_report"): "report"
    }
    
    selected_label = st.radio("", list(pages.keys()), label_visibility="collapsed")
    page = pages[selected_label]
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color: #94a3b8; font-size: 0.8rem;'>
        <p>Built for<br><strong>DB Engineering & Consulting</strong><br>Smart Mobility & Digitalization</p>
        <p style='margin-top:1rem;'>Methodology based on<br>Gartner · Cisco · McKinsey<br>adapted for rail & mobility</p>
    </div>
    """, unsafe_allow_html=True)

# ─── HOME PAGE ───
if page == "home":
    st.markdown(f"""
    <div class="main-header">
        <h1>🚄 {t('title')}</h1>
        <p>{t('subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### {t('home_welcome')}")
    st.markdown(t("home_desc"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊</h3>
            <p><strong>{t('home_m1')}</strong></p>
            <p>{t('home_m1_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯</h3>
            <p><strong>{t('home_m2')}</strong></p>
            <p>{t('home_m2_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🤝</h3>
            <p><strong>{t('home_m3')}</strong></p>
            <p>{t('home_m3_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("**Methodology:** Assessment framework synthesized from Gartner (AI Maturity Model), Cisco (AI Readiness Index), and McKinsey (Rewired), adapted with two rail-specific dimensions: Safety & Regulatory Readiness and Cross-Organizational Collaboration.")
    st.markdown("**Use Case Database:** 40+ real implementations from Deutsche Bahn, SNCF, SBB, MTR, JR East, Trenitalia, Knorr-Bremse, Optibus, and others — aligned to DB's S3 strategy pillars (Punctuality, Reliability, Economic Efficiency).")

# ─── ASSESSMENT PAGE ───
elif page == "assess":
    st.markdown(f"## 📊 {t('assess_title')}")
    st.markdown(t("assess_desc"))
    
    lang = st.session_state.lang
    dimensions = T[lang]["dimensions"]
    questions = T[lang]["questions"]
    scale_labels = T[lang]["scale_labels"]
    
    responses = {}
    
    for dim_key, dim_name in dimensions.items():
        with st.expander(f"**{dim_name}**", expanded=True):
            dim_responses = []
            for i, question in enumerate(questions[dim_key]):
                val = st.select_slider(
                    question,
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    format_func=lambda x: f"{x} — {scale_labels[x-1]}",
                    key=f"{dim_key}_{i}"
                )
                dim_responses.append(val)
            responses[dim_key] = dim_responses
    
    st.markdown("---")
    
    if st.button(f"🚀 {t('assess_btn')}", type="primary", use_container_width=True):
        # Calculate scores with weighting
        weights = {
            "strategy": 1.5, "data": 1.5, "technology": 1.0, "talent": 1.0,
            "governance": 1.0, "culture": 1.0, "safety": 1.0, "collaboration": 1.0
        }
        
        dimension_scores = {}
        for dim_key, vals in responses.items():
            dimension_scores[dim_key] = sum(vals) / len(vals)
        
        weighted_sum = sum(dimension_scores[k] * weights[k] for k in dimension_scores)
        total_weight = sum(weights.values())
        overall_score = weighted_sum / total_weight
        
        if overall_score < 2.0: maturity = 1
        elif overall_score < 2.7: maturity = 2
        elif overall_score < 3.4: maturity = 3
        elif overall_score < 4.2: maturity = 4
        else: maturity = 5
        
        st.session_state.dimension_scores = dimension_scores
        st.session_state.maturity_level = maturity
        st.session_state.overall_score = overall_score
        
        # ─── RESULTS ───
        st.markdown(f"## {t('results_title')}")
        
        level_name = T[lang]["maturity_levels"][maturity]
        st.markdown(f'<div style="text-align:center; margin: 1.5rem 0;"><span class="maturity-badge maturity-{maturity}">Level {maturity}: {level_name}</span></div>', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#64748b;'>{T[lang]['maturity_descriptions'][maturity]}</p>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Radar chart
            dim_names = [T[lang]["dimensions"][k] for k in dimension_scores]
            dim_vals = list(dimension_scores.values())
            benchmark = [2.5] * len(dim_names)  # Industry average
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=dim_vals + [dim_vals[0]],
                theta=dim_names + [dim_names[0]],
                fill='toself',
                name='Your Organization' if lang == 'en' else 'Ihre Organisation',
                fillcolor='rgba(26, 54, 93, 0.2)',
                line=dict(color='#1a365d', width=2)
            ))
            fig.add_trace(go.Scatterpolar(
                r=benchmark + [benchmark[0]],
                theta=dim_names + [dim_names[0]],
                fill='toself',
                name='Rail Industry Average' if lang == 'en' else 'Branchendurchschnitt',
                fillcolor='rgba(148, 163, 184, 0.1)',
                line=dict(color='#94a3b8', width=1, dash='dash')
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5], tickvals=[1,2,3,4,5])),
                showlegend=True,
                height=450,
                margin=dict(t=30, b=30),
                font=dict(family="Source Sans 3")
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
            
            st.markdown(f"#### ✅ {t('strengths')}")
            for dim_key, score in sorted_dims[:2]:
                st.markdown(f"- **{T[lang]['dimensions'][dim_key]}**: {score:.1f}/5.0")
            
            st.markdown(f"#### ⚠️ {t('gaps')}")
            for dim_key, score in sorted_dims[-2:]:
                st.markdown(f"- **{T[lang]['dimensions'][dim_key]}**: {score:.1f}/5.0")
            
            st.markdown("---")
            st.markdown(f"**Overall Score:** {overall_score:.2f}/5.0")

# ─── USE CASES PAGE ───
elif page == "usecases":
    st.markdown(f"## 🎯 {t('uc_title')}")
    st.markdown(t("uc_desc"))
    
    lang = st.session_state.lang
    
    if st.session_state.maturity_level is None:
        st.info(t("uc_no_assessment"))
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        pillars = [t("uc_all"), "Punctuality", "Reliability", "Economic Efficiency"]
        selected_pillar = st.selectbox(t("uc_filter_pillar"), pillars)
    with col2:
        categories = [t("uc_all")] + sorted(set(uc["category"] for uc in use_cases))
        selected_cat = st.selectbox(t("uc_filter_cat"), categories)
    with col3:
        complexities = [t("uc_all"), "Low", "Medium", "High"]
        selected_complexity = st.selectbox(t("uc_filter_complexity"), complexities)
    
    # Filter use cases
    filtered = use_cases.copy()
    if selected_pillar != t("uc_all"):
        filtered = [uc for uc in filtered if uc["s3_pillar"] == selected_pillar]
    if selected_cat != t("uc_all"):
        filtered = [uc for uc in filtered if uc["category"] == selected_cat]
    if selected_complexity != t("uc_all"):
        filtered = [uc for uc in filtered if uc["complexity"] == selected_complexity]
    
    # Show recommended if assessment done
    if st.session_state.maturity_level:
        maturity = st.session_state.maturity_level
        recommended = [uc for uc in filtered if uc["maturity_required"] <= maturity]
        
        st.markdown(f"### {t('recommended_for_you')}")
        
        # Impact vs feasibility chart
        if recommended:
            complexity_map = {"Low": 5, "Medium": 3, "High": 1}
            chart_data = []
            for uc in recommended:
                chart_data.append({
                    "name": uc["name"] if lang == "en" else uc.get("name_de", uc["name"]),
                    "feasibility": complexity_map[uc["complexity"]],
                    "impact": 6 - uc["maturity_required"],
                    "pillar": uc["s3_pillar"],
                    "category": uc["category"]
                })
            
            df_chart = pd.DataFrame(chart_data)
            
            color_map = {
                "Punctuality": "#3b82f6",
                "Reliability": "#22c55e", 
                "Economic Efficiency": "#f59e0b"
            }
            
            fig = px.scatter(
                df_chart, x="feasibility", y="impact", 
                color="pillar", text="name",
                color_discrete_map=color_map,
                labels={
                    "feasibility": "Feasibility →" if lang == "en" else "Machbarkeit →",
                    "impact": "Impact →" if lang == "en" else "Wirkung →",
                    "pillar": "S3 Pillar" if lang == "en" else "S3-Säule"
                }
            )
            fig.update_traces(textposition='top center', marker=dict(size=12))
            fig.update_layout(
                height=450,
                xaxis=dict(range=[0, 6], dtick=1),
                yaxis=dict(range=[0, 6], dtick=1),
                font=dict(family="Source Sans 3"),
                margin=dict(t=30)
            )
            # Add quadrant labels
            fig.add_annotation(x=4.5, y=4.5, text="⭐ Quick Wins", showarrow=False, font=dict(size=14, color="#22c55e"))
            fig.add_annotation(x=1.5, y=4.5, text="🔬 Strategic Bets", showarrow=False, font=dict(size=14, color="#f59e0b"))
            fig.add_annotation(x=4.5, y=1.5, text="✅ Low Effort", showarrow=False, font=dict(size=14, color="#94a3b8"))
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Use case cards
    st.markdown(f"### {t('all_use_cases')} ({len(filtered)})")
    
    for uc in filtered:
        name = uc["name"] if lang == "en" else uc.get("name_de", uc["name"])
        desc = uc["description"] if lang == "en" else uc.get("description_de", uc["description"])
        
        pillar_class = {
            "Punctuality": "pillar-punctuality",
            "Reliability": "pillar-reliability",
            "Economic Efficiency": "pillar-efficiency"
        }.get(uc["s3_pillar"], "")
        
        sust_tag = ""
        if uc["sustainability"]:
            sust_tag = f'<span class="pillar-tag pillar-sustainability">🌱 {uc.get("sustainability_note", "Sustainability")}</span>'
        
        with st.container():
            st.markdown(f"""
            <div class="use-case-card">
                <h4>{name}</h4>
                <p>{desc}</p>
                <span class="pillar-tag {pillar_class}">{uc['s3_pillar']}</span>
                <span class="pillar-tag" style="background:#f1f5f9; color:#475569;">{uc['category']}</span>
                <span class="pillar-tag" style="background:#f1f5f9; color:#475569;">{uc['complexity']}</span>
                {sust_tag}
                <p style="margin-top:0.5rem; color:#64748b; font-size:0.85rem;">
                    <strong>{t('operator')}:</strong> {uc['operator']} · 
                    <strong>{t('impact')}:</strong> {uc['impact']} · 
                    <strong>{t('maturity_req')}:</strong> Level {uc['maturity_required']}
                </p>
            </div>
            """, unsafe_allow_html=True)

# ─── COMMUNITY PAGE ───
elif page == "community":
    st.markdown(f"## 🤝 {t('community_title')}")
    st.markdown(t("community_desc"))
    
    maturity = st.session_state.maturity_level
    
    if maturity is None:
        st.info("Complete the Readiness Assessment first for a personalized playbook. Showing general guidance below." if st.session_state.lang == "en" else "Führen Sie zuerst die Reifegradanalyse durch. Allgemeine Empfehlungen werden unten angezeigt.")
        maturity = 2  # Default
    
    playbooks = {
        1: {
            "title_en": "Foundation Building — Awareness & First Steps",
            "title_de": "Grundlagen schaffen — Bewusstsein & erste Schritte",
            "champion_ratio": "2-3% of users",
            "activities_en": [
                "**AI Awareness Sessions (Monthly):** 30-minute presentations showing real examples of AI in rail from other operators. No technical jargon — focus on business outcomes.",
                "**Curated Prompt Library:** Create a shared collection of 20-30 useful prompts for common tasks (email drafting, document summarization, data analysis). Lower the entry barrier.",
                "**Identify 3-5 Early Adopters:** Find the people who are already experimenting with AI tools. Give them a title ('AI Scout'), visibility, and 2 hours/week of dedicated time."
            ],
            "activities_de": [
                "**KI-Awareness-Sessions (Monatlich):** 30-Minuten-Präsentationen mit realen KI-Beispielen aus der Bahnbranche. Kein technischer Jargon — Fokus auf Geschäftsergebnisse.",
                "**Kuratierte Prompt-Bibliothek:** Gemeinsame Sammlung von 20-30 nützlichen Prompts für häufige Aufgaben erstellen. Einstiegshürde senken.",
                "**3-5 Early Adopters identifizieren:** Mitarbeitende finden, die bereits mit KI-Tools experimentieren. Titel ('KI-Scout'), Sichtbarkeit und 2 Stunden/Woche geben."
            ],
            "kpis_en": ["Number of employees who tried an AI tool", "Prompt library usage count", "Attendance at awareness sessions"],
            "kpis_de": ["Anzahl Mitarbeitender, die ein KI-Tool ausprobiert haben", "Nutzungshäufigkeit der Prompt-Bibliothek", "Teilnahme an Awareness-Sessions"],
            "timeline": "0-3 months"
        },
        2: {
            "title_en": "Pilot & Learn — Structured Experimentation",
            "title_de": "Pilot & Lernen — Strukturiertes Experimentieren",
            "champion_ratio": "5% of users",
            "activities_en": [
                "**Lunch & Learn Series (Bi-weekly):** 45-minute sessions where teams present their AI experiments — successes AND failures. Build psychological safety around experimentation.",
                "**Use Case Submission Portal:** Simple form where any employee can submit AI use case ideas. Review monthly. Celebrate contributors publicly.",
                "**Pilot Showcase Events (Quarterly):** Demo days where pilot teams show real results. Invite leadership. Create internal case studies from successful pilots."
            ],
            "activities_de": [
                "**Lunch & Learn Serie (Zweiwöchentlich):** 45-Minuten-Sessions, in denen Teams ihre KI-Experimente präsentieren — Erfolge UND Misserfolge.",
                "**Use-Case-Einreichungsportal:** Einfaches Formular für KI-Ideen aller Mitarbeitenden. Monatlich prüfen. Beitragende öffentlich würdigen.",
                "**Pilot-Showcase-Events (Vierteljährlich):** Demo-Tage, an denen Pilot-Teams echte Ergebnisse zeigen. Führungsebene einladen."
            ],
            "kpis_en": ["Number of use cases submitted", "Number of pilots launched", "Time from idea to pilot"],
            "kpis_de": ["Anzahl eingereichter Use Cases", "Anzahl gestarteter Piloten", "Zeit von Idee bis Pilot"],
            "timeline": "3-6 months"
        },
        3: {
            "title_en": "Scale & Standardize — From Pilot to Practice",
            "title_de": "Skalieren & Standardisieren — Vom Pilot zur Praxis",
            "champion_ratio": "5-8% of users",
            "activities_en": [
                "**AI Champions Network:** Designate 1 champion per 15-20 employees. Give them training, a Slack/Teams channel, and monthly meetups. They become the local support layer.",
                "**Internal AI Hackathon (Bi-annual):** 2-day event where cross-functional teams prototype solutions for real business problems. Budget for prizes and implementation of winners.",
                "**Standardized Playbooks:** Create step-by-step guides for the 5 most common AI use cases in your organization. Make them self-service."
            ],
            "activities_de": [
                "**KI-Champions-Netzwerk:** 1 Champion pro 15-20 Mitarbeitende. Schulung, Slack/Teams-Kanal und monatliche Treffen. Sie werden zur lokalen Unterstützungsebene.",
                "**Interner KI-Hackathon (Halbjährlich):** 2-Tage-Event, bei dem funktionsübergreifende Teams Lösungen für echte Geschäftsprobleme prototypisieren.",
                "**Standardisierte Playbooks:** Schritt-für-Schritt-Anleitungen für die 5 häufigsten KI-Anwendungsfälle in Ihrer Organisation erstellen."
            ],
            "kpis_en": ["% of employees using AI tools weekly", "Number of scaled (non-pilot) AI implementations", "Champion network engagement rate"],
            "kpis_de": ["% der Mitarbeitenden, die wöchentlich KI-Tools nutzen", "Anzahl skalierter KI-Implementierungen", "Engagement-Rate des Champion-Netzwerks"],
            "timeline": "6-12 months"
        },
        4: {
            "title_en": "Embed & Optimize — AI as Standard Practice",
            "title_de": "Einbetten & Optimieren — KI als Standardpraxis",
            "champion_ratio": "8-10% of users",
            "activities_en": [
                "**AI Center of Excellence:** Formal team that governs AI standards, shares best practices across subsidiaries, and manages the AI use case portfolio.",
                "**Gamification (Galaxy Passport Model):** Award points/badges for AI tool adoption, use case submissions, and knowledge sharing. Leaderboards create friendly competition.",
                "**Cross-Subsidiary Knowledge Exchange:** Quarterly sessions where teams from different entities (e.g., infraView, ESE, inno2grid) share AI solutions that could be reused."
            ],
            "activities_de": [
                "**KI Center of Excellence:** Formales Team für KI-Standards, Best-Practice-Austausch über Tochtergesellschaften und Portfolio-Management.",
                "**Gamification (Galaxy-Passport-Modell):** Punkte/Badges für KI-Tool-Nutzung, Use-Case-Einreichungen und Wissensaustausch vergeben.",
                "**Organisationsübergreifender Wissensaustausch:** Vierteljährliche Sessions, in denen Teams verschiedener Einheiten KI-Lösungen teilen."
            ],
            "kpis_en": ["ROI of AI implementations", "Cross-subsidiary solution reuse rate", "Employee AI proficiency scores"],
            "kpis_de": ["ROI der KI-Implementierungen", "Wiederverwendungsrate von Lösungen über Tochtergesellschaften", "KI-Kompetenzniveau der Mitarbeitenden"],
            "timeline": "12-18 months"
        },
        5: {
            "title_en": "Lead & Innovate — Industry Leadership",
            "title_de": "Führen & Innovieren — Branchenführerschaft",
            "champion_ratio": "10%+ of users",
            "activities_en": [
                "**External AI Community Leadership:** Host industry events, publish case studies, contribute to UIC/UITP knowledge sharing on AI in rail.",
                "**Innovation Lab / AI Sandbox:** Dedicated environment where teams experiment with emerging technologies (foundation models, AI agents, digital twins).",
                "**Ecosystem Development:** Build partnerships with startups, research institutions, and technology partners to co-develop novel AI solutions."
            ],
            "activities_de": [
                "**Externe KI-Community-Führung:** Branchenevents veranstalten, Fallstudien veröffentlichen, zu UIC/UITP-Wissensaustausch beitragen.",
                "**Innovationslabor / KI-Sandbox:** Dedizierte Umgebung für Experimente mit neuen Technologien (Foundation Models, KI-Agenten, digitale Zwillinge).",
                "**Ökosystem-Entwicklung:** Partnerschaften mit Startups, Forschungseinrichtungen und Technologiepartnern aufbauen."
            ],
            "kpis_en": ["Industry recognition / publications", "Revenue from AI-powered consulting services", "Patent or IP development"],
            "kpis_de": ["Branchenanerkennung / Publikationen", "Umsatz aus KI-gestützten Beratungsleistungen", "Patent- oder IP-Entwicklung"],
            "timeline": "18+ months"
        }
    }
    
    pb = playbooks[maturity]
    lang = st.session_state.lang
    
    title = pb[f"title_{lang}"]
    activities = pb[f"activities_{lang}"]
    kpis = pb[f"kpis_{lang}"]
    
    st.markdown(f"### 📋 {title}")
    st.markdown(f"**{'Target Champion Ratio' if lang == 'en' else 'Ziel-Champion-Quote'}:** {pb['champion_ratio']}")
    st.markdown(f"**Timeline:** {pb['timeline']}")
    
    st.markdown(f"#### {'Recommended Activities' if lang == 'en' else 'Empfohlene Aktivitäten'}")
    for activity in activities:
        st.markdown(f"- {activity}")
    
    st.markdown(f"#### {'Key Performance Indicators' if lang == 'en' else 'Leistungskennzahlen'}")
    for kpi in kpis:
        st.markdown(f"- 📏 {kpi}")
    
    st.markdown("---")
    st.markdown(f"#### {'90-Day Action Plan' if lang == 'en' else '90-Tage-Aktionsplan'}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📅</h3>
            <p><strong>{'Days 1-30' if lang == 'en' else 'Tag 1-30'}</strong></p>
            <p>{'Identify champions, set up communication channels, launch awareness campaign' if lang == 'en' else 'Champions identifizieren, Kommunikationskanäle einrichten, Awareness-Kampagne starten'}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📅</h3>
            <p><strong>{'Days 31-60' if lang == 'en' else 'Tag 31-60'}</strong></p>
            <p>{'Launch first pilot, begin training sessions, collect use case ideas' if lang == 'en' else 'Ersten Piloten starten, Schulungen beginnen, Use-Case-Ideen sammeln'}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📅</h3>
            <p><strong>{'Days 61-90' if lang == 'en' else 'Tag 61-90'}</strong></p>
            <p>{'Review pilot results, showcase to leadership, plan next iteration' if lang == 'en' else 'Pilotergebnisse prüfen, Führungsebene präsentieren, nächste Iteration planen'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Methodology informed by AI adoption programs at Citi (4,000 AI Accelerators, 70% adoption), PwC (500+ prompting parties), Accenture (Galaxy Passport gamification), and DB's own Power Platform community (11,000 members, 4,000+ citizen developers).")

# ─── REPORT PAGE ───
elif page == "report":
    st.markdown(f"## 📄 {t('report_title')}")
    st.markdown(t("report_desc"))
    
    if st.session_state.maturity_level is None:
        st.warning(t("report_no_data"))
    else:
        if st.button(f"📥 {t('report_btn')}", type="primary", use_container_width=True):
            lang = st.session_state.lang
            maturity = st.session_state.maturity_level
            scores = st.session_state.dimension_scores
            overall = st.session_state.overall_score
            
            # Generate PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=20)
            
            # Header
            pdf.set_fill_color(26, 54, 93)
            pdf.rect(0, 0, 210, 45, 'F')
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 22)
            pdf.set_y(12)
            pdf.cell(0, 10, 'MobilityAI Navigator', ln=True, align='C')
            pdf.set_font('Helvetica', '', 11)
            pdf.cell(0, 8, 'AI Readiness Assessment Report' if lang == 'en' else 'KI-Reifegrad-Analysebericht', ln=True, align='C')
            pdf.set_font('Helvetica', '', 9)
            pdf.cell(0, 6, f'Generated: {datetime.now().strftime("%B %d, %Y")}', ln=True, align='C')
            
            # Reset text color
            pdf.set_text_color(30, 30, 30)
            pdf.set_y(55)
            
            # Executive Summary
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Executive Summary' if lang == 'en' else 'Zusammenfassung', ln=True)
            pdf.set_font('Helvetica', '', 10)
            level_name = T[lang]["maturity_levels"][maturity]
            
            summary = f"The assessed organization achieved an overall AI maturity score of {overall:.2f}/5.0, classified as Level {maturity}: {level_name}. " if lang == 'en' else f"Die bewertete Organisation erreichte einen KI-Reifegrad von {overall:.2f}/5.0, eingestuft als Stufe {maturity}: {level_name}. "
            summary += T[lang]["maturity_descriptions"][maturity]
            pdf.multi_cell(0, 6, summary)
            pdf.ln(5)
            
            # Dimension Scores
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Dimension Scores' if lang == 'en' else 'Dimensionsbewertungen', ln=True)
            pdf.set_font('Helvetica', '', 10)
            
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for dim_key, score in sorted_scores:
                dim_name = T[lang]["dimensions"][dim_key]
                bar_width = score / 5.0 * 120
                pdf.cell(55, 7, dim_name, border=0)
                
                # Score bar
                pdf.set_fill_color(26, 54, 93)
                pdf.rect(pdf.get_x(), pdf.get_y() + 1, bar_width, 5, 'F')
                pdf.set_fill_color(230, 230, 230)
                pdf.rect(pdf.get_x() + bar_width, pdf.get_y() + 1, 120 - bar_width, 5, 'F')
                pdf.cell(125, 7, '', border=0)
                pdf.cell(0, 7, f'{score:.1f}/5.0', ln=True, align='R')
            
            pdf.ln(5)
            
            # Key Strengths & Gaps
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Key Findings' if lang == 'en' else 'Wichtigste Erkenntnisse', ln=True)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 7, ('Strengths: ' if lang == 'en' else 'Staerken: ') + ', '.join([T[lang]["dimensions"][k] for k, v in sorted_scores[:2]]), ln=True)
            pdf.set_font('Helvetica', '', 10)
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 7, ('Critical Gaps: ' if lang == 'en' else 'Kritische Luecken: ') + ', '.join([T[lang]["dimensions"][k] for k, v in sorted_scores[-2:]]), ln=True)
            
            pdf.ln(5)
            
            # Top Recommended Use Cases
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Top Recommended Use Cases' if lang == 'en' else 'Top-Empfohlene Use Cases', ln=True)
            
            recommended = [uc for uc in use_cases if uc["maturity_required"] <= maturity][:7]
            pdf.set_font('Helvetica', '', 10)
            for i, uc in enumerate(recommended, 1):
                name = uc["name"] if lang == "en" else uc.get("name_de", uc["name"])
                pdf.set_font('Helvetica', 'B', 10)
                pdf.cell(0, 7, f'{i}. {name} ({uc["operator"]})', ln=True)
                pdf.set_font('Helvetica', '', 9)
                desc = uc["description"] if lang == "en" else uc.get("description_de", uc["description"])
                pdf.multi_cell(0, 5, f'   {desc}')
                pdf.cell(0, 5, f'   Impact: {uc["impact"]} | S3: {uc["s3_pillar"]} | Complexity: {uc["complexity"]}', ln=True)
                pdf.ln(2)
            
            # 90-Day Action Plan
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, '90-Day Action Plan' if lang == 'en' else '90-Tage-Aktionsplan', ln=True)
            pdf.set_font('Helvetica', '', 10)
            
            phases = [
                ("Days 1-30" if lang == "en" else "Tag 1-30", 
                 "Identify AI champions, set up communication channels, launch awareness campaign, conduct initial assessment workshops" if lang == "en" else "KI-Champions identifizieren, Kommunikationskanäle einrichten, Awareness-Kampagne starten"),
                ("Days 31-60" if lang == "en" else "Tag 31-60",
                 "Launch first AI pilot based on top recommended use case, begin training sessions, collect use case ideas from business units" if lang == "en" else "Ersten KI-Piloten starten, Schulungen beginnen, Use-Case-Ideen sammeln"),
                ("Days 61-90" if lang == "en" else "Tag 61-90",
                 "Review pilot results, present to leadership, document lessons learned, plan scaling strategy for next quarter" if lang == "en" else "Pilotergebnisse prüfen, Führungsebene präsentieren, nächste Iteration planen")
            ]
            
            for phase_name, phase_desc in phases:
                pdf.set_font('Helvetica', 'B', 11)
                pdf.cell(0, 8, phase_name, ln=True)
                pdf.set_font('Helvetica', '', 10)
                pdf.multi_cell(0, 6, phase_desc)
                pdf.ln(3)
            
            # Footer
            pdf.ln(10)
            pdf.set_font('Helvetica', 'I', 8)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(0, 5, 'MobilityAI Navigator | Methodology: Gartner, Cisco, McKinsey adapted for Rail & Mobility', ln=True, align='C')
            pdf.cell(0, 5, 'Prepared for DB Engineering & Consulting - Smart Mobility & Digitalization', ln=True, align='C')
            
            # Output
            pdf_bytes = pdf.output()
            
            st.download_button(
                label="📥 Download PDF" if lang == "en" else "📥 PDF herunterladen",
                data=bytes(pdf_bytes),
                file_name=f"MobilityAI_Navigator_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            st.success("Report generated successfully!" if lang == "en" else "Bericht erfolgreich erstellt!")
