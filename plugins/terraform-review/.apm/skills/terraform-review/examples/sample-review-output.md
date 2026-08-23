# Sample Terraform Review Output

This is an example review output for a hypothetical Terraform implementation plan.

---

## Review Perspectives Identified

Based on the implementation plan, the following perspectives were applied:

1. Resource Design
2. Security
3. Operations
4. Cost
5. AWS Service Constraints

---

## Review Findings

### Issue 1: Missing State Backend Configuration

- **Location**: main.tf, terraform block
- **Problem**: No remote backend configured. Team collaboration will be hindered, and state could be lost or corrupted when multiple developers work on the infrastructure.
- **Severity**: High
- **Recommendation**: Add S3 backend with DynamoDB locking:

```hcl
terraform {
  backend "s3" {
    bucket         = "mycompany-terraform-state"
    key            = "project/prod/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
```

---

### Issue 2: Overly Permissive Security Group

- **Location**: modules/ec2/security.tf, resource "aws_security_group" "web"
- **Problem**: SSH access (port 22) is open to `0.0.0.0/0`. This exposes the instance to brute-force attacks from the internet.
- **Severity**: High
- **Recommendation**: Restrict SSH access to specific IP ranges or use Session Manager:

```hcl
ingress {
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["10.0.0.0/8"]  # Internal network only
  description = "SSH from internal network"
}
```

---

### Issue 3: No Lifecycle Protection on RDS Instance

- **Location**: modules/rds/main.tf, resource "aws_db_instance" "main"
- **Problem**: Production database has no `prevent_destroy` lifecycle rule. Accidental `terraform destroy` could delete the database.
- **Severity**: High
- **Recommendation**: Add lifecycle protection:

```hcl
resource "aws_db_instance" "main" {
  identifier = "production-db"
  # ... other configuration

  lifecycle {
    prevent_destroy = true
  }
}
```

---

### Issue 4: Inconsistent Tagging Strategy

- **Location**: Multiple files
- **Problem**: Some resources have Environment and Project tags, others don't. This makes cost allocation and resource management difficult.
- **Severity**: Medium
- **Recommendation**: Use `default_tags` in the provider block:

```hcl
provider "aws" {
  region = "ap-northeast-1"

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "terraform"
    }
  }
}
```

---

### Issue 5: Missing Variable Validation

- **Location**: variables.tf, variable "environment"
- **Problem**: Environment variable accepts any string. Typos could lead to misconfiguration.
- **Severity**: Low
- **Recommendation**: Add validation:

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

---

### Issue 6: Provider Version Not Pinned

- **Location**: versions.tf
- **Problem**: AWS provider version not constrained. Future updates could introduce breaking changes.
- **Severity**: Medium
- **Recommendation**: Pin provider version:

```hcl
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

---

## Confirmed - No Issues Found

- **Cost**: Resource sizing appears appropriate for the workload. Spot instances are used for batch processing. S3 lifecycle policies are configured.
- **AWS Service Constraints**: Resource counts are within default quotas. Region-specific features are accounted for.

---

## Summary

**Total Issues Found**: 6

| Severity | Count |
|----------|-------|
| High     | 3     |
| Medium   | 2     |
| Low      | 1     |

**Recommendation**: Address all High severity issues before implementation. Medium issues should be resolved before production deployment. Low issues can be addressed in subsequent iterations.
