admin_cidr_blocks      = ["127.0.0.1/32"]
applications           = ["Hadoop"]
cluster_name           = "Climate Analysis Tool"
core_ebs_volume_iops   = null
core_ebs_volume_size   = 32
core_ebs_volume_type   = "gp2"
core_instance_count    = 2
core_instance_type     = "m4.large"
instance_profile_name  = "EMR_EC2_DefaultRole"
log_uri                = "s3://bucket/path/"
master_instance_count  = 1
master_instance_type   = "m4.large"
release_label          = "emr-5.29.0"
service_role_name      = "EMR_DefaultRole"
subnet_id              = "subnet-12345678"
termination_protection = false
