# Workload federation design extension

The source platform uses managed identities and GitHub OIDC in Azure. These two neutral JSON templates show how an equivalent exact-subject trust can be expressed for Entra and AWS; they do not commission AWS or grant permissions.

Do not blindly construct a legacy `repo:owner/name:ref:refs/heads/main` subject. GitHub's documented immutable OIDC subject behavior can apply to newly created repositories. Observe and review the exact subject for the intended repository/environment, without publishing its bearer token, then set that exact subject and audience in the provider. Do not use wildcard subjects. The AWS account placeholder and Entra credential have no actual authority until an administrator reviews and installs them.

Trusting the identity is only half of the design: scope its cloud permissions to required resources and verify both allowed and denied actions. Keep provisioning identities separate from app-runtime identities. Tokens identify a workload; they do not automatically authorize an application record.
