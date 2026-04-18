# MLOps Project: DVC + GitHub Actions + CML Complete Guide

## **Project Overview**

This is a **complete MLOps pipeline** that automates machine learning model training, evaluation, and reporting. Every time you create a pull request, the pipeline:

- Downloads raw data
- Preprocesses it
- Trains a machine learning model
- Evaluates performance
- Posts results as PR comments
- All automated with zero manual steps

**What makes this special:** True reproducibility + automation + collaboration

---

## **Core Technologies**

### **1. DVC (Data Version Control)**

**What it does:** Tracks data and models like Git tracks code

```
├─ Versioning data without storing in Git (too large)
├─ Defining reproducible pipelines (dvc.yaml)
├─ Tracking dependencies and outputs
├─ Creating dvc.lock for exact reproducibility
└─ Caching to avoid re-running unchanged stages
```

**Key concepts:**

- `dvc.yaml` → Pipeline definition (which stages, in what order)
- `dvc.lock` → Reproducibility record (exact checksums of everything)
- `deps` → Dependencies (inputs to a stage)
- `outs` → Outputs (results from a stage)
- `metrics` → Performance metrics (not cached, always fresh)
- `plots` → Visualizations (confusion matrices, etc.)

### **2. Git LFS (Large File Storage)**

**What it does:** Stores large files (data, models) outside Git

```
├─ Raw CSV data lives in Git LFS
├─ Git tracks pointer files only (small)
├─ Actual data stored on GitHub's LFS servers
└─ GitHub Actions downloads real files automatically
```

**Why needed:** Git has a limit (~100MB per file), data files are larger

### **3. GitHub Actions**

**What it does:** Runs code automatically on GitHub servers

```
Trigger: Pull Request → Runner spins up → Runs workflow → Reports results
```

**In this project:**

- Triggered on every PR to main branch
- Runs on ubuntu-latest (free GitHub server)
- Executes pipeline steps sequentially
- Posts results back to PR as comments

### **4. CML (Continuous Machine Learning)**

**What it does:** Bridges ML output to GitHub

```
├─ Reads metrics.json (model performance)
├─ Reads confusion_matrix.png (visualization)
├─ Creates markdown report
└─ Posts as PR comment for team review
```

---

## **Project Structure**

```
CML_DVC_Learning/
├─ .github/
│  └─ workflows/
│     └─ train_cml.yaml          ← GitHub Actions workflow (the automation)
│
├─ .dvc/
│  ├─ config                     ← DVC settings (remote storage info)
│  └─ cache/                     ← Local DVC cache
│
├─ src/
│  ├─ raw_data/
│  │  └─ weather.csv            ← Raw data (Git LFS tracked)
│  ├─ processed_data/
│  │  └─ weather.csv            ← Output from preprocess stage
│  └─ models/
│     └─ model.pkl              ← Trained model
│
├─ dvc.yaml                      ← Pipeline definition (2 stages)
├─ dvc.lock                      ← Reproducibility record (auto-generated)
├─ .gitignore                    ← Ignores large files, cache, etc.
├─ .gitattributes                ← Git LFS configuration
├─ requirements.txt              ← Python dependencies
├─ metrics.json                  ← Model metrics (generated)
├─ confusion_matrix.png          ← Confusion matrix plot (generated)
│
├─ preprocess_dataset.py         ← Data preprocessing
├─ train.py                      ← Model training
├─ model.py                      ← Model definition & evaluation
├─ metrics_and_plots.py          ← Metrics and visualization
├─ utils_and_constants.py        ← Constants and utilities
└─ README.md                     ← Project documentation
```

---

## **How It Works: Complete Flow**

### **Step 1: Developer Creates PR**

```
You create feature-branch locally
├─ Make code changes
├─ git add . && git commit && git push
└─ Create PR on GitHub
```

### **Step 2: GitHub Actions Triggered**

```
PR created → GitHub detects: pull_request event on main
└─ Automatically spins up ubuntu-latest runner
```

### **Step 3: Checkout Code & Data**

```
Runner executes:
├─ git checkout (gets code)
└─ Git LFS downloads (gets actual weather.csv from GitHub LFS)
```

### **Step 4: Environment Setup**

```
├─ Install Python 3.12
├─ pip install -r requirements.txt
│  └─ pandas, scikit-learn, dvc, matplotlib, seaborn
└─ Setup CML (for reporting)
```

