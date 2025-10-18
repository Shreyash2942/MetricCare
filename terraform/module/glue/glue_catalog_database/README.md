# 🗃️ AWS Glue Catalog Database Module

This module provisions one or more **AWS Glue Databases** that serve as the metadata layer for the **MetricCare Data Lakehouse**.  
Each database corresponds to a data layer (Bronze, Silver, or Gold) and stores the table definitions registered by Glue ETL jobs or Hudi upserts.

---

## 📖 Overview

| Component | Purpose |
|------------|----------|
| **Glue Database (Bronze)** | Stores raw, cleaned FHIR data registered from the ingestion layer. |
| **Glue Database (Silver)** | Contains curated, structured tables used for metric computation (Mortality, Infection, etc.). |
| **Glue Database (Gold)** | Stores aggregated and analytics-ready CMS metric tables for Power BI and Athena. |

---

## 🧩 Use Case in MetricCare Architecture

```
┌────────────┐        Transforms        ┌───────────────────────────┐
│   Glue Job │ ───────────────────────► │  Glue Catalog Database    │
└────────────┘                          └──────────────┬────────────┘
                                                      │
                                                      ▼
                                           Queried via Athena / Power BI
```

- **Glue → Database:** Registers output tables after each ETL job (Bronze → Silver → Gold).  
- **Athena → Database:** Reads from catalog to execute analytical queries.  
- **Power BI / Dashboard:** Visualizes CMS metrics stored in the Gold database.

---

## 🗂️ Module Structure

```bash
glue_catalog_database/
├── main.tf         # Creates Glue databases and manages naming conventions
├── variables.tf    # Input variables (database names, tags)
└── outputs.tf      # Exports database names and ARNs
```

---

## ⚙️ Example Usage

Example usage from your root `main.tf`:

```hcl
module "glue_catalog_database" {
  source = "./module/glue/glue_catalog_database"

  databases = {
    bronze = "metriccare_bronze_db"
    silver = "metriccare_silver_db"
    gold   = "metriccare_gold_db"
  }

  tags = {
    Environment = terraform.workspace
    Project     = "MetricCare"
  }
}
```

> 🧩 The `databases` map allows dynamic creation of multiple Glue databases.

---

## 🔑 Key Variables

| Variable | Description | Type | Default |
|-----------|--------------|------|----------|
| `databases` | Map of database names for different layers. | `map(string)` | `{}` |
| `catalog_id` | AWS account ID for the Glue Catalog. | `string` | `null` |
| `tags` | Key-value pairs of tags applied to each database. | `map(string)` | `{}` |

---

## 📤 Outputs

| Output | Description |
|---------|--------------|
| `database_names` | List of all created database names. |
| `database_arns` | ARNs for each Glue Database. |

---

## 🧠 Best Practices

- Use **environment-prefixed database names**, e.g. `dev_metriccare_bronze_db`.  
- Maintain **separate databases** for each data layer to enforce logical separation.  
- Register **only final tables** (Hudi-managed or partitioned tables).  
- Tag all databases with workspace and project identifiers.  
- Use **Athena** for validation queries to ensure metadata registration.

---

## 🧩 Testing the Module

Deploy and validate databases independently:

```bash
terraform init
terraform apply -target=module.glue_catalog_database -auto-approve
```

Verification steps:
1. Navigate to **AWS Glue Console → Databases**.  
2. Confirm the creation of Bronze, Silver, and Gold databases.  
3. Validate table registration by running a Glue ETL job or Athena query.

---

## 🔗 References

- [Terraform AWS Glue Catalog Database](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_catalog_database)  
- [AWS Glue Data Catalog Overview](https://docs.aws.amazon.com/glue/latest/dg/components-overview.html#data-catalog-overview)  
- [AWS Athena Integration](https://docs.aws.amazon.com/athena/latest/ug/glue-best-practices.html)  
- [AWS Glue Console – Databases](https://console.aws.amazon.com/glue/home#/databases)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Module: glue_catalog_database – Metadata Management for Data Lakehouse*
