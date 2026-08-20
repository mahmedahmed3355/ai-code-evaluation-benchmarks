output "namespace_name" {
  description = "Name of the isolated benchmark namespace."
  value       = kubernetes_namespace_v1.benchmark.metadata[0].name
}
