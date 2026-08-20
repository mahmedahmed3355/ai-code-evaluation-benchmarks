variable "namespace_name" {
  description = "Namespace used to isolate benchmark task execution."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]([-a-z0-9]*[a-z0-9])?$", var.namespace_name))
    error_message = "namespace_name must be a valid DNS label."
  }
}

variable "labels" {
  description = "Additional labels applied to the benchmark namespace."
  type        = map(string)
  default     = {}
}
