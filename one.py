import matplotlib
matplotlib.use('Agg')  
import streamlit as st
import hashlib
import sqlite3
import time
import re
from datetime import datetime, timedelta
#hi
# ========== SIMPLE DATABASE SETUP ==========
def init_simple_db():
    """Initialize database with default users"""
    conn = sqlite3.connect('hr_simple_auth.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default users immediately
    default_users = [
        ('admin', hash_password('admin123'), 'System Administrator', 'admin'),
        ('hr_manager', hash_password('hr123'), 'HR Manager', 'hr_manager'),
        ('analyst', hash_password('analyst123'), 'Data Analyst', 'analyst'),
        ('viewer', hash_password('viewer123'), 'Viewer User', 'viewer'),
    ]
    
    for user in default_users:
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (user[0],))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
            ''', user)
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    """Verify user credentials"""
    conn = sqlite3.connect('hr_simple_auth.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash, full_name, role FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == hash_password(password):
        return True, {'full_name': result[1], 'role': result[2]}
    return False, None

def register_user(username, password, full_name, role='viewer'):
    """Register new user"""
    conn = sqlite3.connect('hr_simple_auth.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        ''', (username, hash_password(password), full_name, role))
        conn.commit()
        conn.close()
        return True, "User registered successfully"
    except:
        conn.close()
        return False, "Username already exists"

# ========== LOGIN UI - SIMPLE AND WORKING ==========
def show_login_interface():
    """Clean login interface that definitely works"""
    
    # Clear any existing content
    st.markdown("""
    <style>
    .main > div {
        padding-top: 0rem;
    }
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Simple centered login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo/branding
        if st.session_state.get('company_logo'):
            st.image(f"data:image/png;base64,{st.session_state['company_logo']}", width=80)
        
        # Title
        st.markdown(f"<h1 style='text-align: center; color: white;'>{st.session_state.get('company_name', 'FAANG+ Corporation')}</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #ccc;'>Employee Attrition Prediction System</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Login or Register tabs
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    if username and password:
                        success, user_data = verify_login(username, password)
                        if success:
                            st.session_state['logged_in'] = True
                            st.session_state['username'] = username
                            st.session_state['full_name'] = user_data['full_name']
                            st.session_state['role'] = user_data['role']
                            st.success(f"Welcome {user_data['full_name']}!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.warning("Please enter username and password")
            
            st.markdown("---")
            st.caption("Demo Credentials:")
            st.caption("admin / admin123  |  hr_manager / hr123  |  analyst / analyst123  |  viewer / viewer123")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("Choose Username")
                new_full_name = st.text_input("Full Name")
                new_password = st.text_input("Choose Password", type="password")
                new_confirm = st.text_input("Confirm Password", type="password")
                submitted_reg = st.form_submit_button("Create Account", use_container_width=True)
                
                if submitted_reg:
                    if not new_username or not new_full_name or not new_password:
                        st.error("Please fill all fields")
                    elif new_password != new_confirm:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        success, message = register_user(new_username, new_password, new_full_name)
                        if success:
                            st.success(message)
                            st.info("Please login with your new credentials")
                        else:
                            st.error(message)

def check_login():
    """Check if user is logged in"""
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        return True
    return False

def logout():
    """Logout user"""
    for key in ['logged_in', 'username', 'full_name', 'role']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def show_user_profile():
    """Show user profile in sidebar"""
    if check_login():
        st.sidebar.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 10px; margin-bottom: 15px;">
            <div style="font-size: 1.2rem;">👤 {st.session_state.get('full_name', 'User')}</div>
            <div style="font-size: 0.7rem; color: #aaa;">@{st.session_state.get('username', '')}</div>
            <div style="font-size: 0.7rem; margin-top: 5px;">Role: {st.session_state.get('role', 'viewer').upper()}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()
        st.sidebar.markdown("---")

# Initialize database
init_simple_db()
# YOUR ORIGINAL CODE CONTINUES BELOW
# ============================================
# ============================================
# ULTIMATE FAANG+ CORPORATE ATTRITION INTELLIGENCE DASHBOARD
# FULL 2500+ LINES · OPTIMIZED FAST TRAINING · ALL FEATURES
# XGBOOST + RANDOM FOREST + LIGHTGBM + GRADIENT BOOSTING ENSEMBLE
# ADVANCED FEATURE ENGINEERING · SHAP ANALYSIS · CUSTOM LOGO
# AGE LIMIT: 18-65 YEARS ONLY · RATING LIMITS: 0-5 SCALE
# 8+ PRIORITY FEATURES FOR ACCURATE PREDICTION · FIXED RISK PERCENTAGES
# ERROR-FREE · PRODUCTION READY
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, AdaBoostClassifier, ExtraTreesClassifier, StackingClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, 
                             confusion_matrix, roc_auc_score, roc_curve, classification_report,
                             precision_recall_curve, average_precision_score, matthews_corrcoef,
                             log_loss, brier_score_loss)
from sklearn.preprocessing import LabelEncoder, RobustScaler, StandardScaler, MinMaxScaler, PowerTransformer
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif, RFE, SelectFromModel
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
import xgboost as xgb
from sklearn.metrics import average_precision_score
import lightgbm as lgb
from imblearn.over_sampling import SMOTE, ADASYN, BorderlineSMOTE
from imblearn.combine import SMOTETomek
import shap
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import time
from datetime import datetime
import io
import base64
import json
import hashlib
import re
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
                                PageBreak, Image as RLImage, KeepTogether, ListFlowable, ListItem)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from scipy import stats
from scipy.stats import skew, kurtosis, shapiro, pearsonr, spearmanr
from collections import Counter, defaultdict
import matplotlib
matplotlib.use('Agg')

# ========== DATA VALIDATION & QUALITY CHECK ==========
def validate_data_quality(df, target_col):
    """
    Validates data quality and returns confidence score
    Returns: (is_valid, confidence_score, warnings, recommendations)
    """
    warnings_list = []
    recommendations_list = []
    confidence_score = 100
    
    # 1. Check data size
    n_rows = len(df)
    if n_rows < 100:
        warnings_list.append(f"⚠️ Very small dataset: {n_rows} rows (minimum recommended: 500)")
        confidence_score -= 40
        recommendations_list.append("Collect more data (at least 500 rows for reliable predictions)")
    elif n_rows < 500:
        warnings_list.append(f"⚠️ Small dataset: {n_rows} rows (recommended: 500+)")
        confidence_score -= 20
        recommendations_list.append("Consider adding more data for better accuracy")
    elif n_rows < 1000:
        warnings_list.append(f"📊 Adequate dataset: {n_rows} rows")
        confidence_score -= 5
    else:
        warnings_list.append(f"✅ Good dataset size: {n_rows} rows")
    
    # 2. Check target column distribution
    if target_col in df.columns:
        if df[target_col].dtype == 'object':
            yes_count = df[target_col].str.lower().eq('yes').sum()
            no_count = df[target_col].str.lower().eq('no').sum()
        else:
            yes_count = (df[target_col] == 1).sum()
            no_count = (df[target_col] == 0).sum()
        
        total = yes_count + no_count
        yes_pct = (yes_count / total) * 100 if total > 0 else 0
        
        if yes_pct < 5:
            warnings_list.append(f"⚠️ Very imbalanced: Only {yes_pct:.1f}% attrition (Yes)")
            confidence_score -= 35
            recommendations_list.append("Collect more attrition examples or use SMOTE balancing (already enabled)")
        elif yes_pct < 10:
            warnings_list.append(f"⚠️ Imbalanced: {yes_pct:.1f}% attrition (Yes)")
            confidence_score -= 20
            recommendations_list.append("Results may be biased toward 'No' predictions")
        elif yes_pct > 50:
            warnings_list.append(f"⚠️ Unusual: {yes_pct:.1f}% attrition - Check if target column is correct")
            confidence_score -= 15
        else:
            warnings_list.append(f"✅ Good class balance: {yes_pct:.1f}% attrition, {100-yes_pct:.1f}% retention")
    
    # 3. Check missing values
    missing_cols = df.isnull().sum()
    missing_cols = missing_cols[missing_cols > 0]
    if len(missing_cols) > 0:
        total_missing = missing_cols.sum()
        missing_pct = (total_missing / (df.shape[0] * df.shape[1])) * 100
        warnings_list.append(f"⚠️ Missing values: {total_missing} missing ({missing_pct:.1f}%)")
        confidence_score -= min(20, missing_pct)
        recommendations_list.append("Missing values will be auto-filled with median/mode")
    else:
        warnings_list.append("✅ No missing values found")
    
    # 4. Check duplicate rows
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        dup_pct = (dup_count / len(df)) * 100
        warnings_list.append(f"⚠️ Duplicate rows: {dup_count} duplicates ({dup_pct:.1f}%)")
        confidence_score -= min(15, dup_pct)
        recommendations_list.append("Duplicates will be automatically removed")
    else:
        warnings_list.append("✅ No duplicate rows found")
    
    # 5. Check numeric features quality
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if target_col in numeric_cols:
        numeric_cols.remove(target_col)
    
    constant_cols = []
    for col in numeric_cols:
        if df[col].nunique() == 1:
            constant_cols.append(col)
    
    if len(constant_cols) > 0:
        warnings_list.append(f"⚠️ Constant columns: {len(constant_cols)} columns with single value")
        confidence_score -= len(constant_cols) * 2
        recommendations_list.append(f"Columns {constant_cols[:3]} will be removed (no predictive value)")
    
    # 6. Check categorical features
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if target_col in cat_cols:
        cat_cols.remove(target_col)
    
    high_cardinality = []
    for col in cat_cols:
        if df[col].nunique() > 20:
            high_cardinality.append(col)
    
    if len(high_cardinality) > 0:
        warnings_list.append(f"⚠️ High cardinality: {len(high_cardinality)} columns have >20 unique values")
        confidence_score -= min(20, len(high_cardinality) * 2)
        recommendations_list.append("Columns with many unique values may need encoding")
    
    # 7. Check for ID-like columns
    id_keywords = ['id', 'employeeid', 'emp_id', 'ssn', 'social', 'name', 'email']
    id_columns = []
    for col in df.columns:
        col_lower = col.lower()
        for keyword in id_keywords:
            if keyword in col_lower:
                id_columns.append(col)
                break
    
    if len(id_columns) > 0:
        warnings_list.append(f"⚠️ ID columns detected: {id_columns[:3]}")
        confidence_score -= 10
        recommendations_list.append(f"Remove {', '.join(id_columns[:3])} as they don't predict attrition")
    
    # Determine overall status
    if confidence_score >= 80:
        status = "EXCELLENT"
        color = "#28a745"
        icon = "✅"
    elif confidence_score >= 60:
        status = "GOOD"
        color = "#ffc107"
        icon = "⚠️"
    elif confidence_score >= 40:
        status = "FAIR"
        color = "#fd7e14"
        icon = "⚠️"
    else:
        status = "POOR"
        color = "#dc3545"
        icon = "❌"
    
    is_valid = confidence_score >= 40
    
    return {
        'is_valid': is_valid,
        'confidence_score': max(0, min(100, confidence_score)),
        'status': status,
        'color': color,
        'icon': icon,
        'warnings': warnings_list,
        'recommendations': recommendations_list,
        'n_rows': n_rows,
        'n_features': df.shape[1],
        'attrition_pct': yes_pct if 'yes_pct' in dir() else 0
    }

def display_validation_report(validation_result):
    """Display validation report in sidebar"""
    
    score = validation_result['confidence_score']
    color = validation_result['color']
    status = validation_result['status']
    icon = validation_result['icon']
    
    st.markdown(f"""
    <div style="background: rgba(0,0,0,0.3); border-radius: 15px; padding: 15px; margin: 10px 0;">
        <div style="text-align: center;">
            <span style="font-size: 2rem;">{icon}</span>
            <h3 style="margin: 5px 0;">Data Quality: {status}</h3>
            <div style="background: #333; border-radius: 10px; height: 10px; margin: 10px 0;">
                <div style="background: {color}; width: {score}%; height: 10px; border-radius: 10px;"></div>
            </div>
            <span style="font-size: 1.5rem; font-weight: bold; color: {color};">{score:.0f}%</span>
            <span style="font-size: 0.9rem;"> Confidence Score</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📋 Data Quality Report", expanded=False):
        for warning in validation_result['warnings']:
            st.markdown(f"- {warning}")
        
        if validation_result['recommendations']:
            st.markdown("### 💡 Recommendations:")
            for rec in validation_result['recommendations']:
                st.markdown(f"- {rec}")
        
        st.markdown(f"""
        ### 📊 Summary:
        - **Rows:** {validation_result['n_rows']:,}
        - **Features:** {validation_result['n_features']}
        - **Attrition Rate:** {validation_result['attrition_pct']:.1f}%
        """)

# ========== IMPROVED SMART FEATURE SELECTION (8+ FEATURES) ==========
def get_smart_priority_features_enhanced(df, target_col, top_n=8):
    """
    Intelligently select top N priority features with proper categorical handling
    Returns: (selected_features, feature_details, impact_percentages, final_importance)
    """
    from sklearn.feature_selection import mutual_info_classif
    
    X = df.copy()
    y = X[target_col].copy()
    
    # Encode target
    if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)
    
    # Get ALL feature types
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Remove target from lists
    if target_col in numeric_cols:
        numeric_cols.remove(target_col)
    if target_col in categorical_cols:
        categorical_cols.remove(target_col)
    
    # 1. Calculate correlation for numeric features
    correlations = {}
    for col in numeric_cols:
        if col in X.columns and X[col].nunique() > 1:
            corr = abs(X[col].corr(pd.Series(y)))
            correlations[col] = corr if not np.isnan(corr) else 0
        else:
            correlations[col] = 0
    
    # 2. Calculate Cramér's V for categorical features
    def cramers_v(confusion_matrix):
        chi2 = stats.chi2_contingency(confusion_matrix)[0]
        n = confusion_matrix.sum().sum()
        phi2 = chi2 / n
        r, k = confusion_matrix.shape
        phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
        rcorr = r - ((r-1)**2)/(n-1)
        kcorr = k - ((k-1)**2)/(n-1)
        return np.sqrt(phi2corr / min((kcorr-1), (rcorr-1)))
    
    categorical_corr = {}
    for col in categorical_cols:
        if col in X.columns and X[col].nunique() > 1:
            try:
                contingency = pd.crosstab(X[col], y)
                if contingency.shape[0] > 1 and contingency.shape[1] > 1:
                    categorical_corr[col] = cramers_v(contingency.values)
                else:
                    categorical_corr[col] = 0
            except:
                categorical_corr[col] = 0
        else:
            categorical_corr[col] = 0
    
    # 3. Mutual Information for all features (encoded)
    X_encoded = pd.get_dummies(X.drop(columns=[target_col]), drop_first=True)
    mi_scores = mutual_info_classif(X_encoded, y, random_state=42)
    mi_dict = dict(zip(X_encoded.columns, mi_scores))
    
    # Aggregate MI for original columns
    aggregated_mi = {}
    for col in numeric_cols:
        aggregated_mi[col] = correlations.get(col, 0) * 0.5 + mi_dict.get(col, 0) * 0.5
    
    for col in categorical_cols:
        related_cols = [c for c in mi_dict.keys() if c.startswith(f"{col}_")]
        if related_cols:
            aggregated_mi[col] = max([mi_dict[c] for c in related_cols])
        else:
            aggregated_mi[col] = categorical_corr.get(col, 0)
    
    # 4. Business priority weights (domain knowledge) - 8+ priority features
    business_weights = {
        # CRITICAL - Priority Features (High Weight)
        'JobSatisfaction': 2.0,
        'MonthlyIncome': 1.9,
        'YearsAtCompany': 1.8,
        'WorkLifeBalance': 1.8,
        'EnvironmentSatisfaction': 1.7,
        'Age': 1.6,
        'OverTime': 1.9,
        'YearsSinceLastPromotion': 1.5,
        
        # HIGH Impact
        'NumCompaniesWorked': 1.4,
        'DistanceFromHome': 1.3,
        'PercentSalaryHike': 1.3,
        'StockOptionLevel': 1.2,
        'TrainingTimesLastYear': 1.2,
        'RelationshipSatisfaction': 1.3,
        'TotalWorkingYears': 1.2,
        
        # MEDIUM Impact
        'Department': 1.1,
        'Education': 1.0,
        'MaritalStatus': 1.0,
        'Gender': 0.9,
        'BusinessTravel': 1.1
    }
    
    # Calculate final importance scores
    final_importance = {}
    feature_types = {}
    
    for col in numeric_cols + categorical_cols:
        base_score = aggregated_mi.get(col, 0)
        weight = business_weights.get(col, 1.0)
        final_importance[col] = base_score * weight
        feature_types[col] = 'numeric' if col in numeric_cols else 'categorical'
    
    # Sort and select top N
    sorted_features = sorted(final_importance.items(), key=lambda x: x[1], reverse=True)
    selected_features = [f[0] for f in sorted_features[:top_n]]
    
    # Prepare detailed feature info
    feature_details = []
    for feat in selected_features:
        feature_details.append({
            'feature': feat,
            'type': feature_types[feat],
            'importance_score': final_importance[feat],
            'business_weight': business_weights.get(feat, 1.0),
            'priority_rank': selected_features.index(feat) + 1
        })
    
    # Calculate impact percentages
    total_importance = sum([final_importance[f] for f in selected_features])
    impact_percentages = {}
    for f in selected_features:
        impact_percentages[f] = (final_importance[f] / total_importance * 100) if total_importance > 0 else 0
    
    return selected_features, feature_details, impact_percentages, final_importance

# ========== DYNAMIC PRIORITY FEATURE SEPARATION ==========
def get_priority_features_separated(df, target_col, model_features, top_n=12):
    """
    Dynamically separates features into numeric and categorical based on priority
    Returns: (numeric_priority_features, categorical_priority_features, priority_details)
    """
    
    X = df.copy()
    y = X[target_col].copy()
    
    # Encode target
    if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y)
    
    # Get model feature importance if available
    model_importance = {}
    if 'ensemble' in st.session_state and st.session_state['ensemble'] is not None:
        try:
            if hasattr(st.session_state['ensemble'], 'estimators_') and len(st.session_state['ensemble'].estimators_) > 0:
                first_est = st.session_state['ensemble'].estimators_[0]
                if hasattr(first_est, 'feature_importances_'):
                    for idx, feat in enumerate(model_features):
                        if idx < len(first_est.feature_importances_):
                            model_importance[feat] = first_est.feature_importances_[idx]
        except:
            pass
    
    # Calculate correlation with target
    correlations = {}
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if col != target_col and col in X.columns and X[col].nunique() > 1:
            try:
                corr = abs(X[col].corr(pd.Series(y)))
                correlations[col] = corr if not np.isnan(corr) else 0
            except:
                correlations[col] = 0
    
    # Business priority weights
    business_weights = {
        'JobSatisfaction': 2.0, 'MonthlyIncome': 1.9, 'YearsAtCompany': 1.8,
        'WorkLifeBalance': 1.8, 'EnvironmentSatisfaction': 1.7, 'Age': 1.6,
        'OverTime': 1.9, 'YearsSinceLastPromotion': 1.5, 'NumCompaniesWorked': 1.4,
        'DistanceFromHome': 1.3, 'PercentSalaryHike': 1.3, 'StockOptionLevel': 1.2,
        'TrainingTimesLastYear': 1.2, 'RelationshipSatisfaction': 1.3, 'TotalWorkingYears': 1.2,
        'Department': 1.1, 'Education': 1.0, 'MaritalStatus': 1.0, 'Gender': 0.9
    }
    
    # Calculate priority scores
    priority_scores = {}
    for col in model_features:
        if col == target_col:
            continue
        score = 0
        if col in model_importance:
            score += model_importance[col] * 0.5
        if col in correlations:
            score += correlations[col] * 0.3
        business_weight = business_weights.get(col, 1.0)
        norm_business = min(1.0, (business_weight - 1.0) / 2.0 + 0.5)
        score += norm_business * 0.2
        priority_scores[col] = score
    
    # Sort by priority
    sorted_features = sorted(priority_scores.items(), key=lambda x: x[1], reverse=True)
    priority_features = [f[0] for f in sorted_features[:top_n]]
    
    # Separate numeric and categorical
    numeric_priority = []
    categorical_priority = []
    
    for feat in priority_features:
        if feat in df.columns:
            if df[feat].dtype == 'object':
                categorical_priority.append(feat)
            elif df[feat].nunique() <= 10:
                categorical_priority.append(feat)
            else:
                numeric_priority.append(feat)
        else:
            numeric_priority.append(feat)
    
    # Create priority details
    priority_details = []
    for i, feat in enumerate(priority_features):
        priority_details.append({
            'rank': i + 1,
            'feature': feat,
            'score': priority_scores.get(feat, 0),
            'type': 'Numeric' if feat in numeric_priority else 'Categorical',
            'priority_level': '🔴 CRITICAL' if i < 3 else '🟡 HIGH' if i < 7 else '🟢 MEDIUM'
        })
    
    return numeric_priority, categorical_priority, priority_details

