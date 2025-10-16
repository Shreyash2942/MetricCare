## step 1 install terraform 
- installing terraform
```bash
    wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    sudo apt update && sudo apt install terraform
```
- check terraform is install or not
```bash
    terraform -verson
```
- file structure
```bazaar
    project-root/
├── main.tf                   # Entry point: calls modules, providers, backends
├── variables.tf              # Input variables
├── outputs.tf                # Output values
├── provider.tf               # AWS provider config (or keep inside main.tf)
├── terraform.tfvars          # Default variable values (optional)
│
├── modules/                  # Reusable modules
│   ├── s3_bucket/            # Example module for S3
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   ├── glue_jobs/            # Example module for Glue jobs
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   └── glue_workflow/        # Example module for Glue workflow/triggers
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
├── environments/             # Env-specific configurations
│   ├── dev/
│   │   └── dev.tfvars
│   ├── qa/
│   │   └── qa.tfvars
│   └── prod/
│       └── prod.tfvars
│
└── README.md                 # Documentation

    
```
---

## step 2 setup AWS credential
- step1
```bash
    mkdir module
    nano module/credentials
```

- step2 copy your AWS credential
```bash
[default]
aws_access_key_id = your_aws_aws_access_key
aws_secret_access_key = your_aws_secret_access_key
```

- step 3 configure aws provider
```bash
provider "aws" {
  region = "Your region"   
  shared_credentials_files = ["${path.module}/module/credentials"]
  profile = "default"  # AWS credential
}
```
- step 4 validate configuration
```bash
terrafom init
```

```bash
terraform validate
```

```bash
terraform test
```

- step 5 creating terraform enviroment

```bash
    terraform new workspace <Environment Name>
```

- step-6 changing environment
```bash
terraform select <Environment Name>
```

- step 7 Running terraform script according your workspace environment

### **plan**
```bash
  terraform plan -var-file=./environments/dev/dev.tfvars
```
### **apply**
```bash
  terraform apply -var-file=./environments/dev/dev.tfvars
```

### **destroy**

```bash
  terraform destory -var-file=./environments/dev/dev.tfvars
```

---

# step 3 create terraform services
- creating s3 bucket
- creating s3 module that upload glue script
- creating glue module that create glue job according the script
- creating glue workflow
- 
    

## 🌐 HelpFull resources

* [Install terraform on docker container](https://developer.hashicorp.com/terraform/install#linux)
* [creating s3 bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket)
* [creating module that upload script into S3]()
* [creating AWS glue job](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_job)
* [creating glue workflow]()
* [uploading athena scripts]()
* [creating lambda funtion]()