### **Step 5: DVC Pipeline Runs**

```
dvc repro executes:

Stage 1: Preprocess
├─ Reads: src/raw_data/weather.csv
├─ Runs: python preprocess_dataset.py
│  ├─ Drops unnecessary columns
│  ├─ Encodes target (Yes/No → 1/0)
│  ├─ Target encodes categorical features
│  └─ Imputes missing values & scales data
├─ Outputs: src/processed_data/weather.csv
└─ DVC tracks dependencies → if unchanged, skips next time

Stage 2: Train
├─ Reads: src/processed_data/weather.csv
├─ Runs: python train.py
│  ├─ Splits: 80/20 train/test
│  ├─ Trains: RandomForestClassifier
│  ├─ Evaluates: accuracy, precision, recall, f1
│  └─ Generates: confusion_matrix.png
├─ Outputs:
│  ├─ metrics.json (performance)
│  ├─ confusion_matrix.png (visualization)
│  └─ src/models/model.pkl (model artifact)
└─ dvc.lock updated with checksums
```

### **Step 6: CML Report Generated**

```
├─ Reads metrics.json
├─ Reads confusion_matrix.png
├─ Creates model_eval_report.md with:
│  ├─ Accuracy: 0.947
│  ├─ Precision: 0.988
│  ├─ Recall: 0.7702
│  ├─ F1-Score: 0.8656
│  └─ [confusion_matrix.png visualization]
└─ Posts to PR as comment ✅
```

### **Step 7: Review & Merge**

```
Team sees:
├─ Code changes
├─ Model metrics in comment
├─ Performance visualization
└─ Decides: "Good metrics, let's merge!"
```

---

## **Key Files Explained**

### **dvc.yaml - The Pipeline Blueprint**

```yaml
stages:
  preprocess:
    cmd: python preprocess_dataset.py
    deps:
      - src/raw_data/weather.csv # Input data
      - preprocess_dataset.py # Script itself
    # No outs: - intermediate file, regenerated fresh each time

  train:
    cmd: python train.py
    deps:
      - src/processed_data/weather.csv # Uses preprocess output
      - train.py
      - model.py
      - utils_and_constants.py
    metrics:
      - metrics.json:
          cache: false # Always regenerated (performance changes)
    plots:
      - confusion_matrix.png:
          cache: false # Always regenerated
    # Note: model.pkl removed from outs (no remote storage)
```

**How DVC uses this:**

1. Read dvc.yaml
2. Check dvc.lock for checksums
3. Compare current checksums with dvc.lock
4. If different → run stage
5. If same → skip (cached)
6. Update dvc.lock with new checksums

### **dvc.lock - The Reproducibility Record**

```yaml
schema: "2.0"
stages:
  preprocess:
    cmd: python preprocess_dataset.py
    deps:
      - path: src/raw_data/weather.csv
        md5: e602b116f50269aa781c0c910cd80db9  ← Exact file hash
        size: 2701130
    outs:
      - path: src/processed_data/weather.csv
        md5: 008e962e77cca08fa800d221609ba147
        size: 10625724
```

**Why important:**

- Records exact checksums
- Next person gets same dvc.lock → same results
- Guarantees reproducibility
- Shows what changed between runs

### **.github/workflows/train_cml.yaml - The Automation**

```yaml
name: model-training
on:
  pull_request:
    branches: main
permissions:
  pull-requests: write # Can post PR comments
  contents: write # Can push commits

jobs:
  train_and_report_eval_performance:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          lfs: true # Get actual files from Git LFS

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.12

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Setup CML
        uses: iterative/setup-cml@v1

      - name: Pull DVC Data
        run: dvc pull --force

      - name: Run DVC Pipeline
        run: dvc repro

      - name: Write CML Report
        env:
          REPO_TOKEN: ${{secrets.GITHUB_TOKEN}}
        run: |
          cat metrics.json >> model_eval_report.md
          echo "![confusion matrix plot](./confusion_matrix.png)" >> model_eval_report.md
          cml comment create model_eval_report.md
```

### **requirements.txt - Dependencies**

```
pandas>=2.0.0           # Data manipulation
scikit-learn>=1.3.0     # ML models & metrics
dvc>=3.0.0              # Data version control
matplotlib>=3.7.0       # Plotting
seaborn>=0.12.0         # Enhanced plotting
```