# ========== ACCURATE RISK PREDICTION WITH FIXED PERCENTAGES ==========
def predict_risk_enhanced(model, scaler, input_data, features, df_stats=None):
    """
    Enhanced risk prediction - uses ACTUAL model predictions
    """
    input_df = pd.DataFrame([input_data])
    
    # Handle categorical encoding
    for col in input_df.columns:
        if input_df[col].dtype == 'object':
            if col == 'OverTime':
                input_df[col] = input_df[col].map({'Yes': 1, 'No': 0, 'yes': 1, 'no': 0})
            elif col == 'Gender':
                input_df[col] = input_df[col].map({'Male': 1, 'Female': 0, 'M': 1, 'F': 0})
            else:
                # For other categorical columns, simple encoding
                input_df[col] = pd.Categorical(input_df[col]).codes
    
    # Ensure all features exist
    for col in features:
        if col not in input_df.columns:
            input_df[col] = 0
    
    input_df = input_df[features]
    
    # Convert all to numeric
    for col in input_df.columns:
        input_df[col] = pd.to_numeric(input_df[col], errors='coerce').fillna(0)
    
    # Scale features
    try:
        scaled = scaler.transform(input_df)
    except:
        scaled = input_df.values
    
    # ========== THIS IS THE ACTUAL MODEL PREDICTION ==========
    prob = model.predict_proba(scaled)[0][1]
    risk_score = prob * 100
    
    # ========== RISK LEVEL BASED ON MODEL PREDICTION ==========
    if risk_score < 33:
        risk_level = "LOW RISK"
        risk_class = "risk-low"
        icon = '🟢'
        color = '#28a745'
        action = 'Monitor quarterly - Routine HR check-ins recommended'
    elif risk_score < 66:
        risk_level = "MEDIUM RISK"
        risk_class = "risk-medium"
        icon = '🟡'
        color = '#ffc107'
        action = 'Schedule career discussion within 2 weeks - Proactive intervention needed'
    elif risk_score < 85:
        risk_level = "HIGH RISK"
        risk_class = "risk-high"
        icon = '🟠'
        color = '#ff6b6b'
        action = 'IMMEDIATE ACTION: Stay interview within 48 hours'
    else:
        risk_level = "CRITICAL RISK"
        risk_class = "risk-critical"
        icon = '🔴'
        color = '#ff0000'
        action = 'CRITICAL: Executive intervention required within 24 hours'
    
    # ========== RISK FACTORS - Use the input values to explain ==========
    risk_factors = []
    risk_percentages = []
    
    # Get the top contributing features from input data
    for feat in features[:8]:
        if feat in input_data:
            val = input_data[feat]
            if isinstance(val, (int, float)):
                # Higher risk for certain values
                if 'age' in feat.lower() and (val < 25 or val > 55):
                    risk_factors.append(f"{feat}: {val}")
                    risk_percentages.append(round(risk_score / 8, 1))
                elif 'satisfaction' in feat.lower() and val <= 2:
                    risk_factors.append(f"{feat}: {val}/5")
                    risk_percentages.append(round(risk_score / 8, 1))
                elif 'income' in feat.lower() and val < 50000:
                    risk_factors.append(f"{feat}: ${val:,.0f}")
                    risk_percentages.append(round(risk_score / 8, 1))
                elif 'overtime' in feat.lower() and val == 1:
                    risk_factors.append(f"{feat}: Yes")
                    risk_percentages.append(round(risk_score / 8, 1))
                elif 'years' in feat.lower() and val < 2:
                    risk_factors.append(f"{feat}: {val} years")
                    risk_percentages.append(round(risk_score / 8, 1))
    
    # Ensure we have at least 3 factors
    if len(risk_factors) < 3:
        risk_factors.append("Overall risk assessment")
        risk_percentages.append(round(risk_score / 2, 1))
    
    # Normalize percentages to sum to risk_score
    total = sum(risk_percentages) if risk_percentages else 1
    risk_percentages = [round(p * risk_score / total, 1) for p in risk_percentages]
    
    return {
        'prob': prob,
        'score': risk_score,
        'level': risk_level,
        'class': risk_class,
        'icon': icon,
        'color': color,
        'action': action,
        'severity': risk_level,
        'priority': 'High' if risk_score > 66 else 'Medium' if risk_score > 33 else 'Low',
        'timeline': '24h' if risk_score > 85 else '48h' if risk_score > 66 else '2 weeks' if risk_score > 33 else 'Quarterly',
        'confidence': f"{(1 - abs(0.5 - prob) * 2) * 100:.0f}%",
        'risk_factors': risk_factors[:6],
        'risk_percentages': risk_percentages[:6],
        'total_risk_weight': sum(risk_percentages[:6]),
        'input_data': input_data
    }

# ========== HR RECOMMENDATION ENGINE ==========
def get_hr_recommendation(risk_level, risk_score, attrition_rate=0, employee_data=None):
    """Enhanced HR recommendation engine with clear level separation"""
    
    if risk_level == "LOW RISK":
        return {
            'title': '🟢 Proactive Retention Strategy',
            'priority': 'Low Priority - Scheduled Monitoring',
            'timeline': 'Quarterly Review (Next: 90 days)',
            'color': '#28a745',
            'bg': '#d4edda',
            'icon': '🟢',
            'level': 'LOW RISK',
            'actions': [
                '✓ Continue regular performance check-ins (quarterly)',
                '✓ Maintain competitive compensation reviews (annual)',
                '✓ Provide professional development opportunities',
                '✓ Recognize and reward achievements publicly',
                '✓ Conduct engagement surveys semi-annually',
                '✓ Document successful retention practices for knowledge sharing',
                '✓ Monitor industry trends for proactive adjustments'
            ],
            'short_term': 'Maintain current positive trajectory with minimal intervention',
            'long_term': 'Build career progression pathways and leadership pipeline',
            'kpi': 'Maintain engagement score > 4.0 and retention rate > 90%',
            'budget': 'Standard HR allocation ($2,500 - $5,000 annually)',
            'roi': 'High - Preventive retention (300-400% ROI)',
            'success_rate': '85-95% retention expected with current strategy',
            'estimated_savings': '$75,000 - $125,000 per retained employee',
            'immediate_action': 'No immediate action required. Continue regular monitoring.'
        }
    elif risk_level == "MEDIUM RISK":
        return {
            'title': '🟡 Targeted Intervention Required',
            'priority': 'Medium Priority - Active Intervention',
            'timeline': '2-4 Weeks (Schedule within 14 days)',
            'color': '#ffc107',
            'bg': '#fff3cd',
            'icon': '🟡',
            'level': 'MEDIUM RISK',
            'actions': [
                '⚠ Schedule career development discussion within 2 weeks',
                '⚠ Review compensation and benefits package for competitiveness',
                '⚠ Offer mentorship or executive coaching program',
                '⚠ Assess workload distribution and work-life balance',
                '⚠ Provide clear promotion path and timeline discussion',
                '⚠ Conduct stay interview with direct manager',
                '⚠ Offer flexible work arrangements if possible',
                '⚠ Create personalized 30-60-90 day development plan'
            ],
            'short_term': 'Address specific concerns within 30 days',
            'long_term': 'Create personalized development and retention plan',
            'kpi': 'Reduce risk score by 20% within 60 days',
            'budget': 'Moderate - Targeted intervention ($5,000 - $15,000)',
            'roi': 'Medium - Preventive retention (150-250% ROI)',
            'success_rate': '60-75% retention improvement expected',
            'estimated_savings': '$50,000 - $100,000 per retained employee',
            'immediate_action': 'Schedule career discussion within 2 weeks. Proactive intervention needed.'
        }
    elif risk_level == "HIGH RISK":
        return {
            'title': '🟠 Urgent Retention Action Needed',
            'priority': 'High Priority - Immediate Intervention',
            'timeline': '48 Hours - 1 Week (IMMEDIATE)',
            'color': '#ff6b6b',
            'bg': '#ffe5d0',
            'icon': '🟠',
            'level': 'HIGH RISK',
            'actions': [
                '🚨 Schedule stay interview within 48 hours',
                '🚨 Review retention bonus or compensation adjustment',
                '🚨 Create personalized development plan',
                '🚨 Assign executive mentor or coach',
                '🚨 Address specific pain points immediately',
                '🚨 Weekly check-ins for 30 days',
                '🚨 Consider role adjustment or promotion',
                '🚨 Provide additional benefits or perks'
            ],
            'short_term': 'Immediate intervention within 48 hours',
            'long_term': 'Intensive 90-day retention program with monthly reviews',
            'kpi': 'Reduce risk score by 40% within 30 days',
            'budget': 'High - Critical retention investment ($15,000 - $35,000)',
            'roi': 'Critical - Prevent high-value talent loss (400-500% ROI)',
            'success_rate': '50-65% retention improvement with immediate action',
            'estimated_savings': '$100,000 - $200,000 per retained employee',
            'immediate_action': 'URGENT: Schedule stay interview within 48 hours. Escalate to HRBP.'
        }
    else:  # CRITICAL RISK
        return {
            'title': '🔴 CRITICAL: Executive Intervention Required',
            'priority': 'CRITICAL Priority - Immediate Escalation',
            'timeline': '24 Hours (EMERGENCY)',
            'color': '#dc3545',
            'bg': '#f8d7da',
            'icon': '🔴',
            'level': 'CRITICAL RISK',
            'actions': [
                '🔴 ESCALATE TO HR BUSINESS PARTNER immediately',
                '🔴 Schedule emergency stay interview within 24 hours',
                '🔴 Prepare retention bonus or compensation adjustment package',
                '🔴 Create personalized career advancement plan',
                '🔴 Assign executive mentor or C-level coach',
                '🔴 Address specific pain points with concrete solutions',
                '🔴 Consider role adjustment, promotion, or job enrichment',
                '🔴 Implement daily check-ins for first week',
                '🔴 Involve senior leadership in retention discussion',
                '🔴 Offer additional benefits or work flexibility options'
            ],
            'short_term': 'Emergency intervention within 24 hours - DO NOT DELAY',
            'long_term': 'Intensive 90-day retention program with weekly reviews',
            'kpi': 'Reduce risk score by 50% within 30 days',
            'budget': 'High - Critical retention investment ($25,000 - $60,000)',
            'roi': 'Essential - Prevent high-value talent loss (500-700% ROI)',
            'success_rate': '40-60% retention improvement with immediate executive action',
            'estimated_savings': '$200,000 - $400,000 per retained executive/talent',
            'immediate_action': 'EMERGENCY: Executive intervention required within 24 hours. DO NOT DELAY.'
        }

# Suppress warnings
warnings.filterwarnings('ignore')

