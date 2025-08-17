# Terraform variables for Vosk STT API service

variable "region" {
  description = "OCI region for deployment"
  type = string
  default = "us-ashburn-1"
}

# The following authentication variables are automatically provided by OCI Resource Manager:
# - tenancy_ocid
# - user_ocid  
# - fingerprint
# - private_key_path

variable "compartment_id" {
  description = "OCI compartment ID"
  type = string
}

variable "availability_domain" {
  description = "Availability domain"
  type = string
}

variable "vm_shape" {
  description = "The shape of the compute instance. Free Tier: E2.1.Micro (1 OCPU/1GB) or A1.Flex (up to 4 OCPU/24GB)"
  type = string
  default = "VM.Standard.A1.Flex"
}

variable "vm_ocpus" {
  description = "Number of OCPUs for flexible shapes. Free Tier A1.Flex supports up to 4 OCPUs."
  type = number
  default = 2
  validation {
    condition = var.vm_ocpus >= 1 && var.vm_ocpus <= 64
    error_message = "OCPUs must be between 1 and 64. Note: Free Tier A1.Flex allows up to 4 OCPUs."
  }
}

variable "vm_memory_gb" {
  description = "Memory in GB for flexible shapes. Free Tier A1.Flex supports up to 24 GB. Minimum 6 GB recommended for STT workloads."
  type = number
  default = 8
  validation {
    condition = var.vm_memory_gb >= 1 && var.vm_memory_gb <= 1024
    error_message = "Memory must be between 1 and 1024 GB. Note: Free Tier A1.Flex allows up to 24 GB, minimum 6 GB recommended for STT."
  }
}

variable "create_vcn" {
  description = "Create new VCN and subnet (true) or use existing (false)"
  type = bool
  default = true
}

variable "subnet_id" {
  description = "Subnet ID (required if create_vcn is false)"
  type = string
  default = ""
}

variable "vcn_id" {
  description = "VCN ID (required if create_vcn is false)"
  type = string
  default = ""
}

variable "image_id" {
  description = "Base image ID (Oracle Linux 8). Leave empty to auto-detect latest image for the region."
  type = string
  default = ""
}

variable "compute_image_strategy" {
  description = "Choose between Platform Image or Custom Image"
  type = string
  default = "Platform Image"
}

variable "operating_system" {
  description = "Operating system for Platform Images"
  type = string
  default = "Oracle Linux"
}

variable "platform_image_ocid" {
  description = "Platform image OCID for selected operating system"
  type = string
  default = ""
}

variable "custom_image_ocid" {
  description = "Custom image OCID (should be based on Oracle Linux 8+)"
  type = string
  default = ""
}

variable "compute_image_strategy_enum" {
  type = map(any)
  default = {
    PLATFORM_IMAGE = "Platform Image"
    CUSTOM_IMAGE   = "Custom Image"
  }
}

variable "ssh_authorized_keys" {
  description = "SSH authorized keys for instance access (optional, leave empty to disable SSH login)"
  type = string
  default = ""
}

variable "api_key" {
  description = "API key for the STT service (must be changed before deployment)"
  type = string
  sensitive = true
  validation {
    condition = var.api_key != "please-change-this-api-key" && length(var.api_key) >= 16
    error_message = "API key must be changed from default and be at least 16 characters long."
  }
}

variable "docker_image_name" {
  description = "Docker image name for the STT API"
  type = string
  default = "vosk-stt-api:latest"
}

variable "github_repo_url" {
  description = "GitHub repository URL for the project"
  type = string
  default = "https://github.com/kouko/oci-vosk-speech2text-api-service.git"
}