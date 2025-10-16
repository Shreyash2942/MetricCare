variable "database_name" {
  type = string                     # The type of the variable, in this case a string
  description = "The name of the database creating in glue catalog" # Description of what this variable represents
}

variable "description_database" {
  type = string
  description = "Description of database"
  default = "Glue catalog database for hudi table"
}

variable "database_location" {
  type = string
  description = "Database location that need to be store"
}
