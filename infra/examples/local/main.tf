module "benchmark_namespace" {
  source = "../../modules/benchmark-namespace"

  namespace_name = "benchmark-local"

  labels = {
    "benchmark.ai/environment" = "local"
    "benchmark.ai/purpose"     = "evaluation"
  }
}

output "namespace_name" {
  value = module.benchmark_namespace.namespace_name
}
