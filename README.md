# Git Branching Workflow Guide

This repository follows a **branch-based workflow** to ensure clean collaboration, avoid code conflicts, and maintain a stable `main` branch. This guide explains how to properly create your own branch and push code safely.

---

## Step-by-Step: Work on Your Own Branch

Follow these steps to create a branch, make changes, and push without affecting the main branch.

### 1. Clone the Repository

If you haven't already cloned the repo:

```bash
git clone git@github.com:metric-care/mc-de-4.git
cd mc-de-4
```

### 2. Create a New Branch
Follow this naming convention for the branch name ```<name>-takeo```

```bash
git checkout -b <your-branch-name>
```

### 3. Make Changes
Make your edits, add features, or fix bugs in your local branch.

4. Stage Your Changes
```bash
git add .
```
Or stage specific files:

```bash
git add path/to/your/file
```

### 5. Commit Your Changes
```bash
git commit -m "Add a clear and concise commit message"
```

### 6. Push to Your Branch
```bash
git push origin <your-branch-name>
```

## 🚫 DO NOT PUSH DIRECTLY TO main
❗ Never push code directly to the main branch.

#### Pushing directly to main can cause:

- Merge conflicts
- Broken builds
- Loss of work by other contributors
- Instead, always work in your own branch and use a Pull Request to merge.

## 🔄 Keep Your Branch Updated
To make sure your branch stays up to date with the latest main changes:

```bash
git fetch origin
git rebase origin/main
```

## 📁 File structure
we are using following file structure
```bazaar
metriccare-project/
├── README.md {write project desctiption}
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci-cd.yml             # GitHub Actions workflow(s) We will come back to this later
├── terraform/
│   ├── modules/
│   └── environments/
│       ├── dev/
│       ├── staging/
│       └── prod/
│   └── main.tf                   # Main infra definition
│   └── variables.tf
│   └── outputs.tf
├── ingestion/  #{this is the folder you can use for ingestion python scripts that you run locally}
│   ├── scripts/  #{inside this folder lets create seperate folder for each FHIR resource we will be working on i.e. patient, encounter, condition etc.}
│   │   └── patient/patient_ingest_source_a.py
|   |   └── encounter/ingest_source_a.py
|   |   └── condition/ingest_source_a.py
│   └── config/          #use this folder for any utility modules (if any)
│       └── source_a_config.json
├── glue_jobs/
│   ├── bronze/          #{inside this folder lets create seperate folder for each FHIR resource we will be working on i.e. patient, encounter, condition etc.}
│   │   └── patient/job_bronze_source_a.py
│   │   └── encounter/job_bronze_source_a.py
│   │   └── condition/job_bronze_source_a.py
│   ├── silver/           #folder and files structure same as bronze layer
│   │   └── job_silver_source_a.py
│   └── utils/             #unities modules if any
│       └── common_transforms.py
├── athena/
│   ├── gold/              #{same file and folder structure as bronze and silver but for sql files}
│   │   └── create_gold_table_a.sql
│   └── views/             #{we will use this folder for any intermediary views for final gold layer}
│       └── intermediate_view_a.sql
├── tests/                 #{if our timeline permits we will work on test cases for TDD from this folder.}
│   ├── ingestion/
│   │   └── test_ingest_source_a.py
│   ├── glue_jobs/
│   │   └── test_common_transforms.py
│   └── athena/
│       └── test_sql_validity.sql
└── config/ 
```

Resolve any conflicts that appear, then continue working or push updated changes.

🙋 Need Help?
If you get stuck or need assistance with Git, reach out to a team member or consult Git documentation.

Happy coding! 🎉`