# Deployer IAM Policies (`nibblaiapp`)

These are the **least-privilege** customer-managed policies for the Terraform
deployer user `nibblaiapp`. They are managed **out-of-band via the AWS CLI**
(not Terraform) on purpose — `nibblaiapp` is the identity Terraform runs as,
so managing its own permissions in Terraform state risks a mid-apply lockout.

> Replace `<AWS_ACCOUNT_ID>` in the JSON files with your 12-digit account ID,
> and set `nibblaiapp` to your actual deployer IAM username, before applying.

| Policy | ARN | Purpose |
|---|---|---|
| `NibblAI-TerraformInfra` | `arn:aws:iam::<AWS_ACCOUNT_ID>:policy/NibblAI-TerraformInfra` | ec2/rds/ecr/s3/dynamodb/kms — region-locked to `us-west-1` + scoped to our buckets/table/repos |
| `NibblAI-TerraformIAM` | `arn:aws:iam::<AWS_ACCOUNT_ID>:policy/NibblAI-TerraformIAM` | IAM writes scoped to `nibblai-*` roles/instance-profiles/policies + the GitHub OIDC provider; `PassRole` only the EC2 role. Read-only IAM elsewhere. **No privilege escalation.** |

Note the policies are named `NibblAI-*` (capitalized) so they fall **outside** the
`policy/nibblai-*` self-manage scope — `nibblaiapp` cannot widen its own grants;
only an admin/root can edit these (separation of duties).

## Apply / update (run as an admin or root, not as nibblaiapp after hardening)
```bash
# create
aws iam create-policy --policy-name NibblAI-TerraformInfra --policy-document file://NibblAI-TerraformInfra.json
# update (new default version)
aws iam create-policy-version --policy-arn arn:aws:iam::<AWS_ACCOUNT_ID>:policy/NibblAI-TerraformInfra \
  --policy-document file://NibblAI-TerraformInfra.json --set-as-default
```

## Rollback (re-grant broad access if ever locked out)
```bash
for p in IAMFullAccess AmazonEC2FullAccess AmazonRDSFullAccess AmazonS3FullAccess \
         AmazonDynamoDBFullAccess AmazonEC2ContainerRegistryFullAccess; do
  aws iam attach-user-policy --user-name nibblaiapp --policy-arn arn:aws:iam::aws:policy/$p
done
```
Root account is the ultimate break-glass (console).
