resource "aws_security_group" "master" {
  name   = "EMR master SSH"
  vpc_id = data.aws_subnet.master.vpc_id

  ingress {
    description = "SSH to master"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.admin_cidr_blocks
  }
}

resource "aws_emr_cluster" "cat" {
  name                   = var.cluster_name
  release_label          = var.release_label
  service_role           = var.service_role_name
  log_uri                = var.log_uri
  applications           = var.applications
  termination_protection = var.termination_protection
  tags = {
    Name = var.cluster_name
  }

  master_instance_group {
    instance_type  = var.master_instance_type
    instance_count = var.master_instance_count
  }

  core_instance_group {
    instance_type  = var.core_instance_type
    instance_count = var.core_instance_count

    ebs_config {
      size = var.core_ebs_volume_size
      type = var.core_ebs_volume_type
      iops = var.core_ebs_volume_iops
    }
  }

  ec2_attributes {
    instance_profile                  = var.instance_profile_name
    key_name                          = var.key_name
    subnet_id                         = var.subnet_id
    additional_master_security_groups = aws_security_group.master.id
  }

  step {
    action_on_failure = "TERMINATE_CLUSTER"
    name              = "Enable Hadoop debugging"

    hadoop_jar_step {
      jar  = "command-runner.jar"
      args = ["state-pusher-script"]
    }
  }

  lifecycle {
    ignore_changes = [step]
  }
}
