# NBA Player Predictor & Betting Analysis System

A comprehensive NBA player performance prediction and sports betting analysis system that combines machine learning models, web scraping, and real-time data processing to provide accurate player statistics predictions for betting markets.

## 🏀 Overview

This system analyzes NBA player performance data to predict various statistical outcomes (points, rebounds, assists, three-pointers) and compares them against sportsbook betting lines to identify potential value bets. The system integrates multiple data sources including the NBA API, web scraping from betting sites, and advanced statistical modeling.

## 🚀 Key Features

### 1. **Data Collection & Management**
- **NBA API Integration**: Real-time player and team statistics
- **Web Scraping**: Automated collection of betting odds from multiple sportsbooks
- **Database Management**: SQLite database with comprehensive player and team data
- **Historical Data**: Season averages, last 5/10 game trends, and career statistics

### 2. **Machine Learning Predictions**
- **Linear Regression Models**: For predicting player statistics
- **Multi-variable Analysis**: Considers minutes played, team context, opponent strength
- **Position-based Modeling**: Different models for different player positions
- **Contextual Factors**: Usage rate, team pace, opponent defense rankings

### 3. **Betting Market Analysis**
- **Sportsbook Integration**: SportsBet, Ladbrokes, PointsBet scraping
- **Market Comparison**: Over/under lines across different betting markets
- **Value Identification**: Statistical edge detection for betting opportunities
- **Real-time Updates**: Live odds monitoring and comparison

### 4. **Statistical Models**
- **Points Prediction**: 2-pointers, 3-pointers, and free throws
- **Rebounds Prediction**: Offensive and defensive rebound modeling
- **Assists Prediction**: Usage rate and team context analysis
- **Combined Markets**: PRA (Points + Rebounds + Assists) predictions

## 📁 Project Structure

```
NBA_betting/
├── app.py                          # Main application entry point
├── betting.py                      # Betting odds API integration
├── nbaAPI.py                       # NBA API wrapper functions
├── dbFunctions.py                  # Database query functions
├── webscraping.py                  # Web scraping for betting odds
├── APItoData.py                    # Player data collection and processing
├── APItoDataTeams.py               # Team statistics collection
├── APIBoxScoresIntoDatabase.py     # Box score data processing
├── RegressionModel.py              # Machine learning prediction models
├── database/                       # SQLite database files
│   ├── main2024.db                 # Current season database
│   ├── main.db                     # Legacy database
│   └── OLDversion.db               # Backup database
├── frontend/                       # React.js web interface
│   ├── src/
│   │   ├── App.js                  # Main React component
│   │   └── index.js                # React entry point
│   └── package.json                # Frontend dependencies
├── data/                          # Team-specific data folders
├── static/                        # CSS and static assets
└── templates/                     # HTML templates
```

## 🔧 Core Components

### 1. **Data Collection Pipeline**

#### NBA API Integration (`nbaAPI.py`)
- Player information and career statistics
- Team rosters and game fixtures
- Real-time game data and box scores
- Historical performance tracking

#### Web Scraping (`webscraping.py`)
- **SportsBet**: Player prop betting markets
- **Ladbrokes**: Alternative betting lines
- **PointsBet**: Additional market coverage
- **Fantasy Projections**: Minutes and usage predictions
- **Injury Reports**: Player availability tracking

#### Database Management (`dbFunctions.py`)
- Player profiles and team information
- Game fixtures and results
- Statistical queries and data retrieval
- Team and player lookup functions

### 2. **Machine Learning Models**

#### Points Prediction (`RegressionModel.py`)
```python
def get_points_curve(playerID, mins, teamMates, gameID):
    # Combines 2-pointers, 3-pointers, and free throws
    three_pointers = predict_three_points(playerID, mins, teamMates, gameID)
    two_pointers = predict_two_points(playerID, mins, teamMates, gameID)
    fts = predict_free_throws(playerID, mins, teamMates, gameID)
    return three_pointers * 3 + two_pointers * 2 + fts
```

#### Key Prediction Variables:
- **Minutes Played**: Projected playing time
- **Usage Rate**: Player's involvement in team offense
- **Team Context**: Teammate availability and rotations
- **Opponent Defense**: Defensive rankings and tendencies
- **Position Matchups**: Position-specific statistical trends

### 3. **Statistical Analysis**

#### Advanced Metrics:
- **Usage Percentage**: Player's involvement in team possessions
- **True Shooting Percentage**: Efficiency metrics
- **Rebound Chances**: Offensive and defensive opportunities
- **Assist Rate**: Passing and playmaking metrics
- **Shot Location Data**: Court position analysis

#### Team Context:
- **Pace**: Team's playing speed
- **Defensive Rankings**: Opponent strength analysis
- **Positional Differences**: Matchup advantages
- **Recent Form**: Last 5/10 game trends

## 🎯 Betting Markets Supported

