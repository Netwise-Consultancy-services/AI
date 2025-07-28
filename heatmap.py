import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium import plugins
import branca.colormap as cm
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Life Expectancy Analysis Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #667eea;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: bold;
}
.sub-header {
    font-size: 1.5rem;
    color: #764ba2;
    text-align: center;
    margin-bottom: 3rem;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
}
.insight-box {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    """Load and process the data with caching for better performance"""
    try:
        # Try to load the data - you'll need to upload this file to your repo
        df = pd.read_csv("merged_community_area_data - Copy.csv")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Identify and exclude death-related factors
        death_keywords = ['deaths', 'death', 'mortality', 'fatalities', 'homicide', 'suicide']
        death_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in death_keywords)]
        
        # Keep only relevant columns (exclude death factors)
        analysis_columns = [col for col in df.columns if col not in death_columns]
        df_analysis = df[analysis_columns].copy()
        
        # Find lat/lon columns
        lat_cols = [col for col in df_analysis.columns if "latitude" in col.lower()]
        lon_cols = [col for col in df_analysis.columns if "longitude" in col.lower()]
        
        if not lat_cols or not lon_cols:
            st.error("Latitude and longitude columns not found in the dataset")
            return None, None, None, None, None
            
        lat_col = lat_cols[0]
        lon_col = lon_cols[0]
        
        # Clean data
        df_analysis = df_analysis.dropna(subset=[lat_col, lon_col, 'Life Expectancy'])
        
        return df_analysis, lat_col, lon_col, death_columns, analysis_columns
        
    except FileNotFoundError:
        st.error("Data file not found. Please upload 'merged_community_area_data - Copy.csv' to your repository.")
        return None, None, None, None, None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None, None

@st.cache_data
def train_prediction_model(df_analysis):
    """Train the prediction model with caching"""
    # Select numeric columns for analysis
    numeric_df = df_analysis.select_dtypes(include=[np.number])
    numeric_df = numeric_df.drop(columns=['GEOID'], errors='ignore')
    
    # Calculate correlations with Life Expectancy
    corr_matrix = numeric_df.corr()
    life_exp_corr = corr_matrix['Life Expectancy'].abs().sort_values(ascending=False)[1:16]
    
    # Prepare features and target
    target_col = 'Life Expectancy'
    feature_cols = [col for col in numeric_df.columns if col != target_col]
    X = numeric_df[feature_cols]
    y = numeric_df[target_col]
    
    # Handle missing values
    imputer = SimpleImputer(strategy='median')
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_imputed), columns=X.columns)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    # Train Random Forest model
    rf_model = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=10)
    rf_model.fit(X_train, y_train)
    
    # Model performance
    y_pred = rf_model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Feature importance analysis
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return rf_model, X_scaled, feature_importance, corr_matrix, rmse, r2, life_exp_corr

def get_life_expectancy_color(life_exp):
    """Return color based on life expectancy"""
    if life_exp >= 80:
        return '#4ECDC4'  # Teal
    elif life_exp >= 75:
        return '#FFE66D'  # Yellow
    else:
        return '#FF6B6B'  # Red

def simulate_improvements(row_data, feature_importances, correlation_matrix, scaled_features, model, improvement_factor=0.2):
    """Simulate life expectancy improvements"""
    try:
        # Get the row's feature values
        if hasattr(row_data, 'name') and row_data.name in scaled_features.index:
            row_features = scaled_features.loc[row_data.name]
        else:
            row_features = scaled_features.iloc[0]
        
        improved_features = row_features.copy()
        
        # Get top 5 most important improvable factors
        top_factors = feature_importances.head(5)
        
        for _, factor_row in top_factors.iterrows():
            feature_name = factor_row['feature']
            if feature_name in improved_features.index:
                current_value = improved_features[feature_name]
                
                # Check correlation direction for improvement
                if feature_name in correlation_matrix.index:
                    correlation = correlation_matrix.loc[feature_name, 'Life Expectancy']
                    
                    if correlation > 0:
                        improved_features[feature_name] = current_value + (improvement_factor * abs(current_value))
                    else:
                        improved_features[feature_name] = current_value - (improvement_factor * abs(current_value))
        
        # Predict with improved features
        improved_prediction = model.predict([improved_features])[0]
        return improved_prediction
    except:
        return row_data.get('Life Expectancy', 75) + 2  # Default improvement