### **Python Scripts**

#### **preprocess_dataset.py**

```
Transforms raw data → clean, ready for ML
├─ read_dataset()
│  ├─ Drops unnecessary columns
│  └─ Encodes target values (Yes/No → 1/0)
├─ target_encode_categorical_features()
│  └─ Converts categories to their mean target value
├─ impute_and_scale_data()
│  ├─ Fills missing values with mean
│  └─ Scales to normal distribution
└─ main()
   └─ Orchestrates everything
```

#### **train.py**

```
Trains model and evaluates
├─ Loads processed data
├─ Splits: 80% train, 20% test
├─ Trains: RandomForestClassifier
├─ Evaluates: metrics (accuracy, precision, recall, f1)
├─ Saves: metrics.json & confusion_matrix.png
└─ Saves: model.pkl
```

#### **model.py**

```
Machine learning components
├─ train_model()
│  └─ Creates & trains RandomForestClassifier
├─ evaluate_model()
│  └─ Calculates accuracy, precision, recall, f1
└─ save_model()
   └─ Pickles model to disk
```

#### **metrics_and_plots.py**

```
Visualization & metrics storage
├─ save_metrics()
│  └─ Writes metrics.json
└─ plot_confusion_matrix()
   └─ Creates confusion_matrix.png
```

---

## **Key Concepts**

### **What is Reproducibility?**

```
Same Input + Same Code → Same Output (Always!)

In your project:
├─ Same weather.csv (tracked by Git LFS)
├─ Same preprocess_dataset.py
├─ Same train.py
└─ → ALWAYS get accuracy: 0.947

Why DVC helps:
├─ dvc.lock records exact data checksums
├─ Next person runs: dvc repro
├─ DVC compares checksums
├─ If unchanged → uses cached results (fast!)
└─ If changed → reruns (fresh!)
```

### **What is Caching?**

```
Day 1: Run full pipeline
├─ Preprocess: 30 seconds
├─ Train: 2 minutes
└─ Total: 2.5 minutes

Day 2: Only train.py changed, raw data unchanged
├─ Preprocess: SKIPPED (cached, 0 seconds)
├─ Train: 2 minutes (must rerun, code changed)
└─ Total: 2 minutes (saves 30 seconds!)

How DVC knows:
├─ Checks MD5 of weather.csv
├─ Matches dvc.lock → no change
├─ Skips preprocess automatically
└─ Smart caching!
```

### **What is Data Versioning?**

```
Problem: How do you version 2GB weather.csv?
└─ Can't put in Git (too large)

Solution: Git LFS + DVC
├─ Git LFS: Stores actual files on GitHub
├─ Git: Tracks small pointer files
├─ DVC: Knows which data version with which code
└─ Result: Full version history!

Scenario:
├─ Version 1: 100k rows (accuracy 0.94)
├─ Version 2: 200k rows (accuracy 0.95)
├─ Version 3: 300k rows (accuracy 0.96)
└─ Can switch between versions: git checkout v2
```

### **What is CI/CD (GitHub Actions)?**

```
Traditional: Developer trains locally
├─ "Works on my machine"
├─ Different Python versions
├─ Different OS
├─ Results not reproducible

CI/CD (Continuous Integration/Deployment):
├─ Standardized environment
├─ Automated testing
├─ Everyone gets same results
├─ No "works on my machine" problems
└─ Trust the pipeline!
```

---

## **Common Workflow Tasks**

### **1. Make Code Changes & Create PR**

```bash
# Create feature branch
git checkout -b feature/improve-model

# Make changes to train.py or preprocess_dataset.py
# Edit code...

# Commit
git add .
git commit -m "Improve preprocessing: add new feature engineering"

# Push
git push origin feature/improve-model

# Create PR on GitHub
# → GitHub Actions automatically runs!
# → See metrics in PR comment
# → Decide if improvement is good
```

### **2. Update Data (Add More Training Data)**

```bash
# Update src/raw_data/weather.csv
# (Weather data with more rows)

# DVC will detect change
git add src/raw_data/weather.csv
git commit -m "Add more weather data - 100k new rows"

git push origin feature/more-data

# Create PR
# → Pipeline reruns with new data
# → See new metrics
# → If better, merge!
```

### **3. Run Pipeline Locally**

