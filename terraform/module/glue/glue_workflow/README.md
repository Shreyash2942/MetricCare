# 🔄 AWS Glue Workflow Module

This module provisions an **AWS Glue Workflow** and associated **triggers** to orchestrate ETL job execution across the MetricCare Lakehouse (Bronze → Silver → Gold).  
It ensures that Glue jobs run in a defined sequence and that downstream jobs only start once their dependencies complete successfully.

---

## 📖 Overview

| Component | Purpose |
|------------|----------|
| **Glue Workflow** | Central orchestration unit that chains ETL jobs together. |
| **Glue Triggers** | Manage execution dependencies between Bronze, Silver, and Gold jobs. |
| **IAM Role** | Grants permissions to start workflows and manage job runs. |

---

## 🧩 Use Case in MetricCare Architecture

```
┌──────────────┐     Workflow Start     ┌──────────────┐     Processed Data     ┌──────────────┐
│  Lambda / EB │ ────────────────────► │  Glue Workflow│ ────────────────────► │  Glue Catalog│
└──────────────┘                       └──────────────┘                       └──────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    ▼                        ▼                        ▼
              Bronze Job                Silver Job                 Gold Job
```

- **Lambda / EventBridge → Workflow:** Triggers the Glue workflow execution.  
- **Workflow → Jobs:** Runs Bronze → Silver → Gold jobs in dependency order.  
- **Catalog → Athena:** Makes processed data queryable for analytics.

---

## 🗂️ Module Structure

```bash
glue_workflow/
├── main.tf                   # Defines Glue Workflow, triggers, and dependencies
├── bronze_job_trigger.tf      # Trigger linking Bronze job to workflow
├── silver_job_trigger.tf      # Trigger linking Silver job after Bronze success
├── gold_job_trigger.tf        # Trigger linking Gold job after Silver success
├── variables.tf               # Input variables for workflow and job names
└── outputs.tf                 # Exports workflow name, ARN, and trigger ARNs
```

---

## ⚙️ Example Usage

Example configuration for orchestrating your ETL workflow:

```hcl
module "glue_workflow" {
  source = "./module/glue/glue_workflow"

  workflow_name = "metriccare_etl_workflow"
  description   = "MetricCare ETL workflow chaining Bronze → Silver → Gold jobs"

  jobs = {
    bronze = module.glue_job.glue_job_names[0]
    silver = module.glue_job.glue_job_names[1]
    gold   = module.glue_job.glue_job_names[2]
  }

  tags = {
    Environment = terraform.workspace
    Project     = "MetricCare"
  }
}
```

> ⚡ The module automatically links Glue jobs using triggers to ensure sequential execution.

---

## 🔑 Key Variables

| Variable | Description | Type | Default |
|-----------|--------------|------|----------|
| `workflow_name` | Name of the Glue Workflow. | `string` | `"metriccare_etl_workflow"` |
| `description` | Description for the workflow. | `string` | `null` |
| `jobs` | Map of Glue job names (bronze, silver, gold). | `map(string)` | `{}` |
| `tags` | Tags applied to all resources. | `map(string)` | `{}` |

---

## 📤 Outputs

| Output | Description |
|---------|--------------|
| `workflow_name` | Name of the created Glue Workflow. |
| `workflow_arn` | ARN of the Glue Workflow. |
| `trigger_arns` | List of trigger ARNs for all dependent jobs. |

---

## 🧠 Best Practices

- Maintain **clear job dependency order** (Bronze → Silver → Gold).  
- Enable **on-failure alerts via SNS** for workflow failures.  
- Keep job run times staggered to reduce cluster contention.  
- Tag each workflow by project and environment for cost visibility.  
- Use **workflow run metrics** in CloudWatch for monitoring and dashboards.  

---

## 🧩 Testing the Module

Run this module independently to validate workflow setup:

```bash
terraform init
terraform apply -target=module.glue_workflow -auto-approve
```

To manually start the workflow:
```bash
aws glue start-workflow-run --name metriccare_etl_workflow
```

Verification steps:
1. Go to **AWS Glue Console → Workflows**.  
2. Confirm job dependencies (Bronze → Silver → Gold).  
3. Check **Run History** and ensure sequential execution order.  

---

## 🔗 References

- [Terraform AWS Glue Workflow Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_workflow)  
- [Terraform AWS Glue Trigger Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_trigger)  
- [AWS Glue Workflows Documentation](https://docs.aws.amazon.com/glue/latest/dg/orchestrate-workflow.html)  
- [AWS CLI – Start Workflow Run](https://docs.aws.amazon.com/cli/latest/reference/glue/start-workflow-run.html)  
- [AWS Glue Triggers](https://docs.aws.amazon.com/glue/latest/dg/trigger-job.html)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Module: glue_workflow – ETL Orchestration for Bronze, Silver, and Gold Layers*