def get_personalized_improvement_factors(row_data, all_feature_importances, df_data, correlation_matrix):
    """Get personalized top 3 improvement factors"""
    improvement_factors = []
    
    for feature in all_feature_importances['feature'][:15]:  # Check top 15 features
        if feature in row_data.index and pd.notna(row_data[feature]):
            importance = all_feature_importances[all_feature_importances['feature'] == feature]['importance'].iloc[0]
            current_value = row_data[feature]
            
            if feature in correlation_matrix.index:
                correlation = correlation_matrix.loc[feature, 'Life Expectancy']
                
                # Calculate improvement potential
                feature_max = df_data[feature].max()
                feature_min = df_data[feature].min()
                if feature_max != feature_min:
                    normalized_value = (current_value - feature_min) / (feature_max - feature_min)
                    if correlation > 0:
                        improvement_potential = 1 - normalized_value
                    else:
                        improvement_potential = normalized_value
                else:
                    improvement_potential = 0.5
                
                combined_score = importance * improvement_potential
                
                improvement_factors.append({
                    'feature': feature,
                    'importance': importance,
                    'current_value': current_value,
                    'improvement_potential': improvement_potential,
                    'combined_score': combined_score,
                    'correlation': correlation
                })
    
    improvement_factors.sort(key=lambda x: x['combined_score'], reverse=True)
    return improvement_factors[:3]

def create_enhanced_map(df_analysis, lat_col, lon_col, feature_importance, corr_matrix):
    """Create the enhanced life expectancy map"""
    # Create base map
    center_lat = df_analysis[lat_col].mean()
    center_lon = df_analysis[lon_col].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10,
        tiles=None,
        prefer_canvas=True
    )
    
    # Add dark theme
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attr='&copy; OpenStreetMap &copy; CARTO',
        name='Dark Theme',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add markers for each area
    for _, row in df_analysis.iterrows():
        life_exp = row['Life Expectancy']
        color = get_life_expectancy_color(life_exp)
        
        # Get community name
        community_name = "Unknown"
        name_columns = [col for col in df_analysis.columns if 'name' in col.lower()]
        if name_columns:
            community_name = str(row.get(name_columns[0], 'Unknown'))
        
        # Get personalized factors
        personalized_factors = get_personalized_improvement_factors(row, feature_importance, df_analysis, corr_matrix)
        
        # Create popup
        popup_html = f"""
        <div style="font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 15px; border-radius: 10px; min-width: 300px;">
            <h3 style="margin: 0; color: #FFE66D;">📍 {community_name}</h3>
            <p style="margin: 5px 0;">GEOID: {row['GEOID']}</p>
            
            <div style="display: flex; justify-content: space-around; margin: 15px 0; 
                        background: rgba(255,255,255,0.1); padding: 10px; border-radius: 6px;">
                <div style="text-align: center;">
                    <div style="font-size: 18px; font-weight: bold; color: #4ECDC4;">{life_exp:.1f}</div>
                    <div style="font-size: 11px;">Current</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 18px; font-weight: bold; color: #FFE66D;">{row.get('Improved_Life_Exp', life_exp + 2):.1f}</div>
                    <div style="font-size: 11px;">Potential</div>
                </div>
            </div>
            
            <h4 style="color: #FFE66D; font-size: 14px;">🎯 Improvement Opportunities</h4>
        """
        
        for i, factor_info in enumerate(personalized_factors, 1):
            feature = factor_info['feature']
            correlation = factor_info['correlation']
            recommendation = "📈 Increase" if correlation > 0 else "📉 Reduce"
            
            popup_html += f"""
            <div style="margin: 8px 0; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 5px;">
                <div style="font-weight: bold; font-size: 12px; color: #FFE66D;">
                    {i}. {recommendation} {feature}
                </div>
            </div>
            """
        
        popup_html += "</div>"
        
        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=8,
            popup=folium.Popup(popup_html, max_width=400),
            color='white',
            weight=2,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            tooltip=f"{community_name}: {life_exp:.1f} years"
        ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 20px; left: 20px; width: 200px; height: auto; 
                background: rgba(0,0,0,0.8); color: white; z-index: 9999; font-size: 14px;
                padding: 15px; border-radius: 10px;">
        <h4 style="margin: 0 0 10px 0; color: #FFE66D;">Life Expectancy</h4>
        <div style="margin: 8px 0;"><span style="color: #4ECDC4;">●</span> 80+ years (Excellent)</div>
        <div style="margin: 8px 0;"><span style="color: #FFE66D;">●</span> 75-79 years (Good)</div>
        <div style="margin: 8px 0;"><span style="color: #FF6B6B;">●</span> Below 75 years (Needs Focus)</div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