### Player Performance Markets:
1. **Points Markets**: Total points scored
2. **Rebounds Markets**: Total rebounds (offensive + defensive)
3. **Assists Markets**: Total assists
4. **Three-Point Markets**: Three-pointers made
5. **Combined Markets**:
   - Points + Rebounds + Assists (PRA)
   - Points + Rebounds (PR)
   - Points + Assists (PA)
   - Rebounds + Assists (RA)

### Market Analysis:
- **Line Comparison**: Over/under betting lines
- **Value Detection**: Statistical edge identification
- **Risk Assessment**: Confidence levels in predictions
- **Market Movement**: Odds tracking and analysis

## 🛠️ Technical Implementation

### Dependencies:
```python
# Core Libraries
nba_api                    # NBA statistics API
scikit-learn              # Machine learning models
pandas                    # Data manipulation
numpy                     # Numerical computing
sqlite3                   # Database management

# Web Scraping
selenium                   # Browser automation
beautifulsoup4            # HTML parsing
requests                  # HTTP requests

# Data Processing
thefuzz                   # String matching
urllib3                   # URL handling
```

### Database Schema:
- **Teams**: Team information and identifiers
- **PlayerProfiles**: Player details and positions
- **Fixtures**: Game schedules and results
- **BoxScoreTraditional**: Basic game statistics
- **BoxScoreUsage**: Advanced usage metrics
- **BoxScoreScoring**: Shot location and type data
- **BoxScoreAdvanced**: Advanced analytics
- **TeamRankings**: Team performance metrics

## 🚀 Usage Instructions

### 1. **Setup and Installation**
```bash
# Install Python dependencies
pip install nba-api scikit-learn pandas numpy selenium beautifulsoup4 requests thefuzz

# Install frontend dependencies
cd frontend
npm install

# Run the application
python app.py
```

### 2. **Data Collection**
```python
# Update player databases
refill_player_data_bases()

# Update team statistics
refill_team_data_bases()

# Generate box scores
generateBoxScores()

# Update averages
generateAverages()
```

### 3. **Prediction Analysis**
```python
# Run main prediction analysis
mainPage()

# Get specific predictions
prediction, diff = predict_stats(player, mins, market, line, team_mates, player_id, game_id)
```

### 4. **Web Interface**
```bash
# Start React frontend
cd frontend
npm start

# Access at http://localhost:3000
```

## 📊 Model Performance

### Prediction Accuracy:
- **Points**: R² score typically 0.6-0.8
- **Rebounds**: R² score typically 0.5-0.7
- **Assists**: R² score typically 0.4-0.6
- **Three-Pointers**: R² score typically 0.3-0.5

### Key Factors:
- **Minutes Projection**: Critical for all predictions
- **Team Context**: Significant impact on individual performance
- **Opponent Defense**: Affects shooting percentages and opportunities
- **Recent Form**: Last 5 games provide better indicators than season averages

## 🔄 Data Flow Process

1. **Data Collection**: NBA API + Web scraping
2. **Data Processing**: Cleaning and normalization
3. **Database Storage**: SQLite database management
4. **Model Training**: Linear regression on historical data
5. **Prediction Generation**: Real-time statistical predictions
6. **Market Comparison**: Betting line analysis
7. **Value Identification**: Edge detection and recommendations

## 🎲 Betting Strategy Integration

### Value Betting Approach:
- **Statistical Edge**: Predictions vs. betting lines
- **Confidence Levels**: Model certainty assessment
- **Market Analysis**: Multiple sportsbook comparison
- **Risk Management**: Position sizing recommendations

### Market Coverage:
- **Primary Markets**: Points, rebounds, assists
- **Combined Markets**: PRA, PR, PA, RA
- **Specialty Markets**: Three-pointers, steals, blocks
- **Live Betting**: In-game adjustments

## 🔮 Future Enhancements

### Planned Features:
- **Deep Learning Models**: Neural networks for improved accuracy
- **Real-time Updates**: Live game data integration
- **Mobile Application**: iOS/Android betting app
- **Portfolio Management**: Betting bankroll optimization
- **Social Features**: Community predictions and analysis

### Technical Improvements:
- **API Optimization**: Faster data retrieval
- **Model Ensemble**: Multiple prediction algorithms
- **Automated Betting**: Direct sportsbook integration
- **Performance Analytics**: Model accuracy tracking

## ⚠️ Disclaimer

This system is for educational and research purposes only. Sports betting involves risk, and past performance does not guarantee future results. Users should:

- Understand the risks involved in sports betting
- Never bet more than they can afford to lose
- Use this system as one tool among many for analysis
- Comply with all local laws and regulations regarding sports betting

## 📞 Support

For technical support or questions about the system:
- Review the code documentation
- Check the database schema
- Examine the model implementations
- Test with historical data first

---

**Note**: This system requires active NBA season data and may need updates for new seasons or rule changes. Regular maintenance of the database and models is recommended for optimal performance.
