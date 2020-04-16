data "aws_subnet" "master" {
  id = "${var.subnet_id}"
}
