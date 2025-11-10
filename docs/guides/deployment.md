# Deployment Guide

Complete guide to deploying Weave workflows across environments with provider, infrastructure, and deployment configuration.

## Table of Contents

- [Overview](#overview)
- [Provider Configuration](#provider-configuration)
- [Environment Configuration](#environment-configuration)
- [Infrastructure Configuration](#infrastructure-configuration)
- [Deployment Configuration](#deployment-configuration)
- [Complete Examples](#complete-examples)
- [Best Practices](#best-practices)

## Overview

Weave provides comprehensive deployment configuration for production-grade deployments:

- **Provider**: Cloud and infrastructure provider settings (AWS, Azure, GCP, Kubernetes)
- **Environment**: Staging and environment management (dev, staging, production)
- **Infrastructure**: Resource requirements and scaling configuration
- **Deployment**: Deployment strategies and health checks (rolling, blue-green, canary)

All configuration is declarative through YAML - no code required.

---

## Provider Configuration

Configure cloud and infrastructure providers.

```yaml
provider:
  provider: "aws"
  region: "us-east-1"
  credentials_source: "env"
```

### Supported Providers

- **local**: Local execution
- **aws**: Amazon Web Services
- **azure**: Microsoft Azure
- **gcp**: Google Cloud Platform
- **kubernetes**: Kubernetes cluster
- **docker**: Docker environment

### Configuration Options

```yaml
provider:
  # Provider identification
  provider: "aws"               # local, aws, azure, gcp, kubernetes, docker
  name: "production-aws"        # Provider instance name

  # Credentials
  credentials_source: "env"     # env, file, vault, keychain
  credentials_path: null        # Path to credentials file
  credentials_env_prefix: "AWS_"  # Environment variable prefix

  # Region/Location
  region: "us-east-1"           # Provider region
  zone: "us-east-1a"            # Availability zone

  # Provider-specific settings
  aws:
    account_id: "123456789012"
    iam_role: "weave-execution-role"
    kms_key_id: "alias/weave-key"

  # API configuration
  api_endpoint: null            # Custom API endpoint
  api_version: null             # API version
  timeout: 30.0                 # API timeout

  # Tags/Labels
  tags:
    project: "weave"
    environment: "production"
```

### AWS Example

```yaml
provider:
  provider: "aws"
  name: "production-aws"
  region: "us-east-1"
  zone: "us-east-1a"

  credentials_source: "env"
  credentials_env_prefix: "AWS_"

  aws:
    account_id: "123456789012"
    iam_role: "arn:aws:iam::123456789012:role/weave-executor"
    kms_key_id: "alias/weave-encryption"
    s3_bucket: "weave-artifacts"
    vpc_id: "vpc-1234567"
    subnet_ids:
      - "subnet-1234567a"
      - "subnet-1234567b"
    security_groups:
      - "sg-weave-agents"

  tags:
    project: "weave"
    environment: "production"
    managed_by: "terraform"
```

### Azure Example

```yaml
provider:
  provider: "azure"
  name: "production-azure"
  region: "eastus"

  credentials_source: "env"
  credentials_env_prefix: "AZURE_"

  azure:
    subscription_id: "12345678-1234-1234-1234-123456789012"
    resource_group: "weave-rg"
    tenant_id: "87654321-4321-4321-4321-210987654321"
    key_vault: "weave-keyvault"
    storage_account: "weaveartifacts"
    vnet: "weave-vnet"
    subnet: "weave-subnet"

  tags:
    project: "weave"
    environment: "production"
```

### GCP Example

```yaml
provider:
  provider: "gcp"
  name: "production-gcp"
  region: "us-central1"
  zone: "us-central1-a"

  credentials_source: "file"
  credentials_path: "/path/to/service-account.json"

  gcp:
    project_id: "my-project-id"
    service_account: "weave-sa@my-project.iam.gserviceaccount.com"
    kms_keyring: "weave-keyring"
    gcs_bucket: "weave-artifacts"
    vpc_network: "weave-network"
    vpc_subnet: "weave-subnet"

  tags:
    project: "weave"
    environment: "production"
```

### Kubernetes Example

```yaml
provider:
  provider: "kubernetes"
  name: "production-k8s"

  kubernetes:
    kubeconfig: "~/.kube/config"
    context: "production-cluster"
    namespace: "weave"
    service_account: "weave-executor"
    image_pull_secrets: ["dockerhub-secret"]

  tags:
    cluster: "production"
    namespace: "weave"
```

---

## Environment Configuration

Manage different environments (dev, staging, production).

```yaml
environment:
  name: "production"
  secrets_backend: "vault"
  require_approval: true
```

### Configuration Options

```yaml
environment:
  # Environment identification
  name: "production"              # dev, staging, production, test
  description: "Production environment"

  # Environment overrides
  config_overrides:
    runtime:
      mode: "parallel"
      max_concurrent_agents: 10
    observability:
      log_level: "WARNING"

  # Secrets management
  secrets_backend: "vault"        # env, vault, aws-secrets, azure-keyvault
  secrets_path: "secret/weave/production"

  # Environment variables
  env_vars:
    LOG_LEVEL: "INFO"
    API_TIMEOUT: "30"
  env_file: ".env.production"

  # Feature flags
  feature_flags:
    new_llm_provider: false
    experimental_tools: false
    beta_features: false

  # Promotion/Demotion
  promote_to: null                # Can't promote from production
  require_approval: true          # Require manual approval

  # Environment constraints
  max_concurrent_runs: 5
  allowed_models:
    - "gpt-4"
    - "claude-3-opus"
    # No experimental models in production
```

### Development Environment

```yaml
environment:
  name: "dev"
  description: "Development environment for testing"

  config_overrides:
    runtime:
      mode: "sequential"
      dry_run: false
      verbose: true
      debug: true
    observability:
      log_level: "DEBUG"
      log_to_console: true

  secrets_backend: "env"

  env_vars:
    DEBUG: "true"
    LOG_LEVEL: "DEBUG"

  feature_flags:
    new_llm_provider: true
    experimental_tools: true
    beta_features: true

  promote_to: "staging"
  require_approval: false

  max_concurrent_runs: 1
  allowed_models:  # All models allowed in dev
    - "*"
```

### Staging Environment

```yaml
environment:
  name: "staging"
  description: "Staging environment for pre-production testing"

  config_overrides:
    runtime:
      mode: "parallel"
      max_concurrent_agents: 3
    observability:
      log_level: "INFO"

  secrets_backend: "vault"
  secrets_path: "secret/weave/staging"

  env_file: ".env.staging"

  feature_flags:
    new_llm_provider: true
    experimental_tools: false
    beta_features: true

  promote_to: "production"
  require_approval: true

  max_concurrent_runs: 3
  allowed_models:
    - "gpt-4"
    - "gpt-3.5-turbo"
    - "claude-3-sonnet"
```

### Production Environment

```yaml
environment:
  name: "production"
  description: "Production environment"

  config_overrides:
    runtime:
      mode: "parallel"
      max_concurrent_agents: 10
      max_retries: 3
      enable_rate_limiting: true
    observability:
      log_level: "WARNING"
      enable_tracing: true
      collect_metrics: true

  secrets_backend: "aws-secrets"
  secrets_path: "weave/production"

  env_file: ".env.production"

  feature_flags:
    new_llm_provider: false
    experimental_tools: false
    beta_features: false

  promote_to: null
  require_approval: true

  max_concurrent_runs: 10
  allowed_models:
    - "gpt-4"
    - "claude-3-opus"
```

---

## Infrastructure Configuration

Define resource requirements and scaling.

```yaml
infrastructure:
  cpu: "2"
  memory: "4Gi"
  auto_scaling: true
  max_replicas: 10
```

### Configuration Options

```yaml
infrastructure:
  # Compute resources
  cpu: "2"                      # 2 CPUs
  memory: "4Gi"                 # 4GB RAM
  gpu: null                     # No GPU

  # Resource limits
  cpu_limit: "4"
  memory_limit: "8Gi"
  gpu_limit: null

  # Networking
  network_mode: "bridge"
  vpc_id: "vpc-1234567"
  subnet_ids:
    - "subnet-1234567a"
    - "subnet-1234567b"
  security_groups:
    - "sg-weave-agents"
  load_balancer: "weave-lb"

  # Storage
  persistent_volumes:
    - name: "weave-storage"
      size: "100Gi"
      storage_class: "gp3"
      mount_path: "/weave/storage"
  ephemeral_storage: "20Gi"

  # Scaling
  min_replicas: 2
  max_replicas: 10
  auto_scaling: true
  scaling_metric: "cpu"
  scaling_threshold: 70.0       # Scale up at 70% CPU

  # Container configuration
  image: "weave/runtime:latest"
  image_pull_policy: "IfNotPresent"
  command: ["/usr/bin/weave"]
  args: ["run", "--config", "/config/weave.yaml"]

  # Service mesh
  service_mesh: true
  service_mesh_type: "istio"

  # Labels and annotations
  labels:
    app: "weave"
    component: "agent-runtime"
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
```

### Kubernetes Deployment Example

```yaml
infrastructure:
  # Compute resources
  cpu: "1"
  memory: "2Gi"
  cpu_limit: "2"
  memory_limit: "4Gi"

  # Networking
  network_mode: "bridge"
  load_balancer: "weave-lb"

  # Storage
  persistent_volumes:
    - name: "weave-data"
      size: "50Gi"
      storage_class: "fast-ssd"
      mount_path: "/data"
    - name: "weave-cache"
      size: "20Gi"
      storage_class: "standard"
      mount_path: "/cache"
  ephemeral_storage: "10Gi"

  # Auto-scaling
  min_replicas: 2
  max_replicas: 20
  auto_scaling: true
  scaling_metric: "cpu"
  scaling_threshold: 75.0

  # Container
  image: "myregistry.io/weave:v1.0.0"
  image_pull_policy: "Always"
  command: ["/usr/local/bin/weave"]
  args: ["run", "--config", "/etc/weave/config.yaml"]

  # Service mesh
  service_mesh: true
  service_mesh_type: "istio"

  # Labels
  labels:
    app: "weave"
    version: "v1.0.0"
    environment: "production"
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "9090"
    sidecar.istio.io/inject: "true"
```

---

## Deployment Configuration

Configure deployment strategies and health checks.

```yaml
deployment:
  strategy: "rolling"
  health_check_enabled: true
  auto_rollback: true
```

### Configuration Options

```yaml
deployment:
  # Deployment identification
  name: "weave-production"
  version: "1.0.0"

  # Deployment strategy
  strategy: "rolling"           # rolling, blue-green, canary, recreate

  # Rolling update
  max_surge: "25%"
  max_unavailable: "25%"

  # Canary deployment
  canary_percentage: 10.0
  canary_increment: 10.0
  canary_interval: 300

  # Blue-green
  blue_green_active: "blue"

  # Health checks
  health_check_enabled: true
  health_check_path: "/health"
  health_check_interval: 10
  health_check_timeout: 5
  health_check_retries: 3

  # Readiness checks
  readiness_check_enabled: true
  readiness_check_path: "/ready"
  readiness_check_initial_delay: 30

  # Liveness checks
  liveness_check_enabled: true
  liveness_check_path: "/health"
  liveness_check_initial_delay: 60

  # Rollback
  auto_rollback: true
  rollback_on_failure: true
  rollback_threshold: 0.05      # Rollback at 5% error rate
  revision_history_limit: 10

  # CI/CD
  ci_cd_enabled: true
  ci_cd_provider: "github-actions"
  ci_cd_webhook: "https://api.github.com/repos/..."

  # Hooks
  pre_deploy_hooks:
    - "scripts/pre-deploy-check.sh"
    - "scripts/backup-state.sh"
  post_deploy_hooks:
    - "scripts/verify-deployment.sh"
    - "scripts/notify-team.sh"

  # Notifications
  notifications_enabled: true
  notification_channels:
    - "slack://deployments"
    - "email://ops-team@company.com"

  # Versioning
  versioning_strategy: "semantic"
  version_prefix: "v"

  # Deployment windows
  maintenance_windows:
    - start: "02:00"
      end: "04:00"
      timezone: "UTC"
  allow_deploy_on_weekend: false
  allow_deploy_on_holiday: false
```

### Rolling Deployment

```yaml
deployment:
  strategy: "rolling"
  max_surge: "50%"              # Allow 50% more pods during update
  max_unavailable: "0%"         # Keep all pods available

  health_check_enabled: true
  health_check_path: "/health"
  health_check_interval: 5
  health_check_retries: 5

  auto_rollback: true
  rollback_threshold: 0.01      # Rollback at 1% error rate
```

### Canary Deployment

```yaml
deployment:
  strategy: "canary"

  canary_percentage: 5.0        # Start with 5% traffic
  canary_increment: 5.0         # Increase by 5% each step
  canary_interval: 600          # Wait 10 minutes between steps

  health_check_enabled: true
  health_check_path: "/health"
  health_check_interval: 5

  auto_rollback: true
  rollback_threshold: 0.02      # Rollback at 2% error rate

  post_deploy_hooks:
    - "scripts/analyze-canary-metrics.sh"
```

### Blue-Green Deployment

```yaml
deployment:
  strategy: "blue-green"
  blue_green_active: "blue"     # Currently active environment

  health_check_enabled: true
  readiness_check_enabled: true
  readiness_check_initial_delay: 60

  # Switch traffic only after all checks pass
  health_check_retries: 10

  auto_rollback: true

  pre_deploy_hooks:
    - "scripts/prepare-green-environment.sh"
  post_deploy_hooks:
    - "scripts/switch-traffic.sh"
    - "scripts/cleanup-old-environment.sh"
```

---

## Complete Examples

### AWS Production Deployment

```yaml
version: "1.0"

# Provider configuration
provider:
  provider: "aws"
  name: "production"
  region: "us-east-1"
  zone: "us-east-1a"

  credentials_source: "env"

  aws:
    account_id: "123456789012"
    iam_role: "arn:aws:iam::123456789012:role/weave-prod"
    kms_key_id: "alias/weave-prod"
    s3_bucket: "weave-prod-artifacts"
    vpc_id: "vpc-prod123"
    subnet_ids:
      - "subnet-prod1a"
      - "subnet-prod1b"
    security_groups:
      - "sg-weave-prod"

  tags:
    environment: "production"
    project: "weave"
    cost_center: "engineering"

# Environment configuration
environment:
  name: "production"
  description: "Production environment with strict controls"

  config_overrides:
    runtime:
      mode: "parallel"
      max_concurrent_agents: 10
      max_retries: 3
      enable_rate_limiting: true
      requests_per_minute: 100
    observability:
      log_level: "INFO"
      enable_tracing: true
      collect_metrics: true
      metrics_endpoint: "http://prometheus:9090"

  secrets_backend: "aws-secrets"
  secrets_path: "weave/production"

  feature_flags:
    experimental_features: false
    beta_tools: false

  require_approval: true
  max_concurrent_runs: 10

  allowed_models:
    - "gpt-4"
    - "claude-3-opus"

# Infrastructure configuration
infrastructure:
  cpu: "4"
  memory: "16Gi"
  cpu_limit: "8"
  memory_limit: "32Gi"

  vpc_id: "vpc-prod123"
  subnet_ids:
    - "subnet-prod1a"
    - "subnet-prod1b"
  security_groups:
    - "sg-weave-prod"
  load_balancer: "weave-prod-lb"

  persistent_volumes:
    - name: "weave-storage"
      size: "500Gi"
      storage_class: "gp3"
      mount_path: "/weave/storage"

  min_replicas: 3
  max_replicas: 20
  auto_scaling: true
  scaling_metric: "cpu"
  scaling_threshold: 70.0

  labels:
    app: "weave"
    environment: "production"
    version: "v1.0.0"

# Deployment configuration
deployment:
  name: "weave-production"
  version: "1.0.0"

  strategy: "rolling"
  max_surge: "25%"
  max_unavailable: "0%"

  health_check_enabled: true
  health_check_path: "/health"
  health_check_interval: 10
  health_check_retries: 5

  readiness_check_enabled: true
  readiness_check_initial_delay: 30

  auto_rollback: true
  rollback_threshold: 0.01
  revision_history_limit: 10

  ci_cd_enabled: true
  ci_cd_provider: "github-actions"

  pre_deploy_hooks:
    - "scripts/backup-production.sh"
    - "scripts/pre-deploy-validation.sh"
  post_deploy_hooks:
    - "scripts/smoke-tests.sh"
    - "scripts/notify-stakeholders.sh"

  notifications_enabled: true
  notification_channels:
    - "slack://prod-deployments"
    - "pagerduty://on-call"

  maintenance_windows:
    - start: "02:00"
      end: "04:00"
      timezone: "UTC"
  allow_deploy_on_weekend: false
  allow_deploy_on_holiday: false

# Storage
storage:
  enabled: true
  base_path: "/weave/storage"
  format: "json"

# Observability
observability:
  enabled: true
  log_level: "INFO"
  log_format: "json"
  collect_metrics: true
  track_token_usage: true
  enable_tracing: true

# Runtime
runtime:
  mode: "parallel"
  max_concurrent_agents: 10
  max_retries: 3
  enable_rate_limiting: true

# Agents and weaves
agents:
  # ... agent definitions

weaves:
  # ... weave definitions
```

### Kubernetes Multi-Environment Setup

**dev.yaml**:
```yaml
version: "1.0"

provider:
  provider: "kubernetes"
  kubernetes:
    namespace: "weave-dev"
    context: "dev-cluster"

environment:
  name: "dev"
  promote_to: "staging"
  max_concurrent_runs: 1

infrastructure:
  cpu: "500m"
  memory: "1Gi"
  min_replicas: 1
  max_replicas: 1
  auto_scaling: false

deployment:
  strategy: "recreate"
  health_check_enabled: true

# ... agents and weaves
```

**staging.yaml**:
```yaml
version: "1.0"

provider:
  provider: "kubernetes"
  kubernetes:
    namespace: "weave-staging"
    context: "staging-cluster"

environment:
  name: "staging"
  promote_to: "production"
  require_approval: true

infrastructure:
  cpu: "1"
  memory: "2Gi"
  min_replicas: 2
  max_replicas: 5
  auto_scaling: true

deployment:
  strategy: "rolling"
  auto_rollback: true

# ... agents and weaves
```

**production.yaml**:
```yaml
version: "1.0"

provider:
  provider: "kubernetes"
  kubernetes:
    namespace: "weave-prod"
    context: "prod-cluster"

environment:
  name: "production"
  require_approval: true

infrastructure:
  cpu: "2"
  memory: "8Gi"
  min_replicas: 5
  max_replicas: 50
  auto_scaling: true

deployment:
  strategy: "canary"
  canary_percentage: 10.0
  auto_rollback: true

# ... agents and weaves
```

---

## Best Practices

### Provider Configuration

1. **Use environment variables for credentials**:
   - Never hardcode credentials
   - Use credential managers (Vault, AWS Secrets Manager)
   - Rotate credentials regularly

2. **Tag all resources**:
   - Environment, project, cost center
   - Owner, team information
   - Facilitates cost tracking and management

3. **Use region-specific configurations**:
   - Deploy close to users
   - Consider data residency requirements
   - Use multiple regions for disaster recovery

### Environment Configuration

1. **Separate configurations per environment**:
   - Different configs for dev, staging, production
   - Use config overrides appropriately
   - Test in staging before production

2. **Implement promotion workflows**:
   - Dev → Staging → Production
   - Require approvals for production
   - Automate promotion where safe

3. **Use feature flags**:
   - Gradually roll out new features
   - Quick rollback without deployment
   - A/B testing capabilities

### Infrastructure Configuration

1. **Right-size resources**:
   - Start conservative, scale up as needed
   - Monitor resource utilization
   - Use auto-scaling for variable load

2. **Set resource limits**:
   - Prevent resource exhaustion
   - Ensure fair resource allocation
   - Protect against runaway processes

3. **Use persistent storage**:
   - Store important data persistently
   - Regular backups
   - Test restore procedures

### Deployment Configuration

1. **Always use health checks**:
   - Prevent serving traffic to unhealthy instances
   - Detect failures quickly
   - Enable auto-remediation

2. **Enable auto-rollback**:
   - Automatic rollback on failures
   - Set appropriate thresholds
   - Monitor rollback frequency

3. **Use appropriate deployment strategy**:
   - Rolling for standard deployments
   - Canary for risky changes
   - Blue-green for zero-downtime

4. **Implement deployment hooks**:
   - Pre-deployment validation
   - Post-deployment verification
   - Automated testing

5. **Configure notifications**:
   - Alert on deployment failures
   - Notify on successful deployments
   - Integration with incident management

### Security

1. **Use secrets management**:
   - Never commit secrets to version control
   - Use dedicated secrets managers
   - Rotate secrets regularly

2. **Implement least privilege**:
   - Minimal IAM permissions
   - Role-based access control
   - Audit access regularly

3. **Enable security scanning**:
   - Scan container images
   - Check for vulnerabilities
   - Automated security updates

4. **Network security**:
   - Use VPCs and security groups
   - Implement service mesh for mTLS
   - Regular security audits

## Summary

- ✅ Configure providers for AWS, Azure, GCP, Kubernetes
- ✅ Manage multiple environments (dev, staging, production)
- ✅ Define infrastructure requirements and auto-scaling
- ✅ Implement deployment strategies (rolling, canary, blue-green)
- ✅ Configure health checks and auto-rollback
- ✅ Use secrets management and credential rotation
- ✅ Enable CI/CD integration
- ✅ Set up notifications and monitoring
- ✅ Follow security best practices

## Next Steps

- [Observability and Runtime Guide](observability-and-runtime.md)
- [Configuration Reference](../reference/configuration.md)
- [Testing Guide](testing.md)
- [Examples](../../examples/)
