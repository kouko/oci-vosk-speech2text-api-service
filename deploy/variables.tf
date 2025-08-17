# Terraform variables for Vosk STT API service

variable "region" {
  description = "OCI region"
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
  description = "VM shape (e.g., VM.Standard.E2.Flex for flexible, VM.Standard.E2.1.Micro for free tier)"
  type = string
  default = "VM.Standard.E2.1.Micro"
}

variable "vm_ocpus" {
  description = "Number of OCPUs for flexible shapes"
  type = number
  default = 1
}

variable "vm_memory_gb" {
  description = "Memory in GB for flexible shapes"
  type = number
  default = 6
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
  description = "Base image ID (Oracle Linux 8)"
  type = string
  # Oracle Linux 8 image OCID for us-ashburn-1
  default = "ocid1.image.oc1.iad.aaaaaaaa6tp7lhyrcokdtf7vrbmxyp2pctgg4uxvqere5gv2be6et62lx3q"
}

variable "ssh_authorized_keys" {
  description = "SSH authorized keys for instance access"
  type = string
}

variable "api_key" {
  description = "API key for the STT service"
  type = string
  sensitive = true
  default = "please-change-this-api-key"
}

variable "docker_image_name" {
  description = "Docker image name for the STT API"
  type = string
  default = "vosk-stt-api:latest"
}