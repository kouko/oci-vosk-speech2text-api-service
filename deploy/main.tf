# Terraform configuration for OCI Vosk STT API service

terraform {
  required_providers {
    oci = {
      source = "oracle/oci"
      version = ">= 4.0"
    }
  }
}

# OCI Resource Manager automatically provides authentication and region
provider "oci" {
  # region is automatically provided by Resource Manager
}

# Get the latest Oracle Linux 8 image for the current region
data "oci_core_images" "oracle_linux" {
  compartment_id   = var.compartment_id
  operating_system = "Oracle Linux"
  operating_system_version = "8"
  shape = var.vm_shape
  sort_by = "TIMECREATED"
  sort_order = "DESC"
}

# Locals for derived values
locals {
  # Select latest Oracle Linux 8 image for the shape
  selected_image_id = data.oci_core_images.oracle_linux.images[0].id
  
  # Determine shape config
  is_flexible_shape = contains(["VM.Standard.A1.Flex", "VM.Standard.E3.Flex", "VM.Standard.E4.Flex"], var.vm_shape)
}

# VCN
resource "oci_core_vcn" "stt_vcn" {
  compartment_id = var.compartment_id
  cidr_blocks    = ["10.0.0.0/16"]
  display_name   = "vosk-stt-vcn"
  dns_label      = "voskstt"
}

# Internet Gateway
resource "oci_core_internet_gateway" "stt_igw" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.stt_vcn.id
  display_name   = "vosk-stt-igw"
}

# Route table
resource "oci_core_route_table" "stt_route_table" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.stt_vcn.id
  display_name   = "vosk-stt-route-table"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.stt_igw.id
  }
}

# Security list
resource "oci_core_security_list" "stt_security_list" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.stt_vcn.id
  display_name   = "vosk-stt-security-list"

  # Outbound rules
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  # Inbound rules
  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 8000
      max = 8000
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 443
      max = 443
    }
  }
}

# Subnet
resource "oci_core_subnet" "stt_subnet" {
  compartment_id    = var.compartment_id
  vcn_id            = oci_core_vcn.stt_vcn.id
  cidr_block        = "10.0.1.0/24"
  display_name      = "vosk-stt-subnet"
  dns_label         = "sttsubnet"
  route_table_id    = oci_core_route_table.stt_route_table.id
  security_list_ids = [oci_core_security_list.stt_security_list.id]
}

# Compute instance
resource "oci_core_instance" "stt_api_instance" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_id
  display_name        = "vosk-stt-api"
  shape               = var.vm_shape

  # Shape config for flexible shapes
  dynamic "shape_config" {
    for_each = local.is_flexible_shape ? [1] : []
    content {
      ocpus         = var.vm_ocpus
      memory_in_gbs = var.vm_memory_gb
    }
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.stt_subnet.id
    display_name     = "vosk-stt-vnic"
    assign_public_ip = true
  }

  source_details {
    source_type = "image"
    source_id   = local.selected_image_id
  }

  metadata = {
    ssh_authorized_keys = var.ssh_authorized_keys != "" ? var.ssh_authorized_keys : null
    user_data = base64encode(templatefile("${path.module}/cloud-init.yaml", {
      api_key = var.api_key
    }))
  }

  freeform_tags = {
    "Project" = "vosk-stt-api"
    "Environment" = "production"
  }
}

# Outputs
output "instance_public_ip" {
  description = "Public IP address of the compute instance"
  value       = oci_core_instance.stt_api_instance.public_ip
}

output "api_url" {
  description = "API endpoint URL"
  value       = "http://${oci_core_instance.stt_api_instance.public_ip}:8000"
}

output "api_docs_url" {
  description = "API documentation URL"
  value       = "http://${oci_core_instance.stt_api_instance.public_ip}:8000/docs"
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = var.ssh_authorized_keys != "" ? "ssh opc@${oci_core_instance.stt_api_instance.public_ip}" : "SSH access disabled (no SSH key provided)"
}

output "logs_command" {
  description = "Command to view deployment logs"
  value       = "sudo tail -f /var/log/vosk-stt-deployment.log"
}

output "deployment_info" {
  description = "Complete deployment information"
  value = {
    instance_ip = oci_core_instance.stt_api_instance.public_ip
    api_url = "http://${oci_core_instance.stt_api_instance.public_ip}:8000"
    docs_url = "http://${oci_core_instance.stt_api_instance.public_ip}:8000/docs"
    ssh_command = var.ssh_authorized_keys != "" ? "ssh opc@${oci_core_instance.stt_api_instance.public_ip}" : "SSH access disabled"
    logs_command = "sudo tail -f /var/log/vosk-stt-deployment.log"
  }
}