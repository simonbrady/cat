# Terraform Template

This directory contains a [Terraform](https://terraform.io) template to deploy an EMR cluster
and configure [debugging](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-debugging.html)
on it. To deploy, edit the variables in [common.mk](../common.mk) and [terraform.tfvars](terraform.tfvars)
then do:
```
make cluster
```

To terminate the cluster when you've finshed, simply do:
```
make terminate
```

If you choose to deploy your cluster without using the template, you should set the `CLUSTER`
variable in [common.mk](../common.mk) to its ID so other components can find it.