```bash
# Full pipeline
dvc repro

# Or specific stage
dvc repro train

# Force rerun (ignore cache)
dvc repro --force
```

### **4. Check What Changed**

```bash
# See metrics comparison
cat metrics.json

# See which stages changed
dvc status

# Visualize pipeline
dvc dag
```

---

## **Why This Project is Important**

### **Before (Traditional ML)**

```
Day 1: Train model (2 hours)
├─ "Works on my machine"
├─ Uses Python 3.9 + numpy 1.20
└─ Saves model

Day 30: Teammate runs code
├─ Gets error (different Python version)
├─ Model results differ (different numpy)
├─ "Why isn't this reproducible?!"
└─ Hours lost debugging
```

### **After (MLOps with DVC + GitHub Actions)**

```
Day 1: Commit code → GitHub Actions runs
├─ Trains in standardized environment
├─ Posts metrics to PR
├─ Reviewers approve
└─ Merge with confidence

Day 30: Teammate pulls code
├─ Runs: dvc repro
├─ Gets EXACT same results
├─ No issues, perfect reproducibility!
└─ Can spend time improving model, not debugging
```

---

## **What You've Learned**

```
✅ Data Version Control (DVC)
   └─ Versioning data & models like Git

✅ Pipeline Management
   └─ Reproducible, dependency-aware pipelines

✅ GitHub Actions
   └─ Automated testing & deployment

✅ CML Integration
   └─ ML metrics reporting to GitHub

✅ ML Best Practices
   └─ Reproducibility, automation, collaboration

✅ End-to-End MLOps
   └─ Real-world ML workflow
```

---

## **Future Improvements**

### **1. Add Remote Storage**

```
Replace Git LFS with:
├─ AWS S3
├─ Google Drive
└─ Azure Blob Storage

Benefits:
├─ Share data with team
├─ Reduce Git repo size
├─ Better for large teams
```

### **2. Track Model Versions**

```
Use DVC Model Registry:
├─ Production model v1.0
├─ Staging model v2.0
└─ Experiment model v3.0

Promote best models to production
```

### **3. Add More Metrics**

```
Beyond accuracy:
├─ ROC-AUC
├─ Precision-Recall curves
├─ Class-wise metrics
└─ Feature importance plots
```

### **4. Hyperparameter Tuning**

```
Try different models:
├─ Logistic Regression
├─ Gradient Boosting
├─ Neural Networks

Compare results in PR comments
```

### **5. Deploy Model**

```
After PR merge:
├─ Build Docker container
├─ Push to cloud (AWS, GCP, Azure)
├─ Deploy as API
└─ Monitor in production
```

---

## **Troubleshooting**

### **"dvc pull" fails**

- Check remote is configured: `dvc remote list`
- Or data is in Git LFS: `git lfs ls-files`

### **Workflow fails - Git error**

- Check permissions in workflow: `permissions: pull-requests: write`
- Use correct push syntax: `git push origin HEAD:${{ github.head_ref }}`

### **Metrics not showing in PR**

- Check CML step has `REPO_TOKEN` secret
- Verify `cml comment create model_eval_report.md` runs

### **Pipeline seems to hang**

- Check if installing large packages
- View runner logs on GitHub Actions page
- May need more time for large datasets

---

## **Key Takeaways**

```
1. DVC = Data Version Control
   └─ Track data & models like Git

2. GitHub Actions = Automation
   └─ Run pipeline on every PR

3. CML = Results Reporting
   └─ Show metrics in PR comments

4. Reproducibility = Trust
   └─ Same code + data = same results

5. Collaboration = Efficiency
   └─ Team reviews before merging
```

---

## **Resources**

- **DVC Docs:** https://dvc.org/doc
- **GitHub Actions:** https://docs.github.com/en/actions
- **CML Docs:** https://cml.dev/doc
- **This Project:** Your local repo (fully documented!)

---

## **Questions? Start Here:**

1. **"What is DVC?"** → See "Core Technologies" section
2. **"How does the pipeline run?"** → See "How It Works: Complete Flow"
3. **"What files do I need to edit?"** → See "Key Files Explained"
4. **"How do I make changes?"** → See "Common Workflow Tasks"
5. **"What comes next?"** → See "Future Improvements"

---

**Last Updated:** April 18, 2026
**Status:** ✅ Full MLOps Pipeline Working
**Next Step:** Merge PR and celebrate! 🎉
