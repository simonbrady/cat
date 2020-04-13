output "cluster_id" {
  value = aws_emr_cluster.cat.id
}

output "cluster_public_dns" {
  value = aws_emr_cluster.cat.master_public_dns
}
