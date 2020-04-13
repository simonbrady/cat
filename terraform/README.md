# Terraform Template

This directory contains a [Terraform](https://terraform.io) template to deploy an EMR cluster
and configure [debugging](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-debugging.html)
on it. To deploy, edit the variables in [terraform.tfvars](terraform.tfvars) then do:
```
make cluster
```

The `key_name` variable shoud match the value of `KEYPAIR` set in [common.mk](../common.mk).

To terminate the cluster when you've finshed, simply do:
```
make terminate
```

If you choose to deploy your cluster without using the template, you should set the CLUSTER
environment variable to its ID since other components' Makefiles expect this to resolve to
the cluster ID.
