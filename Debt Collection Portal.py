import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import plotly.express as px
import plotly.graph_objects as go
import base64
import io

# Configure page
st.set_page_config(
    page_title="Debt Collection Management System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main > div {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .status-badge {
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-align: center;
        display: inline-block;
        margin: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-draft { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
    .status-sent { background: #d1ecf1; color: #0c5460; border: 1px solid #74b9ff; }
    .status-accepted { background: #d4edda; color: #155724; border: 1px solid #00b894; }
    .status-rejected { background: #f8d7da; color: #721c24; border: 1px solid #e17055; }
    .status-pending { background: #e2e3e5; color: #383d41; border: 1px solid #636e72; }
    .status-counter-offer { background: #fff0e6; color: #cc5500; border: 1px solid #fd7900; }
    .status-pending-approval { background: #e6f3ff; color: #0066cc; border: 1px solid #0984e3; }
    .status-rejected-by-supervisor { background: #ffe6e6; color: #cc0000; border: 1px solid #d63031; }
    .status-no-offers { background: #f8f9fa; color: #6c757d; border: 1px solid #dee2e6; }
    
    .info-card {
        background: linear-gradient(135deg, #f8f9ff 0%, #e9f4ff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .success-card {
        background: linear-gradient(135deg, #f0fff4 0%, #e6fffa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #00b894;
        margin-bottom: 1rem;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fffbf0 0%, #fff5e6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #fdcb6e;
        margin-bottom: 1rem;
    }
    
    .error-card {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #e17055;
        margin-bottom: 1rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        padding: 1rem;
    }
    
    .custom-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .custom-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .timeline-item {
        border-left: 3px solid #667eea;
        padding-left: 1.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        background: #f8f9ff;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.5rem;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -8px;
        top: 1rem;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #667eea;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .risk-low { color: #00b894; font-weight: 600; }
    .risk-medium { color: #fdcb6e; font-weight: 600; }
    .risk-high { color: #e17055; font-weight: 600; }
    
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, #667eea, transparent);
        margin: 2rem 0;
        border-radius: 2px;
    }
    
    .hint-tooltip {
        background: #667eea;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
        display: inline-block;
    }
    
    .feature-highlight {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #d63031;
    }

    .detail-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }

    .action-button {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 500;
        margin: 0.2rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .action-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 10px rgba(0, 184, 148, 0.3);
    }

    .danger-button {
        background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
        color: white;
    }

    .danger-button:hover {
        box-shadow: 0 3px 10px rgba(225, 112, 85, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Data Models
class LoanType(Enum):
    PERSONAL = "Personal"
    MORTGAGE = "Mortgage"
    BUSINESS = "Business"
    CREDIT_CARD = "Credit Card"
    AUTO = "Auto Loan"
    STUDENT = "Student Loan"

class WorkflowStatus(Enum):
    SETTLEMENT = "Settlement"
    LEGAL = "Legal"
    BANKRUPTCY = "Bankruptcy"
    PAYMENT_PLAN = "Payment Plan"
    HARDSHIP = "Hardship Program"

class OfferStatus(Enum):
    DRAFT = "Draft"
    SENT = "Sent"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    COUNTER_OFFER = "Counter Offer"
    PENDING_APPROVAL = "Pending Approval"
    REJECTED_BY_SUPERVISOR = "Rejected by Supervisor"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"

class CommunicationChannel(Enum):
    SMS = "SMS"
    EMAIL = "Email"
    PHONE = "Phone"
    MAIL = "Physical Mail"
    PORTAL = "Customer Portal"

class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

@dataclass
class Customer:
    customer_id: str
    name: str
    email: str
    phone: str
    address: str
    risk_profile: str
    credit_score: int
    employment_status: str
    annual_income: float
    preferred_contact: str
    last_contact_date: datetime

@dataclass
class Loan:
    loan_id: str
    customer_id: str
    loan_type: LoanType
    principal_amount: float
    outstanding_principal: float
    interest_amount: float
    penalties: float
    days_overdue: int
    current_balance: float
    workflow_status: WorkflowStatus
    is_secured: bool
    priority: Priority
    assigned_agent: str
    original_due_date: datetime
    last_payment_date: datetime
    last_payment_amount: float

@dataclass
class Offer:
    offer_id: str
    loan_id: str
    agent_id: str
    settlement_percentage: float
    settlement_amount: float
    due_date: datetime
    status: OfferStatus
    justification_notes: str
    created_date: datetime
    sent_date: Optional[datetime] = None
    response_date: Optional[datetime] = None
    supervisor_comments: str = ""
    expiry_date: Optional[datetime] = None
    payment_terms: str = "Lump sum"

@dataclass
class Communication:
    communication_id: str
    loan_id: str
    offer_id: str
    channel: CommunicationChannel
    message_content: str
    sent_date: datetime
    delivery_status: str
    agent_id: str

@dataclass
class CustomerResponse:
    response_id: str
    offer_id: str
    response_type: str
    reason: str
    counter_percentage: Optional[float] = None
    counter_amount: Optional[float] = None
    counter_due_date: Optional[datetime] = None
    agent_notes: str = ""
    response_date: datetime = None

@dataclass
class Note:
    note_id: str
    loan_id: str
    agent_id: str
    note_content: str
    note_type: str  # Call, Email, Meeting, Internal
    created_date: datetime
    is_important: bool = False

# Initialize session state with enhanced data
def initialize_session_state():
    if 'customers' not in st.session_state:
        st.session_state.customers = generate_enhanced_customers()
    if 'loans' not in st.session_state:
        st.session_state.loans = generate_enhanced_loans()
    if 'offers' not in st.session_state:
        st.session_state.offers = generate_enhanced_offers()
    if 'communications' not in st.session_state:
        st.session_state.communications = generate_sample_communications()
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    if 'notes' not in st.session_state:
        st.session_state.notes = generate_sample_notes()
    if 'current_user' not in st.session_state:
        st.session_state.current_user = {
            "name": "John Smith", 
            "role": "Senior Agent", 
            "user_id": "agent_001",
            "team": "Settlement Team Alpha",
            "experience_level": "Expert"
        }
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    if 'show_hints' not in st.session_state:
        st.session_state.show_hints = True

def generate_enhanced_customers():
    customers = []
    names = [
        "Alice Johnson", "Bob Wilson", "Carol Davis", "David Brown", "Eva Martinez", 
        "Frank Taylor", "Grace Chen", "Henry Rodriguez", "Isabel Thompson", "Jack Anderson",
        "Karen Williams", "Liam O'Connor", "Maya Patel", "Noah Garcia", "Olivia Kim",
        "Paul Mitchell"
    ]
    
    employment_statuses = ["Employed", "Self-Employed", "Unemployed", "Retired", "Part-Time", "Contract"]
    contact_preferences = ["Email", "Phone", "SMS", "Mail"]
    
    for i, name in enumerate(names):
        customer = Customer(
            customer_id=f"CUST_{i+1:03d}",
            name=name,
            email=f"{name.lower().replace(' ', '.')}@email.com",
            phone=f"+1-555-{1000+i:04d}",
            address=f"{100+i*10} Main St, {['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'][i % 5]}, {['NY', 'CA', 'IL', 'TX', 'AZ'][i % 5]}",
            risk_profile=np.random.choice(["Low", "Medium", "High"], p=[0.2, 0.6, 0.2]),
            credit_score=np.random.randint(300, 800),
            employment_status=np.random.choice(employment_statuses),
            annual_income=np.random.uniform(25000, 120000),
            preferred_contact=np.random.choice(contact_preferences),
            last_contact_date=datetime.now() - timedelta(days=np.random.randint(1, 90))
        )
        customers.append(customer)
    return customers

def generate_enhanced_loans():
    loans = []
    agents = ["agent_001", "agent_002", "agent_003", "agent_004"]
    
    for i, customer in enumerate(st.session_state.customers):
        principal = np.random.uniform(5000, 100000)
        outstanding = principal * np.random.uniform(0.3, 1.0)
        interest = outstanding * np.random.uniform(0.10, 0.25)
        penalties = outstanding * np.random.uniform(0.02, 0.15)
        
        loan = Loan(
            loan_id=f"LOAN_{i+1:03d}",
            customer_id=customer.customer_id,
            loan_type=np.random.choice(list(LoanType)),
            principal_amount=principal,
            outstanding_principal=outstanding,
            interest_amount=interest,
            penalties=penalties,
            days_overdue=np.random.randint(15, 500),
            current_balance=outstanding + interest + penalties,
            workflow_status=np.random.choice(list(WorkflowStatus)),
            is_secured=np.random.choice([True, False], p=[0.3, 0.7]),
            priority=np.random.choice(list(Priority)),
            assigned_agent=np.random.choice(agents),
            original_due_date=datetime.now() - timedelta(days=np.random.randint(100, 600)),
            last_payment_date=datetime.now() - timedelta(days=np.random.randint(30, 180)),
            last_payment_amount=np.random.uniform(100, 2000)
        )
        loans.append(loan)
    return loans

def generate_enhanced_offers():
    offers = []
    for i, loan in enumerate(st.session_state.loans[:8]):  # Generate offers for first 8 loans
        settlement_pct = np.random.uniform(30, 80)
        settlement_amt = loan.current_balance * (settlement_pct / 100)
        
        offer = Offer(
            offer_id=f"OFFER_{i+1:03d}",
            loan_id=loan.loan_id,
            agent_id=loan.assigned_agent,
            settlement_percentage=settlement_pct,
            settlement_amount=settlement_amt,
            due_date=datetime.now() + timedelta(days=np.random.randint(15, 90)),
            status=np.random.choice(list(OfferStatus)),
            justification_notes=f"Settlement offer based on customer financial analysis. Risk profile considered.",
            created_date=datetime.now() - timedelta(days=np.random.randint(1, 45)),
            expiry_date=datetime.now() + timedelta(days=np.random.randint(30, 120)),
            payment_terms=np.random.choice(["Lump sum", "2 installments", "3 installments"])
        )
        offers.append(offer)
    return offers

def generate_sample_communications():
    communications = []
    for i, offer in enumerate(st.session_state.offers[:5]):
        communication = Communication(
            communication_id=f"COMM_{i+1:03d}",
            loan_id=offer.loan_id,
            offer_id=offer.offer_id,
            channel=np.random.choice(list(CommunicationChannel)),
            message_content=f"Settlement offer sent for loan {offer.loan_id}",
            sent_date=datetime.now() - timedelta(days=np.random.randint(1, 30)),
            delivery_status=np.random.choice(["Delivered", "Pending", "Failed"]),
            agent_id=offer.agent_id
        )
        communications.append(communication)
    return communications

def generate_sample_notes():
    notes = []
    note_types = ["Call", "Email", "Meeting", "Internal", "Follow-up"]
    sample_notes = [
        "Customer expressed financial hardship due to job loss",
        "Discussed payment options with customer",
        "Customer requested settlement offer",
        "Follow-up required in 2 weeks",
        "Customer showed interest in payment plan",
        "Internal review needed for high-value account",
        "Customer dispute on penalty charges",
        "Positive response to initial contact"
    ]
    
    for i, loan in enumerate(st.session_state.loans[:10]):
        for j in range(np.random.randint(1, 4)):  # 1-3 notes per loan
            note = Note(
                note_id=f"NOTE_{i+1:03d}_{j+1}",
                loan_id=loan.loan_id,
                agent_id=loan.assigned_agent,
                note_content=np.random.choice(sample_notes),
                note_type=np.random.choice(note_types),
                created_date=datetime.now() - timedelta(days=np.random.randint(1, 60)),
                is_important=np.random.choice([True, False], p=[0.2, 0.8])
            )
            notes.append(note)
    return notes

# Enhanced utility functions
def get_customer_by_id(customer_id: str) -> Optional[Customer]:
    return next((c for c in st.session_state.customers if c.customer_id == customer_id), None)

def get_loan_by_id(loan_id: str) -> Optional[Loan]:
    return next((l for l in st.session_state.loans if l.loan_id == loan_id), None)

def get_offers_by_loan_id(loan_id: str) -> List[Offer]:
    return [o for o in st.session_state.offers if o.loan_id == loan_id]

def get_notes_by_loan_id(loan_id: str) -> List[Note]:
    return [n for n in st.session_state.notes if n.loan_id == loan_id]

def format_currency(amount: float) -> str:
    return f"${amount:,.2f}"

def get_status_badge_html(status: str) -> str:
    status_class = f"status-{status.lower().replace(' ', '-')}"
    return f'<span class="status-badge {status_class}">{status}</span>'

def get_risk_class(risk: str) -> str:
    return f"risk-{risk.lower()}"

def show_hint(text: str):
    if st.session_state.show_hints:
        st.markdown(f'<div class="hint-tooltip">💡 {text}</div>', unsafe_allow_html=True)

# Professional Sidebar with Enhanced Features
def render_enhanced_sidebar():
    with st.sidebar:
        # User Profile Section
        st.markdown("### 👤 User Profile")
        with st.container():
            st.markdown(f"**{st.session_state.current_user['name']}**")
            st.markdown(f"*{st.session_state.current_user['role']}*")
            st.markdown(f"Team: {st.session_state.current_user['team']}")
            st.markdown(f"Experience: {st.session_state.current_user['experience_level']}")
        
        st.markdown("---")
        
        # Quick Settings
        st.markdown("### ⚙️ Quick Settings")
        st.session_state.show_hints = st.toggle("Show Hints", value=st.session_state.show_hints)
        
        theme_mode = st.selectbox("UI Theme", ["Professional Blue", "Dark Mode", "Light Mode"])
        
        st.markdown("---")
        
        # Navigation with hints
        st.markdown("### 🧭 Navigation")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
        with col2:
            if st.button("❓", key="dash_hint"):
                st.info("View all loans, metrics, and queue management")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("📊 Analytics", use_container_width=True):
                st.session_state.current_page = "analytics"
                st.rerun()
        with col2:
            if st.button("❓", key="analytics_hint"):
                st.info("Performance metrics, charts, and reporting")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("👨‍💼 Supervisor Panel", use_container_width=True):
                st.session_state.current_page = "supervisor"
                st.rerun()
        with col2:
            if st.button("❓", key="super_hint"):
                st.info("Review and approve settlement offers")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("📝 Bulk Operations", use_container_width=True):
                st.session_state.current_page = "bulk_ops"
                st.rerun()
        with col2:
            if st.button("❓", key="bulk_hint"):
                st.info("Mass actions, imports, and batch processing")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("📋 Reports", use_container_width=True):
                st.session_state.current_page = "reports"
                st.rerun()
        with col2:
            if st.button("❓", key="reports_hint"):
                st.info("Generate detailed reports and exports")
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📈 Quick Stats")
        total_loans = len(st.session_state.loans)
        my_loans = len([l for l in st.session_state.loans if l.assigned_agent == st.session_state.current_user['user_id']])
        pending_approvals = len([o for o in st.session_state.offers if o.status == OfferStatus.PENDING_APPROVAL])
        
        st.metric("Total Loans", total_loans, delta=f"You: {my_loans}")
        st.metric("Pending Approvals", pending_approvals)
        st.metric("Success Rate", "73.5%", delta="5.2%")

# Enhanced Dashboard with Professional UI
def render_enhanced_dashboard():
    st.markdown('''
    <div class="main-header">
        <h1>💰 Debt Collection Management System</h1>
        <p>Professional Settlement & Recovery Platform</p>
    </div>
    ''', unsafe_allow_html=True)
    
    if st.session_state.show_hints:
        show_hint("Dashboard provides real-time overview of all loans, performance metrics, and actionable insights")
    
    # Enhanced KPI Section
    st.subheader("📊 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_loans = len(st.session_state.loans)
    total_balance = sum(loan.current_balance for loan in st.session_state.loans)
    pending_offers = len([o for o in st.session_state.offers if o.status in [OfferStatus.DRAFT, OfferStatus.SENT]])
    accepted_offers = len([o for o in st.session_state.offers if o.status == OfferStatus.ACCEPTED])
    recovery_amount = sum(o.settlement_amount for o in st.session_state.offers if o.status == OfferStatus.ACCEPTED)
    
    with col1:
        st.metric("Total Loans", f"{total_loans:,}", delta="12 new this week")
    
    with col2:
        st.metric("Total Balance", format_currency(total_balance), delta="-2.3% from last month")
    
    with col3:
        st.metric("Active Offers", pending_offers, delta=f"+{pending_offers-5} this week")
    
    with col4:
        st.metric("Successful Settlements", accepted_offers, delta="73.5% success rate")
    
    with col5:
        st.metric("Recovery Amount", format_currency(recovery_amount), delta="+15.2% vs target")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Enhanced Filter Section
    st.subheader("🔍 Advanced Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        workflow_filter = st.selectbox("Workflow Type", 
                                     options=["All"] + [w.value for w in WorkflowStatus])
    
    with col2:
        priority_filter = st.selectbox("Priority Level", 
                                     options=["All"] + [p.value for p in Priority])
    
    with col3:
        agent_filter = st.selectbox("Assigned Agent", 
                                  options=["All", "My Loans Only", "agent_001", "agent_002", "agent_003", "agent_004"])
    
    with col4:
        balance_filter = st.selectbox("Balance Range", 
                                    options=["All", "< $10K", "$10K - $50K", "$50K - $100K", "> $100K"])
    
    # Enhanced Loan Queue with Professional Styling
    st.subheader("📋 Loan Management Queue")
    
    if st.session_state.show_hints:
        show_hint("Click on any loan row to view detailed information and available actions")
    
    # Apply filters
    filtered_loans = st.session_state.loans.copy()
    
    if workflow_filter != "All":
        filtered_loans = [l for l in filtered_loans if l.workflow_status.value == workflow_filter]
    
    if priority_filter != "All":
        filtered_loans = [l for l in filtered_loans if l.priority.value == priority_filter]
    
    if agent_filter == "My Loans Only":
        filtered_loans = [l for l in filtered_loans if l.assigned_agent == st.session_state.current_user['user_id']]
    elif agent_filter != "All":
        filtered_loans = [l for l in filtered_loans if l.assigned_agent == agent_filter]
    
    if balance_filter != "All":
        if balance_filter == "< $10K":
            filtered_loans = [l for l in filtered_loans if l.current_balance < 10000]
        elif balance_filter == "$10K - $50K":
            filtered_loans = [l for l in filtered_loans if 10000 <= l.current_balance <= 50000]
        elif balance_filter == "$50K - $100K":
            filtered_loans = [l for l in filtered_loans if 50000 <= l.current_balance <= 100000]
        elif balance_filter == "> $100K":
            filtered_loans = [l for l in filtered_loans if l.current_balance > 100000]
    
    # Prepare enhanced display data
    loan_data = []
    for loan in filtered_loans:
        customer = get_customer_by_id(loan.customer_id)
        offers = get_offers_by_loan_id(loan.loan_id)
        latest_offer_status = offers[-1].status.value if offers else "No Offers"
        
        # Calculate days since last contact
        days_since_contact = (datetime.now() - customer.last_contact_date).days if customer else 0
        
        loan_data.append({
            "Loan ID": loan.loan_id,
            "Customer": customer.name if customer else "Unknown",
            "Type": loan.loan_type.value,
            "Balance": format_currency(loan.current_balance),
            "Overdue Days": loan.days_overdue,
            "Priority": loan.priority.value,
            "Status": latest_offer_status,
            "Agent": loan.assigned_agent,
            "Workflow": loan.workflow_status.value,
            "Last Contact": f"{days_since_contact} days ago",
            "Risk": customer.risk_profile if customer else "Unknown"
        })
    
    if loan_data:
        df = pd.DataFrame(loan_data)
        
        # Display enhanced table
        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )
        
        # Enhanced selection interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_loan_id = st.selectbox(
                "🎯 Select a loan for detailed view:",
                options=["Choose a loan..."] + [row["Loan ID"] for row in loan_data],
                help="Select any loan to view detailed information and perform actions"
            )
        
        with col2:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
        
        # Display detailed loan information
        if selected_loan_id != "Choose a loan...":
            render_loan_detail_view(selected_loan_id)
    
    else:
        st.warning("No loans match the selected criteria.")

def render_loan_detail_view(loan_id: str):
    """Render detailed view for a specific loan"""
    loan = get_loan_by_id(loan_id)
    customer = get_customer_by_id(loan.customer_id)
    offers = get_offers_by_loan_id(loan_id)
    notes = get_notes_by_loan_id(loan_id)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.subheader(f"🔍 Detailed View: {loan_id}")
    
    # Customer & Loan Information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="detail-card">
            <h4>👤 Customer Information</h4>
            <p><strong>Name:</strong> {customer.name}</p>
            <p><strong>Email:</strong> {customer.email}</p>
            <p><strong>Phone:</strong> {customer.phone}</p>
            <p><strong>Credit Score:</strong> {customer.credit_score}</p>
            <p><strong>Employment:</strong> {customer.employment_status}</p>
            <p><strong>Annual Income:</strong> {format_currency(customer.annual_income)}</p>
            <p><strong>Risk Profile:</strong> <span class="{get_risk_class(customer.risk_profile)}">{customer.risk_profile}</span></p>
            <p><strong>Preferred Contact:</strong> {customer.preferred_contact}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="detail-card">
            <h4>💰 Loan Information</h4>
            <p><strong>Loan Type:</strong> {loan.loan_type.value}</p>
            <p><strong>Principal Amount:</strong> {format_currency(loan.principal_amount)}</p>
            <p><strong>Outstanding Balance:</strong> {format_currency(loan.current_balance)}</p>
            <p><strong>Interest Amount:</strong> {format_currency(loan.interest_amount)}</p>
            <p><strong>Penalties:</strong> {format_currency(loan.penalties)}</p>
            <p><strong>Days Overdue:</strong> {loan.days_overdue}</p>
            <p><strong>Priority:</strong> {loan.priority.value}</p>
            <p><strong>Workflow Status:</strong> {loan.workflow_status.value}</p>
            <p><strong>Secured:</strong> {"Yes" if loan.is_secured else "No"}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Action Buttons
    st.subheader("🎯 Available Actions")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("💼 Create Offer", use_container_width=True):
            st.session_state.show_offer_modal = loan_id
    
    with col2:
        if st.button("📞 Contact Customer", use_container_width=True):
            st.session_state.show_contact_modal = loan_id
    
    with col3:
        if st.button("📝 Add Note", use_container_width=True):
            st.session_state.show_note_modal = loan_id
    
    with col4:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.show_analytics_modal = loan_id
    
    with col5:
        if st.button("🔄 Update Status", use_container_width=True):
            st.session_state.show_status_modal = loan_id
    
    # Offer History
    if offers:
        st.subheader("📋 Offer History")
        
        offer_data = []
        for offer in offers:
            offer_data.append({
                "Offer ID": offer.offer_id,
                "Created": offer.created_date.strftime("%Y-%m-%d"),
                "Settlement %": f"{offer.settlement_percentage:.1f}%",
                "Amount": format_currency(offer.settlement_amount),
                "Status": offer.status.value,
                "Due Date": offer.due_date.strftime("%Y-%m-%d"),
                "Payment Terms": offer.payment_terms
            })
        
        offer_df = pd.DataFrame(offer_data)
        st.dataframe(offer_df, use_container_width=True)
    
    # Notes Timeline
    if notes:
        st.subheader("📝 Communication Timeline")
        
        # Sort notes by date (most recent first)
        sorted_notes = sorted(notes, key=lambda x: x.created_date, reverse=True)
        
        for note in sorted_notes:
            importance_icon = "🔥" if note.is_important else "📝"
            st.markdown(f"""
            <div class="timeline-item">
                <h5>{importance_icon} {note.note_type} - {note.created_date.strftime("%Y-%m-%d %H:%M")}</h5>
                <p>{note.note_content}</p>
                <small>Agent: {note.agent_id}</small>
            </div>
            """, unsafe_allow_html=True)

# Modals for various actions
def render_modals():
    """Render various modal dialogs"""
    
    # Create Offer Modal
    if 'show_offer_modal' in st.session_state:
        render_create_offer_modal()
    
    # Contact Customer Modal
    if 'show_contact_modal' in st.session_state:
        render_contact_modal()
    
    # Add Note Modal
    if 'show_note_modal' in st.session_state:
        render_add_note_modal()

def render_create_offer_modal():
    """Modal for creating settlement offers"""
    loan_id = st.session_state.show_offer_modal
    loan = get_loan_by_id(loan_id)
    
    st.markdown("---")
    st.subheader("💼 Create Settlement Offer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        settlement_percentage = st.slider(
            "Settlement Percentage",
            min_value=20.0,
            max_value=100.0,
            value=60.0,
            step=1.0,
            help="Percentage of total balance to settle for"
        )
        
        settlement_amount = loan.current_balance * (settlement_percentage / 100)
        st.metric("Settlement Amount", format_currency(settlement_amount))
        
        payment_terms = st.selectbox(
            "Payment Terms",
            options=["Lump sum", "2 installments", "3 installments", "6 installments"]
        )
    
    with col2:
        due_date = st.date_input(
            "Due Date",
            value=datetime.now() + timedelta(days=30),
            min_value=datetime.now().date()
        )
        
        expiry_date = st.date_input(
            "Offer Expiry Date",
            value=datetime.now() + timedelta(days=60),
            min_value=datetime.now().date()
        )
        
        justification = st.text_area(
            "Justification Notes",
            placeholder="Enter justification for this settlement offer...",
            height=100
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Create Offer", use_container_width=True):
            new_offer = Offer(
                offer_id=f"OFFER_{len(st.session_state.offers)+1:03d}",
                loan_id=loan_id,
                agent_id=st.session_state.current_user['user_id'],
                settlement_percentage=settlement_percentage,
                settlement_amount=settlement_amount,
                due_date=datetime.combine(due_date, datetime.min.time()),
                status=OfferStatus.DRAFT,
                justification_notes=justification,
                created_date=datetime.now(),
                expiry_date=datetime.combine(expiry_date, datetime.min.time()),
                payment_terms=payment_terms
            )
            
            st.session_state.offers.append(new_offer)
            st.success(f"✅ Offer {new_offer.offer_id} created successfully!")
            del st.session_state.show_offer_modal
            st.rerun()
    
    with col2:
        if st.button("📤 Create & Send", use_container_width=True):
            new_offer = Offer(
                offer_id=f"OFFER_{len(st.session_state.offers)+1:03d}",
                loan_id=loan_id,
                agent_id=st.session_state.current_user['user_id'],
                settlement_percentage=settlement_percentage,
                settlement_amount=settlement_amount,
                due_date=datetime.combine(due_date, datetime.min.time()),
                status=OfferStatus.SENT,
                justification_notes=justification,
                created_date=datetime.now(),
                sent_date=datetime.now(),
                expiry_date=datetime.combine(expiry_date, datetime.min.time()),
                payment_terms=payment_terms
            )
            
            st.session_state.offers.append(new_offer)
            st.success(f"✅ Offer {new_offer.offer_id} created and sent!")
            del st.session_state.show_offer_modal
            st.rerun()
    
    with col3:
        if st.button("❌ Cancel", use_container_width=True):
            del st.session_state.show_offer_modal
            st.rerun()

def render_contact_modal():
    """Modal for contacting customers"""
    loan_id = st.session_state.show_contact_modal
    loan = get_loan_by_id(loan_id)
    customer = get_customer_by_id(loan.customer_id)
    
    st.markdown("---")
    st.subheader("📞 Contact Customer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        channel = st.selectbox(
            "Contact Method",
            options=[c.value for c in CommunicationChannel],
            index=[c.value for c in CommunicationChannel].index(customer.preferred_contact)
        )
        
        message_template = st.selectbox(
            "Message Template",
            options=[
                "Settlement Offer",
                "Payment Reminder",
                "Document Request",
                "Follow-up Call",
                "Custom Message"
            ]
        )
    
    with col2:
        st.info(f"""
        **Customer Preferences:**
        - Preferred Contact: {customer.preferred_contact}
        - Last Contact: {customer.last_contact_date.strftime("%Y-%m-%d")}
        - Phone: {customer.phone}
        - Email: {customer.email}
        """)
    
    message_content = st.text_area(
        "Message Content",
        placeholder="Enter your message here...",
        height=150
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Send Message", use_container_width=True):
            new_communication = Communication(
                communication_id=f"COMM_{len(st.session_state.communications)+1:03d}",
                loan_id=loan_id,
                offer_id="",  # Can be linked to specific offer if needed
                channel=CommunicationChannel(channel),
                message_content=message_content,
                sent_date=datetime.now(),
                delivery_status="Sent",
                agent_id=st.session_state.current_user['user_id']
            )
            
            st.session_state.communications.append(new_communication)
            
            # Update customer's last contact date
            customer.last_contact_date = datetime.now()
            
            st.success("✅ Message sent successfully!")
            del st.session_state.show_contact_modal
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            del st.session_state.show_contact_modal
            st.rerun()

def render_add_note_modal():
    """Modal for adding notes"""
    loan_id = st.session_state.show_note_modal
    
    st.markdown("---")
    st.subheader("📝 Add Note")
    
    col1, col2 = st.columns(2)
    
    with col1:
        note_type = st.selectbox(
            "Note Type",
            options=["Call", "Email", "Meeting", "Internal", "Follow-up", "Payment", "Legal"]
        )
        
        is_important = st.checkbox("Mark as Important", value=False)
    
    with col2:
        st.info("""
        **Note Guidelines:**
        - Be specific and factual
        - Include relevant dates/amounts
        - Use professional language
        - Important notes are highlighted
        """)
    
    note_content = st.text_area(
        "Note Content",
        placeholder="Enter detailed note about customer interaction, payment discussion, etc...",
        height=150
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Add Note", use_container_width=True):
            new_note = Note(
                note_id=f"NOTE_{len(st.session_state.notes)+1:03d}",
                loan_id=loan_id,
                agent_id=st.session_state.current_user['user_id'],
                note_content=note_content,
                note_type=note_type,
                created_date=datetime.now(),
                is_important=is_important
            )
            
            st.session_state.notes.append(new_note)
            st.success("✅ Note added successfully!")
            del st.session_state.show_note_modal
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            del st.session_state.show_note_modal
            st.rerun()

# Analytics Page
def render_analytics_page():
    st.markdown('''
    <div class="main-header">
        <h1>📊 Analytics & Performance</h1>
        <p>Comprehensive insights and reporting dashboard</p>
    </div>
    ''', unsafe_allow_html=True)
    
    if st.session_state.show_hints:
        show_hint("Analytics provide insights into collection performance, trends, and agent productivity")
    
    # Performance Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_recovery = sum(o.settlement_amount for o in st.session_state.offers if o.status == OfferStatus.ACCEPTED)
    total_portfolio = sum(l.current_balance for l in st.session_state.loans)
    recovery_rate = (total_recovery / total_portfolio * 100) if total_portfolio > 0 else 0
    
    with col1:
        st.metric("Recovery Rate", f"{recovery_rate:.1f}%", delta="2.3%")
    
    with col2:
        avg_settlement = np.mean([o.settlement_percentage for o in st.session_state.offers if o.status == OfferStatus.ACCEPTED])
        st.metric("Avg Settlement %", f"{avg_settlement:.1f}%", delta="-1.2%")
    
    with col3:
        active_cases = len([l for l in st.session_state.loans if l.days_overdue > 0])
        st.metric("Active Cases", active_cases, delta="-5 this week")
    
    with col4:
        avg_days = np.mean([l.days_overdue for l in st.session_state.loans])
        st.metric("Avg Days Overdue", f"{avg_days:.0f}", delta="-3 days")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Portfolio by Status
        status_counts = {}
        for offer in st.session_state.offers:
            status = offer.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig_pie = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Portfolio Distribution by Offer Status"
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Recovery Trend
        dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
        amounts = [np.random.uniform(5000, 15000) for _ in range(30)]
        
        fig_line = px.line(
            x=dates,
            y=amounts,
            title="Daily Recovery Trend (Last 30 Days)",
            labels={'x': 'Date', 'y': 'Recovery Amount ($)'}
        )
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)
    
    # Agent Performance
    st.subheader("👥 Agent Performance Analysis")
    
    agent_data = []
    agents = ["agent_001", "agent_002", "agent_003", "agent_004"]
    
    for agent in agents:
        agent_loans = [l for l in st.session_state.loans if l.assigned_agent == agent]
        agent_offers = [o for o in st.session_state.offers if o.agent_id == agent]
        successful_offers = [o for o in agent_offers if o.status == OfferStatus.ACCEPTED]
        
        agent_data.append({
            "Agent": agent,
            "Active Loans": len(agent_loans),
            "Offers Created": len(agent_offers),
            "Successful Settlements": len(successful_offers),
            "Success Rate": f"{len(successful_offers)/len(agent_offers)*100:.1f}%" if agent_offers else "0%",
            "Avg Settlement": f"{np.mean([o.settlement_percentage for o in successful_offers]):.1f}%" if successful_offers else "0%",
            "Total Recovery": format_currency(sum(o.settlement_amount for o in successful_offers))
        })
    
    agent_df = pd.DataFrame(agent_data)
    st.dataframe(agent_df, use_container_width=True)

# Supervisor Panel
def render_supervisor_panel():
    st.markdown('''
    <div class="main-header">
        <h1>👨‍💼 Supervisor Panel</h1>
        <p>Review and approve settlement offers</p>
    </div>
    ''', unsafe_allow_html=True)
    
    if st.session_state.show_hints:
        show_hint("Review settlement offers requiring supervisor approval and manage team performance")
    
    # Pending Approvals
    pending_offers = [o for o in st.session_state.offers if o.status == OfferStatus.PENDING_APPROVAL]
    
    st.subheader(f"📋 Pending Approvals ({len(pending_offers)})")
    
    if pending_offers:
        for offer in pending_offers:
            loan = get_loan_by_id(offer.loan_id)
            customer = get_customer_by_id(loan.customer_id)
            
            with st.container():
                st.markdown(f"""
                <div class="detail-card">
                    <h4>Offer {offer.offer_id} - {customer.name}</h4>
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <p><strong>Loan Balance:</strong> {format_currency(loan.current_balance)}</p>
                            <p><strong>Settlement:</strong> {offer.settlement_percentage:.1f}% ({format_currency(offer.settlement_amount)})</p>
                            <p><strong>Savings:</strong> {format_currency(loan.current_balance - offer.settlement_amount)}</p>
                        </div>
                        <div>
                            <p><strong>Days Overdue:</strong> {loan.days_overdue}</p>
                            <p><strong>Risk Profile:</strong> <span class="{get_risk_class(customer.risk_profile)}">{customer.risk_profile}</span></p>
                            <p><strong>Agent:</strong> {offer.agent_id}</p>
                        </div>
                    </div>
                    <p><strong>Justification:</strong> {offer.justification_notes}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{offer.offer_id}"):
                        offer.status = OfferStatus.SENT
                        offer.sent_date = datetime.now()
                        st.success(f"Offer {offer.offer_id} approved and sent!")
                        st.rerun()
                
                with col2:
                    if st.button(f"❌ Reject", key=f"reject_{offer.offer_id}"):
                        offer.status = OfferStatus.REJECTED_BY_SUPERVISOR
                        st.warning(f"Offer {offer.offer_id} rejected!")
                        st.rerun()
                
                with col3:
                    if st.button(f"📝 Request Changes", key=f"changes_{offer.offer_id}"):
                        st.session_state.request_changes_offer = offer.offer_id
                
                with col4:
                    if st.button(f"👁️ View Details", key=f"details_{offer.offer_id}"):
                        st.session_state.view_offer_details = offer.offer_id
                
                st.markdown("---")
    
    else:
        st.info("No offers pending approval at this time.")

# Reports Page
def render_reports_page():
    st.markdown('''
    <div class="main-header">
        <h1>📋 Reports & Export</h1>
        <p>Generate detailed reports and export data</p>
    </div>
    ''', unsafe_allow_html=True)
    
    if st.session_state.show_hints:
        show_hint("Generate comprehensive reports for management, compliance, and analysis")
    
    # Report Options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Available Reports")
        
        report_types = [
            "Portfolio Summary",
            "Agent Performance",
            "Settlement Analysis",
            "Communication Log",
            "Recovery Trends",
            "Risk Assessment",
            "Compliance Report"
        ]
        
        selected_reports = st.multiselect("Select Reports", report_types)
        
        date_range = st.date_input(
            "Date Range",
            value=[datetime.now().date() - timedelta(days=30), datetime.now().date()],
            help="Select the date range for the report"
        )
    
    with col2:
        st.subheader("⚙️ Export Options")
        
        export_format = st.selectbox("Export Format", ["Excel", "CSV", "PDF"])
        include_charts = st.checkbox("Include Charts", value=True)
        include_details = st.checkbox("Include Detailed Records", value=False)
        
        if st.button("🚀 Generate Report", use_container_width=True):
            # Simulate report generation
            with st.spinner("Generating report..."):
                import time
                time.sleep(2)
            
            st.success("Report generated successfully!")
            
            # Show sample report data
            st.subheader("📄 Report Preview")
            
            # Sample data for demonstration
            report_data = {
                "Metric": [
                    "Total Loans",
                    "Total Balance",
                    "Recovery Amount",
                    "Success Rate",
                    "Average Settlement %"
                ],
                "Value": [
                    len(st.session_state.loans),
                    f"${sum(l.current_balance for l in st.session_state.loans):,.2f}",
                    f"${sum(o.settlement_amount for o in st.session_state.offers if o.status == OfferStatus.ACCEPTED):,.2f}",
                    f"{len([o for o in st.session_state.offers if o.status == OfferStatus.ACCEPTED])/len(st.session_state.offers)*100:.1f}%",
                    f"{np.mean([o.settlement_percentage for o in st.session_state.offers]):.1f}%"
                ]
            }
            
            report_df = pd.DataFrame(report_data)
            st.dataframe(report_df, use_container_width=True)

# Bulk Operations Page
def render_bulk_operations_page():
    st.markdown('''
    <div class="main-header">
        <h1>📝 Bulk Operations</h1>
        <p>Mass actions, imports, and batch processing</p>
    </div>
    ''', unsafe_allow_html=True)
    
    if st.session_state.show_hints:
        show_hint("Perform bulk operations on multiple loans, import data, and execute batch processes")
    
    # Bulk Actions Section
    st.subheader("⚡ Quick Bulk Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>📤 Bulk Communication</h4>
            <p>Send messages to multiple customers at once</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Send Bulk Messages", use_container_width=True):
            st.session_state.show_bulk_communication = True
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>🔄 Status Updates</h4>
            <p>Update workflow status for multiple loans</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Bulk Status Update", use_container_width=True):
            st.session_state.show_bulk_status = True
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h4>📊 Data Import</h4>
            <p>Import customer and loan data from files</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Import Data", use_container_width=True):
            st.session_state.show_data_import = True
    
    # File Upload Section
    st.subheader("📂 Data Import & Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Customer/Loan Data",
            type=['csv', 'xlsx'],
            help="Upload CSV or Excel files with customer or loan data"
        )
        
        if uploaded_file is not None:
            st.success("File uploaded successfully!")
            if st.button("Process Import"):
                # Simulate file processing
                with st.spinner("Processing import..."):
                    import time
                    time.sleep(2)
                st.success("Data imported successfully!")
    
    with col2:
        st.markdown("**Export Options:**")
        
        export_options = st.multiselect(
            "Select data to export:",
            ["All Loans", "Customer Data", "Offers", "Communications", "Notes"]
        )
        
        if export_options and st.button("Export Selected Data"):
            st.success(f"Exported: {', '.join(export_options)}")

# Main Application Function
def main():
    """Main application entry point"""
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_enhanced_sidebar()
    
    # Render modals (these appear on top of main content)
    render_modals()
    
    # Main content area based on current page
    if st.session_state.current_page == "dashboard":
        render_enhanced_dashboard()
    
    elif st.session_state.current_page == "analytics":
        render_analytics_page()
    
    elif st.session_state.current_page == "supervisor":
        render_supervisor_panel()
    
    elif st.session_state.current_page == "bulk_ops":
        render_bulk_operations_page()
    
    elif st.session_state.current_page == "reports":
        render_reports_page()
    
    else:
        # Default to dashboard
        render_enhanced_dashboard()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>Debt Collection Management System v2.0 | Built with Streamlit</p>
        <p>© 2024 Professional Collections Platform</p>
    </div>
    """, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main()