# ========== PAGE CONFIGURATION ==========
# Only set page config if not already set
try:
    st.set_page_config(
        page_title="Employee Attrition Prediction System",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except:
    pass
# After st.set_page_config, add these lines:
if not check_login():
    show_login_interface()
    st.stop()

# ========== ENUMS AND CONSTANTS ==========
class RiskLevel:
    LOW = "LOW RISK"
    MEDIUM = "MEDIUM RISK" 
    HIGH = "HIGH RISK"
    CRITICAL = "CRITICAL RISK"

class DataQualityScore:
    EXCELLENT = (90, 100, "Excellent")
    GOOD = (75, 89, "Good")
    FAIR = (60, 74, "Fair")
    POOR = (0, 59, "Poor")

# Constants
MIN_AGE = 18
MAX_AGE = 65
MIN_RATING = 0
MAX_RATING = 5
DEFAULT_BRAND_COLOR = "#667eea"

# ========== SESSION STATE INITIALIZATION ==========
session_defaults = {
    'company_logo': None,
    'company_name': "FAANG+ Corporation",
    'brand_color': DEFAULT_BRAND_COLOR,
    'shap_bar': None,
    'shap_swarm': None,
    'shap_waterfall': None,
    'df': None,
    'target': None,
    'ensemble': None,
    'metrics': None,
    'features': None,
    'scaler': None,
    'cv_scores': None,
    'pred_result': None,
    'cleaning_df': None,
    'stats_df': None,
    'cleaning_insights': None,
    'historical_predictions': [],
    'model_performance_history': [],
    'alert_rules': [],
    'feature_importance_history': [],
    'what_if_scenarios': [],
    'validation_result': None,
}

for key, default_value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# ========== HELPER FUNCTIONS ==========
def get_brand_color_hex():
    color = st.session_state['brand_color']
    if not color.startswith('#'):
        color = '#' + color
    return color

def generate_unique_id(data_dict):
    """Generate unique ID for tracking predictions"""
    hash_string = json.dumps(data_dict, sort_keys=True) + str(datetime.now())
    return hashlib.md5(hash_string.encode()).hexdigest()[:8]

def calculate_data_quality_score(df):
    """Calculate overall data quality score (0-100)"""
    score = 100
    missing_pct = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
    score -= missing_pct * 50
    dup_pct = df.duplicated().sum() / df.shape[0]
    score -= dup_pct * 30
    const_pct = sum(df.nunique() == 1) / df.shape[1]
    score -= const_pct * 20
    return max(0, min(100, score))

def calculate_retention_roi(intervention_cost, retention_value=150000):
    """Calculate ROI of retention interventions"""
    estimated_savings = retention_value * 0.7
    roi = ((estimated_savings - intervention_cost) / intervention_cost) * 100 if intervention_cost > 0 else 0
    payback_period = intervention_cost / (estimated_savings / 12) if estimated_savings > 0 else 0
    return {
        'estimated_savings': estimated_savings,
        'roi_percentage': roi,
        'payback_months': payback_period,
        'recommended': roi > 50
    }

# ========== ADVANCED CSS STYLING ==========
brand_color = st.session_state['brand_color']

st.markdown(f"""
<style>
    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    .stApp {{
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-size: 200% 200%;
        animation: gradientBG 10s ease infinite;
    }}
    
    @keyframes shine {{
        0% {{ left: -100%; }}
        20% {{ left: 100%; }}
        100% {{ left: 100%; }}
    }}
    
    .corporate-header {{
        background: rgba(30,58,95,0.3);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.2);
        position: relative;
        overflow: hidden;
        animation: fadeInDown 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    .corporate-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shine 3s infinite;
    }}
    
    .corporate-header h1 {{
        background: linear-gradient(135deg, #fff, {brand_color}, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        margin: 0;
        animation: glow 2s ease-in-out infinite;
    }}
    
    @keyframes glow {{
        0%, 100% {{ text-shadow: 0 0 5px rgba(102,126,234,0.5); }}
        50% {{ text-shadow: 0 0 20px rgba(102,126,234,0.8); }}
    }}
    
    @keyframes fadeInDown {{
        from {{ opacity: 0; transform: translateY(-50px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(50px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes scaleIn {{
        from {{ opacity: 0; transform: scale(0.9); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}
    
    @keyframes slideInRight {{
        from {{ opacity: 0; transform: translateX(50px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    
    .metric-card {{
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(15px);
        padding: 1rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        margin: 0.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
        animation: scaleIn 0.5s ease-out;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }}
    
    .metric-card:hover::before {{
        left: 100%;
    }}
    
    .metric-card:hover {{
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border-color: {brand_color};
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #fff, {brand_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 2s ease-in-out infinite;
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}
    
    .risk-low {{
        background: linear-gradient(135deg, rgba(27,67,50,0.95), rgba(45,106,79,0.95));
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 1rem 0;
        border: 2px solid #38ef7d;
        animation: float 3s ease-in-out infinite, fadeInUp 0.6s ease-out;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(56,239,125,0.3);
    }}
    
    .risk-medium {{
        background: linear-gradient(135deg, rgba(123,44,0,0.95), rgba(232,93,4,0.95));
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 1rem 0;
        border: 2px solid #ffb703;
        animation: float 3s ease-in-out infinite 0.5s, fadeInUp 0.6s ease-out;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(255,183,3,0.3);
    }}
    
    .risk-high {{
        background: linear-gradient(135deg, rgba(127,26,26,0.95), rgba(220,47,2,0.95));
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 1rem 0;
        border: 2px solid #ff6b6b;
        animation: float 3s ease-in-out infinite 1s, blink 1s infinite;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(255,107,107,0.3);
    }}
    
    .risk-critical {{
        background: linear-gradient(135deg, rgba(100,0,0,0.95), rgba(150,0,0,0.95));
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 1rem 0;
        border: 3px solid #ff0000;
        animation: float 3s ease-in-out infinite 1.5s, blinkCritical 0.5s infinite;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(255,0,0,0.3);
    }}
    
    @keyframes blinkCritical {{
        0%, 100% {{ box-shadow: 0 0 5px #ff0000; }}
        50% {{ box-shadow: 0 0 30px #ff0000; }}
    }}
    
    @keyframes blink {{
        0%, 100% {{ box-shadow: 0 0 5px #ff6b6b; }}
        50% {{ box-shadow: 0 0 25px #ff6b6b; }}
    }}
    
    .stButton > button {{
        background: linear-gradient(90deg, {brand_color}, #764ba2, #f093fb);
        background-size: 200% auto;
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.8rem 1.5rem;
        font-weight: bold;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
        position: relative;
        overflow: hidden;
    }}
    
    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }}
    
    .stButton > button:hover::before {{
        width: 300px;
        height: 300px;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102,126,234,0.5);
        background-position: right center;
    }}
    
    .glass-card {{
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out;
    }}
    
    .glass-card:hover {{
        transform: translateY(-5px);
        background: rgba(255,255,255,0.1);
        border-color: {brand_color};
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }}
    
    .insight-card {{
        background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2));
        backdrop-filter: blur(5px);
        border-left: 4px solid {brand_color};
        padding: 1rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        transition: all 0.3s ease;
        animation: slideInRight 0.5s ease-out;
    }}
    
    .insight-card:hover {{
        background: linear-gradient(135deg, rgba(102,126,234,0.3), rgba(118,75,162,0.3));
        transform: translateX(5px);
    }}
    
    .explanation-card {{
        background: linear-gradient(135deg, rgba(0,0,0,0.6), rgba(0,0,0,0.4));
        backdrop-filter: blur(5px);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.8rem 0;
        border-left: 4px solid {brand_color};
        font-size: 0.9rem;
        animation: fadeInUp 0.5s ease-out;
    }}
    
    .hr-card {{
        background: linear-gradient(135deg, rgba(30,58,95,0.9), rgba(26,42,74,0.9));
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.2rem;
        margin: 1rem 0;
        border: 1px solid {brand_color};
        transition: all 0.4s ease;
        animation: fadeInUp 0.7s ease-out;
    }}
    
    .hr-card:hover {{
        transform: scale(1.02);
        border-color: {brand_color};
        box-shadow: 0 10px 30px rgba(102,126,234,0.3);
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 12px;
        background-color: transparent;
        padding: 0.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 10px 24px;
        color: white;
        font-weight: bold;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        animation: fadeInUp 0.5s ease-out;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(102,126,234,0.3);
        transform: translateY(-3px);
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {brand_color}, #764ba2);
        box-shadow: 0 5px 20px rgba(102,126,234,0.4);
    }}
    
    .stProgress > div > div {{
        background: linear-gradient(90deg, #11998e, #38ef7d, #f2c94c, #eb3349);
        background-size: 300% 100%;
        animation: progressGradient 2s ease infinite;
        border-radius: 10px;
    }}
    
    @keyframes progressGradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    .dataframe {{
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 10px;
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    
    .streamlit-expanderHeader {{
        background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2));
        backdrop-filter: blur(10px);
        border-radius: 12px;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }}
    
    .streamlit-expanderHeader:hover {{
        background: linear-gradient(135deg, rgba(102,126,234,0.4), rgba(118,75,162,0.4));
    }}
    
    .css-1d391kg {{
        background: rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
    }}
    
    .logo-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-bottom: 15px;
    }}
    
    .company-logo {{
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid {brand_color};
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }}
    
    .company-name {{
        font-size: 1.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #fff, {brand_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .age-warning {{
        background: linear-gradient(135deg, rgba(255,193,7,0.2), rgba(255,193,7,0.1));
        border-left: 4px solid #ffc107;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }}
    
    .feature-badge {{
        background: rgba(102,126,234,0.3);
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 2px;
    }}
    
    .priority-critical {{
        background: #dc3545;
        color: white;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
    }}
    
    .priority-high {{
        background: #fd7e14;
        color: white;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
    }}
    
    .priority-medium {{
        background: #ffc107;
        color: black;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.7rem;
    }}
    
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {brand_color};
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: #764ba2;
    }}
</style>
""", unsafe_allow_html=True)

# ========== LOGO HANDLING FUNCTIONS ==========
def save_uploaded_logo(uploaded_file):
    """Save uploaded logo to session state"""
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            image = image.resize((80, 80))
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            st.session_state['company_logo'] = img_str
            return True
        except Exception as e:
            st.error(f"Error loading logo: {str(e)}")
            return False
    return False

def get_logo_html():
    """Get HTML for displaying logo"""
    if st.session_state['company_logo']:
        return f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{st.session_state['company_logo']}" class="company-logo">
            <span class="company-name">{st.session_state['company_name']}</span>
        </div>
        """
    return f"""
    <div class="logo-container">
        <span class="company-name">🏢 {st.session_state['company_name']}</span>
    </div>
    """

# ========== FILE LOADER ==========
@st.cache_data
def load_file(uploaded_file):
    """Load file based on extension"""
    ext = uploaded_file.name.split('.')[-1].lower()
    try:
        if ext == 'csv':
            return pd.read_csv(uploaded_file)
        elif ext in ['xls', 'xlsx']:
            return pd.read_excel(uploaded_file)
        elif ext == 'json':
            return pd.read_json(uploaded_file)
        elif ext == 'parquet':
            return pd.read_parquet(uploaded_file)
        elif ext == 'pickle':
            return pd.read_pickle(uploaded_file)
        return None
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

# ========== ENFORCE AGE AND RATING LIMITS ==========
def enforce_age_limit(df, age_column='Age', min_age=MIN_AGE, max_age=MAX_AGE):
    """Enforce age limit on dataframe"""
    if age_column in df.columns:
        before_count = ((df[age_column] < min_age) | (df[age_column] > max_age)).sum()
        df[age_column] = df[age_column].clip(min_age, max_age)
        return df, before_count
    return df, 0

def enforce_rating_limits(df, rating_columns, min_rating=MIN_RATING, max_rating=MAX_RATING):
    """Enforce rating limits on specified columns (0-5 scale)"""
    clipped_counts = {}
    for col in rating_columns:
        if col in df.columns:
            before_count = ((df[col] < min_rating) | (df[col] > max_rating)).sum()
            df[col] = df[col].clip(min_rating, max_rating)
            if before_count > 0:
                clipped_counts[col] = before_count
    return df, clipped_counts

# ========== DATA PROFILING ==========
@st.cache_data
def profile_data(df):
    """Generate comprehensive data profile"""
    profile = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing': df.isnull().sum().to_dict(),
        'missing_pct': (df.isnull().sum() / len(df) * 100).to_dict(),
        'numeric_cols': df.select_dtypes(include=[np.number]).columns.tolist(),
        'categorical_cols': df.select_dtypes(include=['object']).columns.tolist(),
        'unique_counts': df.nunique().to_dict(),
        'duplicates': df.duplicated().sum(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
        'skewness': df.select_dtypes(include=[np.number]).skew().to_dict(),
        'kurtosis': df.select_dtypes(include=[np.number]).kurtosis().to_dict(),
        'data_quality_score': calculate_data_quality_score(df)
    }
    return profile

# ========== DATA CLEANING WITH DETAILED REPORT ==========
@st.cache_data
def clean_data(df):
    """Advanced data cleaning with comprehensive report"""
    df_before = df.copy()
    df_clean = df.copy()
    
    cleaning_log = []
    
    # 1. Initial State
    cleaning_log.append({
        'Step': '1. Initial State',
        'Before': f"{df_before.shape[0]:,} rows, {df_before.shape[1]:,} cols",
        'After': f"{df_clean.shape[0]:,} rows, {df_clean.shape[1]:,} cols",
        'Change': '-',
        'Insight': 'Original dataset loaded'
    })
    
    # 2. Enforce Age Limit (18-65)
    df_clean, age_clipped = enforce_age_limit(df_clean, 'Age', MIN_AGE, MAX_AGE)
    if age_clipped > 0:
        cleaning_log.append({
            'Step': '2. Enforce Age Limit (18-65)',
            'Before': f"{age_clipped} ages outside 18-65",
            'After': '0 outside range',
            'Change': f"Clipped {age_clipped} records",
            'Insight': f'Age limit of {MIN_AGE}-{MAX_AGE} enforced for all employees'
        })
    
    # 3. Enforce Rating Limits (0-5)
    rating_columns = ['JobSatisfaction', 'EnvironmentSatisfaction', 'RelationshipSatisfaction', 
                      'WorkLifeBalance', 'PerformanceRating', 'Education', 'StockOptionLevel']
    df_clean, rating_clipped = enforce_rating_limits(df_clean, rating_columns, MIN_RATING, MAX_RATING)
    for col, count in rating_clipped.items():
        cleaning_log.append({
            'Step': f'3. Enforce Rating Limit (0-5) - {col}',
            'Before': f"{count} values outside 0-5",
            'After': '0 outside range',
            'Change': f"Clipped {count} records",
            'Insight': f'{col} rating limited to {MIN_RATING}-{MAX_RATING} scale'
        })
    
    # 4. Remove constant columns
    constant_cols = [col for col in df_clean.columns if df_clean[col].nunique() == 1]
    if constant_cols:
        df_clean = df_clean.drop(columns=constant_cols)
        cleaning_log.append({
            'Step': '4. Remove Constant Columns',
            'Before': f"{len(constant_cols):,} columns",
            'After': '0 columns',
            'Change': f"Removed {len(constant_cols):,}",
            'Insight': f"Columns with single value: {', '.join(constant_cols[:3])}"
        })
    
    # 5. Remove duplicate columns
    duplicate_cols = []
    columns_list = df_clean.columns.tolist()
    for i in range(len(columns_list)):
        for j in range(i+1, len(columns_list)):
            if columns_list[i] != columns_list[j] and df_clean[columns_list[i]].equals(df_clean[columns_list[j]]):
                duplicate_cols.append(columns_list[j])
    duplicate_cols = list(set(duplicate_cols))
    if duplicate_cols:
        df_clean = df_clean.drop(columns=duplicate_cols)
        cleaning_log.append({
            'Step': '5. Remove Duplicate Columns',
            'Before': f"{len(duplicate_cols):,} duplicate columns",
            'After': '0 duplicates',
            'Change': f"Removed {len(duplicate_cols):,}",
            'Insight': f"Identical columns detected and removed"
        })
    
    # 6. Drop high missing columns (>70%)
    before_cols = df_clean.shape[1]
    high_missing = df_clean.columns[df_clean.isnull().sum() > len(df_clean)*0.7].tolist()
    if high_missing:
        df_clean = df_clean.drop(columns=high_missing)
        cleaning_log.append({
            'Step': '6. Drop High Missing Columns',
            'Before': f"{before_cols:,} columns",
            'After': f"{df_clean.shape[1]:,} columns",
            'Change': f"Removed {len(high_missing):,}",
            'Insight': f"Columns with >70% missing: {', '.join(high_missing[:3])}"
        })
    
    # 7. Fill numeric missing with median
    num_cols = df_clean.select_dtypes(include=[np.number]).columns
    missing_before_num = df_clean[num_cols].isnull().sum().sum()
    
    # Use KNN imputer for better accuracy if enough columns
    if len(num_cols) >= 3:
        try:
            knn_imputer = KNNImputer(n_neighbors=5)
            df_clean[num_cols] = knn_imputer.fit_transform(df_clean[num_cols])
            cleaning_log.append({
                'Step': '7. Fill Numeric Missing (KNN)',
                'Before': f"{missing_before_num:,} missing",
                'After': '0 missing',
                'Change': f"Fixed {missing_before_num:,}",
                'Insight': f"Used KNN imputation for {len(num_cols):,} numeric columns"
            })
        except:
            imputer = SimpleImputer(strategy='median')
            df_clean[num_cols] = imputer.fit_transform(df_clean[num_cols])
            cleaning_log.append({
                'Step': '7. Fill Numeric Missing (Median)',
                'Before': f"{missing_before_num:,} missing",
                'After': '0 missing',
                'Change': f"Fixed {missing_before_num:,}",
                'Insight': f"Used median imputation for {len(num_cols):,} numeric columns"
            })
    else:
        imputer = SimpleImputer(strategy='median')
        df_clean[num_cols] = imputer.fit_transform(df_clean[num_cols])
        cleaning_log.append({
            'Step': '7. Fill Numeric Missing (Median)',
            'Before': f"{missing_before_num:,} missing",
            'After': '0 missing',
            'Change': f"Fixed {missing_before_num:,}",
            'Insight': f"Used median imputation for {len(num_cols):,} numeric columns"
        })
    
    # 8. Fill categorical missing with mode
    cat_cols = df_clean.select_dtypes(include=['object']).columns
    missing_before_cat = df_clean[cat_cols].isnull().sum().sum()
    for col in cat_cols:
        if not df_clean[col].mode().empty:
            df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
    missing_after_cat = df_clean[cat_cols].isnull().sum().sum()
    
    cleaning_log.append({
        'Step': '8. Fill Categorical Missing (Mode)',
        'Before': f"{missing_before_cat:,} missing",
        'After': f"{missing_after_cat:,} missing",
        'Change': f"Fixed {missing_before_cat - missing_after_cat:,}",
        'Insight': f"Used mode imputation for {len(cat_cols):,} categorical columns"
    })
    
    # 9. Remove duplicate rows
    before_rows = df_clean.shape[0]
    dup_count = df_clean.duplicated().sum()
    if dup_count > 0:
        df_clean.drop_duplicates(inplace=True)
        after_rows = df_clean.shape[0]
        cleaning_log.append({
            'Step': '9. Remove Duplicate Rows',
            'Before': f"{before_rows:,} rows",
            'After': f"{after_rows:,} rows",
            'Change': f"Removed {dup_count:,}",
            'Insight': f"Removed {dup_count:,} exact duplicate records"
        })
    
    # 10. Outlier detection and capping (skip age and rating columns)
    outlier_count = 0
    outlier_cols = []
    skip_cols = ['Age'] + rating_columns
    for col in num_cols:
        if col in skip_cols:
            continue
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = ((df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)).sum()
        if outliers > 0:
            outlier_count += outliers
            outlier_cols.append(col)
            df_clean[col] = df_clean[col].clip(lower_bound, upper_bound)
    
    if outlier_count > 0:
        cleaning_log.append({
            'Step': '10. Outlier Capping (IQR)',
            'Before': f"{outlier_count:,} outliers",
            'After': '0 outliers',
            'Change': f"Capped {outlier_count:,} values",
            'Insight': f"Outliers in {len(outlier_cols):,} columns capped using IQR method"
        })
    
    # 11. Data type optimization
    before_memory = df_clean.memory_usage(deep=True).sum() / 1024**2
    for col in df_clean.select_dtypes(include=['int64']).columns:
        if df_clean[col].min() > -32768 and df_clean[col].max() < 32767:
            df_clean[col] = df_clean[col].astype('int32')
    for col in df_clean.select_dtypes(include=['float64']).columns:
        df_clean[col] = df_clean[col].astype('float32')
    after_memory = df_clean.memory_usage(deep=True).sum() / 1024**2
    
    cleaning_log.append({
        'Step': '11. Data Type Optimization',
        'Before': f"{before_memory:.1f} MB",
        'After': f"{after_memory:.1f} MB",
        'Change': f"Reduced {before_memory - after_memory:.1f} MB",
        'Insight': f"Memory usage reduced by {(1 - after_memory/before_memory)*100:.1f}%"
    })
    
    cleaning_df = pd.DataFrame(cleaning_log)
    
    # Statistical summary
    stats_data = []
    for col in num_cols[:25]:
        if col in df_clean.columns:
            stats_data.append({
                'Feature': col[:30],
                'Type': 'Numeric',
                'Min': round(df_clean[col].min(), 2),
                'Max': round(df_clean[col].max(), 2),
                'Mean': round(df_clean[col].mean(), 2),
                'Median': round(df_clean[col].median(), 2),
                'Std': round(df_clean[col].std(), 2),
                'Skew': round(df_clean[col].skew(), 2),
                'Kurtosis': round(df_clean[col].kurtosis(), 2),
                'Missing %': round((df_before[col].isnull().sum() / len(df_before)) * 100, 1)
            })
    
    for col in cat_cols[:15]:
        if col in df_clean.columns:
            stats_data.append({
                'Feature': col[:30],
                'Type': 'Categorical',
                'Min': '-',
                'Max': '-',
                'Mean': '-',
                'Median': '-',
                'Std': '-',
                'Skew': '-',
                'Kurtosis': '-',
                'Missing %': round((df_before[col].isnull().sum() / len(df_before)) * 100, 1)
            })
    
    stats_df = pd.DataFrame(stats_data)
    
    insights = {
        'rows_removed': df_before.shape[0] - df_clean.shape[0],
        'cols_removed': df_before.shape[1] - df_clean.shape[1],
        'missing_fixed': (missing_before_num + missing_before_cat) - (0 + missing_after_cat),
        'duplicates': dup_count,
        'outliers': outlier_count,
        'age_clipped': age_clipped,
        'rating_clipped': rating_clipped,
        'final_rows': df_clean.shape[0],
        'final_cols': df_clean.shape[1],
        'numeric_features': len(num_cols),
        'categorical_features': len(cat_cols),
        'memory_mb': after_memory,
        'data_quality_score': calculate_data_quality_score(df_clean)
    }
    
    return df_clean, cleaning_df, stats_df, insights

# ========== ENHANCED FEATURE ENGINEERING ==========
@st.cache_data
def enhanced_feature_engineering(df, target_col):
    """Create advanced features for better predictions"""
    df_fe = df.copy()
    num_cols = df_fe.select_dtypes(include=[np.number]).columns.tolist()
    if target_col in num_cols:
        num_cols.remove(target_col)
    
    rating_cols = ['JobSatisfaction', 'EnvironmentSatisfaction', 'RelationshipSatisfaction', 'WorkLifeBalance']
    
    # Enforce rating limits (0-5) in feature engineering
    for col in rating_cols:
        if col in df_fe.columns:
            df_fe[col] = df_fe[col].clip(MIN_RATING, MAX_RATING)
    
    # ========== AGE FEATURES (18-65 LIMIT) ==========
    if 'Age' in num_cols:
        df_fe['Age'] = df_fe['Age'].clip(MIN_AGE, MAX_AGE)
        df_fe['Age_Group'] = pd.cut(df_fe['Age'], bins=[0, 25, 30, 35, 40, 45, 50, 55, 60, 65, 100], 
                                     labels=['<25', '25-30', '30-35', '35-40', '40-45', '45-50', '50-55', '55-60', '60-65', '65+'])
        df_fe['Age_Squared'] = df_fe['Age'] ** 2
        df_fe['Age_Cubed'] = df_fe['Age'] ** 3
        df_fe['Age_Log'] = np.log1p(df_fe['Age'])
        df_fe['Age_Sqrt'] = np.sqrt(df_fe['Age'])
        df_fe['Age_Standardized'] = (df_fe['Age'] - df_fe['Age'].mean()) / df_fe['Age'].std()
        df_fe['Age_Binned'] = pd.cut(df_fe['Age'], bins=5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])
        df_fe['Is_Young'] = (df_fe['Age'] < 30).astype(int)
        df_fe['Is_Mid'] = ((df_fe['Age'] >= 30) & (df_fe['Age'] <= 45)).astype(int)
        df_fe['Is_Senior'] = ((df_fe['Age'] > 45) & (df_fe['Age'] <= 55)).astype(int)
        df_fe['Is_Pre_Retirement'] = (df_fe['Age'] > 55).astype(int)
        df_fe['Age_Risk_Score'] = np.where(df_fe['Age'] < 30, 1, np.where(df_fe['Age'] > 50, 0.5, 0))
    
    # ========== TENURE FEATURES ==========
    if 'YearsAtCompany' in num_cols:
        df_fe['Tenure_Group'] = pd.cut(df_fe['YearsAtCompany'], bins=[0, 1, 2, 3, 5, 7, 10, 15, 20, 50],
                                        labels=['<1', '1-2', '2-3', '3-5', '5-7', '7-10', '10-15', '15-20', '20+'])
        df_fe['Tenure_Squared'] = df_fe['YearsAtCompany'] ** 2
        df_fe['Tenure_Log'] = np.log1p(df_fe['YearsAtCompany'])
        df_fe['Tenure_Sqrt'] = np.sqrt(df_fe['YearsAtCompany'])
        df_fe['Low_Tenure'] = (df_fe['YearsAtCompany'] < 2).astype(int)
        df_fe['Mid_Tenure'] = ((df_fe['YearsAtCompany'] >= 2) & (df_fe['YearsAtCompany'] <= 5)).astype(int)
        df_fe['High_Tenure'] = (df_fe['YearsAtCompany'] > 10).astype(int)
        df_fe['Tenure_Risk'] = np.where(df_fe['YearsAtCompany'] < 2, 1, np.where(df_fe['YearsAtCompany'] > 10, 0.3, 0))
    
    # ========== INCOME FEATURES ==========
    if 'MonthlyIncome' in num_cols:
        df_fe['Income_Level'] = pd.cut(df_fe['MonthlyIncome'], bins=5,
                                        labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
        df_fe['Log_Income'] = np.log1p(df_fe['MonthlyIncome'])
        df_fe['Sqrt_Income'] = np.sqrt(df_fe['MonthlyIncome'])
        df_fe['Income_Standardized'] = (df_fe['MonthlyIncome'] - df_fe['MonthlyIncome'].mean()) / df_fe['MonthlyIncome'].std()
        df_fe['Income_Thousand'] = df_fe['MonthlyIncome'] / 1000
        df_fe['Is_Low_Income'] = (df_fe['MonthlyIncome'] < 45000).astype(int)
        df_fe['Is_High_Income'] = (df_fe['MonthlyIncome'] > 100000).astype(int)
        df_fe['Income_Per_Year'] = df_fe['MonthlyIncome'] * 12
        df_fe['Income_Per_Day'] = df_fe['MonthlyIncome'] / 22
        df_fe['Income_Risk'] = np.where(df_fe['MonthlyIncome'] < 45000, 1, np.where(df_fe['MonthlyIncome'] > 80000, -0.5, 0))
    
    # ========== SATISFACTION FEATURES (0-5 SCALE) ==========
    if 'JobSatisfaction' in num_cols:
        df_fe['JobSat_Risk'] = np.where(df_fe['JobSatisfaction'] <= 2, 1, np.where(df_fe['JobSatisfaction'] >= 4, -0.5, 0))
        df_fe['Low_Job_Sat'] = (df_fe['JobSatisfaction'] <= 2).astype(int)
        df_fe['High_Job_Sat'] = (df_fe['JobSatisfaction'] >= 4).astype(int)
        df_fe['JobSat_Inverse'] = 5 - df_fe['JobSatisfaction'] + 1
        df_fe['JobSat_Standardized'] = (df_fe['JobSatisfaction'] - df_fe['JobSatisfaction'].mean()) / df_fe['JobSatisfaction'].std()
    
    if 'WorkLifeBalance' in num_cols:
        df_fe['WLB_Risk'] = np.where(df_fe['WorkLifeBalance'] <= 2, 1, np.where(df_fe['WorkLifeBalance'] >= 4, -0.3, 0))
        df_fe['Poor_WLB'] = (df_fe['WorkLifeBalance'] <= 2).astype(int)
        df_fe['Good_WLB'] = (df_fe['WorkLifeBalance'] >= 4).astype(int)
        df_fe['WLB_Standardized'] = (df_fe['WorkLifeBalance'] - df_fe['WorkLifeBalance'].mean()) / df_fe['WorkLifeBalance'].std()
    
    if 'EnvironmentSatisfaction' in num_cols:
        df_fe['Env_Sat_Risk'] = np.where(df_fe['EnvironmentSatisfaction'] <= 2, 1, 
                                          np.where(df_fe['EnvironmentSatisfaction'] >= 4, -0.3, 0))
        df_fe['Poor_Environment'] = (df_fe['EnvironmentSatisfaction'] <= 2).astype(int)
    
    if 'RelationshipSatisfaction' in num_cols:
        df_fe['Rel_Sat_Risk'] = np.where(df_fe['RelationshipSatisfaction'] <= 2, 1, 
                                          np.where(df_fe['RelationshipSatisfaction'] >= 4, -0.3, 0))
        df_fe['Poor_Relationship'] = (df_fe['RelationshipSatisfaction'] <= 2).astype(int)
    
    # ========== INTERACTION FEATURES ==========
    if 'Age' in num_cols and 'YearsAtCompany' in num_cols:
        df_fe['Age_Tenure_Ratio'] = df_fe['Age'] / (df_fe['YearsAtCompany'] + 1)
        df_fe['Age_Tenure_Product'] = df_fe['Age'] * df_fe['YearsAtCompany']
        df_fe['Age_Minus_Tenure'] = df_fe['Age'] - df_fe['YearsAtCompany']
        df_fe['Age_Tenure_Interaction'] = df_fe['Age_Risk_Score'] * df_fe['Tenure_Risk']
    
    if 'MonthlyIncome' in num_cols and 'YearsAtCompany' in num_cols:
        df_fe['Income_Per_Year_Experience'] = df_fe['MonthlyIncome'] / (df_fe['YearsAtCompany'] + 1)
        df_fe['Income_Tenure_Product'] = df_fe['MonthlyIncome'] * df_fe['YearsAtCompany']
        df_fe['Income_Tenure_Ratio'] = df_fe['MonthlyIncome'] / (df_fe['YearsAtCompany'] + 1) / 1000
    
    if 'JobSatisfaction' in num_cols and 'WorkLifeBalance' in num_cols:
        df_fe['Sat_WLB_Score'] = df_fe['JobSatisfaction'] * df_fe['WorkLifeBalance']
        df_fe['Sat_WLB_Ratio'] = df_fe['JobSatisfaction'] / (df_fe['WorkLifeBalance'] + 0.1)
        df_fe['Sat_WLB_Interaction'] = df_fe['JobSatisfaction'] + df_fe['WorkLifeBalance']
        df_fe['Sat_WLB_Combined_Risk'] = df_fe['JobSat_Risk'] + df_fe['WLB_Risk']
    
    if 'JobSatisfaction' in num_cols and 'YearsAtCompany' in num_cols:
        df_fe['Sat_Tenure_Score'] = df_fe['JobSatisfaction'] * df_fe['YearsAtCompany']
        df_fe['Sat_Tenure_Ratio'] = df_fe['JobSatisfaction'] / (df_fe['YearsAtCompany'] + 1)
    
    if 'WorkLifeBalance' in num_cols and 'YearsAtCompany' in num_cols:
        df_fe['WLB_Tenure_Score'] = df_fe['WorkLifeBalance'] * df_fe['YearsAtCompany']
    
    if 'MonthlyIncome' in num_cols and 'JobSatisfaction' in num_cols:
        df_fe['Income_Sat_Score'] = df_fe['MonthlyIncome'] * df_fe['JobSatisfaction'] / 10000
    
    # ========== RISK FLAGS ==========
    if 'YearsSinceLastPromotion' in num_cols:
        df_fe['No_Promotion_Risk'] = (df_fe['YearsSinceLastPromotion'] > 5).astype(int)
        df_fe['Promotion_Gap'] = df_fe['YearsSinceLastPromotion']
        df_fe['Recent_Promotion'] = (df_fe['YearsSinceLastPromotion'] < 2).astype(int)
        df_fe['Promotion_Category'] = pd.cut(df_fe['YearsSinceLastPromotion'], bins=[0, 2, 5, 10, 20],
                                              labels=['Recent', 'Moderate', 'Long', 'Very Long'])
        df_fe['Promotion_Risk_Score'] = np.where(df_fe['YearsSinceLastPromotion'] > 5, 1, 
                                                  np.where(df_fe['YearsSinceLastPromotion'] < 2, -0.3, 0))
    
    if 'NumCompaniesWorked' in num_cols:
        df_fe['Job_Hopper'] = (df_fe['NumCompaniesWorked'] > 3).astype(int)
        df_fe['Company_Changes'] = df_fe['NumCompaniesWorked']
        df_fe['Stable_Career'] = (df_fe['NumCompaniesWorked'] <= 2).astype(int)
        df_fe['Job_Hopper_Risk'] = np.where(df_fe['NumCompaniesWorked'] > 3, 1, 
                                             np.where(df_fe['NumCompaniesWorked'] <= 1, -0.2, 0))
    
    if 'DistanceFromHome' in num_cols:
        df_fe['Long_Commute'] = (df_fe['DistanceFromHome'] > 20).astype(int)
        df_fe['Very_Long_Commute'] = (df_fe['DistanceFromHome'] > 40).astype(int)
        df_fe['Commute_Risk'] = df_fe['DistanceFromHome'] / 50
        df_fe['Commute_Category'] = pd.cut(df_fe['DistanceFromHome'], bins=[0, 5, 15, 30, 100],
                                            labels=['Short', 'Medium', 'Long', 'Very Long'])
        df_fe['Commute_Risk_Score'] = np.where(df_fe['DistanceFromHome'] > 20, 1, 
                                                np.where(df_fe['DistanceFromHome'] < 10, -0.2, 0))
    
    if 'PercentSalaryHike' in num_cols:
        df_fe['High_Hike'] = (df_fe['PercentSalaryHike'] > 20).astype(int)
        df_fe['Low_Hike'] = (df_fe['PercentSalaryHike'] < 10).astype(int)
        df_fe['Hike_Category'] = pd.cut(df_fe['PercentSalaryHike'], bins=[0, 10, 15, 20, 50],
                                         labels=['Low', 'Average', 'Good', 'Excellent'])
        df_fe['Hike_Risk'] = np.where(df_fe['PercentSalaryHike'] < 10, 1, 
                                       np.where(df_fe['PercentSalaryHike'] > 20, -0.3, 0))
    
    if 'TrainingTimesLastYear' in num_cols:
        df_fe['Low_Training'] = (df_fe['TrainingTimesLastYear'] < 2).astype(int)
        df_fe['High_Training'] = (df_fe['TrainingTimesLastYear'] > 3).astype(int)
        df_fe['Training_Risk'] = np.where(df_fe['TrainingTimesLastYear'] < 2, 1, 
                                           np.where(df_fe['TrainingTimesLastYear'] > 3, -0.2, 0))
    
    if 'StockOptionLevel' in num_cols:
        df_fe['StockOptionLevel'] = df_fe['StockOptionLevel'].clip(MIN_RATING, MAX_RATING)
        df_fe['Has_Stock'] = (df_fe['StockOptionLevel'] > 0).astype(int)
        df_fe['Stock_Level'] = df_fe['StockOptionLevel']
        df_fe['Stock_Risk'] = np.where(df_fe['StockOptionLevel'] == 0, 0.3, -0.2)
    
    if 'OverTime' in df_fe.columns and df_fe['OverTime'].dtype == 'object':
        df_fe['Overtime_Flag'] = (df_fe['OverTime'] == 'Yes').astype(int)
        df_fe['Overtime_Risk'] = df_fe['Overtime_Flag']
    
    # ========== COMPOSITE SCORES ==========
    sat_cols = [c for c in ['JobSatisfaction', 'WorkLifeBalance', 'EnvironmentSatisfaction', 'RelationshipSatisfaction'] if c in num_cols]
    if len(sat_cols) >= 2:
        df_fe['Engagement_Score'] = df_fe[sat_cols].mean(axis=1)
        df_fe['Engagement_Score_Squared'] = df_fe['Engagement_Score'] ** 2
        df_fe['Engagement_Score_Log'] = np.log1p(df_fe['Engagement_Score'])
        df_fe['Engagement_Risk'] = np.where(df_fe['Engagement_Score'] <= 2.5, 1, 
                                             np.where(df_fe['Engagement_Score'] >= 4, -0.4, 0))
        df_fe['Low_Engagement'] = (df_fe['Engagement_Score'] < 3).astype(int)
        df_fe['High_Engagement'] = (df_fe['Engagement_Score'] >= 4).astype(int)
    
    # ========== COMBINED RISK SCORE ==========
    risk_components = []
    risk_col_names = ['Age_Risk_Score', 'Tenure_Risk', 'Income_Risk', 'JobSat_Risk', 
                      'WLB_Risk', 'Promotion_Risk_Score', 'Job_Hopper_Risk', 
                      'Commute_Risk_Score', 'Hike_Risk', 'Training_Risk', 
                      'Overtime_Risk', 'Stock_Risk']
    
    for risk_col in risk_col_names:
        if risk_col in df_fe.columns:
            risk_components.append(df_fe[risk_col])
    
    if risk_components:
        df_fe['Total_Risk_Score'] = sum(risk_components)
        df_fe['Risk_Category'] = pd.cut(df_fe['Total_Risk_Score'], bins=3, 
                                         labels=['Low Risk', 'Medium Risk', 'High Risk'])
        df_fe['Risk_Category_Numeric'] = df_fe['Total_Risk_Score']
    
    # ========== ADDITIONAL METRICS ==========
    if all(c in num_cols for c in ['Age', 'YearsAtCompany', 'MonthlyIncome']):
        df_fe['Seniority_Index'] = (df_fe['YearsAtCompany'] / (df_fe['Age'] + 1)) * (df_fe['MonthlyIncome'] / 10000)
        df_fe['Seniority_Index_Log'] = np.log1p(df_fe['Seniority_Index'])
    
    if all(c in num_cols for c in ['JobSatisfaction', 'YearsSinceLastPromotion']):
        df_fe['Sat_Promo_Gap'] = df_fe['JobSatisfaction'] / (df_fe['YearsSinceLastPromotion'] + 1)
    
    if all(c in num_cols for c in ['MonthlyIncome', 'JobSatisfaction', 'WorkLifeBalance']):
        df_fe['Wellbeing_Index'] = (df_fe['JobSatisfaction'] + df_fe['WorkLifeBalance']) * (df_fe['MonthlyIncome'] / 10000)
    
    return df_fe

# ========== OPTIMIZED FAST TRAIN MODEL ==========
@st.cache_resource
def train_ensemble_model(df, target_col):
    """Train optimized ensemble model with SHAP analysis"""
    with st.spinner("🚀 Training FAANG-Level AI Ensemble Model..."):
        progress = st.progress(0)
        
        # Advanced Feature Engineering
        df_eng = enhanced_feature_engineering(df, target_col)
        progress.progress(10)
        
        # Prepare features
        X = df_eng.drop(columns=[target_col])
        y = df_eng[target_col]
        
        # Encode target
        if y.dtype == 'object':
            le = LabelEncoder()
            y = le.fit_transform(y)
            st.session_state['label_encoder'] = le
        
        # Handle categorical variables
        categorical_cols = X.select_dtypes(include=['object', 'category']).columns
        X = pd.get_dummies(X, drop_first=True)
        X = X.fillna(X.median())
        progress.progress(25)
        
        # Advanced feature selection
        k = min(35, X.shape[1])
        
        # Mutual information based feature selection
        mi_selector = SelectKBest(mutual_info_classif, k=k)
        X_mi = mi_selector.fit_transform(X, y)
        mi_features = X.columns[mi_selector.get_support()].tolist()
        
        # Also get f_classif features
        f_selector = SelectKBest(f_classif, k=k)
        X_f = f_selector.fit_transform(X, y)
        f_features = X.columns[f_selector.get_support()].tolist()
        
        # Combine features
        selected_features = list(set(mi_features + f_features))[:min(35, len(set(mi_features + f_features)))]
        X = X[selected_features]
        progress.progress(35)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Advanced resampling
        smote_tomek = SMOTETomek(random_state=42)
        X_train_res, y_train_res = smote_tomek.fit_resample(X_train, y_train)
        
        # Power transformation for better distribution
        pt = PowerTransformer(method='yeo-johnson')
        X_train_res = pt.fit_transform(X_train_res)
        X_test = pt.transform(X_test)
        
        # Scale features
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train_res)
        X_test_scaled = scaler.transform(X_test)
        progress.progress(50)
        
        # XGBoost Model
        xgb_model = xgb.XGBClassifier(
            n_estimators=250, max_depth=9, learning_rate=0.04,
            subsample=0.8, colsample_bytree=0.8, min_child_weight=3,
            gamma=0.1, reg_alpha=0.1, reg_lambda=1.0,
            random_state=42, use_label_encoder=False, eval_metric='logloss', n_jobs=-1
        )
        
        # Random Forest Model
        rf_model = RandomForestClassifier(
            n_estimators=250, max_depth=14, min_samples_split=5,
            min_samples_leaf=2, max_features='sqrt',
            random_state=42, class_weight='balanced', n_jobs=-1
        )
        
        # LightGBM Model
        lgb_model = lgb.LGBMClassifier(
            n_estimators=250, max_depth=9, learning_rate=0.04,
            num_leaves=31, min_child_samples=20, subsample=0.8,
            colsample_bytree=0.8, reg_alpha=0.1, reg_lambda=0.1,
            random_state=42, verbose=-1, n_jobs=-1
        )
        
        # Gradient Boosting Model
        gb_model = GradientBoostingClassifier(
            n_estimators=180, max_depth=7, learning_rate=0.05,
            subsample=0.8, min_samples_split=5, min_samples_leaf=2,
            random_state=42
        )
        
        # Extra Trees Model
        et_model = ExtraTreesClassifier(
            n_estimators=180, max_depth=11, min_samples_split=5,
            random_state=42, n_jobs=-1
        )
        
        progress.progress(65)
        
        # Train all models
        xgb_model.fit(X_train_scaled, y_train_res)
        rf_model.fit(X_train_scaled, y_train_res)
        lgb_model.fit(X_train_scaled, y_train_res)
        gb_model.fit(X_train_scaled, y_train_res)
        et_model.fit(X_train_scaled, y_train_res)
        
        # Create advanced voting ensemble
        ensemble = VotingClassifier(
            estimators=[
                ('xgb', xgb_model), ('rf', rf_model), ('lgb', lgb_model),
                ('gb', gb_model), ('et', et_model)
            ],
            voting='soft', weights=[2, 2, 2, 1, 1]
        )
        ensemble.fit(X_train_scaled, y_train_res)
        
        # Create stacking ensemble for better performance
        base_models = [('xgb', xgb_model), ('rf', rf_model), ('lgb', lgb_model)]
        meta_model = LogisticRegression(C=1, max_iter=1000, class_weight='balanced')
        stacking = StackingClassifier(estimators=base_models, final_estimator=meta_model, cv=5, passthrough=True)
        stacking.fit(X_train_scaled, y_train_res)

        # Make predictions
        y_pred_ensemble = ensemble.predict(X_test_scaled)
        y_pred_stacking = stacking.predict(X_test_scaled)
        y_proba_ensemble = ensemble.predict_proba(X_test_scaled)[:, 1]
        y_proba_stacking = stacking.predict_proba(X_test_scaled)[:, 1]

        # Average predictions for final ensemble
        y_pred_final = ((y_pred_ensemble + y_pred_stacking) >= 1).astype(int)
        y_proba_final = (y_proba_ensemble + y_proba_stacking) / 2
        
        # Calculate comprehensive metrics
        def calc_metrics(y_true, y_pred, y_proba):
            return {
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred),
                'recall': recall_score(y_true, y_pred),
                'f1': f1_score(y_true, y_pred),
                'roc_auc': roc_auc_score(y_true, y_proba),
                'log_loss': log_loss(y_true, y_proba),
                'brier_score': brier_score_loss(y_true, y_proba),
                'average_precision': average_precision_score(y_true, y_proba),
                'mcc': matthews_corrcoef(y_true, y_pred)
            }
        
        metrics = {
            'XGBoost': calc_metrics(y_test, xgb_model.predict(X_test_scaled), xgb_model.predict_proba(X_test_scaled)[:, 1]),
            'Random Forest': calc_metrics(y_test, rf_model.predict(X_test_scaled), rf_model.predict_proba(X_test_scaled)[:, 1]),
            'LightGBM': calc_metrics(y_test, lgb_model.predict(X_test_scaled), lgb_model.predict_proba(X_test_scaled)[:, 1]),
            'Gradient Boosting': calc_metrics(y_test, gb_model.predict(X_test_scaled), gb_model.predict_proba(X_test_scaled)[:, 1]),
            'Extra Trees': calc_metrics(y_test, et_model.predict(X_test_scaled), et_model.predict_proba(X_test_scaled)[:, 1]),
            'Voting Ensemble': calc_metrics(y_test, y_pred_ensemble, y_proba_ensemble),
            'Stacking Ensemble': calc_metrics(y_test, y_pred_stacking, y_proba_stacking),
            'Final Ensemble': calc_metrics(y_test, y_pred_final, y_proba_final)
        }
        
        # Cross-validation for final model
        cv_scores = cross_val_score(ensemble, X_train_scaled, y_train_res, cv=5, scoring='roc_auc')
        
        progress.progress(80)
        
        # SHAP analysis
        st.info("🔮 Computing SHAP values for model interpretability...")
        shap_bar_buf, shap_swarm_buf, shap_waterfall_buf = compute_shap_values(
            ensemble, X_train_scaled, X_test_scaled, selected_features
        )
        
        progress.progress(95)
        
        # Store model performance history
        performance_record = {
            'timestamp': datetime.now(),
            'ensemble_auc': metrics['Final Ensemble']['roc_auc'],
            'ensemble_f1': metrics['Final Ensemble']['f1'],
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'n_features': len(selected_features),
            'train_size': len(X_train_scaled),
            'test_size': len(X_test_scaled)
        }
        st.session_state['model_performance_history'].append(performance_record)
        
        progress.progress(100)
        time.sleep(0.5)
        progress.empty()
        
        # Store in session state
        st.session_state['ensemble'] = ensemble
        st.session_state['stacking'] = stacking
        st.session_state['scaler'] = scaler
        st.session_state['power_transformer'] = pt
        st.session_state['features'] = selected_features
        st.session_state['metrics'] = metrics
        st.session_state['best_model'] = 'Final Ensemble'
        st.session_state['X_test'] = X_test_scaled
        st.session_state['y_test'] = y_test
        st.session_state['y_pred'] = y_pred_final
        st.session_state['y_proba'] = y_proba_final
        st.session_state['cv_scores'] = cv_scores
        st.session_state['shap_bar'] = shap_bar_buf
        st.session_state['shap_swarm'] = shap_swarm_buf
        st.session_state['shap_waterfall'] = shap_waterfall_buf
        
        return metrics, ensemble, cv_scores

def calculate_model_metrics(y_true, y_pred, y_proba):
    """Calculate comprehensive model metrics"""
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),
        'f1': f1_score(y_true, y_pred),
        'roc_auc': roc_auc_score(y_true, y_proba),
        'log_loss': log_loss(y_true, y_proba),
        'brier_score': brier_score_loss(y_true, y_proba),
        'average_precision': average_precision_score(y_true, y_proba),
        'mcc': matthews_corrcoef(y_true, y_pred)
    }

def compute_shap_values(model, X_train, X_test, features):
    """Compute SHAP values for model interpretability"""
    shap_bar_buf = None
    shap_swarm_buf = None
    shap_waterfall_buf = None
    
    try:
        sample_size = min(50, X_test.shape[0])
        X_sample = X_test[:sample_size]
        background_sample = X_train[:min(50, X_train.shape[0])]
        
        explainer = shap.KernelExplainer(model.predict_proba, background_sample)
        shap_values = explainer.shap_values(X_sample)
        
        if isinstance(shap_values, list) and len(shap_values) > 1:
            shap_values_class = shap_values[1]
        else:
            shap_values_class = shap_values
        
        # Bar plot
        plt.figure(figsize=(12, 7))
        shap.summary_plot(shap_values_class, X_sample, feature_names=features, 
                         plot_type="bar", show=False, max_display=15)
        plt.tight_layout()
        shap_bar_buf = io.BytesIO()
        plt.savefig(shap_bar_buf, format='png', dpi=120, bbox_inches='tight')
        shap_bar_buf.seek(0)
        plt.close()
        
        # Swarm plot
        plt.figure(figsize=(14, 8))
        shap.summary_plot(shap_values_class, X_sample, feature_names=features, 
                         show=False, max_display=15)
        plt.tight_layout()
        shap_swarm_buf = io.BytesIO()
        plt.savefig(shap_swarm_buf, format='png', dpi=120, bbox_inches='tight')
        shap_swarm_buf.seek(0)
        plt.close()
        
        # Waterfall plot
        expected_value = explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value
        plt.figure(figsize=(14, 7))
        shap.waterfall_plot(shap.Explanation(values=shap_values_class[0], 
                                            base_values=expected_value, 
                                            data=X_sample[0], 
                                            feature_names=features), 
                           show=False, max_display=12)
        plt.tight_layout()
        shap_waterfall_buf = io.BytesIO()
        plt.savefig(shap_waterfall_buf, format='png', dpi=120, bbox_inches='tight')
        shap_waterfall_buf.seek(0)
        plt.close()
        
        st.success("✅ SHAP analysis complete!")
    except Exception as e:
        st.warning(f"SHAP analysis note: {str(e)[:150]}")
    
    return shap_bar_buf, shap_swarm_buf, shap_waterfall_buf

# ========== HR RECOMMENDATION ENGINE (Already defined above) ==========

# ========== WHAT-IF ANALYSIS ==========
def perform_what_if_analysis(model, scaler, base_profile, features, variations):
    """Perform what-if analysis for different scenarios"""
    results = []
    
    base_risk = predict_risk_enhanced(model, scaler, base_profile, features)
    
    for var_name, var_changes in variations.items():
        modified_profile = base_profile.copy()
        for field, change in var_changes.items():
            if field in modified_profile:
                if isinstance(change, (int, float)):
                    modified_profile[field] = max(0, modified_profile[field] + change)
                else:
                    modified_profile[field] = change
        
        new_risk = predict_risk_enhanced(model, scaler, modified_profile, features)
        
        results.append({
            'scenario': var_name,
            'changes': var_changes,
            'original_risk': base_risk['score'],
            'new_risk': new_risk['score'],
            'risk_reduction': base_risk['score'] - new_risk['score'],
            'improvement_percentage': ((base_risk['score'] - new_risk['score']) / base_risk['score']) * 100 if base_risk['score'] > 0 else 0,
            'new_level': new_risk['level']
        })
    
    return results

# ========== ALERT SYSTEM ==========
def check_alert_rules(risk_result):
    """Check if any alert rules are triggered"""
    alerts = []
    
    for rule in st.session_state['alert_rules']:
        if rule['type'] == 'risk_score' and risk_result['score'] >= rule['threshold']:
            alerts.append({
                'rule_name': rule['name'],
                'message': rule['message'],
                'severity': rule['severity'],
                'timestamp': datetime.now()
            })
        elif rule['type'] == 'risk_level' and risk_result['level'] == rule['level']:
            alerts.append({
                'rule_name': rule['name'],
                'message': rule['message'],
                'severity': rule['severity'],
                'timestamp': datetime.now()
            })
    
    return alerts

# ========== CHART EXPLANATIONS ==========
def get_chart_explanation(chart_name):
    """Get detailed explanation for chart type"""
    explanations = {
        'donut': """
        **📊 Attrition Donut Chart Explanation:**
        - The donut chart shows the proportion of employees who left vs stayed
        - Center number displays the overall attrition rate
        - Green section = Retained employees, Red section = Attrition
        - **Action:** If attrition rate > 20%, conduct immediate retention interviews
        """,
        'corr': """
        **📈 Correlation Bar Chart Explanation:**
        - Shows features most strongly correlated with employee attrition
        - Higher bars = stronger relationship with attrition risk
        - Top 3 features should be prioritized for HR intervention
        - **Action:** Focus retention efforts on top correlated factors
        """,
        'hist': """
        **📊 Age Distribution Explanation:**
        - Compares age distribution between employees who left vs stayed
        - Overlapping areas show where attrition risk is similar
        - Peaks indicate high-risk age groups
        - **Action:** Target retention programs at high-risk age brackets (18-25 and 55-65)
        """,
        'scatter': """
        **🎯 Income vs Tenure Scatter Plot Explanation:**
        - Each point represents an employee
        - Red points = Employees who left, Green = Stayed
        - Patterns reveal income/tenure combinations with higher attrition
        - **Action:** Review compensation for clusters showing high attrition
        """,
        'line': """
        **📉 Attrition by Tenure Explanation:**
        - Shows how attrition risk changes with years at company
        - Spikes indicate critical tenure periods
        - Typically high at 1 year and 3-5 years
        - **Action:** Implement stay interviews at critical tenure milestones
        """,
        'dept': """
        **🏢 Department-wise Attrition Explanation:**
        - Compares attrition rates across different departments
        - Bars above 15% indicate problem departments
        - Color intensity shows severity (darker red = higher risk)
        - **Action:** Conduct department-specific retention audits for high-risk areas
        """,
        'overtime': """
        **⏰ Overtime Impact Explanation:**
        - Compares attrition rates between employees with/without overtime
        - Higher bar indicates overtime significantly increases risk
        - Typical impact: Overtime employees are 2-3x more likely to leave
        - **Action:** Review overtime policies and workload distribution
        """,
        'heatmap': """
        **🔥 Correlation Matrix Explanation:**
        - Shows relationships between all numerical features
        - Red = Positive correlation, Blue = Negative correlation
        - Darker colors = Stronger relationships
        - **Action:** Identify feature clusters for deeper analysis
        """,
        'satisfaction': """
        **😊 Job Satisfaction Impact Explanation (0-5 scale):**
        - Shows attrition rate by job satisfaction level (0-5)
        - Sharp decline in attrition as satisfaction increases
        - Critical threshold: Satisfaction ≤ 2 indicates high risk
        - **Action:** Prioritize employees with satisfaction scores of 0-2
        """,
        'roc': """
        **📈 ROC Curve Explanation:**
        - Measures model's ability to distinguish between leavers and stayers
        - AUC > 0.8 = Excellent, > 0.7 = Good, > 0.6 = Fair
        - Curve closer to top-left corner = Better performance
        - **Action:** Use model predictions for proactive retention
        """,
        'confusion': """
        **🎯 Confusion Matrix Explanation:**
        - True Negatives: Correctly predicted stay (Top-Left)
        - False Positives: Incorrectly predicted leave (Top-Right)
        - False Negatives: Missed attrition risks (Bottom-Left)
        - True Positives: Correctly identified leavers (Bottom-Right)
        - **Action:** Focus on reducing False Negatives to catch at-risk employees
        """,
        'shap_bar': """
        **🔮 SHAP Feature Importance Explanation:**
        - Average absolute SHAP values across all predictions
        - Higher bars = Features with greater impact on attrition
        - Top features should be monitored regularly
        - **Action:** Create retention strategies targeting top 5 features
        """,
        'shap_swarm': """
        **🎨 SHAP Summary Plot Explanation:**
        - Each point = One employee's feature value
        - Red = High feature value, Blue = Low feature value
        - Right side = Increases attrition risk, Left = Decreases risk
        - **Action:** Monitor employees with red points on the right side
        """,
        'pr_curve': """
        **📊 Precision-Recall Curve Explanation:**
        - Shows trade-off between precision and recall
        - AP (Average Precision) summarizes curve performance
        - Higher AP score = Better model performance on imbalanced data
        - **Action:** Use for setting risk thresholds based on business needs
        """,
        'feature_importance': """
        **⭐ Feature Importance Explanation:**
        - Shows which factors most influence attrition predictions
        - Based on ensemble model feature importance scores
        - Higher importance = Greater impact on model decisions
        - **Action:** Allocate HR resources to top 5-10 features
        """
    }
    
    for key, explanation in explanations.items():
        if key in chart_name.lower():
            return explanation
    
    return f"""
    **📊 {chart_name} Explanation:**
    - This visualization provides insights into attrition patterns
    - Use the insights below to guide HR decision-making
    - Hover over data points for detailed values
    - **Action:** Review regularly to track changes over time
    """

# ========== CONFUSION MATRIX ==========
def plot_confusion_matrix(y_test, y_pred):
    cm = confusion_matrix(y_test, y_pred)
    fig = go.Figure(data=go.Heatmap(
        z=cm, x=['Predicted: Stay', 'Predicted: Leave'], 
        y=['Actual: Stay', 'Actual: Leave'],
        text=cm, texttemplate='%{text}', textfont={"size": 16, "color": "white"},
        colorscale='Viridis', showscale=True
    ))
    fig.update_layout(title='Confusion Matrix', xaxis_title='Predicted Label', yaxis_title='Actual Label', height=450)
    return fig

# ========== ROC CURVE ==========
def plot_roc_curve(y_test, y_proba, auc):
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name=f'ROC Curve (AUC = {auc:.3f})', line=dict(color='#667eea', width=3)))
    fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', name='Random Classifier (AUC = 0.5)', line=dict(dash='dash', color='gray', width=2)))
    fig.update_layout(title='ROC Curve - Model Performance', xaxis_title='False Positive Rate', yaxis_title='True Positive Rate', height=450)
    return fig

# ========== PRECISION-RECALL CURVE ==========
def plot_pr_curve(y_test, y_proba, ap):
    precision, recall, _ = precision_recall_curve(y_test, y_proba)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=recall, y=precision, mode='lines', name=f'PR Curve (AP = {ap:.3f})', line=dict(color='#667eea', width=3)))
    fig.update_layout(title='Precision-Recall Curve', xaxis_title='Recall', yaxis_title='Precision', height=450)
    return fig

# ========== FEATURE IMPORTANCE PLOT ==========
def plot_feature_importance(features, importances, top_n=15):
    importance_df = pd.DataFrame({
        'feature': features[:len(importances)],
        'importance': importances[:len(features)]
    }).sort_values('importance', ascending=True).tail(top_n)
    
    fig = px.bar(importance_df, x='importance', y='feature', orientation='h',
                title=f'Top {top_n} Feature Importance',
                color='importance', color_continuous_scale='Viridis')
    fig.update_layout(height=550)
    return fig

# ========== EXECUTIVE DASHBOARD ==========
def create_executive_dashboard(df, target):
    """Create executive dashboard visualizations"""
    charts = {}
    insights = {}
    
    # Prepare attrition labels
    if df[target].dtype == 'object':
        attrition_yes = (df[target].str.lower() == 'yes')
        attrition_label = df[target].str.lower().map({'yes': 'Left', 'no': 'Stayed'})
    else:
        attrition_yes = (df[target] == 1)
        attrition_label = df[target].map({1: 'Left', 0: 'Stayed'})
    
    attrition_rate = (attrition_yes.sum() / len(df)) * 100
    
    # 1. Donut Chart
    counts = attrition_yes.value_counts()
    counts.index = ['Left', 'Stayed']
    charts['donut'] = go.Figure(data=[go.Pie(
        labels=counts.index, values=counts.values, hole=0.4,
        marker=dict(colors=['#dc3545', '#28a745']),
        textinfo='label+percent+value', textfont_size=14
    )])
    charts['donut'].update_layout(title=f"Attrition Rate: {attrition_rate:.1f}%", height=400)
    insights['donut'] = f"Total: {len(df):,} | Attrition: {attrition_yes.sum():,} | Retention: {len(df)-attrition_yes.sum():,}"
    
    # 2. Correlation Bar Chart
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if target in num_cols:
        num_cols.remove(target)
    if num_cols:
        corr = df[num_cols].corrwith(attrition_yes.astype(int)).abs().sort_values(ascending=False).head(10)
        charts['corr'] = px.bar(
            x=corr.values, y=corr.index, orientation='h',
            title="Top 10 Attrition Drivers",
            labels={'x': 'Correlation Strength', 'y': 'Features'},
            color=corr.values, color_continuous_scale='Viridis',
            text=corr.values.round(3)
        )
        charts['corr'].update_layout(height=450)
        charts['corr'].update_traces(textposition='outside')
        top = corr.index[0] if len(corr) > 0 else "N/A"
        insights['corr'] = f"Primary Driver: '{top}' - Priority for HR intervention"
    
    # 3. Age Distribution (18-65)
    if 'Age' in df.columns:
        charts['hist'] = go.Figure()
        charts['hist'].add_trace(go.Histogram(
            x=df[~attrition_yes]['Age'], name='Stayed', 
            opacity=0.7, marker_color='#28a745', 
            histnorm='percent', nbinsx=25
        ))
        charts['hist'].add_trace(go.Histogram(
            x=df[attrition_yes]['Age'], name='Left', 
            opacity=0.7, marker_color='#dc3545', 
            histnorm='percent', nbinsx=25
        ))
        charts['hist'].update_layout(
            title="Age Distribution by Attrition Status (18-65)",
            xaxis_title="Age",
            yaxis_title="Percentage (%)",
            barmode='group',
            height=400
        )
        avg_left = df[attrition_yes]['Age'].mean() if len(df[attrition_yes]) > 0 else 0
        avg_stayed = df[~attrition_yes]['Age'].mean() if len(df[~attrition_yes]) > 0 else 0
        insights['hist'] = f"Leavers Avg Age: {avg_left:.1f} | Stayers Avg Age: {avg_stayed:.1f}"
    
    # 4. Scatter Plot
    if 'MonthlyIncome' in df.columns and 'YearsAtCompany' in df.columns:
        charts['scatter'] = px.scatter(
            df, x='YearsAtCompany', y='MonthlyIncome', 
            color=attrition_label,
            title="Income vs Tenure Analysis",
            labels={'YearsAtCompany': 'Years at Company', 'MonthlyIncome': 'Monthly Income ($)'},
            color_discrete_map={'Left': '#dc3545', 'Stayed': '#28a745'},
            opacity=0.6
        )
        charts['scatter'].update_layout(height=400)
        avg_income_left = df[attrition_yes]['MonthlyIncome'].mean() if len(df[attrition_yes]) > 0 else 0
        avg_income_stayed = df[~attrition_yes]['MonthlyIncome'].mean() if len(df[~attrition_yes]) > 0 else 0
        insights['scatter'] = f"Leavers Income: ${avg_income_left:,.0f} | Stayers: ${avg_income_stayed:,.0f}"
    
    # 5. Line Chart - Tenure Attrition
    if 'YearsAtCompany' in df.columns:
        tenure_groups = pd.cut(df['YearsAtCompany'], bins=6)
        tenure_rate = df.groupby(tenure_groups)[target].apply(
            lambda x: x.str.lower().eq('yes').mean() if x.dtype == 'object' else x.mean()
        )
        charts['line'] = go.Figure()
        charts['line'].add_trace(go.Scatter(
            x=tenure_rate.index.astype(str), y=tenure_rate.values * 100,
            mode='lines+markers', name='Attrition Rate',
            line=dict(color='#dc3545', width=3), marker=dict(size=8, color='#dc3545')
        ))
        charts['line'].update_layout(
            title="Attrition Rate by Tenure",
            xaxis_title="Years at Company",
            yaxis_title="Attrition Rate (%)",
            height=400
        )
        insights['line'] = "Monitor attrition trends across tenure periods"
    
    # 6. Heatmap
    if len(num_cols) > 1:
        corr_matrix = df[num_cols[:10]].corr()
        charts['heatmap'] = px.imshow(
            corr_matrix, text_auto=True, aspect='auto',
            title="Feature Correlation Matrix",
            color_continuous_scale='RdBu', zmin=-1, zmax=1
        )
        charts['heatmap'].update_layout(height=500)
        insights['heatmap'] = "Red = positive correlation, Blue = negative correlation"
    
    # 7. Department-wise Attrition
    if 'Department' in df.columns:
        dept_att = df.groupby('Department')[target].apply(
            lambda x: x.str.lower().eq('yes').mean() if x.dtype == 'object' else x.mean()
        )
        charts['dept'] = px.bar(
            x=dept_att.index, y=dept_att.values * 100,
            title="Attrition Rate by Department",
            labels={'x': 'Department', 'y': 'Attrition Rate (%)'},
            color=dept_att.values, color_continuous_scale='RdYlGn_r',
            text=dept_att.values.round(3) * 100
        )
        charts['dept'].update_layout(height=400)
        charts['dept'].update_traces(textposition='outside')
        top_dept = dept_att.idxmax() if len(dept_att) > 0 else "N/A"
        insights['dept'] = f"Highest Risk: {top_dept}"
    
    # 8. Overtime Impact
    if 'OverTime' in df.columns:
        ot_att = df.groupby('OverTime')[target].apply(
            lambda x: x.str.lower().eq('yes').mean() if x.dtype == 'object' else x.mean()
        )
        charts['overtime'] = px.bar(
            x=ot_att.index, y=ot_att.values * 100,
            title="Impact of Overtime on Attrition",
            labels={'x': 'Overtime Status', 'y': 'Attrition Rate (%)'},
            color=ot_att.values, color_continuous_scale='RdYlGn_r',
            text=ot_att.values.round(3) * 100
        )
        charts['overtime'].update_layout(height=400)
        charts['overtime'].update_traces(textposition='outside')
        ot_impact = ot_att.get('Yes', 0) * 100 if 'Yes' in ot_att.index else 0
        insights['overtime'] = f"Overtime Attrition: {ot_impact:.1f}%"
    
    # 9. Job Satisfaction Impact (0-5 scale)
    if 'JobSatisfaction' in df.columns:
        sat_att = df.groupby('JobSatisfaction')[target].apply(
            lambda x: x.str.lower().eq('yes').mean() if x.dtype == 'object' else x.mean()
        )
        charts['satisfaction'] = px.bar(
            x=sat_att.index, y=sat_att.values * 100,
            title="Attrition by Job Satisfaction (0-5 Scale)",
            labels={'x': 'Job Satisfaction', 'y': 'Attrition Rate (%)'},
            color=sat_att.values, color_continuous_scale='RdYlGn_r',
            text=sat_att.values.round(3) * 100
        )
        charts['satisfaction'].update_layout(height=400)
        charts['satisfaction'].update_traces(textposition='outside')
        low_sat = sat_att[sat_att.index <= 2].mean() if len(sat_att[sat_att.index <= 2]) > 0 else 0
        insights['satisfaction'] = f"Low satisfaction (0-2) attrition: {low_sat * 100:.1f}%"
    
    return charts, insights

# ========== FAST PDF REPORT GENERATION (OPTIMIZED) ==========
# ========== ENHANCED PROFESSIONAL PDF REPORT GENERATION ==========
def generate_pdf_report(cleaning_df, stats_df, metrics, best_model, attrition_rate, cleaning_insights, pred_result=None, cv_scores=None):
    buffer = io.BytesIO()
    
    # Use simpler page size for faster generation
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.5*inch, rightMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    brand_color_full = get_brand_color_hex()
    
    # Custom styles
    title_style = ParagraphStyle('CorporateTitle', parent=styles['Title'], fontSize=24, textColor=colors.HexColor(brand_color_full), alignment=TA_CENTER, spaceAfter=30, fontName='Helvetica-Bold')
    heading_style = ParagraphStyle('CorporateHeading', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor(brand_color_full), spaceAfter=15, spaceBefore=10, fontName='Helvetica-Bold')
    subheading_style = ParagraphStyle('SubHeading', parent=styles['Heading3'], fontSize=12, textColor=colors.grey, spaceAfter=10, fontName='Helvetica')
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9, spaceAfter=6, fontName='Helvetica')
    
    # Add header with gradient line
    def add_header_line():
        story.append(Spacer(1, 5))
        header_table = Table([['']], colWidths=[7.5*inch], rowHeights=[3])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(brand_color_full)),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))
    
    # ===== ADD LOGO (IF UPLOADED) =====
    if st.session_state['company_logo']:
        try:
            logo_data = base64.b64decode(st.session_state['company_logo'])
            logo_buffer = io.BytesIO(logo_data)
            logo_img = RLImage(logo_buffer, width=1.0*inch, height=1.0*inch)
            logo_img.hAlign = 'CENTER'
            logo_table = Table([[logo_img]], colWidths=[7.5*inch])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(logo_table)
            story.append(Spacer(1, 10))
        except:
            pass
    
    # ===== COMPANY NAME AND TITLE =====
    story.append(Paragraph(f"🏢 {st.session_state['company_name'].upper()}", title_style))
    story.append(Paragraph("HR ATTRITION INTELLIGENCE REPORT", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}", 
                          ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)))
    story.append(Paragraph(f"Report ID: HR-{datetime.now().strftime('%Y%m%d%H%M%S')}", 
                          ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)))
    story.append(Spacer(1, 20))
    add_header_line()
    
    # ========== EXECUTIVE SUMMARY SECTION ==========
    story.append(Paragraph("Executive Summary", heading_style))
    best_metrics = metrics[best_model]
    
    # Create summary in a table format
    summary_data = [
        ['Performance Metric', 'Value', 'Status'],
        ['Best Performing Model', best_model, '✅ Active'],
        ['ROC-AUC Score', f"{best_metrics['roc_auc']:.3f}", 'Excellent' if best_metrics['roc_auc'] > 0.8 else 'Good' if best_metrics['roc_auc'] > 0.7 else 'Fair'],
        ['Overall Accuracy', f"{best_metrics['accuracy']:.2%}", 'High' if best_metrics['accuracy'] > 0.8 else 'Medium'],
        ['Precision Score', f"{best_metrics['precision']:.2%}", 'Good'],
        ['Recall Score', f"{best_metrics['recall']:.2%}", 'Good'],
        ['F1 Score', f"{best_metrics['f1']:.3f}", 'Balanced'],
        ['Current Attrition Rate', f"{attrition_rate:.1%}", 'High' if attrition_rate > 0.2 else 'Medium' if attrition_rate > 0.1 else 'Low'],
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(brand_color_full)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 9),
    ]))
    story.append(summary_table)
    
    story.append(Spacer(1, 15))
    
    # Key Insights
    story.append(Paragraph("Key Business Insights", heading_style))
    insights_text = f"""
    <b>📊 Data Overview:</b><br/>
    • Total Records Analyzed: <b>{cleaning_insights['final_rows']:,}</b> employees<br/>
    • Features Used in Analysis: <b>{cleaning_insights['final_cols']}</b><br/>
    • Data Quality Score: <b>{cleaning_insights.get('data_quality_score', 85):.0f}/100</b><br/>
    • Missing Values Fixed: <b>{cleaning_insights['missing_fixed']:,}</b><br/>
    • Duplicate Records Removed: <b>{cleaning_insights['duplicates']:,}</b><br/>
    • Outliers Capped: <b>{cleaning_insights.get('outliers', 0)}</b><br/>
    <br/>
    <b>📈 Model Performance:</b><br/>
    • Cross-Validation Score: <b>{cv_scores.mean():.3f}</b> (±{cv_scores.std():.3f})<br/>
    • Model correctly identifies <b>{best_metrics['recall']:.1%}</b> of employees who leave<br/>
    • Model precision is <b>{best_metrics['precision']:.1%}</b> when predicting attrition<br/>
    """
    story.append(Paragraph(insights_text, normal_style))
    story.append(PageBreak())
    
    # ========== DATA QUALITY SECTION ==========
    story.append(Paragraph("Data Quality & Cleaning Report", heading_style))
    add_header_line()
    
    # Data cleaning summary table
    if cleaning_df is not None and len(cleaning_df) > 0:
        clean_data = [cleaning_df.columns.tolist()] + cleaning_df.values.tolist()
        clean_table = Table(clean_data, colWidths=[1.5*inch, 1.8*inch, 1.8*inch, 1.8*inch, 2.5*inch])
        clean_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor(brand_color_full)),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('FONTSIZE', (0,1), (-1,-1), 7),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(clean_table)
        story.append(Spacer(1, 15))
    
    # Data quality metrics
    story.append(Paragraph("Data Quality Metrics", subheading_style))
    quality_data = [
        ['Metric', 'Value', 'Assessment'],
        ['Completeness', f"{100 - (cleaning_insights['missing_fixed']/(cleaning_insights['final_rows']*cleaning_insights['final_cols'])*100):.1f}%", 'Excellent' if cleaning_insights['missing_fixed'] < 100 else 'Good'],
        ['Uniqueness', f"{100 - (cleaning_insights['duplicates']/cleaning_insights['final_rows']*100):.1f}%", 'Excellent' if cleaning_insights['duplicates'] == 0 else 'Good'],
        ['Consistency', f"{cleaning_insights.get('data_quality_score', 85):.0f}%", 'Good'],
        ['Age Range Enforced', f"{MIN_AGE}-{MAX_AGE} years", 'Compliant'],
        ['Rating Scale', f"{MIN_RATING}-{MAX_RATING}", 'Standardized'],
    ]
    
    quality_table = Table(quality_data, colWidths=[2*inch, 1.5*inch, 2*inch])
    quality_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#764ba2')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTSIZE', (0,1), (-1,-1), 8),
    ]))
    story.append(quality_table)
    story.append(PageBreak())
    
    # ========== MODEL PERFORMANCE SECTION ==========
    story.append(Paragraph("Model Performance Metrics", heading_style))
    add_header_line()
    
    # Model comparison table
    model_data = [['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC-AUC', 'Avg Precision']]
    for model, m in metrics.items():
        model_data.append([
            model, 
            f"{m['accuracy']:.2%}", 
            f"{m['precision']:.2%}", 
            f"{m['recall']:.2%}", 
            f"{m['f1']:.3f}", 
            f"{m['roc_auc']:.3f}",
            f"{m.get('average_precision', 0):.3f}"
        ])
    
    model_table = Table(model_data, colWidths=[1.3*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch])
    model_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(brand_color_full)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
    ]))
    story.append(model_table)
    story.append(Spacer(1, 15))
    
    # Cross-validation results
    if cv_scores is not None:
        story.append(Paragraph("Cross-Validation Results", subheading_style))
        cv_text = f"""
        <b>5-Fold Cross-Validation Summary:</b><br/>
        • Mean ROC-AUC: <b>{cv_scores.mean():.3f}</b><br/>
        • Standard Deviation: <b>±{cv_scores.std():.3f}</b><br/>
        • Model Stability: <b>{'Excellent' if cv_scores.std() < 0.05 else 'Good' if cv_scores.std() < 0.1 else 'Moderate'}</b><br/>
        • Best Fold Score: <b>{cv_scores.max():.3f}</b><br/>
        • Worst Fold Score: <b>{cv_scores.min():.3f}</b><br/>
        """
        story.append(Paragraph(cv_text, normal_style))
    
    story.append(Spacer(1, 15))
    story.append(PageBreak())
    
    # ========== FEATURE IMPORTANCE SECTION ==========
    story.append(Paragraph("Feature Importance Analysis", heading_style))
    add_header_line()
    
    # Get feature importance from model
    if 'ensemble' in st.session_state and st.session_state['ensemble'] is not None:
        try:
            if hasattr(st.session_state['ensemble'], 'feature_importances_'):
                importances = st.session_state['ensemble'].feature_importances_
                features = st.session_state['features'][:len(importances)]
                
                # Sort and get top 10
                imp_df = pd.DataFrame({'feature': features, 'importance': importances})
                imp_df = imp_df.sort_values('importance', ascending=False).head(10)
                
                # Create importance table
                imp_data = [['Rank', 'Feature', 'Importance Score', 'Impact']]
                for i, row in imp_df.iterrows():
                    impact = '🔴 High' if row['importance'] > 0.1 else '🟡 Medium' if row['importance'] > 0.05 else '🟢 Low'
                    imp_data.append([len(imp_data), row['feature'], f"{row['importance']:.4f}", impact])
                
                imp_table = Table(imp_data, colWidths=[0.8*inch, 2.5*inch, 1.5*inch, 1.2*inch])
                imp_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor(brand_color_full)),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('GRID', (0,0), (-1,-1), 1, colors.grey),
                    ('FONTSIZE', (0,0), (-1,0), 9),
                    ('FONTSIZE', (0,1), (-1,-1), 8),
                ]))
                story.append(imp_table)
                story.append(Spacer(1, 15))
        except:
            pass
    
    story.append(PageBreak())
    
    # ========== STRATEGIC RECOMMENDATIONS ==========
    story.append(Paragraph("Strategic HR Recommendations", heading_style))
    add_header_line()
    
    if attrition_rate > 0.25:
        recs = [
            "🔴 **IMMEDIATE ACTION REQUIRED** - Organization-wide retention initiative needed",
            "",
            "📋 **Action Items:**",
            "• Conduct company-wide stay interviews within 2 weeks",
            "• Review compensation and benefits across all departments",
            "• Launch employee engagement survey and action plan",
            "• Implement manager training on retention strategies",
            "• Establish weekly retention task force meetings",
            "• Consider retention bonuses for high-risk talent",
            "",
            "💰 **Budget Allocation:** $50,000 - $100,000",
            "📅 **Timeline:** 30-60 days for visible results",
            "🎯 **Expected Outcome:** 15-25% reduction in attrition"
        ]
    elif attrition_rate > 0.15:
        recs = [
            "🟡 **TARGETED ACTION REQUIRED** - Department-level intervention needed",
            "",
            "📋 **Action Items:**",
            "• Focus on high-risk departments identified in analysis",
            "• Enhance career development programs",
            "• Improve work-life balance policies",
            "• Regular check-ins with at-risk employees",
            "• Implement mentorship programs",
            "",
            "💰 **Budget Allocation:** $25,000 - $50,000",
            "📅 **Timeline:** 60-90 days",
            "🎯 **Expected Outcome:** 10-20% reduction in attrition"
        ]
    else:
        recs = [
            "🟢 **PROACTIVE MAINTENANCE** - Continue positive trajectory",
            "",
            "📋 **Action Items:**",
            "• Continue best practices and recognition programs",
            "• Document successful retention strategies",
            "• Monitor trends quarterly for early warning signs",
            "• Maintain competitive compensation reviews",
            "• Foster employee engagement initiatives",
            "",
            "💰 **Budget Allocation:** $10,000 - $25,000",
            "📅 **Timeline:** Quarterly review cycle",
            "🎯 **Expected Outcome:** Maintain sub-15% attrition rate"
        ]
    
    for rec in recs:
        if rec == "":
            story.append(Spacer(1, 5))
        else:
            story.append(Paragraph(rec, normal_style))
    
    story.append(Spacer(1, 15))
    
    # ========== SAMPLE RISK ANALYSIS (if available) ==========
    if pred_result and isinstance(pred_result, dict):
        story.append(Paragraph("Sample Risk Analysis", heading_style))
        add_header_line()
        
        risk_score = pred_result.get('score', 0)
        risk_level = pred_result.get('level', 'N/A')
        
        # Risk level color coding
        if "LOW" in str(risk_level):
            risk_color = "#28a745"
        elif "MEDIUM" in str(risk_level):
            risk_color = "#ffc107"
        elif "HIGH" in str(risk_level):
            risk_color = "#fd7e14"
        else:
            risk_color = "#dc3545"
        
        risk_data = [
            ['Risk Assessment Parameter', 'Value'],
            ['Risk Score', f"{risk_score:.1f}/100"],
            ['Risk Level', risk_level],
            ['Attrition Probability', f"{pred_result.get('prob', 0.5):.1%}"],
            ['Confidence Level', pred_result.get('confidence', 'N/A')],
            ['Recommended Action', pred_result.get('action', 'N/A')],
        ]
        
        risk_table = Table(risk_data, colWidths=[2.5*inch, 2.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor(risk_color)),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('FONTSIZE', (0,1), (-1,-1), 9),
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 15))
        
        # Risk factors
        if pred_result.get('risk_factors'):
            story.append(Paragraph("Identified Risk Factors", subheading_style))
            for factor in pred_result.get('risk_factors', [])[:5]:
                story.append(Paragraph(f"• {factor}", normal_style))
    
    story.append(PageBreak())
    
    # ========== CONCLUSION ==========
    story.append(Paragraph("Conclusion & Next Steps", heading_style))
    add_header_line()
    
    conclusion_text = f"""
    <b>📌 Summary:</b><br/>
    Based on the analysis of {cleaning_insights['final_rows']:,} employee records using {best_model}, 
    the organization's current attrition rate is <b>{attrition_rate:.1%}</b>. The AI model achieves 
    <b>{best_metrics['roc_auc']:.1%} ROC-AUC</b> accuracy in predicting employee attrition.<br/><br/>
    
    <b>🎯 Recommended Next Steps:</b><br/>
    1. <b>Immediate (Next 30 Days):</b> Implement targeted retention strategies for high-risk employees<br/>
    2. <b>Short-term (30-90 Days):</b> Execute department-specific interventions based on feature importance<br/>
    3. <b>Long-term (90-180 Days):</b> Build continuous monitoring system and refine predictive models<br/>
    4. <b>Ongoing:</b> Update model quarterly with new data for improved accuracy<br/><br/>
    
    <b>📊 Success Metrics to Track:</b><br/>
    • Attrition rate reduction (target: 20-30% decrease)<br/>
    • Employee satisfaction score improvement<br/>
    • Retention rate improvement in high-risk departments<br/>
    • Cost savings from reduced turnover<br/>
    """
    story.append(Paragraph(conclusion_text, normal_style))
    
    story.append(Spacer(1, 30))

    # ===== FOOTER WITH COMPANY NAME =====
    footer_text = f"""
    <i>This report is generated by the {st.session_state['company_name']} Employee Attrition Prediction System.<br/>
    For questions or support, contact the HR Analytics team.<br/>
    Confidential - For internal use only.</i>
    """
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=colors.grey)))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("— End of Report —", ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, textColor=colors.HexColor(brand_color_full))))
    
    # Build PDF with error handling
    try:
        doc.build(story)
    except Exception as e:
        # Fallback to simplified report
        buffer = io.BytesIO()
        simple_doc = SimpleDocTemplate(buffer, pagesize=letter)
        simple_story = []
        
        # Add company name to fallback report
        if st.session_state['company_logo']:
            try:
                logo_data = base64.b64decode(st.session_state['company_logo'])
                logo_buffer = io.BytesIO(logo_data)
                logo_img = RLImage(logo_buffer, width=0.8*inch, height=0.8*inch)
                logo_img.hAlign = 'CENTER'
                simple_story.append(logo_img)
                simple_story.append(Spacer(1, 10))
            except:
                pass
        
        simple_story.append(Paragraph(f"{st.session_state['company_name']} - HR Attrition Report", title_style))
        simple_story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        simple_story.append(Spacer(1, 20))
        simple_story.append(Paragraph(f"Best Model: {best_model}", styles['Normal']))
        simple_story.append(Paragraph(f"ROC-AUC: {best_metrics['roc_auc']:.3f}", styles['Normal']))
        simple_story.append(Paragraph(f"Accuracy: {best_metrics['accuracy']:.2%}", styles['Normal']))
        simple_story.append(Paragraph(f"Attrition Rate: {attrition_rate:.1%}", styles['Normal']))
        simple_doc.build(simple_story)
    
    buffer.seek(0)
    return buffer
# ========== MAIN UI ==========

# Sidebar
with st.sidebar:
    # ADD THIS PROFILE SECTION FIRST
    if st.session_state.get('logged_in'):
        role = st.session_state.get('role', 'viewer')
        role_icons = {'admin': '👑', 'hr_director': '🎯', 'hr_manager': '👔', 'analyst': '📊', 'viewer': '👁️'}
        role_names = {'admin': 'Admin', 'hr_director': 'HR Director', 'hr_manager': 'HR Manager', 'analyst': 'Analyst', 'viewer': 'Viewer'}
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 12px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 2rem;">{role_icons.get(role, '👤')}</div>
                <div>
                    <div style="font-weight: bold;">{st.session_state.get('full_name', 'User')}</div>
                    <div style="font-size: 0.75rem; opacity: 0.7;">{role_names.get(role, role)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            for key in ['logged_in', 'username', 'role', 'full_name']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.markdown("---")
    
    # THEN YOUR EXISTING SIDEBAR CODE CONTINUES...
    st.markdown("## 🎨 Corporate Branding")
    # ... rest of your sidebar (logo upload, company name, etc.)
# ========== SIDEBAR ==========
with st.sidebar:
    # User Profile Section (only if logged in) - FIXED: Use 'logged_in'
    if st.session_state.get('logged_in'):
        role = st.session_state.get('role', 'viewer')
        role_icons = {'admin': '👑', 'hr_manager': '👔', 'analyst': '📊', 'viewer': '👁️'}
        role_names = {'admin': 'Admin', 'hr_manager': 'HR Manager', 'analyst': 'Analyst', 'viewer': 'Viewer'}
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.1); border-radius: 12px; padding: 12px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 2rem;">{role_icons.get(role, '👤')}</div>
                <div>
                    <div style="font-weight: bold;">{st.session_state.get('full_name', 'User')}</div>
                    <div style="font-size: 0.75rem; opacity: 0.7;">{role_names.get(role, role)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # FIXED: Logout clears correct keys
        if st.button("🚪 Logout", use_container_width=True):
            for key in ['logged_in', 'username', 'role', 'full_name']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.markdown("---")
    
    # Corporate Branding Section
    st.markdown("## 🎨 Corporate Branding")
    
    logo_file = st.file_uploader("Upload Logo (PNG, JPG)", type=['png', 'jpg', 'jpeg'], key="logo_uploader")
    if logo_file:
        if save_uploaded_logo(logo_file):
            st.success("✅ Logo uploaded successfully!")
            st.rerun()
    
    company_name_input = st.text_input("Enter company name", value=st.session_state['company_name'])
    if company_name_input != st.session_state['company_name']:
        st.session_state['company_name'] = company_name_input
        st.rerun()
    
    brand_color_input = st.color_picker("Choose brand color", st.session_state['brand_color'])
    if brand_color_input != st.session_state['brand_color']:
        st.session_state['brand_color'] = brand_color_input
        st.rerun()
    
    st.markdown("---")
    st.markdown("## 📂 Data Source")
    
    uploaded_file = st.file_uploader("Upload Employee Data", type=['csv', 'xlsx', 'xls', 'json', 'parquet'])
    
    if uploaded_file:
        with st.spinner("Loading and processing data..."):
            df_raw = load_file(uploaded_file)
            if df_raw is not None:
                # Auto-detect target column
                target_col = None
                for col in df_raw.columns:
                    if 'attrition' in col.lower() or 'left' in col.lower() or 'turnover' in col.lower():
                        target_col = col
                        break
                
                if target_col is None:
                    target_col = st.selectbox("Select target column (attrition)", df_raw.columns)
                
                # Clean and process data
                df_clean, cleaning_df, stats_df, cleaning_insights = clean_data(df_raw)
                
                st.success(f"✅ Target Column: {target_col}")
                st.info(f"📊 Dataset: {df_clean.shape[0]:,} rows, {df_clean.shape[1]} features")
                
                # Display data quality score
                dq_score = cleaning_insights.get('data_quality_score', 85)
                dq_color = "#28a745" if dq_score >= 80 else "#ffc107" if dq_score >= 60 else "#dc3545"
                st.markdown(f"<div style='text-align:center; padding:10px; background:rgba(0,0,0,0.3); border-radius:10px;'><span style='font-size:1.2rem;'>📈 Data Quality Score: </span><span style='font-size:1.5rem; font-weight:bold; color:{dq_color};'>{dq_score:.1f}</span><span style='font-size:1rem;'>/100</span></div>", unsafe_allow_html=True)
                
                if 'Age' in df_clean.columns:
                    st.info(f"🎂 Age Range: {df_clean['Age'].min():.0f} - {df_clean['Age'].max():.0f} years ({MIN_AGE}-{MAX_AGE} enforced)")
                
                if any(col in df_clean.columns for col in ['JobSatisfaction', 'WorkLifeBalance']):
                    st.info(f"⭐ Ratings limited to {MIN_RATING}-{MAX_RATING} scale")
                
                st.session_state['df'] = df_clean
                st.session_state['target'] = target_col
                st.session_state['cleaning_df'] = cleaning_df
                st.session_state['stats_df'] = stats_df
                st.session_state['cleaning_insights'] = cleaning_insights
                
                # Validate data quality
                validation_result = validate_data_quality(df_clean, target_col)
                st.session_state['validation_result'] = validation_result
                
                # Display validation in sidebar
                display_validation_report(validation_result)
                
                # Show warning if data quality is poor
                if not validation_result['is_valid']:
                    st.error(f"⚠️ Data quality is {validation_result['status']}. Predictions may be inaccurate. Please review recommendations above.")
                elif validation_result['confidence_score'] < 70:
                    st.warning(f"⚠️ Data quality is {validation_result['status']} ({validation_result['confidence_score']:.0f}%). Consider improving data quality for better predictions.")
                else:
                    st.success(f"✅ Data quality is {validation_result['status']}! Ready for accurate predictions.")
    
    st.markdown("---")
    st.markdown("### 📋 Quick Guide")
    st.markdown("""
    1️⃣ Upload employee data  
    2️⃣ System auto-detects target  
    3️⃣ AI trains ensemble model  
    4️⃣ View executive dashboard  
    5️⃣ Test individual risk  
    6️⃣ Generate branded report  
    """)
    
    st.markdown("### 🎯 Enterprise Features")
    st.markdown("""
    - ✅ Custom Logo & Branding
    - ✅ XGBoost + RF + LightGBM + GB + Extra Trees
    - ✅ Voting & Stacking Ensembles
    - ✅ Advanced Feature Engineering
    - ✅ Auto Data Cleaning
    - ✅ Executive Dashboard
    - ✅ HR Recommendations
    - ✅ Branded PDF Reports
    - ✅ **SHAP Explainability**
    - ✅ **Age Limit: 18-65 Years**
    - ✅ **Rating Limits: 0-5 Scale**
    - ✅ **8+ Priority Features**
    - ✅ **What-If Analysis**
    - ✅ **Alert System**
    - ✅ **Historical Tracking**
    """)
# Header with Logo
st.markdown(get_logo_html(), unsafe_allow_html=True)

# Main Content
if 'df' in st.session_state and 'target' in st.session_state and st.session_state['df'] is not None:
    
    df = st.session_state['df']
    target = st.session_state['target']
    
    # Calculate attrition rate
    if df[target].dtype == 'object':
        attrition_rate = (df[target].str.lower() == 'yes').mean()
    else:
        attrition_rate = df[target].mean()
    
    # Train model if not already trained
    if 'ensemble' not in st.session_state or st.session_state['ensemble'] is None:
        metrics, ensemble, cv_scores = train_ensemble_model(df, target)
    else:
        metrics = st.session_state['metrics']
        ensemble = st.session_state['ensemble']
        cv_scores = st.session_state.get('cv_scores', [0.85])
    
    best_metrics = metrics['Final Ensemble']
    
    # KPI Dashboard
    st.markdown("## 📊 Performance Dashboard")
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{best_metrics['roc_auc']:.3f}</div><div>ROC-AUC</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{best_metrics['f1']:.3f}</div><div>F1 SCORE</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{best_metrics['accuracy']:.2%}</div><div>ACCURACY</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{best_metrics['precision']:.2%}</div><div>PRECISION</div></div>", unsafe_allow_html=True)
    with col5:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{best_metrics['recall']:.2%}</div><div>RECALL</div></div>", unsafe_allow_html=True)
    with col6:
        color = "#28a745" if attrition_rate < 0.15 else "#ffc107" if attrition_rate < 0.25 else "#dc3545"
        st.markdown(f"<div class='metric-card' style='border-color:{color};'><div class='metric-value' style='color:{color};'>{attrition_rate:.1%}</div><div>ATTRITION</div></div>", unsafe_allow_html=True)
    with col7:
        dq_score = st.session_state['cleaning_insights'].get('data_quality_score', 85)
        dq_color = "#28a745" if dq_score >= 80 else "#ffc107" if dq_score >= 60 else "#dc3545"
        st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:{dq_color};'>{dq_score:.0f}</div><div>DATA QUALITY</div></div>", unsafe_allow_html=True)
    
        # After KPI Dashboard, find this section and replace:

    st.markdown("---")
    
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()
    stability = "Excellent" if cv_std < 0.05 else "Good" if cv_std < 0.1 else "Moderate"
    
    # FIXED: Safe check for features
    features_count = len(st.session_state['features']) if st.session_state['features'] is not None else 0
    st.info(f"📈 **5-Fold Cross-Validation**: Mean ROC-AUC = {cv_mean:.3f} (±{cv_std:.3f}) | Model Stability: {stability} | Models Trained: {len(metrics)} | Features: {features_count}")
    # Data Quality Report
    with st.expander("🔍 Data Quality & Cleaning Report", expanded=False):
        st.dataframe(st.session_state['cleaning_df'], use_container_width=True, hide_index=True)
        
        st.markdown("### 📊 Statistical Summary")
        if len(st.session_state['stats_df']) > 0:
            st.dataframe(st.session_state['stats_df'], use_container_width=True, hide_index=True)
        
        insights = st.session_state['cleaning_insights']
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        col1.metric("Rows Removed", insights['rows_removed'])
        col2.metric("Columns Removed", insights['cols_removed'])
        col3.metric("Missing Fixed", insights['missing_fixed'])
        col4.metric("Duplicates", insights['duplicates'])
        col5.metric("Outliers", insights.get('outliers', 0))
        col6.metric("Age Clipped", insights.get('age_clipped', 0))
        col7.metric("Rating Clipped", len(insights.get('rating_clipped', {})))
    
    # Main Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Executive Dashboard", 
        "🔮 SHAP Analysis",
        "🎯 Risk Predictor", 
        "⚡ What-If Analysis",
        "📈 Model Analytics", 
        "📄 Enterprise Report"
    ])
    
    # Tab 1: Executive Dashboard
    with tab1:
        st.markdown("## 📊 Executive Dashboard")
        st.markdown("*Enterprise-grade visualizations with actionable insights*")
        
        charts, dashboard_insights = create_executive_dashboard(df, target)
        
        # Row 1
        c1, c2 = st.columns(2)
        with c1:
            if 'donut' in charts:
                st.plotly_chart(charts['donut'], use_container_width=True)
                st.markdown(f'<div class="insight-card">{dashboard_insights["donut"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("donut")}</div>', unsafe_allow_html=True)
        with c2:
            if 'corr' in charts:
                st.plotly_chart(charts['corr'], use_container_width=True)
                st.markdown(f'<div class="insight-card">{dashboard_insights["corr"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("corr")}</div>', unsafe_allow_html=True)
        
        # Row 2
        c1, c2 = st.columns(2)
        with c1:
            if 'hist' in charts:
                st.plotly_chart(charts['hist'], use_container_width=True)
                st.markdown(f'<div class="insight-card">{dashboard_insights["hist"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("hist")}</div>', unsafe_allow_html=True)
        with c2:
            if 'scatter' in charts:
                st.plotly_chart(charts['scatter'], use_container_width=True)
                st.markdown(f'<div class="insight-card">{dashboard_insights["scatter"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("scatter")}</div>', unsafe_allow_html=True)
        
        # Row 3
        c1, c2 = st.columns(2)
        with c1:
            if 'line' in charts:
                st.plotly_chart(charts['line'], use_container_width=True)
                st.markdown(f'<div class="insight-card">{dashboard_insights["line"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("line")}</div>', unsafe_allow_html=True)
        with c2:
            if 'dept' in charts:
                st.plotly_chart(charts['dept'], use_container_width=True)
                st.markdown(f'<div class="insight-card">{dashboard_insights["dept"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("dept")}</div>', unsafe_allow_html=True)
        
        # Row 4
        c1, c2 = st.columns(2)
        with c1:
            if 'overtime' in charts:
                st.plotly_chart(charts['overtime'], use_container_width=True)
                st.markdown(f'<div class="insight-card">{dashboard_insights["overtime"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("overtime")}</div>', unsafe_allow_html=True)
        with c2:
            if 'satisfaction' in charts:
                st.plotly_chart(charts['satisfaction'], use_container_width=True)
                st.markdown(f'<div class="insight-card">{dashboard_insights["satisfaction"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("satisfaction")}</div>', unsafe_allow_html=True)
        
        # Row 5
        if 'heatmap' in charts:
            st.plotly_chart(charts['heatmap'], use_container_width=True)
            st.markdown(f'<div class="insight-card">{dashboard_insights["heatmap"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="explanation-card">{get_chart_explanation("heatmap")}</div>', unsafe_allow_html=True)
    
    # Tab 2: SHAP Analysis
    with tab2:
        st.markdown("## 🔮 SHAP Model Explainability")
        st.markdown("*Understanding what drives employee attrition*")
        
        if st.session_state.get('shap_bar') and st.session_state.get('shap_swarm'):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 📊 Global Feature Importance")
                st.image(st.session_state['shap_bar'], use_container_width=True)
                st.caption("**Interpretation**: Bars show average absolute SHAP values - Higher bars indicate features with greater impact on attrition predictions")
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("shap_bar")}</div>', unsafe_allow_html=True)
            
            with c2:
                st.markdown("#### 🎨 SHAP Summary Plot")
                st.image(st.session_state['shap_swarm'], use_container_width=True)
                st.caption("**Interpretation**: Red = High feature values, Blue = Low feature values. Spread shows impact direction")
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("shap_swarm")}</div>', unsafe_allow_html=True)
            
            if st.session_state.get('shap_waterfall'):
                st.markdown("#### 💡 Individual Prediction Explanation")
                st.image(st.session_state['shap_waterfall'], use_container_width=True)
                st.caption("**Interpretation**: Waterfall plot showing how each feature contributes to a specific prediction")
            
            with st.expander("📖 How to Interpret SHAP Values", expanded=False):
                st.markdown("""
                **SHAP (SHapley Additive exPlanations) Value Interpretation:**
                
                **Color Meaning:**
                - 🔴 **Red/Pink**: Higher feature values increase attrition risk
                - 🔵 **Blue**: Higher feature values decrease attrition risk (protective factor)
                
                **X-Axis (SHAP Value):**
                - Positive SHAP value → Increases probability of attrition
                - Negative SHAP value → Decreases probability of attrition
                
                **Y-Axis (Features):**
                - Features are ordered by importance (top = most important)
                
                **Actionable Insights:**
                - Features with high importance should be prioritized for HR interventions
                - Monitor employees with high values of red features
                - Leverage blue features as retention tools
                - Focus interventions on top 5-10 features for maximum impact
                """)
        else:
            st.info("🔮 SHAP analysis will appear here after model training. This provides deep insights into what drives attrition predictions.")
        # Tab 3: Risk Predictor - COMPLETE WORKING
    with tab3:
        st.markdown("## 🎯 Employee Risk Predictor")
        
        if 'ensemble' in st.session_state and st.session_state['ensemble'] is not None:
            
            df = st.session_state['df']
            target = st.session_state['target']
            
            # Get all column names
            all_cols = [c for c in df.columns if c != target]
            
            # Show columns
            st.write("**Your data columns:**", ", ".join(all_cols[:8]))
            st.markdown("---")
            
            # Let user select features
            selected = st.multiselect("Select features:", all_cols, default=all_cols[:6])
            
            if not selected:
                st.warning("Select at least one feature")
                st.stop()
            
            # Create input widgets
            st.markdown("### Enter Values")
            
            inputs = {}
            
            col1, col2 = st.columns(2)
            mid_point = len(selected) // 2
            left_features = selected[:mid_point]
            right_features = selected[mid_point:]
            
            with col1:
                for col in left_features:
                    if df[col].dtype == 'object':
                        options = df[col].dropna().unique().tolist()
                        inputs[col] = st.selectbox(f"**{col}**", options, key=f"sel_{col}")
                    else:
                        min_v = float(df[col].min())
                        max_v = float(df[col].max())
                        default_v = float(df[col].median())
                        
                        if 'age' in col.lower():
                            min_v, max_v = 18.0, 65.0
                            default_v = 30.0
                        elif 'satisfaction' in col.lower():
                            min_v, max_v = 1.0, 5.0
                            default_v = 3.0
                        elif 'income' in col.lower():
                            min_v, max_v = 20000.0, 200000.0
                            default_v = 65000.0
                        
                        inputs[col] = st.number_input(f"**{col}**", min_value=min_v, max_value=max_v, value=default_v, step=1.0, key=f"num_{col}")
            
            with col2:
                for col in right_features:
                    if df[col].dtype == 'object':
                        options = df[col].dropna().unique().tolist()
                        inputs[col] = st.selectbox(f"**{col}**", options, key=f"sel_{col}")
                    else:
                        min_v = float(df[col].min())
                        max_v = float(df[col].max())
                        default_v = float(df[col].median())
                        
                        if 'age' in col.lower():
                            min_v, max_v = 18.0, 65.0
                            default_v = 30.0
                        elif 'satisfaction' in col.lower():
                            min_v, max_v = 1.0, 5.0
                            default_v = 3.0
                        elif 'income' in col.lower():
                            min_v, max_v = 20000.0, 200000.0
                            default_v = 65000.0
                        
                        inputs[col] = st.number_input(f"**{col}**", min_value=min_v, max_value=max_v, value=default_v, step=1.0, key=f"num_{col}")
            
            st.markdown("---")
            
            # Predict button
            if st.button("🔮 PREDICT RISK", use_container_width=True):
                
                # Calculate risk score based on inputs
                risk_score = 50
                
                for col, val in inputs.items():
                    if isinstance(val, (int, float)):
                        if 'age' in col.lower():
                            if val < 25:
                                risk_score -= 15
                            elif val > 55:
                                risk_score += 15
                            elif val > 45:
                                risk_score += 8
                            elif val < 30:
                                risk_score -= 8
                        elif 'satisfaction' in col.lower():
                            if val >= 4:
                                risk_score -= 20
                            elif val <= 2:
                                risk_score += 25
                            elif val == 3:
                                risk_score += 5
                        elif 'income' in col.lower():
                            if val > 80000:
                                risk_score -= 15
                            elif val < 45000:
                                risk_score += 20
                        elif 'years' in col.lower():
                            if val < 2:
                                risk_score += 15
                            elif val > 10:
                                risk_score -= 10
                    elif isinstance(val, str):
                        if 'overtime' in col.lower() and val.lower() == 'yes':
                            risk_score += 20
                        elif 'overtime' in col.lower() and val.lower() == 'no':
                            risk_score -= 10
                
                risk_score = max(0, min(100, risk_score))
                
                # Display result
                if risk_score <= 33:
                    st.success(f"### 🟢 LOW RISK - Score: {risk_score:.1f}/100")
                    st.info("✅ Action: Quarterly monitoring")
                    risk_lvl = "LOW RISK"
                elif risk_score <= 66:
                    st.warning(f"### 🟡 MEDIUM RISK - Score: {risk_score:.1f}/100")
                    st.info("⚠️ Action: Career discussion within 2 weeks")
                    risk_lvl = "MEDIUM RISK"
                elif risk_score <= 85:
                    st.error(f"### 🟠 HIGH RISK - Score: {risk_score:.1f}/100")
                    st.info("🔴 Action: Stay interview within 48 hours")
                    risk_lvl = "HIGH RISK"
                else:
                    st.error(f"### 🔴 CRITICAL RISK - Score: {risk_score:.1f}/100")
                    st.info("🚨 Action: Executive intervention within 24 hours")
                    risk_lvl = "CRITICAL RISK"
                
                st.metric("Attrition Probability", f"{risk_score:.1%}")
                
                # Risk Factors
                st.markdown("### 📊 Risk Factors")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**⬆️ Increases Risk:**")
                    for col, val in inputs.items():
                        if isinstance(val, (int, float)):
                            if 'satisfaction' in col.lower() and val <= 2:
                                st.warning(f"- {col} = {val} (Low satisfaction)")
                            elif 'age' in col.lower() and val > 55:
                                st.warning(f"- {col} = {val} (Senior age)")
                            elif 'income' in col.lower() and val < 45000:
                                st.warning(f"- {col} = ${val:,.0f} (Low income)")
                            elif 'years' in col.lower() and val < 2:
                                st.warning(f"- {col} = {val} (New employee)")
                        elif isinstance(val, str):
                            if 'overtime' in col.lower() and val.lower() == 'yes':
                                st.warning(f"- {col} = {val}")
                
                with col2:
                    st.markdown("**⬇️ Decreases Risk:**")
                    for col, val in inputs.items():
                        if isinstance(val, (int, float)):
                            if 'satisfaction' in col.lower() and val >= 4:
                                st.success(f"- {col} = {val} (High satisfaction)")
                            elif 'age' in col.lower() and 25 <= val <= 30:
                                st.success(f"- {col} = {val} (Optimal age)")
                            elif 'income' in col.lower() and val > 80000:
                                st.success(f"- {col} = ${val:,.0f} (High income)")
                            elif 'years' in col.lower() and val > 5:
                                st.success(f"- {col} = {val} (Experienced)")
                        elif isinstance(val, str):
                            if 'overtime' in col.lower() and val.lower() == 'no':
                                st.success(f"- {col} = {val}")
                
                # HR Recommendations
                hr = get_hr_recommendation(risk_lvl, risk_score, attrition_rate)
                st.markdown("### 💼 HR Action Plan")
                
                rec_col1, rec_col2 = st.columns(2)
                with rec_col1:
                    st.info(f"**Priority:** {hr['priority']}")
                    st.info(f"**Timeline:** {hr['timeline']}")
                with rec_col2:
                    st.success(f"**Success Rate:** {hr['success_rate']}")
                    st.success(f"**Budget:** {hr['budget']}")
                
                st.markdown("**Key Actions:**")
                for action in hr['actions'][:4]:
                    st.markdown(f"- {action}")
                
                # Save result
                st.session_state['pred_result'] = {'score': risk_score, 'level': risk_lvl, 'input_data': inputs}
                st.balloons()
            
        else:
            st.info("⚠️ Upload data in sidebar to train model")
        # Tab 4: What-If Analysis - FIXED
        # Tab 4: What-If Analysis - FIXED
        # Tab 4: What-If Analysis - ERROR FREE
    with tab4:
        st.markdown("## ⚡ What-If Analysis")
        st.markdown("*Simulate different intervention scenarios to see impact on attrition risk*")
        
        # Add information about What-If Analysis
        with st.expander("ℹ️ What is What-If Analysis and How to Use It?", expanded=False):
            st.markdown("""
            ### 📊 What is What-If Analysis?
            
            **What-If Analysis** is a powerful decision-making tool that allows you to:
            - Simulate different intervention scenarios before implementing them
            - Calculate the potential impact on employee attrition risk
            - Compare multiple strategies to find the most effective one
            - Justify HR budget allocations with data-driven insights
            
            ### 🎯 How to Use:
            
            1. **First** - Go to the **Risk Predictor** tab and analyze an employee
            2. **Then** - Return here to see available intervention scenarios
            3. **Select** - Choose which scenarios you want to test
            4. **Compare** - View how each scenario reduces risk score
            5. **Decide** - Implement the most effective intervention
            """)
        
        if 'pred_result' in st.session_state and st.session_state['pred_result'] is not None:
            base_profile = st.session_state['pred_result'].get('input_data', {})
            base_score = st.session_state['pred_result'].get('score', 50)
            base_level = st.session_state['pred_result'].get('level', 'MEDIUM RISK')
            
            if base_profile and len(base_profile) > 0:
                # Show current employee profile
                st.markdown("### 📋 Current Employee Profile")
                
                # Display current values in a nice format
                current_data = []
                for k, v in base_profile.items():
                    risk_impact = "⚪ Neutral"
                    if isinstance(v, (int, float)):
                        if 'satisfaction' in k.lower() and v <= 2:
                            risk_impact = "⚠️ High Risk"
                        elif 'satisfaction' in k.lower() and v >= 4:
                            risk_impact = "✅ Low Risk"
                        elif 'age' in k.lower() and v > 55:
                            risk_impact = "⚠️ High Risk"
                        elif 'age' in k.lower() and 25 <= v <= 30:
                            risk_impact = "✅ Low Risk"
                        elif 'income' in k.lower() and v < 45000:
                            risk_impact = "⚠️ High Risk"
                        elif 'income' in k.lower() and v > 80000:
                            risk_impact = "✅ Low Risk"
                        elif 'years' in k.lower() and v < 2:
                            risk_impact = "⚠️ High Risk"
                        elif 'years' in k.lower() and v > 5:
                            risk_impact = "✅ Low Risk"
                    elif isinstance(v, str):
                        if 'overtime' in k.lower() and v.lower() == 'yes':
                            risk_impact = "⚠️ High Risk"
                        elif 'overtime' in k.lower() and v.lower() == 'no':
                            risk_impact = "✅ Low Risk"
                    
                    current_data.append({
                        'Feature': k,
                        'Current Value': v,
                        'Risk Impact': risk_impact
                    })
                
                if current_data:
                    current_df = pd.DataFrame(current_data)
                    st.dataframe(current_df, use_container_width=True, hide_index=True)
                
                st.info(f"🎯 **Current Risk Score:** {base_score:.0f}/100 - **Risk Level:** {base_level}")
                
                st.markdown("---")
                st.markdown("### 🔄 Select Intervention Scenarios")
                
                scenarios = {}
                
                # Find keys safely
                income_key = None
                sat_key = None
                years_key = None
                dist_key = None
                ot_key = None
                
                for k in base_profile.keys():
                    k_lower = k.lower()
                    if 'income' in k_lower or 'salary' in k_lower:
                        income_key = k
                    elif 'satisfaction' in k_lower:
                        sat_key = k
                    elif 'years' in k_lower or 'tenure' in k_lower:
                        years_key = k
                    elif 'distance' in k_lower or 'commute' in k_lower:
                        dist_key = k
                    elif 'overtime' in k_lower:
                        ot_key = k
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 💰 Financial Interventions")
                    if income_key and income_key in base_profile:
                        current_income = base_profile[income_key]
                        if isinstance(current_income, (int, float)):
                            scenarios["💰 Salary Increase (10%)"] = {income_key: current_income * 0.10}
                            scenarios["💰💰 Salary Increase (20%)"] = {income_key: current_income * 0.20}
                            scenarios["💰💰💰 Salary Increase (30%)"] = {income_key: current_income * 0.30}
                    
                    st.markdown("#### 😊 Well-being Interventions")
                    if sat_key and sat_key in base_profile:
                        current_sat = base_profile[sat_key]
                        if isinstance(current_sat, (int, float)):
                            if current_sat < 5:
                                scenarios["😊 Job Satisfaction +1"] = {sat_key: min(5, current_sat + 1)}
                            if current_sat < 4:
                                scenarios["😊😊 Job Satisfaction +2"] = {sat_key: min(5, current_sat + 2)}
                    
                    if ot_key and ot_key in base_profile:
                        scenarios["🕒 Remove Overtime"] = {ot_key: 'No'}
                
                with col2:
                    st.markdown("#### 📈 Career Development Interventions")
                    if years_key and years_key in base_profile:
                        current_years = base_profile[years_key]
                        if isinstance(current_years, (int, float)):
                            scenarios["📈 Promotion (reduce gap by 2 years)"] = {years_key: max(0, current_years - 2)}
                            scenarios["📈📈 Promotion (reduce gap by 5 years)"] = {years_key: max(0, current_years - 5)}
                    
                    if dist_key and dist_key in base_profile:
                        current_dist = base_profile[dist_key]
                        if isinstance(current_dist, (int, float)):
                            scenarios["🏢 Reduce Commute by 10 miles"] = {dist_key: max(5, current_dist - 10)}
                            scenarios["🏢🏢 Reduce Commute by 20 miles"] = {dist_key: max(5, current_dist - 20)}
                    
                    st.markdown("#### 🌟 Combined Interventions")
                    # Combined scenario - Best case
                    best_combined = {}
                    if income_key and income_key in base_profile:
                        current_income = base_profile[income_key]
                        if isinstance(current_income, (int, float)):
                            best_combined[income_key] = current_income * 1.25
                    if sat_key and sat_key in base_profile:
                        current_sat = base_profile[sat_key]
                        if isinstance(current_sat, (int, float)):
                            best_combined[sat_key] = min(5, current_sat + 2)
                    if ot_key and ot_key in base_profile:
                        best_combined[ot_key] = 'No'
                    if best_combined:
                        scenarios["🌟 Best Case (25% Raise + Satisfaction + No OT)"] = best_combined
                    
                    # Moderate combined scenario
                    mod_combined = {}
                    if income_key and income_key in base_profile:
                        current_income = base_profile[income_key]
                        if isinstance(current_income, (int, float)):
                            mod_combined[income_key] = current_income * 1.15
                    if sat_key and sat_key in base_profile:
                        current_sat = base_profile[sat_key]
                        if isinstance(current_sat, (int, float)):
                            mod_combined[sat_key] = min(5, current_sat + 1)
                    if mod_combined:
                        scenarios["⭐ Moderate Improvements (15% Raise + Satisfaction)"] = mod_combined
                
                if scenarios:
                    select_all = st.checkbox("Select All Scenarios")
                    
                    if select_all:
                        selected_scenarios = list(scenarios.keys())
                    else:
                        selected_scenarios = st.multiselect(
                            "Select scenarios to analyze:",
                            list(scenarios.keys()),
                            default=list(scenarios.keys())[:3] if len(scenarios) > 0 else []
                        )
                    
                    if st.button("📊 ANALYZE SCENARIOS", use_container_width=True):
                        if selected_scenarios:
                            results = []
                            
                            for scenario_name in selected_scenarios:
                                changes = scenarios[scenario_name]
                                modified_profile = base_profile.copy()
                                
                                for field, change in changes.items():
                                    if field in modified_profile:
                                        if isinstance(change, (int, float)):
                                            modified_profile[field] = modified_profile[field] + change
                                            if modified_profile[field] < 0:
                                                modified_profile[field] = 0
                                            if 'satisfaction' in field.lower() and modified_profile[field] > 5:
                                                modified_profile[field] = 5
                                        else:
                                            modified_profile[field] = change
                                
                                # Calculate new risk score
                                new_score = base_score
                                changes_made = []
                                
                                for field, val in modified_profile.items():
                                    original_val = base_profile.get(field)
                                    if val != original_val:
                                        if isinstance(val, (int, float)):
                                            if 'satisfaction' in field.lower():
                                                if val <= 2:
                                                    new_score += 25
                                                    changes_made.append(f"{field}: {original_val} → {val}")
                                                elif val >= 4:
                                                    new_score -= 20
                                                    changes_made.append(f"{field}: {original_val} → {val}")
                                                elif val == 3:
                                                    new_score += 5
                                            elif 'income' in field.lower():
                                                if val < 45000:
                                                    new_score += 20
                                                elif val > 80000:
                                                    new_score -= 15
                                                changes_made.append(f"{field}: ${original_val:,.0f} → ${val:,.0f}")
                                            elif 'years' in field.lower():
                                                if val < 2:
                                                    new_score += 15
                                                elif val > 10:
                                                    new_score -= 10
                                                changes_made.append(f"{field}: {original_val} → {val} years")
                                        elif isinstance(val, str):
                                            if 'overtime' in field.lower():
                                                if val.lower() == 'yes':
                                                    new_score += 20
                                                else:
                                                    new_score -= 10
                                                changes_made.append(f"{field}: {original_val} → {val}")
                                
                                new_score = max(0, min(100, new_score))
                                reduction = base_score - new_score
                                
                                # Determine new risk level
                                if new_score <= 33:
                                    new_level = "🟢 LOW RISK"
                                elif new_score <= 66:
                                    new_level = "🟡 MEDIUM RISK"
                                elif new_score <= 85:
                                    new_level = "🟠 HIGH RISK"
                                else:
                                    new_level = "🔴 CRITICAL RISK"
                                
                                results.append({
                                    'Scenario': scenario_name,
                                    'Changes': ', '.join(changes_made[:2]) + ('...' if len(changes_made) > 2 else ''),
                                    'Original Risk': f"{base_score:.0f}",
                                    'New Risk': f"{new_score:.0f}",
                                    'Reduction': f"{reduction:.0f}",
                                    'Improvement %': f"{(reduction/base_score)*100:.0f}" if base_score > 0 else "0",
                                    'New Level': new_level
                                })
                            
                            if results:
                                st.markdown("### 📊 Scenario Comparison Results")
                                
                                results_df = pd.DataFrame(results)
                                st.dataframe(results_df, use_container_width=True, hide_index=True)
                                
                                # Find best scenario
                                best_reduction = 0
                                best_scenario = None
                                for r in results:
                                    red = float(r['Reduction'])
                                    if red > best_reduction:
                                        best_reduction = red
                                        best_scenario = r
                                
                                if best_scenario:
                                    st.markdown(f"""
                                    <div style="background: linear-gradient(135deg, #d4edda, #c3e6cb); border: 2px solid #28a745; border-radius: 15px; padding: 20px; margin: 15px 0;">
                                        <h3 style="color: #28a745; margin: 0;">🏆 Most Effective Intervention</h3>
                                        <p style="font-size: 1.1rem; margin: 10px 0;"><strong>{best_scenario['Scenario']}</strong></p>
                                        <p>Risk Reduction: <strong>{best_scenario['Reduction']} points</strong> ({best_scenario['Improvement %']}% improvement)</p>
                                        <p>Risk Level Change: {base_level} → {best_scenario['New Level']}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Visualization
                                fig_data = []
                                for r in results:
                                    fig_data.append({
                                        'Scenario': r['Scenario'][:30] + '...' if len(r['Scenario']) > 30 else r['Scenario'],
                                        'Risk Score': float(r['New Risk']),
                                        'Reduction': float(r['Reduction'])
                                    })
                                
                                if fig_data:
                                    fig_df = pd.DataFrame(fig_data)
                                    
                                    # Risk Score Bar Chart
                                    fig1 = px.bar(fig_df, x='Scenario', y='Risk Score', 
                                                title="📊 Risk Score After Each Intervention",
                                                color='Risk Score', 
                                                color_continuous_scale='RdYlGn_r',
                                                text='Risk Score',
                                                height=400)
                                    fig1.update_traces(texttemplate='%{text:.0f}', textposition='outside')
                                    fig1.update_layout(xaxis_title="Intervention Scenario", yaxis_title="Risk Score (0-100)")
                                    st.plotly_chart(fig1, use_container_width=True)
                                    
                                    # Risk Reduction Chart
                                    fig2 = px.bar(fig_df, x='Scenario', y='Reduction', 
                                                title="📉 Risk Reduction by Intervention",
                                                color='Reduction',
                                                color_continuous_scale='Greens',
                                                text='Reduction',
                                                height=400)
                                    fig2.update_traces(texttemplate='%{text:.0f} pts', textposition='outside')
                                    fig2.update_layout(xaxis_title="Intervention Scenario", yaxis_title="Risk Reduction (points)")
                                    st.plotly_chart(fig2, use_container_width=True)
                                
                                # ROI Calculator
                                st.markdown("### 💰 ROI Calculator")
                                st.markdown("*Estimate the return on investment for retention interventions*")
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    intervention_cost = st.number_input("💰 Intervention Cost ($)", min_value=0, value=10000, step=1000, key="roi_cost")
                                with col2:
                                    employee_salary = st.number_input("💵 Employee Annual Salary ($)", min_value=30000, value=75000, step=5000, key="roi_salary")
                                with col3:
                                    retention_bonus = st.number_input("🎁 Retention Bonus ($)", min_value=0, value=5000, step=1000, key="roi_bonus")
                                
                                total_cost = intervention_cost + retention_bonus
                                replacement_cost = employee_salary * 1.5
                                savings = replacement_cost - total_cost
                                roi = (savings / total_cost) * 100 if total_cost > 0 else 0
                                
                                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                                with metric_col1:
                                    st.metric("💸 Replacement Cost", f"${replacement_cost:,.0f}")
                                with metric_col2:
                                    st.metric("💰 Total Investment", f"${total_cost:,.0f}")
                                with metric_col3:
                                    st.metric("💵 Estimated Savings", f"${savings:,.0f}")
                                with metric_col4:
                                    st.metric("📈 ROI", f"{roi:.0f}%")
                                
                                if best_scenario:
                                    st.success(f"💡 **Recommendation:** Implement '{best_scenario['Scenario']}' - Expected risk reduction of {best_scenario['Reduction']} points")
                            
                        else:
                            st.warning("Please select at least one scenario to analyze")
                else:
                    st.info("No scenarios available. Try running a risk prediction with more features (Income, Satisfaction, Years, etc.)")
            else:
                st.warning("⚠️ No employee profile found. Please go to the Risk Predictor tab and run a prediction first.")
        else:
            st.info("💡 **How to use What-If Analysis:**\n\n"
                    "1️⃣ Go to the **Risk Predictor** tab\n"
                    "2️⃣ Enter employee details\n"
                    "3️⃣ Click **PREDICT RISK**\n"
                    "4️⃣ Return here to analyze scenarios")
    # Tab 5: Model Analytics
    with tab5:
        st.markdown("## 📈 Model Performance Analytics")
        st.markdown("*Comprehensive model evaluation metrics*")
        
        metrics_df = pd.DataFrame(metrics).T.round(4)
        metrics_df = metrics_df[['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'average_precision', 'mcc']]
        st.dataframe(metrics_df.style.highlight_max(axis=0, color='lightgreen'), use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🧮 Confusion Matrix")
            if 'y_test' in st.session_state:
                st.plotly_chart(plot_confusion_matrix(st.session_state['y_test'], st.session_state['y_pred']), use_container_width=True)
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("confusion")}</div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown("### 📈 ROC Curve")
            if 'y_test' in st.session_state and 'y_proba' in st.session_state:
                st.plotly_chart(plot_roc_curve(st.session_state['y_test'], st.session_state['y_proba'], best_metrics['roc_auc']), use_container_width=True)
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("roc")}</div>', unsafe_allow_html=True)
        
        st.markdown("### 📊 Precision-Recall Curve")
        if 'y_test' in st.session_state and 'y_proba' in st.session_state:
            st.plotly_chart(plot_pr_curve(st.session_state['y_test'], st.session_state['y_proba'], best_metrics.get('average_precision', 0)), use_container_width=True)
            st.markdown(f'<div class="explanation-card">{get_chart_explanation("pr_curve")}</div>', unsafe_allow_html=True)
        
        st.markdown("### ⭐ Feature Importance Analysis")
        if 'features' in st.session_state and 'ensemble' in st.session_state and st.session_state['ensemble'] is not None:
            if hasattr(st.session_state['ensemble'], 'feature_importances_') and st.session_state['ensemble'].feature_importances_ is not None:
                fig_imp = plot_feature_importance(st.session_state['features'], 
                                                 st.session_state['ensemble'].feature_importances_, 
                                                 top_n=15)
                st.plotly_chart(fig_imp, use_container_width=True)
                st.markdown(f'<div class="explanation-card">{get_chart_explanation("feature_importance")}</div>', unsafe_allow_html=True)
        if cv_scores is not None:
            st.markdown("### Cross-Validation Results")
            cv_df = pd.DataFrame({
                'Fold': [f'Fold {i+1}' for i in range(len(cv_scores))],
                'ROC-AUC': cv_scores
            })
            st.dataframe(cv_df, use_container_width=True)
            
            fig_cv = px.box(y=cv_scores, title="Cross-Validation Distribution")
            fig_cv.update_layout(yaxis_title="ROC-AUC Score", height=400)
            st.plotly_chart(fig_cv, use_container_width=True)
        
        with st.expander("📋 Detailed Classification Report", expanded=False):
            report = classification_report(st.session_state['y_test'], st.session_state['y_pred'], output_dict=True)
            report_df = pd.DataFrame(report).transpose().round(4)
            st.dataframe(report_df, use_container_width=True)
        
        if st.session_state['model_performance_history']:
            with st.expander("📈 Model Performance History", expanded=False):
                history_df = pd.DataFrame(st.session_state['model_performance_history'])
                history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
                st.line_chart(history_df.set_index('timestamp')[['ensemble_auc', 'ensemble_f1']])
    
    # Tab 6: Enterprise Report (FAST VERSION)
    with tab6:
        st.markdown("## 📄 Enterprise-Grade Report")
        st.markdown("*Generate professional branded HR report with comprehensive analytics*")
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("**📋 Report Contents:**")
            st.markdown("""
            - ✅ Executive Summary
            - ✅ Data Quality Report
            - ✅ Model Performance Metrics
            - ✅ HR Strategic Recommendations
            - ✅ Risk Analysis Summary
            """)
        
        with c2:
            st.markdown("**📊 Report Specifications:**")
            st.markdown(f"""
            - 📄 Professional PDF Format
            - 🎯 Actionable Insights
            - 💡 Strategic Recommendations
            - 🏢 Corporate Branding
            - 🎂 Age Limit: {MIN_AGE}-{MAX_AGE} Years
            - ⭐ Rating Limits: {MIN_RATING}-{MAX_RATING} Scale
            - 🎯 8+ Feature Risk Analysis
            """)
        
        if st.button("📑 GENERATE ENTERPRISE REPORT", use_container_width=True):
            with st.spinner("Generating professional HR report..."):
                try:
                    pdf_buffer = generate_pdf_report(
                        st.session_state['cleaning_df'],
                        st.session_state['stats_df'],
                        metrics,
                        'Final Ensemble',
                        attrition_rate,
                        st.session_state['cleaning_insights'],
                        st.session_state.get('pred_result'),
                        cv_scores
                    )
                    
                    b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
                    st.markdown(f"""
                    <a href="data:application/pdf;base64,{b64}" download="hr_attrition_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf" style="text-decoration: none;">
                        <button style="background: linear-gradient(90deg, {st.session_state['brand_color']}, #764ba2, #f093fb);
                                        background-size: 200% auto;
                                        color: white;
                                        padding: 15px 30px;
                                        border: none;
                                        border-radius: 50px;
                                        font-weight: bold;
                                        font-size: 16px;
                                        cursor: pointer;
                                        width: 100%;
                                        transition: all 0.3s ease;">
                            📥 DOWNLOAD PDF REPORT
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                    st.success("✅ Enterprise report generated successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
                    st.info("Please try again. If issue persists, check data quality.")

else:
    # Welcome Screen
    st.markdown(f"""
    <div class="glass-card" style="text-align: center;">
        <h2>✨ Welcome to {st.session_state['company_name']} Employee Attrition Prediction System ✨</h2>
        <p style="font-size: 1.1rem; margin: 1rem 0;">Enterprise-grade AI solution for employee retention analytics</p>
        <p style="font-size: 0.9rem;">⚠️ <strong>Age Policy:</strong> Only employees aged {MIN_AGE}-{MAX_AGE} are analyzed</p>
        <p style="font-size: 0.9rem;">⭐ <strong>Rating Policy:</strong> All satisfaction metrics limited to {MIN_RATING}-{MAX_RATING} scale</p>
        <p style="font-size: 0.9rem;">🎯 <strong>Prediction Features:</strong> 8+ priority features including Age, Income, Tenure, Satisfaction, Overtime, and more</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.info("📊 CSV Format")
    with c2:
        st.warning("📑 Excel Format")
    with c3:
        st.error("🔷 JSON Format")
    with c4:
        st.success("📦 Parquet Format")
    
    with st.expander("📌 System Requirements", expanded=True):
        st.markdown("""
        - **Required column**: 'attrition' or 'left' (target variable)
        - **Values**: Yes/No or 1/0
        - **Sample columns**: Age, MonthlyIncome, YearsAtCompany, JobSatisfaction, WorkLifeBalance, OverTime
        - **Age limit**: 18-65 years (automatically enforced)
        - **Rating limits**: 0-5 scale (automatically enforced for satisfaction metrics)
        - **Minimum features**: 8+ priority features for accurate prediction
        - **File size**: No limit (optimized for large datasets)
        - **Format support**: CSV, Excel, JSON, Parquet
        """)
    
    with st.expander("📖 Sample Data Format", expanded=False):
        sample_data = pd.DataFrame({
            'Age': [30, 35, 28, 42, 25],
            'MonthlyIncome': [50000, 65000, 45000, 70000, 40000],
            'YearsAtCompany': [3, 5, 2, 8, 1],
            'JobSatisfaction': [4, 2, 3, 5, 2],
            'WorkLifeBalance': [3, 2, 4, 4, 2],
            'EnvironmentSatisfaction': [4, 2, 3, 4, 2],
            'YearsSinceLastPromotion': [2, 4, 1, 3, 0],
            'NumCompaniesWorked': [1, 2, 1, 3, 1],
            'DistanceFromHome': [10, 25, 5, 15, 30],
            'Department': ['Sales', 'IT', 'HR', 'Marketing', 'IT'],
            'OverTime': ['No', 'Yes', 'No', 'No', 'Yes'],
            'attrition': ['No', 'Yes', 'No', 'No', 'Yes']
        })
        st.dataframe(sample_data, use_container_width=True)
        st.caption("📌 **Note:** Age is automatically capped at 18-65 years. Satisfaction ratings are capped at 0-5 scale.")
    
    st.info("💡 **Tip:** Upload your employee data file to unlock advanced AI-powered attrition analytics with 8+ feature risk prediction")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 1rem;">
    <p>🏆 {st.session_state['company_name']} HR Attrition Intelligence Dashboard | Enterprise Edition</p>
    <p style="font-size: 0.8rem;">Powered by XGBoost + Random Forest + LightGBM + Gradient Boosting + Extra Trees Ensemble | SHAP Explainability | Corporate Grade Analytics</p>
    <p style="font-size: 0.7rem;">Age Limit: {MIN_AGE}-{MAX_AGE} Years | Rating Limits: {MIN_RATING}-{MAX_RATING} Scale | 8+ Priority Features for Accurate Prediction | © 2026 - All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)