# Main Streamlit App
def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 Life Expectancy Analysis Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Community Health Intelligence Platform</p>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading and processing data..."):
        data_result = load_and_process_data()
        
    if data_result[0] is None:
        st.error("Unable to load data. Please check if the data file is available.")
        st.info("Expected file: `merged_community_area_data - Copy.csv`")
        st.stop()
    
    df_analysis, lat_col, lon_col, death_columns, analysis_columns = data_result
    
    # Global variables for model components
    global rf_model, X_scaled, feature_importance, corr_matrix
    
    # Train model
    with st.spinner("Training predictive model..."):
        rf_model, X_scaled, feature_importance, corr_matrix, rmse, r2, life_exp_corr = train_prediction_model(df_analysis)
    
    # Calculate improvement potential
    df_analysis['Improved_Life_Exp'] = df_analysis.apply(
        lambda row: simulate_improvements(row, feature_importance, corr_matrix, X_scaled, rf_model), axis=1
    )
    df_analysis['Improvement_Potential'] = (df_analysis['Improved_Life_Exp'] - df_analysis['Life Expectancy']).clip(0, 10)
    
    # Sidebar
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
    st.sidebar.header("📊 Analysis Overview")
    st.sidebar.metric("Total Areas", len(df_analysis))
    st.sidebar.metric("Average Life Expectancy", f"{df_analysis['Life Expectancy'].mean():.1f} years")
    st.sidebar.metric("Model Accuracy (R²)", f"{r2:.3f}")
    st.sidebar.metric("Prediction Error (RMSE)", f"{rmse:.2f} years")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "📈 Key Insights", "🎯 Recommendations"])
    
    with tab1:
        st.markdown("### Enhanced Life Expectancy Map")
        st.markdown("Click on any marker to see detailed insights and improvement opportunities for that area.")
        
        # Create and display map
        with st.spinner("Generating interactive map..."):
            map_obj = create_enhanced_map(df_analysis, lat_col, lon_col, feature_importance, corr_matrix)
            
        # Display map using streamlit-folium
        st_folium(map_obj, width=1200, height=600)
        
        # Map legend explanation
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4>🟢 Excellent Areas</h4>
                <p>80+ years life expectancy<br>Strong health outcomes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h4>🟡 Good Areas</h4>
                <p>75-79 years life expectancy<br>Room for improvement</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h4>🔴 Priority Areas</h4>
                <p>Below 75 years<br>Needs immediate focus</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Key Insights from Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top correlations chart
            st.markdown("#### Top Factors Correlated with Life Expectancy")
            top_corr = life_exp_corr.head(10)
            
            fig = px.bar(
                x=top_corr.values,
                y=top_corr.index,
                orientation='h',
                color=top_corr.values,
                color_continuous_scale='viridis',
                title="Correlation Strength"
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Feature importance chart
            st.markdown("#### Top Predictive Features")
            top_features = feature_importance.head(10)
            
            fig = px.bar(
                x=top_features['importance'],
                y=top_features['feature'],
                orientation='h',
                color=top_features['importance'],
                color_continuous_scale='plasma',
                title="Model Feature Importance"
            )
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        st.markdown("#### Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Lowest Life Expectancy", 
                f"{df_analysis['Life Expectancy'].min():.1f} years"
            )
        with col2:
            st.metric(
                "Highest Life Expectancy", 
                f"{df_analysis['Life Expectancy'].max():.1f} years"
            )
        with col3:
            st.metric(
                "Average Improvement Potential", 
                f"{df_analysis['Improvement_Potential'].mean():.1f} years"
            )
        with col4:
            st.metric(
                "Max Improvement Potential", 
                f"{df_analysis['Improvement_Potential'].max():.1f} years"
            )
    
    with tab3:
        st.markdown("### Strategic Recommendations")
        
        # Priority areas
        st.markdown("#### Areas Requiring Immediate Attention")
        priority_areas = df_analysis.nsmallest(5, 'Life Expectancy')[['GEOID', 'Life Expectancy', 'Improvement_Potential']]
        
        for _, area in priority_areas.iterrows():
            st.markdown(f"""
            <div class="insight-box">
                <strong>GEOID {area['GEOID']}</strong><br>
                Current Life Expectancy: <strong>{area['Life Expectancy']:.1f} years</strong><br>
                Improvement Potential: <strong>+{area['Improvement_Potential']:.1f} years</strong>
            </div>
            """, unsafe_allow_html=True)
        
        # High potential areas
        st.markdown("#### Areas with Highest Improvement Potential")
        potential_areas = df_analysis.nlargest(5, 'Improvement_Potential')[['GEOID', 'Life Expectancy', 'Improvement_Potential']]
        
        for _, area in potential_areas.iterrows():
            st.markdown(f"""
            <div class="insight-box">
                <strong>GEOID {area['GEOID']}</strong><br>
                Current Life Expectancy: <strong>{area['Life Expectancy']:.1f} years</strong><br>
                Improvement Potential: <strong>+{area['Improvement_Potential']:.1f} years</strong>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
