locals {
  benchmark_labels = merge(
    {
      "app.kubernetes.io/managed-by" = "terraform"
      "app.kubernetes.io/component"  = "benchmark-execution"
      "benchmark.ai/isolation"       = "enabled"

      "pod-security.kubernetes.io/enforce"         = "restricted"
      "pod-security.kubernetes.io/audit"           = "restricted"
      "pod-security.kubernetes.io/warn"            = "restricted"
      "pod-security.kubernetes.io/enforce-version" = "latest"
    },
    var.labels,
  )
}

resource "kubernetes_namespace_v1" "benchmark" {
  metadata {
    name   = var.namespace_name
    labels = local.benchmark_labels
  }
}
