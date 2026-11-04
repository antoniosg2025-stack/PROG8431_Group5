# PROG8431 – Problem Analysis Workshop B
## K-Means Clustering: Ontario Property Dataset · Group 5

| Team member | Student ID |
|:--|--:|
| Asangika Hettiarachchi | 7461502 |
| Juan Antonio Sainz Galvez | 9072844 |
| Ved Vishal Patel | 9111628 |

## Goal
Use K-Means clustering to let the data define Ontario housing market segments, based on **price** and **distance to downtown Toronto**, as part of our term project comparing Kitchener-Waterloo / Cambridge with the Toronto area.

## Data
- **Source:** [Ontario Residential Property Data – Kaggle](https://www.kaggle.com/datasets/mnabaee/ontarioproperties)
- **File:** `data/properties.csv` (25,351 listings: address, area name, price, latitude, longitude)
- **Cleaning:** removed missing coordinates (-999), coordinates outside Ontario, and prices under $10,000. 24,254 listings remain.

## Method
1. Inspect and clean the data
2. Choose two clustering variables: `Price ($)` and `Distance to Toronto (km)` (haversine distance from lat/lng)
3. Standardize both variables with z-scores
4. Run K-Means for K = 2–10 and choose K with the elbow method and the silhouette score
5. Final model with K = 3: sizes, centroids, within-cluster sum of squares, charts and cluster summary
6. Cluster names and insights

## Project structure
```
ProblemAnalysisWorkshopB/
├── Workshop_B_Property_Clustering.ipynb   # main notebook (also used for the presentation)
├── data/properties.csv                    # dataset
├── requirements.txt                       # pinned Python packages
└── README.md
```

## How to run (Windows, VS Code)
```powershell
cd ProblemAnalysisWorkshopB
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Open `Workshop_B_Property_Clustering.ipynb` in VS Code, select the `.venv` kernel and choose **Run All**.

## Contributions
| Member | Work |
|:--|:--|
| Asangika Hettiarachchi | Initial notebook: data loading, inspection, standardization, elbow method, final model, centroids, visualization and cluster summary |
| Juan Antonio Sainz Galvez | Data cleaning rules, two-variable design (price + distance to Toronto), standardization reasoning, silhouette score and K justification, term-project explanation, team table fix, README, UTF-8 requirements |
| Ved Vishal Patel | Descriptive cluster names and insights summary |
