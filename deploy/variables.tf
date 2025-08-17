# Terraform variables for Vosk STT API service

# region is automatically provided by OCI Resource Manager

variable "compartment_id" {
  description = "OCI compartment ID for compute resources"
  type = string
}

variable "availability_domain" {
  description = "Availability domain"
  type = string
}

variable "api_key" {
  description = "API key for STT service authentication"
  type = string
  sensitive = true
  
  validation {
    condition = length(var.api_key) >= 16
    error_message = "API key must be at least 16 characters long."
  }
}

variable "ssh_authorized_keys" {
  description = "SSH public key for instance access (optional)"
  type = string
  default = ""
}

variable "vm_shape" {
  description = "The shape of the compute instance"
  type = string
  default = "VM.Standard.A1.Flex"
  
  validation {
    condition = contains([
      "VM.Standard.E2.1.Micro",
      "VM.Standard.A1.Flex", 
      "VM.Standard.E3.Flex",
      "VM.Standard.E4.Flex"
    ], var.vm_shape)
    error_message = "VM shape must be one of the supported types."
  }
}

variable "vm_ocpus" {
  description = "Number of OCPUs for flexible shapes"
  type = number
  default = 2
  
  validation {
    condition = var.vm_ocpus >= 1 && var.vm_ocpus <= 8
    error_message = "OCPUs must be between 1 and 8. Free Tier A1.Flex allows up to 4 OCPUs."
  }
}

variable "vm_memory_gb" {
  description = "Memory in GB for flexible shapes"
  type = number
  default = 8
  
  validation {
    condition = var.vm_memory_gb >= 6 && var.vm_memory_gb <= 24
    error_message = "Memory must be between 6 and 24 GB. Free Tier A1.Flex allows up to 24 GB."
  }
}