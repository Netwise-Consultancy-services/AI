import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Life Expectancy Simulator",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme with white fonts
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
        padding-top: 1rem;
        background-color: #0e1117;
        color: white;
    }
    
       
    /* Alternative sidebar padding classes */
    .css-17eq0hr, .css-1lcbmhc {
        padding-top: 1rem !important;
    }
    
        /* Reduce space around title */
    h1 {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }
    /* Radio button title text */
.stRadio label {
    color: #ffffff !important;
    font-size: 36px !important;
    font-weight: bold !important;
}

/* Radio button option text */
.stRadio div[role="radiogroup"] > div {
    font-size: 36px !important;
    font-weight: bold !important;
    color: #ffffff !important;
}

/* Radio button container styling */
.stRadio div[role="radiogroup"] {
    gap: 20px !important;
}

/* Individual radio option styling */
.stRadio div[role="radiogroup"] > div > label {
    font-size: 36px !important;
    font-weight: bold !important;
    color: #ffffff !important;
}

/* Radio button circles */
.stRadio div[role="radiogroup"] > div > label > div:first-child {
    width: 24px !important;
    height: 24px !important;
}
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
        color: white;
    }
    
    .life-expectancy {
        font-size: 4rem;
        font-weight: bold;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .community-name {
        font-size: 1.5rem;
        color: #ffffff;
        margin-bottom: 1rem;
    }
    
    .factor-card {
        background: rgba(30, 41, 59, 0.9);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #3b82f6;
        color: white;
    }
 .metric-text {
            color: white;
            font-size: 18px;
            font-weight: bold;
        }
[data-testid="stMetricValue"] {
        color: white !important;
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
        color: white;
    }
    
    .prediction-card {
        background: linear-gradient(135deg, #7c2d12 0%, #ea580c 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(234, 88, 12, 0.3);
        color: white;
    }
    
    .stSelectbox > div > div {
        background-color: #002060;
        color: white;
    }
    
    .stSelectbox label {
        color: white !important;
    }
    
    .stNumberInput label {
        color: white !important;
    }
    
    .stSlider label {
        color: white !important;
    }
    
       
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    .impact-positive {
        color: #10b981;
        font-weight: bold;
    }
    
    .impact-negative {
        color: #ef4444;
        font-weight: bold;
    }
    
    .stDataFrame {
        background-color: #002060;
        color: white;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    .stMarkdown {
        color: white;
    }
    
    .element-container {
        color: white;
    }
    
    .stSidebar {
        background-color: #002060;
    }
    
    .stSidebar .stMarkdown {
        color: white;
    }
    
    .stMetric {
        background-color: #002060;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .stMetric label {
        color: white !important;
    }
    
    .stMetric [data-testid="metric-value"] {
        color: #3b82f6 !important;
        font-size: 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class LifeExpectancySimulator:
    def __init__(self):
        self.data = None
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.feature_importance = {}
        
    def load_data(self, file_path):
        """Load and preprocess the dataset"""
        try:
            if os.path.exists("merged_community_area_data - Copy.csv"):
                self.data = pd.read_csv(file_path)
                # Remove the success message
                return True
            else:
                st.error(f"File not found: {file_path}")
                return False
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False
    
    def preprocess_data(self):
        """Clean and prepare data for modeling"""
        if self.data is None:
            return False
            
        # Display basic info about the dataset - REMOVED
        
        # Identify the life expectancy column (case insensitive)
        life_exp_cols = [col for col in self.data.columns if 'life' in col.lower() and 'expect' in col.lower()]
        if not life_exp_cols:
            st.error("No 'Life Expectancy' column found in the dataset")
            return False
        
        life_exp_col = life_exp_cols[0]
        # Remove the info message about target variable
        
        # Select numeric columns (excluding GEOID and target)
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        exclude_cols = ['GEOID', life_exp_col, 'Longitude', 'Latitude', 'Population']
        self.feature_names = [col for col in numeric_cols if col not in exclude_cols]
        
        # Remove rows with missing target values
        before_count = len(self.data)
        self.data = self.data.dropna(subset=[life_exp_col])
        after_count = len(self.data)
        
        if before_count != after_count:
            st.warning(f"Removed {before_count - after_count} rows with missing life expectancy values")
        
        # Rename the life expectancy column for consistency
        self.data = self.data.rename(columns={life_exp_col: 'Life Expectancy'})
        
        # Fill missing values in features with median
        for col in self.feature_names:
            if col in self.data.columns:
                missing_count = self.data[col].isna().sum()
                if missing_count > 0:
                    self.data[col] = self.data[col].fillna(self.data[col].median())
        
        return True
    
    def train_model(self):
        """Train Random Forest model and calculate feature importance"""
        if self.data is None or not self.feature_names:
            return False, 0, 0
        
        # Prepare features and target
        available_features = [col for col in self.feature_names if col in self.data.columns]
        self.feature_names = available_features
        
        X = self.data[self.feature_names]
        y = self.data['Life Expectancy']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Calculate feature importance
        importance = self.model.feature_importances_
        self.feature_importance = dict(zip(self.feature_names, importance))
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        return True, r2, rmse
    
    def get_top_factors(self, geoid, n_factors=5):
        """Get top N factors affecting life expectancy for a specific area"""
        if self.data is None:
            return []
        
        # Handle different GEOID column names
        geoid_col = None
        for col in self.data.columns:
            if 'geoid' in col.lower() or col.lower() == 'id':
                geoid_col = col
                break
        
        if geoid_col is None:
            # Use index if no GEOID column found
            if geoid <= len(self.data):
                area_data = self.data.iloc[[geoid-1]]
            else:
                return []
        else:
            area_data = self.data[self.data[geoid_col] == geoid]
        
        if area_data.empty:
            return []
        
        # Sort features by importance
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        top_factors = []
        for feature, importance in sorted_features[:n_factors]:
            if feature not in area_data.columns:
                continue
                
            current_value = area_data[feature].iloc[0]
            
            # Determine if higher values are generally good or bad
            positive_indicators = [
                'life expectancy', 'employer health ins', 'dental cleanings',
                'personal doctor', 'routine checkup', 'healthcare satisfaction',
                'easy access to care', 'easy fruit/veg access', 'fruit/veg daily',
                'adequate prenatal care', '1st trimester prenatal care',
                'education', 'income', 'college', 'employment', 'graduation'
            ]
            
            negative_indicators = [
                'binge drinking', 'current smokers', 'no physical activity',
                'uninsured residents', 'poverty', 'unemployment', 'crime',
                'mortality', 'death', 'disease'
            ]
            
            is_positive = any(indicator in feature.lower() for indicator in positive_indicators)
            is_negative = any(indicator in feature.lower() for indicator in negative_indicators)
            
            if is_negative:
                is_positive = False
            
            direction = "↑" if is_positive else "↓"
            
            top_factors.append({
                'factor': feature,
                'current_value': current_value,
                'importance': importance,
                'direction': direction,
                'is_positive': is_positive
            })
        
        return top_factors
    
    def predict_life_expectancy(self, geoid, feature_changes=None):
        """Predict life expectancy with optional feature modifications"""
        if self.model is None or self.data is None:
            return None
        
        # Handle different GEOID column names
        geoid_col = None
        for col in self.data.columns:
            if 'geoid' in col.lower() or col.lower() == 'id':
                geoid_col = col
                break
        
        if geoid_col is None:
            if geoid <= len(self.data):
                area_data = self.data.iloc[[geoid-1]]
            else:
                return None
        else:
            area_data = self.data[self.data[geoid_col] == geoid]
        
        if area_data.empty:
            return None
        
        # Get current feature values
        features = area_data[self.feature_names].iloc[0].copy()
        
        # Apply changes if provided
        if feature_changes:
            for feature, new_value in feature_changes.items():
                if feature in features.index:
                    features[feature] = new_value
        
        # Scale and predict
        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict(features_scaled)[0]
        
        return prediction
    
    def simulate_target_life_expectancy(self, geoid, target_life_exp):
        """Simulate changes needed to reach target life expectancy"""
        if self.model is None or self.data is None:
            return []
        
        # Get current life expectancy
        geoid_col = None
        for col in self.data.columns:
            if 'geoid' in col.lower() or col.lower() == 'id':
                geoid_col = col
                break
        
        if geoid_col is None:
            if geoid <= len(self.data):
                current_life_exp = self.data.iloc[geoid-1]['Life Expectancy']
            else:
                return []
        else:
            area_data = self.data[self.data[geoid_col] == geoid]
            if area_data.empty:
                return []
            current_life_exp = area_data['Life Expectancy'].iloc[0]
        
        if target_life_exp <= current_life_exp:
            return []
        
        top_factors = self.get_top_factors(geoid)
        recommendations = []
        
        # Simple optimization: adjust top factors incrementally
        for factor_info in top_factors:
            factor = factor_info['factor']
            current_val = factor_info['current_value']
            is_positive = factor_info['is_positive']
            
            # Calculate reasonable adjustment range
            factor_data = self.data[factor].dropna()
            factor_std = factor_data.std()
            factor_mean = factor_data.mean()
            
            if is_positive:
                # For positive factors, suggest increase
                suggested_change = min(factor_std * 0.5, abs(factor_mean * 0.2))
                new_value = min(factor_data.max(), current_val + suggested_change)
                recommendation = f"Increase by {suggested_change:.2f} units"
            else:
                # For negative factors, suggest decrease
                suggested_change = min(factor_std * 0.5, abs(factor_mean * 0.2))
                new_value = max(factor_data.min(), current_val - suggested_change)
                recommendation = f"Decrease by {suggested_change:.2f} units"
            
            recommendations.append({
                'factor': factor,
                'current_value': current_val,
                'suggested_value': new_value,
                'change': suggested_change if is_positive else -suggested_change,
                'recommendation': recommendation,
                'direction': factor_info['direction']
            })
        
        return recommendations

# Initialize the simulator
@st.cache_data

def load_simulator():
    simulator = LifeExpectancySimulator()
    
    # In Streamlit Cloud, files are typically in the same directory
    file_path = "merged_community_area_data - Copy.csv"
    
    # Check if file exists
    import os
    if not os.path.exists(file_path):
        st.error(f"CSV file not found: {file_path}")
        st.write("Available files:")
        try:
            files = [f for f in os.listdir('.') if f.endswith('.csv')]
            for f in files:
                st.write(f"- {f}")
        except:
            st.write("Could not list files")
        return None, 0, 0
    
    # Try to load the CSV file
    if simulator.load_data(file_path):
        if simulator.preprocess_data():
            success, r2, rmse = simulator.train_model()
            return simulator, r2, rmse
    
    st.error("Failed to load and process the data. Please check the file path and data format.")
    return None, 0, 0

# Main Streamlit App
def main():
    st.title("🏥 Life Expectancy Simulator")
    st.markdown("### Interactive Community Health Analysis Tool")
    
    # Load simulator
    with st.spinner("Loading data and training model..."):
        result = load_simulator()
        
    if result[0] is None:
        st.error("Cannot proceed without valid data. Please check your CSV file.")
        st.stop()
        
    simulator, r2_score, rmse = result
    
    # Sidebar for model info
    with st.sidebar:
        # Add Innova Solutions logo with reduced top margin
        st.markdown(
            """
            <div style="display: flex; justify-content: center; margin-top: -10px; margin-bottom: 15px;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Innova%E2%84%A2.jpg" 
                     alt="Innova Solutions Logo" 
                     style="width: 180px; height: auto; border-radius: 8px;">
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.header("📊 Model Performance")
        st.metric("R² Score", f"{r2_score:.3f}")
        st.metric("RMSE", f"{rmse:.2f} years")
        st.markdown("---")
        st.markdown("**Dataset Info:**")
        st.write(f"Total records: {len(simulator.data)}")
        st.write(f"Features used: {len(simulator.feature_names)}")
        st.markdown("---")
        st.markdown("**Instructions:**")
        st.markdown("1. Select a community area")
        st.markdown("2. Choose simulation mode")
        st.markdown("3. Explore predictions!")
    
    # Main interface
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("🎯 Select Community")
        
        # Get available GEOIDs and community names
        geoid_col = None
        name_col = None
        
        # Find GEOID column
        for col in simulator.data.columns:
            if 'geoid' in col.lower() or col.lower() == 'id':
                geoid_col = col
                break
        
        # Find community name column
        for col in simulator.data.columns:
            if 'name' in col.lower() or 'community' in col.lower():
                name_col = col
                break
        
        if geoid_col and name_col:
            # Create a mapping of community names to GEOIDs
            community_mapping = {}
            for _, row in simulator.data.iterrows():
                community_name = str(row[name_col])
                geoid_value = row[geoid_col]
                community_mapping[community_name] = geoid_value
            
            # Sort community names alphabetically
            sorted_communities = sorted(community_mapping.keys())
            
            selected_community = st.selectbox(
                "Select Community:",
                options=sorted_communities,
                index=0
            )
            
            geoid = community_mapping[selected_community]
            area_data = simulator.data[simulator.data[geoid_col] == geoid].iloc[0]
            community_name = selected_community
            
        elif geoid_col:
            # Fallback to GEOID selection if no name column
            available_geoids = sorted(simulator.data[geoid_col].unique())
            geoid = st.selectbox(
                f"Select {geoid_col}:",
                options=available_geoids,
                index=0
            )
            area_data = simulator.data[simulator.data[geoid_col] == geoid].iloc[0]
            
            # Try to get community name
            name_cols = [col for col in simulator.data.columns if 'name' in col.lower()]
            if name_cols:
                community_name = str(area_data[name_cols[0]])
            else:
                community_name = f"Area {geoid}"
        else:
            # Fallback to index selection
            geoid = st.selectbox(
                "Select Area (by index):",
                options=list(range(1, len(simulator.data) + 1)),
                index=0
            )
            area_data = simulator.data.iloc[geoid-1]
            community_name = f"Area {geoid}"
        
        current_life_exp = area_data['Life Expectancy']
        
        # Display current life expectancy
        st.markdown(f"""
        <div class="metric-card">
            <div class="community-name">{community_name}</div>
            <div class="life-expectancy">{current_life_exp:.1f}</div>
            <div style="color: #e2e8f0;">Years Life Expectancy</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show top factors
        st.header("🔍 Top 5 Factors")
        top_factors = simulator.get_top_factors(geoid)
        
        for i, factor in enumerate(top_factors):
            impact_class = "impact-positive" if factor['is_positive'] else "impact-negative"
            factor_display = factor['factor'][:30] + '...' if len(factor['factor']) > 30 else factor['factor']
            st.markdown(f"""
            <div class="factor-card">
                <strong>{factor_display}</strong><br>
                Value: {factor['current_value']:.2f}<br>
                Impact: <span class="{impact_class}">{factor['direction']}</span>
                Importance: {factor['importance']:.3f}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.header("🧠 Simulation Options")
        
        simulation_mode = st.radio(
            "Choose Simulation Mode:",
            ["🎯 Target Life Expectancy", "🔧 Manual Feature Adjustment"],
            horizontal=True
        )
        
        if simulation_mode == "🎯 Target Life Expectancy":
            st.subheader("Set Target Life Expectancy")
            
            target_life_exp = st.number_input(
                f"Target Life Expectancy (current: {current_life_exp:.1f}):",
                min_value=float(current_life_exp + 0.1),
                max_value=90.0,
                value=float(current_life_exp + 2.0),
                step=0.1
            )
            
            if st.button("🔮 Generate Recommendations", type="primary"):
                recommendations = simulator.simulate_target_life_expectancy(geoid, target_life_exp)
                
                if recommendations:
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <h3 style="color: white; margin-top: 0;">🎯 Recommendations to reach {target_life_exp:.1f} years</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create recommendations table
                    rec_df = pd.DataFrame([{
                        'Factor': rec['factor'][:25] + '...' if len(rec['factor']) > 25 else rec['factor'],
                        'Current': f"{rec['current_value']:.2f}",
                        'Suggested': f"{rec['suggested_value']:.2f}",
                        'Change': rec['recommendation'],
                        'Direction': rec['direction']
                    } for rec in recommendations])
                    
                    # Reset index to start from 1 instead of 0
                    rec_df.index = range(1, len(rec_df) + 1)
                    
                    st.dataframe(rec_df, use_container_width=True)
                    
                    # Test the recommendations
                    feature_changes = {rec['factor']: rec['suggested_value'] for rec in recommendations}
                    predicted_life_exp = simulator.predict_life_expectancy(geoid, feature_changes)
                    
                    if predicted_life_exp:
                        improvement = predicted_life_exp - current_life_exp
                        st.success(f"Predicted improvement: +{improvement:.2f} years → {predicted_life_exp:.1f} years")
                else:
                    st.warning("No recommendations could be generated. The target may already be achieved or too high.")
        
        else:  # Manual Feature Adjustment
            st.subheader("Adjust Top 5 Factors")
            
            feature_changes = {}
            top_factors = simulator.get_top_factors(geoid)
            
            if not top_factors:
                st.warning("No factors available for adjustment.")
            else:
                for factor in top_factors:
                    factor_name = factor['factor']
                    current_val = factor['current_value']
                    
                    # Create reasonable bounds for sliders
                    factor_data = simulator.data[factor_name].dropna()
                    min_val = max(0, factor_data.min())
                    max_val = factor_data.max()
                    
                    if min_val < max_val:  # Only create slider if valid range
                        new_value = st.slider(
                            f"{factor_name[:30]}{'...' if len(factor_name) > 30 else ''}",
                            min_value=float(min_val),
                            max_value=float(max_val),
                            value=float(current_val),
                            step=0.1,
                            help=f"Current: {current_val:.2f}, Direction: {factor['direction']}"
                        )
                        
                        if abs(new_value - current_val) > 0.01:
                            feature_changes[factor_name] = new_value
                
                # Predict with changes
                if feature_changes:
                    predicted_life_exp = simulator.predict_life_expectancy(geoid, feature_changes)
                    
                    if predicted_life_exp:
                        improvement = predicted_life_exp - current_life_exp
                        color = "#10b981" if improvement >= 0 else "#ef4444"
                        sign = "+" if improvement >= 0 else ""
                        
                        st.markdown(f"""
                        <div class="prediction-card">
                            <h3 style="color: white; margin-top: 0;">🔮 Predicted Life Expectancy</h3>
                            <div style="font-size: 2.5rem; font-weight: bold; color: white;">
                                {predicted_life_exp:.1f} years
                            </div>
                            <div style="font-size: 1.2rem; color: {color};">
                                {sign}{improvement:.2f} years change
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show changes summary
                        if len(feature_changes) > 0:
                            st.subheader("📋 Changes Summary")
                            changes_df = pd.DataFrame([
                                {
                                    'Factor': factor[:25] + '...' if len(factor) > 25 else factor,
                                    'Original': f"{area_data[factor]:.2f}",
                                    'Modified': f"{value:.2f}",
                                    'Change': f"{value - area_data[factor]:.2f}"
                                }
                                for factor, value in feature_changes.items()
                            ])
                            st.dataframe(changes_df, use_container_width=True)
                
                else:
                    st.info("Adjust the sliders above to see predicted changes in life expectancy.")
    
    # Footer
    st.markdown("---")
    st.markdown("### 📈 Visualization")
    
    # Create a comparison chart
    if simulation_mode == "🔧 Manual Feature Adjustment" and len(feature_changes) > 0:
        predicted_life_exp = simulator.predict_life_expectancy(geoid, feature_changes)
        
        if predicted_life_exp:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Current', 'Predicted'],
                y=[current_life_exp, predicted_life_exp],
                marker_color=['#3b82f6', '#10b981'],
                text=[f'{current_life_exp:.1f}', f'{predicted_life_exp:.1f}'],
                textposition='outside',
                textfont=dict(color='white', size=14)
            ))
            
            fig.update_layout(
                title=f"Life Expectancy Comparison - {community_name}",
                yaxis_title="Life Expectancy (Years)",
                template="plotly_dark",
                height=400,
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
