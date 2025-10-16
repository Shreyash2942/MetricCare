output "database_name" {
  value = aws_glue_catalog_database.this.name                                         # The actual value to be outputted
  description = "Glue catalog database name" # Description of what this output represents
}