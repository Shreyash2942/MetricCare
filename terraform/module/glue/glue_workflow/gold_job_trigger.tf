resource "aws_glue_trigger" "glue_job_gold" {
  name = "${terraform.workspace}-gold_layer-mc-de-4-sp"
  type = "CONDITIONAL"
  workflow_name = aws_glue_workflow.glue_workflow.name
  start_on_creation = false   # prevents automatic run

  dynamic "actions" {
    for_each = var.gold_job
    content {
      job_name = "${terraform.workspace}-${actions.value}"
    }
  }

  predicate {
    dynamic "conditions" {
      for_each = var.silver_job #after success of silver layer
      content {
        job_name="${terraform.workspace}-${conditions.value}"
        state="SUCCEEDED"
        logical_operator="EQUALS"

      }
    }
  }
}