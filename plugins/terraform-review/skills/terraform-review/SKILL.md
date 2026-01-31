---
name: Terraform Review
description: This skill should be used when the user asks to "review Terraform code", "Terraform plan review", "check Terraform implementation", "validate infrastructure code", "IaC review", or mentions reviewing Terraform plans, modules, or infrastructure-as-code for production readiness.
version: 0.1.0
---

# Terraform Implementation Plan Review

## Purpose

This skill provides a structured approach to reviewing Terraform implementation plans before deployment. The focus is on identifying technical issues that should be fixed before implementation begins, with emphasis on production stability and minimizing operational burden.

## When to Use

- Reviewing Terraform implementation plans or designs
- Pre-deployment infrastructure code review
- Validating Terraform module configurations
- Assessing infrastructure-as-code for production readiness

## Review Process

### Step 1: Establish Review Perspectives

Before reviewing, identify applicable review perspectives based on the plan content. Common perspectives include:

| Category | Focus Areas |
|----------|-------------|
| Resource Design | Dependencies, configuration consistency, lifecycle management |
| Security | IAM permissions, network settings, secrets management |
| Operations | Naming conventions, tagging, module structure, state management |
| Cost | Resource sizing, unused resources, cost optimization options |
| Constraints/Risks | Service limits, quotas, region dependencies |

Adapt perspectives based on the specific plan. Add domain-specific perspectives as needed (e.g., compliance for regulated industries).

### Step 2: Execute Review

Examine the plan against each perspective. For categories with no issues, document as "Confirmed - No issues found."

### Step 3: Document Findings

Use the standard output format for each issue found.

## Output Format

For each issue discovered:

```markdown
### Issue N: [Issue Title]
- **Location**: Filename/Section, specific configuration item
- **Problem**: What is wrong, why it's a problem
- **Severity**: High/Medium/Low
  - High: Deployment failure, security vulnerability, data loss risk
  - Medium: Operational difficulty, scalability constraints, maintainability issues
  - Low: Best practice deviation, readability concerns
- **Recommendation**: Suggested fix (include code example if applicable)
```

Conclude with a summary:
```markdown
---
**Summary**: X issues found
- High: N
- Medium: N
- Low: N
```

## Review Perspectives Details

For comprehensive review criteria and checklists, see:
- **`references/review-perspectives.md`** - Detailed review criteria per category

## Example Output

For a complete review example, see:
- **`examples/sample-review-output.md`** - Sample Terraform review output

## Key Principles

1. **Production stability first**: Prioritize issues affecting production reliability
2. **Operational burden**: Identify configurations that increase operational complexity
3. **Actionable feedback**: Provide specific, implementable recommendations
4. **No false positives**: Only report genuine issues, not stylistic preferences
5. **Context-aware**: Adapt severity based on the deployment target (dev vs prod)

## Common Issue Patterns

### High Severity Patterns
- Missing required provider configuration
- Hardcoded secrets or credentials
- Overly permissive IAM policies (`*` wildcards)
- No state backend configuration for team environments
- Missing lifecycle rules causing accidental resource destruction

### Medium Severity Patterns
- Inconsistent naming conventions
- Missing or incomplete tagging strategy
- No resource dependencies explicitly defined
- Missing output values for inter-module communication
- Suboptimal resource sizing

### Low Severity Patterns
- Variable descriptions missing
- No validation rules on variables
- Inconsistent formatting
- Missing README documentation
