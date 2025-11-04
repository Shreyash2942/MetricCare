# 🏥 MetricCare – AWS Healthcare Data Lakehouse

**MetricCare** is a SaaS-based, multi-tenant **real-time analytics platform** for **CMS (Centers for Medicare & Medicaid Services)** compliance and healthcare quality monitoring.  
It empowers hospitals to measure, benchmark, and improve clinical and operational performance through automated data pipelines and interactive dashboards.

---

## 📌 Project Purpose
MetricCare enables hospitals to track CMS compliance, improve patient satisfaction, and optimize performance.  
It supports data-driven decision-making with real-time KPIs and alerts — ensuring compliance readiness and reducing audit risks.

---

## 🎯 Objectives

- **Regulatory Compliance** – Real-time CMS metric tracking (Mortality, Infection, Readmission, ALOS).  
- **Patient Satisfaction Insights** – Integrate Press Ganey survey data for quality correlation.  
- **Operational Efficiency** – Forecast and monitor ER wait times, bed occupancy, and staff workload.  
- **Benchmarking & Reporting** – Compare hospital performance against national and regional averages.  
- **User-Centric Design** – Role-based dashboards for administrators, clinicians, and compliance officers.

---

## 📊 Core CMS Metrics

| Metric | Derived From | FHIR Resources Used | Description |
|--------|---------------|---------------------|--------------|
| **Mortality Rate** | Condition.code = “Death” | Patient, Encounter, Condition | Measures in-hospital deaths per 100 discharges. |
| **Readmission Rate (30-Day)** | Encounter.period | Patient, Encounter | Tracks patients readmitted within 30 days. |
| **Infection Rate (HAI)** | Condition.onsetDateTime > 48h post-admission | Condition, Encounter | Hospital-acquired infection rate. |
| **Average Length of Stay (ALOS)** | Encounter.period.start–end | Encounter | Average days per admission. |

> CMS metrics are simulated using **FHIR-standard Patient, Encounter, and Condition** resources enriched with **SNOMED-CT codes**.

---

## 🧬 Data Pipeline Overview

1. **Synthetic Data Generation (FHIR)**  
   - Python + Faker generate Patient, Encounter, and Condition JSONs.  
   - Aligned with HL7 FHIR R4 and SNOMED CT codes for realism.  

2. **Data Lakehouse (S3 + Glue + Hudi + Athena)**  
   - **S3 Bronze** – Raw FHIR JSONs  
   - **S3 Silver** – Cleaned and normalized Hudi tables  
   - **S3 Gold** – Aggregated CMS metrics  

3. **ETL Orchestration**  
   - AWS **Glue Jobs & Workflows** handle transformations (Bronze → Silver → Gold).  
   - **Lambda** triggers workflows on new S3 events.  
   - **DynamoDB** tracks processed files (idempotent ingestion).  

4. **Automation & Monitoring**  
   - **EventBridge** schedules workflows; **SNS** sends job alerts.  
   - **CloudWatch** provides logs and metrics for observability.  

5. **Analytics Layer**  
   - **Athena** validates metrics through SQL queries.  
   - **Power BI** visualizes CMS metrics by department, year, and demographic.  

---

## 🧱 Architecture Diagram

```
                ┌───────────────┐
                │  Synthetic FHIR│
                │  Data (Python) │
                └──────┬────────┘
                       │ Upload
                       ▼
              ┌──────────────────┐
              │  S3 Bronze Layer  │
              │  (Raw JSON)       │
              └──────┬───────────┘
                     │ Glue ETL
                     ▼
              ┌──────────────────┐
              │ S3 Silver Layer   │
              │ (Cleaned Hudi)    │
              └──────┬───────────┘
                     │ Aggregation
                     ▼
              ┌──────────────────┐
              │ S3 Gold Layer     │
              │ (CMS Metrics)     │
              └──────┬───────────┘
                     │ Athena SQL
                     ▼
              ┌──────────────────┐
              │ Power BI Dashboard│
              └──────────────────┘
```
---
## another Diagram
(https://github.com/Shreyash2942/MetricCare/blob/main/Documents/MetricCare_AWS_architectures.gif)
<iframe src="Documents/MetricCare.html" width="100%" height="600px"></iframe>
![Diagrame](https://github.com/Shreyash2942/MetricCare/blob/main/Documents/MetricCare.html)
![MetricCare_AWS_architectures](https://github.com/user-attachments/assets/bc41ba1b-774a-4c32-b719-64f9cf6e1c8f)



---

## ⚙️ Infrastructure Automation

- **Terraform** provisions all AWS components:  
  - S3, Glue, Lambda, EventBridge, SNS, DynamoDB  
- **GitHub Actions** automates CI/CD for infrastructure updates.  
- Uses **Terraform workspaces** for environment isolation (dev/prod).  

---

## 🔔 Monitoring & Notifications

- **EventBridge** schedules Glue workflows.  
- **SNS** notifies pipeline success/failure.  
- **DynamoDB** ensures incremental and consistent data ingestion.  

---

## 📈 Dashboard Insights

Power BI dashboard includes:
- Mortality, Infection, and Readmission Rates by hospital and year  
- Department-level Infection Rate donut chart  
- Readmission Rate by hospital bar chart  
- Mortality Rate trend line (yearly)  
- Overall CMS compliance summary

---

## 📜 Success Criteria

| Objective | Success Metric |
|------------|----------------|
| Compliance alerts | Trigger < 1 minute after threshold |
| Dashboard refresh | Every 15 minutes |
| Forecast accuracy | ≥ 80% for patient/staff prediction |
| Usability | ≥ 4/5 user rating |
| Report generation | < 3 seconds export time |

---

## 🧠 Key Learnings

- Designing **incremental ETL pipelines** using Glue Workflows and Hudi.  
- Managing schema evolution and governance via Glue Catalog.  
- Automating IaC with Terraform and GitHub Actions.  
- Creating **HIPAA-compliant** data flows and access controls.  

---

## 🧩 Technologies Used

| Category | Tools |
|-----------|-------|
| **Data Lake** | Amazon S3, Apache Hudi |
| **ETL / Orchestration** | AWS Glue, Lambda, EventBridge |
| **Storage / Governance** | Glue Catalog, DynamoDB, IAM |
| **Analytics** | Athena, Power BI |
| **IaC & DevOps** | Terraform, GitHub Actions |
| **Data Simulation** | Python, Faker, FHIR, SNOMED |

---

## 📚 References

- CMS Quality Reporting: [https://www.cms.gov/](https://www.cms.gov/)  
- FHIR Standard: [https://hl7.org/fhir/](https://hl7.org/fhir/)  
- SNOMED CT: [https://www.snomed.org/](https://www.snomed.org/)  
- AWS Glue: [https://aws.amazon.com/glue/](https://aws.amazon.com/glue/)  
- Terraform: [https://developer.hashicorp.com/terraform](https://developer.hashicorp.com/terraform)

---

> 🧱 **Author:** Shreyash Patel  
> 💼 *AWS Data Engineer | Healthcare Analytics | IaC Automation*  
> 🔗 *Project: MetricCare – Real-Time CMS Compliance Platform*
