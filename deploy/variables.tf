# Terraform variables for Vosk STT API service

variable "region" {
  description = "OCI region for deployment"
  type = string
  default = "us-ashburn-1"
}

variable "tenancy_ocid" {
  description = "OCI tenancy OCID"
  type = string
}

variable "user_ocid" {
  description = "OCI user OCID"
  type = string
}

variable "fingerprint" {
  description = "OCI user fingerprint"
  type = string
}

variable "private_key_path" {
  description = "Path to OCI user private key"
  type = string
}

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
  description = "Number of OCPUs for flexible shapes (1-8). Each OCPU supports 1-16 GB RAM."
  type = number
  default = 2
  validation {
    condition = var.vm_ocpus >= 1 && var.vm_ocpus <= 8
    error_message = "OCPUs must be between 1 and 8."
  }
}

variable "vm_memory_gb" {
  description = "Memory in GB for flexible shapes (1-128). Recommend 6-8 GB for STT workloads."
  type = number
  default = 8
  validation {
    condition = var.vm_memory_gb >= 1 && var.vm_memory_gb <= 128
    error_message = "Memory must be between 1 and 128 GB."
  }
  validation {
    condition = var.vm_memory_gb <= var.vm_ocpus * 16
    error_message = "Memory cannot exceed 16 GB per OCPU (current limit: ${var.vm_ocpus * 16} GB)."
  }
  validation {
    condition = !(var.vm_shape == "VM.Standard.A1.Flex" && var.vm_ocpus > 4)
    error_message = "A1.Flex Free Tier is limited to 4 OCPUs. Choose fewer OCPUs or upgrade to paid tier."
  }
  validation {
    condition = !(var.vm_shape == "VM.Standard.A1.Flex" && var.vm_memory_gb > 24)
    error_message = "A1.Flex Free Tier is limited to 24 GB RAM. Choose less memory or upgrade to paid tier."
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

variable "ssh_authorized_keys" {
  description = "SSH authorized keys for instance access (required)"
  type = string
  validation {
    condition = length(var.ssh_authorized_keys) > 0
    error_message = "SSH authorized keys must be provided for secure access."
  }
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