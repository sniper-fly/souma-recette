# Terraform Review Perspectives - Detailed Criteria

This document provides comprehensive review criteria for each perspective when reviewing Terraform implementation plans.

## 1. Resource Design

### Dependencies
- [ ] Explicit `depends_on` for resources with implicit dependencies
- [ ] Proper use of `for_each` vs `count` for dynamic resources
- [ ] Resource references use proper interpolation (`resource.name.attribute`)
- [ ] No circular dependencies

### Configuration Consistency
- [ ] Consistent use of locals for repeated values
- [ ] Variables have appropriate types and defaults
- [ ] No hardcoded values that should be variables
- [ ] Consistent use of data sources vs resources

### Lifecycle Management
- [ ] `create_before_destroy` for zero-downtime updates
- [ ] `prevent_destroy` for critical resources
- [ ] `ignore_changes` for externally managed attributes
- [ ] Proper handling of `replace_triggered_by`

### Common Issues
```hcl
# Bad: Missing lifecycle for critical database
resource "aws_db_instance" "main" {
  identifier = "production-db"
  # Missing: lifecycle { prevent_destroy = true }
}

# Good: Protected critical resource
resource "aws_db_instance" "main" {
  identifier = "production-db"

  lifecycle {
    prevent_destroy = true
  }
}
```

## 2. Security

### IAM Permissions
- [ ] Principle of least privilege applied
- [ ] No wildcard (`*`) actions unless justified
- [ ] No wildcard resources unless justified
- [ ] Conditions used where applicable
- [ ] Service-linked roles preferred over custom roles

### Network Settings
- [ ] Security groups have minimal required ingress rules
- [ ] No `0.0.0.0/0` for sensitive ports (SSH, RDP, DB)
- [ ] VPC endpoints used for AWS service access
- [ ] Network ACLs complement security groups
- [ ] Private subnets used for internal resources

### Secrets Management
- [ ] No plaintext secrets in Terraform files
- [ ] Secrets stored in AWS Secrets Manager / Parameter Store
- [ ] `sensitive = true` for sensitive variables
- [ ] No secrets in terraform.tfvars committed to git

### Common Issues
```hcl
# Bad: Overly permissive IAM policy
resource "aws_iam_policy" "bad" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:*"]
      Resource = ["*"]
    }]
  })
}

# Good: Scoped permissions
resource "aws_iam_policy" "good" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.data.arn,
        "${aws_s3_bucket.data.arn}/*"
      ]
    }]
  })
}
```

## 3. Operations

### Naming Conventions
- [ ] Consistent naming pattern across resources
- [ ] Environment prefix/suffix included
- [ ] Names reflect resource purpose
- [ ] No special characters that cause issues

### Tagging Strategy
- [ ] Required tags present (Environment, Project, Owner, CostCenter)
- [ ] Consistent tag keys and values
- [ ] Tags applied via `default_tags` provider block
- [ ] Resource-specific tags where needed

### Module Structure
- [ ] Modules have clear, single responsibility
- [ ] Module inputs validated with `validation` blocks
- [ ] Outputs expose necessary values
- [ ] Module version pinned in source

### State Management
- [ ] Remote backend configured for team environments
- [ ] State locking enabled (DynamoDB for S3 backend)
- [ ] State file encryption enabled
- [ ] Appropriate state file granularity (not too large)

### Common Issues
```hcl
# Bad: No tagging strategy
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = "t3.micro"
  # No tags
}

# Good: Comprehensive tagging
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = "t3.micro"

  tags = merge(var.common_tags, {
    Name      = "${var.project}-${var.environment}-web"
    Component = "web-server"
  })
}
```

## 4. Cost

### Resource Sizing
- [ ] Instance types appropriate for workload
- [ ] Auto-scaling configured where beneficial
- [ ] Spot instances considered for fault-tolerant workloads
- [ ] Reserved capacity considered for predictable workloads

### Unused Resources
- [ ] No orphaned EBS volumes
- [ ] No unused Elastic IPs
- [ ] No idle load balancers
- [ ] No empty security groups

### Cost Optimization Options
- [ ] S3 lifecycle policies for old objects
- [ ] RDS storage auto-scaling enabled
- [ ] NAT Gateway vs NAT Instance evaluated
- [ ] Data transfer costs considered

### Common Issues
```hcl
# Bad: Over-provisioned for dev environment
resource "aws_instance" "dev" {
  instance_type = "r5.4xlarge"  # 16 vCPU, 128GB RAM for dev?
}

# Good: Right-sized with variable
resource "aws_instance" "dev" {
  instance_type = var.environment == "prod" ? "r5.4xlarge" : "t3.medium"
}
```

## 5. Constraints and Risks

### Service Limits
- [ ] Aware of regional service quotas
- [ ] No assumptions about default limits
- [ ] Quota increases requested proactively

### Region Dependencies
- [ ] Resources in correct region
- [ ] Multi-region considerations documented
- [ ] Region-specific features accounted for

### Provider Constraints
- [ ] Provider version constraints specified
- [ ] Required providers block present
- [ ] Terraform version constraint specified

### Common Issues
```hcl
# Bad: No version constraints
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      # Missing version constraint
    }
  }
}

# Good: Pinned versions
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

## AWS-Specific Checks

### EC2
- [ ] IMDSv2 enforced (`metadata_options.http_tokens = "required"`)
- [ ] EBS volumes encrypted
- [ ] Appropriate placement groups for HPC

### RDS
- [ ] Multi-AZ for production
- [ ] Automated backups enabled
- [ ] Performance Insights enabled
- [ ] Storage encryption enabled

### S3
- [ ] Public access blocked by default
- [ ] Versioning enabled for important data
- [ ] Server-side encryption configured
- [ ] Lifecycle policies for cost management

### Lambda
- [ ] Reserved concurrency set appropriately
- [ ] VPC configuration if accessing private resources
- [ ] Memory and timeout tuned

## GCP-Specific Checks

### Compute Engine
- [ ] Shielded VM options enabled
- [ ] Service account with minimal permissions
- [ ] Labels applied consistently

### Cloud SQL
- [ ] High availability for production
- [ ] Automated backups enabled
- [ ] Private IP preferred over public

### GCS
- [ ] Uniform bucket-level access
- [ ] Versioning for important data
- [ ] Lifecycle rules configured

## Azure-Specific Checks

### Virtual Machines
- [ ] Managed disks used
- [ ] Availability zones/sets for HA
- [ ] Azure Hybrid Benefit evaluated

### Azure SQL
- [ ] Zone redundancy for production
- [ ] Threat detection enabled
- [ ] Auditing configured

### Storage Accounts
- [ ] Secure transfer required
- [ ] Network rules configured
- [ ] Soft delete enabled
