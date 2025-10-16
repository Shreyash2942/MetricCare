resource "aws_glue_trigger" "glue_job_bronze" {
  name = "${terraform.workspace}-bronze_layer-mc-de-4-sp"
  type = "ON_DEMAND"
  workflow_name = aws_glue_workflow.glue_workflow.name
  start_on_creation = false   # prevents automatic run


  dynamic "actions" {
    for_each = var.bronze_job
    content {
      job_name = "${terraform.workspace}-${actions.value}"
    }
  }
}