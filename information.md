# FHIRPulse Lakehouse Overview

FHIRPulse Lakehouse is an AWS-native data platform that automates the ingestion, curation, and analytics of synthetic FHIR healthcare data. Terraform provisions every layer—from storage to orchestration—so environments stay reproducible and easy to showcase.

---

## Platform Highlights
- **Infrastructure as Code**: Terraform builds S3 buckets, Glue catalog objects, Glue jobs, DynamoDB metadata tables, Lambda triggers, SNS topics, and EventBridge rules in a single apply.
- **Config-Driven Workflows**: Environment JSON files (for example `config/dev/dev_config.json`) define input paths, table names, and logging locations, letting you promote changes without code edits.
- **FHIR Data Simulation**: Python generators under `ingestion/script` mint realistic patient, encounter, and condition resources using `fhir.resources` + Faker, then push them to S3.
- **Layered Lakehouse**: Bronze, Silver, and Gold Glue jobs transform raw JSON into Apache Hudi tables with audit logs. Gold jobs publish KPIs such as infection, mortality, and readmission rates.
- **Insight Ready**: Athena SQL scripts (`Athena/gold_table`) query curated datasets so BI tools can visualize trends immediately after the Glue workflow finishes.

---

## Data Flow Summary
1. **Synthetic Data Generation** – Run ingestion scripts locally to create FHIR bundles and upload them to the raw S3 prefix.
2. **Bronze Ingestion** – Glue bronze jobs hydrate raw JSON into schema-aware Hudi tables, logging file-level metadata to DynamoDB for idempotency.
3. **Silver Refinement** – Silver jobs standardize, cleanse, and enrich records, maintaining operational logs for observability.
4. **Gold Aggregation** – Gold jobs compute clinical KPIs and write results to curated locations consumed by Athena.
5. **Consumption** – Analysts run Athena SQL or dashboards (QuickSight, Tableau) against the gold datasets to monitor care metrics.

---

## Deployment Snapshot
```bash
cd terraform
terraform init
terraform workspace select dev || terraform workspace new dev
terraform apply -var-file="environments/dev.tfvars"
```
After provisioning, generate data via `ingestion/script/main_generate.py` and trigger the Glue workflow through Lambda or the AWS console.

---

## Monitoring & Reliability
- **SNS Subscribers** receive Glue failure alerts via email/SMS.
- **EventBridge Rules** watch Glue job state changes to fan out notifications.
- **CloudWatch Logs** capture structured metrics from Glue jobs and Lambda wrappers for troubleshooting.

---

## Portfolio Talking Points
- Demonstrates mastery of AWS Glue, Lambda, DynamoDB, S3, and Terraform.
- Highlights data engineering best practices: config-driven jobs, multi-layer architecture, and automated alerting.
- Provides end-to-end storytelling: from synthetic data creation to curated analytics ready for business stakeholders.

