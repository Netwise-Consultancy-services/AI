PHM (Predictive Health Monitoring) Demo
A Streamlit web application for predictive health monitoring using machine learning techniques. This application analyzes health data, provides visualizations, and generates predictive models for health metrics.

🚀 Live Demo
Access the live application at: phmdemo.streamlit.app

📋 Features
Data Analysis: Comprehensive analysis of health monitoring datasets
Interactive Visualizations: Dynamic charts and graphs using seaborn and matplotlib
Geographic Mapping: Location-based health data visualization with Folium maps
Machine Learning Models: Random Forest regression for predictive analytics
Report Generation: Automated Word document report generation
Data Processing: Advanced data cleaning and preprocessing capabilities
🛠️ Technologies Used
Frontend: Streamlit
Data Processing: Pandas, NumPy
Visualization: Matplotlib, Seaborn, Folium
Machine Learning: Scikit-learn
Document Generation: python-docx
Mapping: Folium with Branca colormap
📊 Machine Learning Components
Algorithm: Random Forest Regressor
Data Preprocessing:
Missing value imputation using SimpleImputer
Feature scaling with StandardScaler
Train-test split for model validation
Evaluation Metrics:
Mean Squared Error (MSE)
R² Score
📁 Project Structure
phm/
├── phm1.py              # Main Streamlit application
├── dataset.csv          # Health monitoring dataset
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
🔧 Installation & Setup
Local Development
Clone the repository
bash
git clone https://github.com/yourusername/phm.git
cd phm
Install dependencies
bash
pip install -r requirements.txt
Run the application
bash
streamlit run phm1.py
Access the app Open your browser and navigate to http://localhost:8501
Streamlit Cloud Deployment
This application is automatically deployed on Streamlit Cloud. Any changes pushed to the main branch will trigger an automatic redeployment.

📋 Requirements
All required Python packages are listed in requirements.txt:

streamlit
pandas
numpy
seaborn
matplotlib
folium
branca
scikit-learn
python-docx
🗂️ Dataset
The application works with health monitoring datasets containing various health metrics and parameters. Ensure your dataset is in CSV format and placed in the root directory.

🎯 Usage
Upload Data: Load your health monitoring dataset
Explore Data: View statistical summaries and data distributions
Visualize: Generate interactive charts and geographic maps
Model Training: Train Random Forest models for predictive analysis
Generate Reports: Create comprehensive Word document reports
Download Results: Export analysis results and predictions
🔍 Key Features Explained
Data Analysis
Statistical summaries of health metrics
Missing value detection and handling
Data distribution analysis
Visualization
Correlation heatmaps
Distribution plots
Time series analysis
Geographic health data mapping
Predictive Modeling
Feature engineering and selection
Model training with cross-validation
Performance evaluation and metrics
Prediction generation
Report Generation
Automated Word document creation
Statistical summaries inclusion
Visualization embedding
Formatted analysis results
🤝 Contributing
Fork the repository
Create a feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🐛 Troubleshooting
Common Issues
Import Errors: Ensure all dependencies are installed via requirements.txt
Data Loading: Verify dataset format and file path
Memory Issues: For large datasets, consider data sampling
Deployment Issues: Check Streamlit Cloud logs for detailed error messages
Support
For issues and questions:

Check the Issues section
Create a new issue with detailed description
Include error logs and system information
📈 Future Enhancements
 Additional ML algorithms (XGBoost, Neural Networks)
 Real-time data streaming capabilities
 Advanced visualization dashboards
 Multi-user authentication
 API integration for external data sources
 Mobile-responsive design improvements
👥 Authors
Meet Golakiya
🙏 Acknowledgments
Streamlit community for the amazing framework
Scikit-learn contributors for machine learning tools
Open source community for various visualization libraries
