variable "applications" {
  type        = list(string)
  description = "List of EMR applications to deploy to cluster"
}

variable "cluster_name" {
  type        = string
  description = "Human-readable name of cluster"
}

variable "core_ebs_volume_iops" {
  type        = number
  description = "EBS volume provisioned IOPS for core instance group (optional)"
}

variable "core_ebs_volume_size" {
  type        = number
  description = "EBS volume size in GB for core instance group"
}

variable "core_ebs_volume_type" {
  type        = string
  description = "EBS volume type for core instance group"
}

variable "core_instance_count" {
  type        = number
  description = "Number of instances in core instance group"
}

variable "core_instance_type" {
  type        = string
  description = "Instance type for core instance group"
}

variable "instance_profile_name" {
  type        = string
  description = "Name of EC2 instance profile for cluster nodes"
}

variable "key_name" {
  type        = string
  description = "EC2 key pair for cluster nodes, derived from KEYPAIR in common.mk"
}

variable "log_uri" {
  type        = string
  description = "S3 path to write logs to, or null"
}

variable "master_instance_count" {
  type        = number
  description = "Number of instances in master instance group"
}

variable "master_instance_type" {
  type        = string
  description = "Instance type for master instance group"
}

variable "region" {
  type        = string
  description = "AWS region to deploy into, set as REGION in common.mk"
}

variable "release_label" {
  type        = string
  description = "EMR release to deploy"
}

variable "service_role_name" {
  type        = string
  description = "Name of service-linked IAM role created for EMR"
}

variable "subnet_id" {
  type        = string
  description = "Subnet to deploy cluster nodes into"
}

variable "termination_protection" {
  type        = bool
  description = "Protect cluster from accidental termination"
}
